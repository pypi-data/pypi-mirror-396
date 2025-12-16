"""
Agent creation for Consult
"""

from typing import List, Optional, Type, Dict, Any
from pydantic import BaseModel
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_core.models import ModelInfo

from ..config import Config, ProviderType
from ..core.exceptions import MissingAPIKeyError, InvalidProviderError, FeatureGatedError
from ..core.paths import get_logs_dir
from ..core.security import get_contextual_logger
from ..core.feature_gate import check_expert_count, require_team_mode, check_feature

# Module logger
_logger = None


def _get_logger():
    """Get or create the agents logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.agents", log_file=str(log_file))
    return _logger


from ..models.responses import (
    ExpertAnalysis, PeerFeedback, EvolvedSolution,
    ConsensusEvaluation, ProposalEvaluation, OrchestratorDecision
)
from ..prompts.prompts import Prompts


# Centralized format templates
class ResponseFormats:
    """Centralized response format templates"""
    
    STANDARD = """
RESPONSE FORMAT (REQUIRED):
Lead with your recommendation, not your reasoning. Structure for scannability:

## 🎯 RECOMMENDATION
[State your core recommendation in 1-2 clear sentences - what should be done]

## 📊 Confidence: [0.0-1.0]
[One sentence explaining your confidence level]

## 💡 KEY POINTS
• [Actionable point 1 - specific and concise]
• [Actionable point 2 - specific and concise]
• [Actionable point 3 - specific and concise]

## ⚖️ TRADE-OFFS
| Option | Pros | Cons |
|--------|------|------|
| [Option A] | [benefit] | [drawback] |
| [Option B] | [benefit] | [drawback] |

## 📋 DETAILED ANALYSIS
[Full technical analysis - keep explanations under 3 sentences per point]
1. [Analysis point with supporting evidence]
2. [Analysis point with supporting evidence]

{ConfidenceFramework.get_compact_framework_text()}
"""

    FEEDBACK = """
FEEDBACK FORMAT (REQUIRED):
Lead with your verdict. Ground every critique in YOUR domain expertise.

## VERDICT
[Production-ready for my domain? Yes/No/Conditional - one sentence why]

## STRENGTHS (From My Domain View)
• [Strength 1 - what they got RIGHT about my domain, why it's correct]
• [Strength 2 - specific technical merit from my expertise]

## CRITICAL FLAWS & GAPS
• [Flaw 1]: As a [your role], I see [specific problem] → Impact: [quantified] → Fix: [concrete alternative]
• [Flaw 2]: As a [your role], I see [specific problem] → Impact: [quantified] → Fix: [concrete alternative]

## CROSS-DOMAIN INTEGRATION ISSUES
[Where their solution meets MY domain - what breaks at the boundaries?]
• [Issue]: Their [approach] assumes [X] but my domain requires [Y] → Consequence: [specific failure]

## DOMAIN-SPECIFIC CONCERNS
[Issues only someone with my expertise would catch]
• [Concern]: [Technical detail only a specialist would know]

## REQUIRED CHANGES (Priority Order)
1. **[Change 1]**: [Specific change] → [Why from my domain] → [Expected outcome]
2. **[Change 2]**: [Specific change] → [Why from my domain] → [Expected outcome]
"""

    FEEDBACK_ANALYSIS = """
FEEDBACK ANALYSIS FORMAT (REQUIRED):
Lead with decisions. Use tables for clarity:

## 🎯 DECISIONS MADE
| Feedback | Decision | Rationale |
|----------|----------|-----------|
| [Point 1] | ✅ Accept / 🔄 Modify / ❌ Reject | [Brief why] |
| [Point 2] | ✅ Accept / 🔄 Modify / ❌ Reject | [Brief why] |

## 📊 Updated Confidence: [0.0-1.0]
[One sentence on confidence change]

## 🔧 CHANGES MADE
• [Specific change 1 incorporating feedback]
• [Specific change 2 incorporating feedback]

## 📋 REFINED SOLUTION
[Your updated solution - concise, focused on what changed]

{ConfidenceFramework.get_compact_framework_text()}
"""

    ORCHESTRATOR_INTERVENTION = """
ORCHESTRATOR INTERVENTION FORMAT (REQUIRED):
Lead with the compromise. Tables for conflicts:

## 🎯 PROPOSED COMPROMISE
[Your synthesized solution in 2-3 sentences - the path forward]

## ⚖️ CONFLICT RESOLUTION
| Issue | Expert A | Expert B | Resolution |
|-------|----------|----------|------------|
| [Topic 1] | [Position] | [Position] | [How resolved] |
| [Topic 2] | [Position] | [Position] | [How resolved] |

## ✅ CONSENSUS POINTS
• [What all agree on - builds confidence]
• [What all agree on - builds confidence]

## 🔧 IMPLEMENTATION STEPS
1. [Step 1 - specific action]
2. [Step 2 - specific action]
3. [Step 3 - specific action]

## 📊 SUCCESS CRITERIA
• [Measurable criterion 1]
• [Measurable criterion 2]

ORCHESTRATION_COMPLETE
"""

    PROPOSAL_EVALUATION = """
PROPOSAL EVALUATION FORMAT (REQUIRED):
Lead with your decision. Use tables for assessment:

## 🎯 DECISION: [Accept / Accept with Mods / Neutral / Reject]
**Confidence:** [0.0-1.0] — [One sentence rationale]

## 📊 TECHNICAL ASSESSMENT
| Aspect | Rating | Notes |
|--------|--------|-------|
| [Aspect 1] | ✅ Strong / ⚠️ Adequate / ❌ Weak | [Brief note] |
| [Aspect 2] | ✅ Strong / ⚠️ Adequate / ❌ Weak | [Brief note] |

## ✅ ALIGNMENT WITH MY POSITION
• [Where proposal matches my recommendations]
• [Where proposal matches my recommendations]

## ⚠️ CONCERNS
• [Specific concern and impact]
• [Specific concern and impact]

## 🔧 REQUIRED MODIFICATIONS (if any)
1. [Specific change needed]
2. [Specific change needed]
"""


# Import expert registry and confidence framework  
from .expert_registry import get_expert_config, get_expert_set
from ..utils.confidence_framework import ConfidenceFramework


def create_model_client_for_provider(provider: ProviderType):
    """Create a model client for a specific provider"""
    logger = _get_logger()

    if provider == "openai":
        if not Config.OPENAI_API_KEY:
            logger.error(f"Model client creation FAILED | provider=openai | error=missing API key")
            raise MissingAPIKeyError("openai")
        model = Config.get_model_for_provider("openai")
        logger.info(f"Model client created | provider=openai | model={model}")
        return OpenAIChatCompletionClient(
            model=model,
            api_key=Config.OPENAI_API_KEY
        )
    elif provider == "anthropic":
        if not Config.ANTHROPIC_API_KEY:
            logger.error(f"Model client creation FAILED | provider=anthropic | error=missing API key")
            raise MissingAPIKeyError("anthropic")
        model = Config.get_model_for_provider("anthropic")
        logger.info(f"Model client created | provider=anthropic | model={model}")
        return AnthropicChatCompletionClient(
            model=model,
            api_key=Config.ANTHROPIC_API_KEY
        )
    elif provider == "google":
        if not Config.GOOGLE_API_KEY:
            logger.error(f"Model client creation FAILED | provider=google | error=missing API key")
            raise MissingAPIKeyError("google")
        # Use OpenAI-compatible client for Gemini
        model_name = Config.get_model_for_provider("google")
        logger.info(f"Model client created | provider=google | model={model_name}")
        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=Config.GOOGLE_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model_info=ModelInfo(
                vision=True,
                function_calling=True,
                json_output=True,
                family="unknown",
                structured_output=True
            )
        )
    else:
        available_providers = ["openai", "anthropic", "google"]
        logger.error(f"Model client creation FAILED | provider={provider} | error=invalid provider")
        raise InvalidProviderError(provider, available_providers)


def create_model_client():
    """Create a single model client using the default provider"""
    available_providers = Config.get_available_providers()
    provider_priority = ["anthropic", "openai", "google"]

    for provider in provider_priority:
        if provider in available_providers:
            return create_model_client_for_provider(provider)

    # No providers available
    raise MissingAPIKeyError("any", {"available_providers": available_providers})


def create_sota_model_client():
    """Create model client using the state-of-the-art model.

    Used for critical agents: Meta Reviewer, Presentation Agent, Orchestrator.
    Configured via Config.SOTA_MODEL and Config.SOTA_PROVIDER.
    """
    if Config.SOTA_PROVIDER == "anthropic":
        if not Config.ANTHROPIC_API_KEY:
            raise MissingAPIKeyError("anthropic")
        from autogen_ext.models.anthropic import AnthropicChatCompletionClient
        return AnthropicChatCompletionClient(
            model=Config.SOTA_MODEL,
            api_key=Config.ANTHROPIC_API_KEY
        )
    elif Config.SOTA_PROVIDER == "openai":
        if not Config.OPENAI_API_KEY:
            raise MissingAPIKeyError("openai")
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        return OpenAIChatCompletionClient(
            model=Config.SOTA_MODEL,
            api_key=Config.OPENAI_API_KEY
        )
    elif Config.SOTA_PROVIDER == "google":
        if not Config.GOOGLE_API_KEY:
            raise MissingAPIKeyError("google")
        from autogen_ext.models.google import GoogleChatCompletionClient
        return GoogleChatCompletionClient(
            model=Config.SOTA_MODEL,
            api_key=Config.GOOGLE_API_KEY
        )
    else:
        raise ValueError(f"Unsupported SOTA provider: {Config.SOTA_PROVIDER}")


def build_expert_system_message(expert_type: str, include_formats: bool = True, team_name: str = None) -> str:
    """Build system message for an expert with optional format templates"""
    expert_config = get_expert_config(expert_type)
    base_message = expert_config.base_message
    
    # Add team identity if provided
    if team_name:
        message = f"You represent Team {team_name} in a multi-team competition.\n\n{base_message}"
    else:
        message = base_message
    
    # Add format templates if requested
    if include_formats:
        message += Prompts.get_expert_format_instructions(include_formats)
    
    # Add team competition note if applicable
    if team_name:
        message += """

IMPORTANT: You are competing against other AI teams (each using different models). Provide your best expert analysis while being collaborative within the consensus process. Your goal is to contribute the strongest technical solution from your perspective."""
    
    return message


def create_expert_agent(
    expert_type: str,
    model_client: Any,
    name_prefix: str = "",
    include_formats: bool = True,
    team_name: str = None,
    output_type: Optional[Type[BaseModel]] = None,
    memory_context: Optional[Dict[str, Any]] = None
) -> AssistantAgent:
    """Create a single expert agent with consistent configuration

    Args:
        expert_type: Type of expert to create
        model_client: Model client for the agent
        name_prefix: Prefix for agent name
        include_formats: Whether to include format templates
        team_name: Team name for competition mode
        output_type: Structured output type if needed
        memory_context: Memory context to include in system message
    """
    logger = _get_logger()

    try:
        expert_config = get_expert_config(expert_type)
    except Exception as e:
        logger.error(f"Expert agent creation FAILED | expert_type={expert_type} | error=invalid expert type: {e}")
        raise
    
    # Build agent name
    name = f"{name_prefix}_{expert_type}" if name_prefix else expert_type
    
    # Build description
    description = expert_config.description
    if team_name:
        description = f"{team_name} Team - {description}"
    
    # Build system message with optional memory context
    system_message = build_expert_system_message(expert_type, include_formats, team_name)
    
    # Add memory context if provided
    if memory_context:
        from ..memory.memory_manager import MemoryManager
        memory_manager = MemoryManager()
        context_str = memory_manager.format_context_for_prompt(memory_context)
        if context_str:
            system_message = context_str + "\n" + system_message
    
    # Create agent parameters
    agent_params = {
        "name": name,
        "model_client": model_client,
        "description": description,
        "system_message": system_message,
    }
    
    # Add structured output if specified AND provider supports it
    # Note: AutoGen only supports structured output for OpenAI models
    if output_type:
        model_name = getattr(model_client, 'model', '').lower()
        is_openai = 'gpt' in model_name or 'o1' in model_name or 'o3' in model_name
        if is_openai:
            agent_params["output_content_type"] = output_type
            agent_params["reflect_on_tool_use"] = False

    try:
        agent = AssistantAgent(**agent_params)
        team_info = f" | team={team_name}" if team_name else ""
        logger.debug(f"Expert agent created | name={name} | type={expert_type}{team_info}")
        return agent
    except Exception as e:
        logger.error(f"Expert agent creation FAILED | name={name} | type={expert_type} | error={type(e).__name__}: {e}")
        raise


def create_expert_agents(
    expert_types: List[str] = None,
    expert_set: str = "default",
    provider: ProviderType = None,
    memory_context: Optional[Dict[str, Any]] = None
) -> List[AssistantAgent]:
    """Create expert agents for single-provider mode

    Args:
        expert_types: List of expert type names. If None, uses expert_set.
        expert_set: Name of predefined expert set to use (default: "default")
        provider: Provider to use for all agents
        memory_context: Memory context to provide to all agents
    """
    logger = _get_logger()

    # Use expert set if no specific types provided
    if expert_types is None:
        expert_types = get_expert_set(expert_set)

    logger.info(f"Creating expert panel | mode=single | experts={expert_types} | provider={provider or 'auto'}")

    # Check expert count limit (defensive - should be checked at CLI/TUI layer)
    check_expert_count(len(expert_types))

    # Create model client
    if provider:
        model_client = create_model_client_for_provider(provider)
    else:
        model_client = create_model_client()

    # Create agents
    agents = []
    for expert_type in expert_types:
        agent = create_expert_agent(
            expert_type=expert_type,
            model_client=model_client,
            include_formats=True,
            memory_context=memory_context
        )
        agents.append(agent)

    logger.info(f"Expert panel ready | count={len(agents)} | names={[a.name for a in agents]}")
    return agents


def create_team_expert_agents(
    expert_types: List[str] = None,
    expert_set: str = "default"
) -> Dict[str, List[AssistantAgent]]:
    """Create expert agents organized by team/provider

    Args:
        expert_types: List of expert type names. If None, uses expert_set.
        expert_set: Name of predefined expert set to use (default: "default")
    """
    logger = _get_logger()

    # Use expert set if no specific types provided
    if expert_types is None:
        expert_types = get_expert_set(expert_set)

    logger.info(f"Creating expert panel | mode=team | experts={expert_types}")

    # Check team mode access (defensive - should be checked at CLI/TUI layer)
    require_team_mode()

    # Check expert count limit
    check_expert_count(len(expert_types))

    # Get available team clients
    team_clients = {}
    available_providers = Config.get_team_providers()

    for provider in available_providers:
        try:
            team_clients[provider] = create_model_client_for_provider(provider)
        except ValueError as e:
            logger.warning(f"Team provider skipped | provider={provider} | error={e}")
            continue

    if len(team_clients) < 2:
        logger.error(f"Team mode FAILED | available_providers={list(team_clients.keys())} | error=need at least 2 providers")
        raise ValueError("Need at least 2 providers for team mode")

    # Create teams
    teams = {}
    for provider, client in team_clients.items():
        team_agents = []
        provider_display = provider.title()

        for expert_type in expert_types:
            agent = create_expert_agent(
                expert_type=expert_type,
                model_client=client,
                name_prefix=f"team_{provider}",
                include_formats=True,
                team_name=provider_display
            )
            team_agents.append(agent)

        teams[provider] = team_agents
        logger.debug(f"Team created | provider={provider} | agents={len(team_agents)}")

    logger.info(f"Team panel ready | teams={list(teams.keys())} | agents_per_team={len(expert_types)}")
    return teams


def create_solution_agent() -> AssistantAgent:
    """Create solution synthesis agent"""
    model_client = create_model_client()
    
    return AssistantAgent(
        "solution_synthesizer",
        model_client=model_client,
        description="Solution synthesizer who combines expert recommendations.",
        system_message=Prompts.get_solution_agent_system_message()
    )




class StructuredAgentFactory:
    """Factory for creating agents with specific structured output types"""
    
    @staticmethod
    def create_for_phase(
        base_agent: AssistantAgent,
        phase: str,
        output_type: Type[BaseModel]
    ) -> AssistantAgent:
        """Create agent configured for a specific phase with structured output"""
        # Extract expert type from agent name
        expert_type = base_agent.name.split('_')[-1]
        
        # Determine format suffix and description based on phase
        phase_config = {
            "initial": ("", "Provide your analysis in a structured format."),
            "feedback": (ResponseFormats.FEEDBACK, "Provide peer feedback in a structured format."),
            "evolution": (ResponseFormats.FEEDBACK_ANALYSIS, "Provide your evolved solution in a structured format."),
            "consensus": ("", "Evaluate consensus in a structured format."),
            "proposal": (ResponseFormats.PROPOSAL_EVALUATION, "Evaluate the orchestrator's proposal in a structured format.")
        }
        
        format_addition, instruction = phase_config.get(phase, ("", ""))
        
        # Build system message
        try:
            expert_config = get_expert_config(expert_type)
            base_message = expert_config.base_message
        except ValueError:
            base_message = "You are an expert analyst."
        
        system_message = base_message
        if format_addition:
            system_message += "\n\n" + format_addition
        system_message += "\n\n" + instruction

        # Build agent parameters
        agent_kwargs = {
            "name": f"{base_agent.name}_{phase}",
            "model_client": base_agent._model_client,
            "description": base_agent.description,
            "system_message": system_message,
            "reflect_on_tool_use": False
        }

        # Only use structured output for OpenAI models (AutoGen limitation)
        model_name = getattr(base_agent._model_client, 'model', '').lower()
        is_openai = 'gpt' in model_name or 'o1' in model_name or 'o3' in model_name
        if is_openai:
            agent_kwargs["output_content_type"] = output_type

        return AssistantAgent(**agent_kwargs)
    
    @staticmethod
    def create_for_initial_analysis(base_agent: AssistantAgent) -> AssistantAgent:
        """Create agent configured for initial analysis structured output"""
        return StructuredAgentFactory.create_for_phase(base_agent, "initial", ExpertAnalysis)
    
    @staticmethod
    def create_for_peer_feedback(base_agent: AssistantAgent) -> AssistantAgent:
        """Create agent configured for peer feedback structured output"""
        return StructuredAgentFactory.create_for_phase(base_agent, "feedback", PeerFeedback)
    
    @staticmethod
    def create_for_evolved_solution(base_agent: AssistantAgent) -> AssistantAgent:
        """Create agent configured for evolved solution structured output"""
        return StructuredAgentFactory.create_for_phase(base_agent, "evolution", EvolvedSolution)
    
    @staticmethod
    def create_for_consensus_evaluation(base_agent: AssistantAgent) -> AssistantAgent:
        """Create agent configured for consensus evaluation structured output"""
        return StructuredAgentFactory.create_for_phase(base_agent, "consensus", ConsensusEvaluation)
    
    @staticmethod
    def create_for_proposal_evaluation(base_agent: AssistantAgent) -> AssistantAgent:
        """Create agent configured for proposal evaluation structured output"""
        return StructuredAgentFactory.create_for_phase(base_agent, "proposal", ProposalEvaluation)