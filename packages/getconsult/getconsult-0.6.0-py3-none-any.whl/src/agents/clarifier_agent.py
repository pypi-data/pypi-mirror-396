"""
Clarifier Agent for detecting ambiguous or incomplete queries.

This lightweight agent uses fast models (Haiku, GPT-4o-mini, Flash) to quickly
analyze queries and generate clarifying questions when needed.
"""

import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_core.models import ModelInfo

from ..config import Config, ProviderType


# Lightweight models for fast clarification
CLARIFIER_MODELS = {
    "anthropic": "claude-3-5-haiku-20241022",
    "openai": "gpt-4o-mini",
    "google": "gemini-2.0-flash-lite"
}


@dataclass
class ClarificationQuestion:
    """A single clarification question with options"""
    question: str
    options: List[str]
    multi_select: bool = False


@dataclass
class ClarificationResult:
    """Result of clarification analysis"""
    needs_clarification: bool
    questions: List[ClarificationQuestion] = field(default_factory=list)
    reasoning: str = ""


CLARIFIER_SYSTEM_MESSAGE = """You are a senior technical analyst performing triage on incoming queries before they reach a panel of domain experts. Your job: identify ONLY the ambiguities that would cause experts to waste cycles or diverge in incompatible directions.

## DECISION FRAMEWORK

Ask yourself: "If I gave this query to 5 senior engineers independently, would they interpret it the same way?"
- If YES → no clarification needed
- If NO → identify the specific fork points that cause divergence

## AMBIGUITY TAXONOMY (prioritized)

1. **Scope Ambiguity** [HIGH IMPACT] - What's in/out of bounds?
   - "Improve the API" → which endpoints? performance? DX? security?
   - "Fix the auth" → login flow? tokens? permissions? all of it?

2. **Constraint Ambiguity** [HIGH IMPACT] - What limits apply?
   - Backwards compatibility requirements?
   - Performance/latency budgets?
   - Technology restrictions?

3. **Success Criteria Ambiguity** [MEDIUM IMPACT] - How do we know we're done?
   - "Make it faster" → 10% faster? 10x faster? sub-100ms?
   - "Better UX" → for whom? measured how?

4. **Context Ambiguity** [MEDIUM IMPACT] - Missing situational info
   - Environment (prod/dev/local)?
   - Scale (10 users? 10M users?)?
   - Timeline (MVP? production-ready?)

5. **Implementation Ambiguity** [LOW IMPACT - usually skip]
   - Experts can decide implementation details
   - Only ask if choice fundamentally changes architecture

## QUESTION QUALITY CRITERIA

Each question MUST be:
- **Actionable**: Answer directly influences solution approach
- **Discriminating**: Options lead to meaningfully different solutions
- **Concrete**: Specific enough that user can answer confidently
- **Non-obvious**: Experts couldn't reasonably infer the answer

Bad: "What's your preference?" (vague, philosophical)
Good: "Should this handle real-time updates or is batch processing acceptable?" (concrete fork point)

## OPTION DESIGN

- 2-4 options per question (more causes decision paralysis)
- Options must be mutually exclusive (unless multi_select)
- Include a spectrum: conservative → aggressive, simple → comprehensive
- Each option should be a legitimate choice, not a strawman
- Phrase as noun phrases or short statements, not questions

## FOLLOW-UP QUERIES

When context indicates continuing conversation:
- User already has an answer and is drilling deeper
- The PREVIOUS SOLUTION is critical context - read it carefully
- Most follow-ups need NO clarification:
  - "Explain X more" → clear, just elaborate
  - "What about Y?" → clear, address Y
  - "Can you show code?" → clear, show code
- Only clarify if follow-up introduces NEW ambiguity not covered by prior context

## WHEN TO SKIP CLARIFICATION

- Query is already specific and actionable
- Context provides sufficient constraints
- Ambiguity is low-impact (experts can make reasonable default choices)
- Asking would feel pedantic or condescending
- Follow-up is clearly scoped by previous answer

## OUTPUT FORMAT

Return ONLY valid JSON (no markdown, no explanation outside JSON):

{
  "needs_clarification": boolean,
  "reasoning": "One sentence: why clarification helps or why query is already clear",
  "questions": [
    {
      "question": "Specific question targeting a fork point",
      "options": ["Concrete option A", "Concrete option B", "Concrete option C"],
      "multi_select": false
    }
  ]
}

Maximum 3 questions. If needs_clarification is false, questions must be empty array."""


def create_clarifier_model_client(provider: ProviderType):
    """Create a lightweight model client for clarification"""
    model = CLARIFIER_MODELS.get(provider)

    if provider == "openai":
        if not Config.OPENAI_API_KEY:
            return None
        return OpenAIChatCompletionClient(
            model=model,
            api_key=Config.OPENAI_API_KEY
        )
    elif provider == "anthropic":
        if not Config.ANTHROPIC_API_KEY:
            return None
        return AnthropicChatCompletionClient(
            model=model,
            api_key=Config.ANTHROPIC_API_KEY
        )
    elif provider == "google":
        if not Config.GOOGLE_API_KEY:
            return None
        return OpenAIChatCompletionClient(
            model=model,
            api_key=Config.GOOGLE_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model_info=ModelInfo(
                vision=False,
                function_calling=True,
                json_output=True,
                family="unknown",
                structured_output=True
            )
        )
    return None


class ClarifierAgent:
    """Agent that analyzes queries and generates clarifying questions if needed"""

    def __init__(self, provider: ProviderType = "anthropic"):
        """Initialize clarifier with specified provider

        Args:
            provider: Provider to use for clarification model
        """
        self.provider = provider
        self.model_client = create_clarifier_model_client(provider)

        if self.model_client is None:
            # Fallback to any available provider
            for fallback in ["anthropic", "openai", "google"]:
                self.model_client = create_clarifier_model_client(fallback)
                if self.model_client:
                    self.provider = fallback
                    break

        if self.model_client is None:
            raise ValueError("No valid API key found for clarifier agent")

        self._agent = AssistantAgent(
            name="clarifier",
            model_client=self.model_client,
            description="Query clarification specialist",
            system_message=CLARIFIER_SYSTEM_MESSAGE
        )

    async def analyze_query(self, query: str, context: Optional[str] = None) -> ClarificationResult:
        """Analyze a query and determine if clarification is needed

        Args:
            query: The user's query to analyze
            context: Optional context (e.g., from memory) to consider

        Returns:
            ClarificationResult with questions if clarification is needed
        """
        from autogen_agentchat.messages import TextMessage
        from autogen_core import CancellationToken

        # Build analysis prompt
        if context and "CONTINUING CONVERSATION" in context:
            # This is a follow-up - structure prompt to emphasize continuity
            prompt = f"""## SITUATION: Follow-up query in ongoing conversation

{context}

## NEW QUERY
{query}

## TASK
Analyze if this follow-up introduces ambiguity NOT already resolved by the conversation context.
Remember: most follow-ups are clarifying or drilling deeper - they rarely need additional clarification."""
        elif context:
            prompt = f"""## CONTEXT
{context}

## QUERY
{query}

## TASK
Identify fork points where 5 senior engineers might diverge. Only surface HIGH/MEDIUM impact ambiguities."""
        else:
            prompt = f"""## QUERY
{query}

## TASK
Identify fork points where 5 senior engineers might diverge. Only surface HIGH/MEDIUM impact ambiguities."""

        try:
            response = await self._agent.on_messages(
                [TextMessage(content=prompt, source="user")],
                CancellationToken()
            )

            # Parse JSON response
            response_text = response.chat_message.content

            # Clean up response - remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())

            # Convert to dataclass
            questions = []
            for q in result.get("questions", []):
                questions.append(ClarificationQuestion(
                    question=q["question"],
                    options=q["options"],
                    multi_select=q.get("multi_select", False)
                ))

            return ClarificationResult(
                needs_clarification=result.get("needs_clarification", False),
                questions=questions,
                reasoning=result.get("reasoning", "")
            )

        except (json.JSONDecodeError, KeyError) as e:
            # If parsing fails, assume no clarification needed
            return ClarificationResult(
                needs_clarification=False,
                reasoning=f"Failed to parse clarification response: {e}"
            )
        except Exception as e:
            # On any error, don't block the workflow
            return ClarificationResult(
                needs_clarification=False,
                reasoning=f"Clarification check failed: {e}"
            )

    def format_enhanced_query(self, original_query: str, responses: Dict[str, Any]) -> str:
        """Format the original query with clarification responses

        Args:
            original_query: The original user query
            responses: Dict mapping question text to user's response(s)

        Returns:
            Enhanced query string with clarifications incorporated
        """
        if not responses:
            return original_query

        clarifications = []
        for question, answer in responses.items():
            if isinstance(answer, list):
                answer_str = ", ".join(answer)
            else:
                answer_str = str(answer)
            clarifications.append(f"- {question}: {answer_str}")

        enhanced = f"""{original_query}

CLARIFICATIONS PROVIDED:
{chr(10).join(clarifications)}"""

        return enhanced
