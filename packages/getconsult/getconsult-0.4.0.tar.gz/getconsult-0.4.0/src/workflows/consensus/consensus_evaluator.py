"""
Consensus evaluation component - TRUE cross-expert approval

TRUE CONSENSUS: Not "how similar are we?" but "Would I sign off on THIS going to production?"

Each expert explicitly approves/objects to each other expert's solution.
Final consensus = aggregate of all pairwise approval scores.

Uses structured output (Pydantic models) for deterministic parsing.
"""

import asyncio
import json
import time
from typing import List, Dict, Optional
from autogen_agentchat.agents import AssistantAgent

from ..base.agent_communicator import AgentCommunicator
from ..base.workflow_state import WorkflowState
from ..base.events import EventEmitter, EventTypes
from ...prompts.prompts import Prompts
from ...agents.expert_registry import get_expert_config
from ...models.responses import CrossExpertApproval
from ...core.paths import get_logs_dir
from ...core.security import get_contextual_logger

# Module logger
_logger = None


def _get_logger():
    """Get or create the evaluator logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.evaluator", log_file=str(log_file))
    return _logger


class ConsensusEvaluator:
    """Handles TRUE consensus evaluation - cross-expert approval

    Old (flawed): Each expert rates "how aligned are we?" (self-assessed similarity)
    New (true): Each expert says "Would I approve THIS going to production?" (explicit approval)

    Uses structured output for deterministic parsing - no regex needed.
    """

    def __init__(self, communicator: AgentCommunicator, emitter: EventEmitter):
        self.communicator = communicator
        self.emitter = emitter
        self.logger = _get_logger()

    async def evaluate_consensus(self, agents: List[AssistantAgent], state: WorkflowState,
                                   threshold: float = 0.8) -> float:
        """Evaluate TRUE consensus via cross-expert approval (PARALLELIZED)

        Each expert reviews each other expert's solution and decides:
        "Would I sign off on this for production?"

        Args:
            agents: Expert agents to evaluate
            state: Current workflow state with solutions
            threshold: Consensus threshold (default 0.8) for event reporting

        Returns aggregate approval score (0.0-1.0)
        """
        self._threshold = threshold  # Store for event emission
        eval_start = time.time()
        num_pairs = len(agents) * (len(agents) - 1)  # Each evaluates all others

        self.logger.info(f"Consensus evaluation starting | {len(agents)} agents, {num_pairs} pairwise reviews")

        # Emit consensus evaluation start
        self.emitter.emit(EventTypes.CONSENSUS_EVALUATION_START)

        # Show all agents starting evaluation
        for evaluator in agents:
            self.emitter.emit(
                EventTypes.AGENT_THINKING,
                agent_name=evaluator.name,
                action="reviewing peers' solutions for production approval"
            )

        # Create pairwise approval tasks for parallel execution
        approval_tasks = []
        task_info = []  # Track which evaluator → target for each task

        for evaluator in agents:
            evaluator_solution = state.current_solutions[evaluator.name]['answer']

            for target in agents:
                if target.name == evaluator.name:
                    continue  # Don't approve own solution

                target_solution = state.current_solutions[target.name]['answer']

                task = self._get_cross_expert_approval(
                    evaluator, target,
                    evaluator_solution, target_solution
                )
                approval_tasks.append(task)
                task_info.append((evaluator.name, target.name))

        # Execute all approval evaluations in parallel
        approval_results = await asyncio.gather(*approval_tasks, return_exceptions=True)

        # Process results into approval matrix
        approval_matrix: Dict[str, Dict[str, Dict]] = {}
        all_approval_scores = []

        for evaluator in agents:
            approval_matrix[evaluator.name] = {}

        for (evaluator_name, target_name), result in zip(task_info, approval_results):
            if isinstance(result, Exception):
                score = 0.5  # Neutral on error
                verdict = "ERROR"
                approval_data = None
                self.logger.error(f"Approval FAILED: {evaluator_name} → {target_name} | {type(result).__name__}: {result}")
                self.emitter.emit(
                    EventTypes.WORKFLOW_ERROR,
                    message=f"Error in approval {evaluator_name} → {target_name}: {result}"
                )
            else:
                # Result is CrossExpertApproval (structured output)
                approval_data = result
                score = approval_data.approval_score
                verdict = approval_data.overall_verdict.replace('_', ' ')
                self.logger.debug(f"Approval: {evaluator_name} → {target_name} | {verdict} ({score:.2f})")

            approval_matrix[evaluator_name][target_name] = {
                'approval_data': approval_data,
                'score': score,
                'verdict': verdict
            }
            all_approval_scores.append(score)

            # Emit individual approval event
            self.emitter.emit(
                EventTypes.CROSS_EXPERT_APPROVAL,
                evaluator=evaluator_name,
                target=target_name,
                verdict=verdict,
                score=score,
                endorsements=approval_data.endorsements if approval_data else [],
                concerns=approval_data.concerns if approval_data else [],
                objections=approval_data.objections if approval_data else []
            )

        # Calculate final consensus score
        final_score = sum(all_approval_scores) / len(all_approval_scores) if all_approval_scores else 0.5

        # Build detailed evaluation summary
        agent_evaluations = self._build_evaluation_summary(agents, approval_matrix)

        # Determine interpretation
        interpretation = self._interpret_consensus(final_score, approval_matrix)

        eval_elapsed = time.time() - eval_start
        self.logger.info(f"Consensus evaluation complete | {eval_elapsed:.1f}s | "
                        f"score={final_score:.2f} vs threshold={threshold} | "
                        f"{'REACHED' if final_score >= threshold else 'NOT REACHED'}")

        # Emit comprehensive consensus check event
        self.emitter.emit(
            EventTypes.CONSENSUS_CHECK,
            agent_evaluations=agent_evaluations,
            approval_matrix=approval_matrix,
            individual_scores=all_approval_scores,
            final_score=final_score,
            threshold=self._threshold,
            reached=final_score >= self._threshold,
            interpretation=interpretation
        )

        return final_score

    def _get_expertise_areas(self, agent_name: str) -> Optional[List[str]]:
        """Extract expertise areas for an agent from registry"""
        expert_types = [
            "database_expert", "backend_expert", "infrastructure_expert",
            "software_architect", "cloud_engineer", "security_expert",
            "performance_expert", "frontend_expert", "ux_expert",
            "data_expert", "ml_expert"
        ]

        for expert_type in expert_types:
            if expert_type in agent_name:
                try:
                    config = get_expert_config(expert_type)
                    return config.expertise_areas
                except ValueError:
                    pass
        return None

    async def _get_cross_expert_approval(
        self,
        evaluator: AssistantAgent,
        target: AssistantAgent,
        evaluator_solution: str,
        target_solution: str
    ) -> CrossExpertApproval:
        """Get explicit approval/objection from evaluator for target's solution

        Uses structured output for OpenAI, JSON prompting for others.
        """
        expertise_areas = self._get_expertise_areas(evaluator.name)

        approval_prompt = Prompts.cross_expert_approval_prompt(
            evaluator_name=evaluator.name,
            target_name=target.name,
            target_solution=target_solution,
            evaluator_solution=evaluator_solution,
            evaluator_expertise_areas=expertise_areas
        )

        # Check if we need to add JSON instructions (non-OpenAI models)
        model_name = getattr(evaluator._model_client, 'model', '').lower()
        is_openai = 'gpt' in model_name or 'o1' in model_name or 'o3' in model_name

        if not is_openai:
            # Add JSON output instructions for non-OpenAI models
            approval_prompt += self._get_json_output_instructions()

        # Create structured output agent for this approval
        structured_agent = self._create_structured_approval_agent(evaluator)

        # Get response as structured output
        response = await self.communicator.get_response(structured_agent, approval_prompt)

        # Parse JSON response to CrossExpertApproval
        return self._parse_approval_response(response, evaluator.name, target.name)

    def _get_json_output_instructions(self) -> str:
        """Get JSON output instructions for non-OpenAI models."""
        return '''

---

## REQUIRED OUTPUT FORMAT

You MUST respond with ONLY a JSON object (no markdown, no explanation, just JSON).

```json
{
  "evaluator": "<your name>",
  "target": "<target expert name>",
  "requirements": {
    "dimension": "requirements",
    "verdict": "APPROVE|CONCERNS|OBJECT",
    "score": <0.0|0.7|1.0>,
    "reasoning": "<specific reasoning>"
  },
  "approach": {
    "dimension": "approach",
    "verdict": "APPROVE|CONCERNS|OBJECT",
    "score": <0.0|0.7|1.0>,
    "reasoning": "<specific reasoning>"
  },
  "tradeoffs": {
    "dimension": "tradeoffs",
    "verdict": "APPROVE|CONCERNS|OBJECT",
    "score": <0.0|0.7|1.0>,
    "reasoning": "<specific reasoning>"
  },
  "architecture": {
    "dimension": "architecture",
    "verdict": "APPROVE|CONCERNS|OBJECT",
    "score": <0.0|0.7|1.0>,
    "reasoning": "<specific reasoning>"
  },
  "implementation": {
    "dimension": "implementation",
    "verdict": "APPROVE|CONCERNS|OBJECT",
    "score": <0.0|0.7|1.0>,
    "reasoning": "<specific reasoning>"
  },
  "overall_verdict": "APPROVE|APPROVE_WITH_CONCERNS|OBJECT",
  "approval_score": <weighted score 0.0-1.0>,
  "endorsements": ["<specific things you approve>"],
  "concerns": ["<issues that don't block but should be noted>"],
  "objections": ["<blocking issues if any>"]
}
```

IMPORTANT: Output ONLY the JSON object. No markdown code fences. No additional text.'''

    def _create_structured_approval_agent(self, base_agent: AssistantAgent) -> AssistantAgent:
        """Create agent configured for structured CrossExpertApproval output.

        Note: AutoGen only supports structured output for OpenAI models.
        For Anthropic/Google, we skip structured output and parse JSON manually.
        """
        # Detect provider from model name
        model_name = getattr(base_agent._model_client, 'model', '').lower()
        is_openai = 'gpt' in model_name or 'o1' in model_name or 'o3' in model_name

        agent_kwargs = {
            "name": f"{base_agent.name}_approval",
            "model_client": base_agent._model_client,
            "description": base_agent.description,
            "system_message": base_agent._system_messages[0].content if base_agent._system_messages else "",
            "reflect_on_tool_use": False
        }

        # Only use structured output for OpenAI models (AutoGen limitation)
        if is_openai:
            agent_kwargs["output_content_type"] = CrossExpertApproval

        return AssistantAgent(**agent_kwargs)

    def _parse_approval_response(self, response: str, evaluator_name: str, target_name: str) -> CrossExpertApproval:
        """Parse structured output response to CrossExpertApproval model"""
        try:
            # Try to extract JSON from response (may have markdown fences or extra text)
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            return CrossExpertApproval(**data)
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: create default approval with error noted
            from ...models.responses import DimensionApproval
            return CrossExpertApproval(
                evaluator=evaluator_name,
                target=target_name,
                requirements=DimensionApproval(dimension="requirements", verdict="CONCERNS", score=0.5, reasoning="Parse error"),
                approach=DimensionApproval(dimension="approach", verdict="CONCERNS", score=0.5, reasoning="Parse error"),
                tradeoffs=DimensionApproval(dimension="tradeoffs", verdict="CONCERNS", score=0.5, reasoning="Parse error"),
                architecture=DimensionApproval(dimension="architecture", verdict="CONCERNS", score=0.5, reasoning="Parse error"),
                implementation=DimensionApproval(dimension="implementation", verdict="CONCERNS", score=0.5, reasoning="Parse error"),
                overall_verdict="APPROVE_WITH_CONCERNS",
                approval_score=0.5,
                endorsements=["Unable to parse structured response"],
                concerns=[f"Parse error: {str(e)}"],
                objections=[]
            )

    def _extract_json(self, response: str) -> str:
        """Extract JSON from response that may contain markdown fences or extra text."""
        import re

        # If it's already valid JSON, return as-is
        response = response.strip()
        if response.startswith('{') and response.endswith('}'):
            return response

        # Try to extract JSON from markdown code fence
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            return json_match.group(1)

        # Try to find JSON object anywhere in the response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)

        # Last resort: return original response
        return response

    def _build_evaluation_summary(
        self,
        agents: List[AssistantAgent],
        approval_matrix: Dict[str, Dict[str, Dict]]
    ) -> List[Dict]:
        """Build summary of each agent's approval decisions"""
        summaries = []

        for agent in agents:
            agent_name = agent.name
            approvals_given = approval_matrix.get(agent_name, {})

            # Calculate this agent's average approval of others
            given_scores = [data['score'] for data in approvals_given.values()]
            avg_given = sum(given_scores) / len(given_scores) if given_scores else 0.5

            # Calculate average approval this agent received
            received_scores = []
            for other_name, other_approvals in approval_matrix.items():
                if agent_name in other_approvals:
                    received_scores.append(other_approvals[agent_name]['score'])
            avg_received = sum(received_scores) / len(received_scores) if received_scores else 0.5

            summaries.append({
                'agent_name': agent_name,
                'approvals_given': approvals_given,
                'avg_approval_given': avg_given,
                'avg_approval_received': avg_received
            })

        return summaries

    def _interpret_consensus(
        self,
        final_score: float,
        approval_matrix: Dict[str, Dict[str, Dict]]
    ) -> str:
        """Generate human-readable interpretation of consensus state"""
        # Count verdicts
        approve_count = 0
        concerns_count = 0
        object_count = 0

        for evaluator_approvals in approval_matrix.values():
            for approval_data in evaluator_approvals.values():
                verdict = approval_data.get('verdict', '').upper()
                if 'APPROVE' in verdict and 'CONCERN' not in verdict:
                    approve_count += 1
                elif 'CONCERN' in verdict:
                    concerns_count += 1
                elif 'OBJECT' in verdict:
                    object_count += 1

        total = approve_count + concerns_count + object_count

        if final_score >= 0.85:
            return f"Strong consensus - {approve_count}/{total} approvals. Ready for production."
        elif final_score >= 0.7:
            return f"Good consensus - {approve_count}/{total} approvals, {concerns_count} with concerns. Minor refinements suggested."
        elif final_score >= 0.5:
            return f"Moderate consensus - {concerns_count} concerns, {object_count} objections. Iteration recommended."
        else:
            return f"Low consensus - {object_count}/{total} objections. Significant disagreement requires orchestrator intervention."