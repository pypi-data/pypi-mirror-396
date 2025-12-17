"""
Presentation agent for clean, human-friendly final results.

Uses SOTA model (Config.SOTA_MODEL) for high-quality synthesis.
"""
from autogen_agentchat.agents import AssistantAgent
from ..config import Config
from .agents import create_sota_model_client
from ..prompts.prompts import Prompts


def create_presentation_agent() -> AssistantAgent:
    """Create agent focused solely on presenting final results clearly.

    Uses SOTA model for comprehensive, high-quality presentation synthesis.
    """
    # Use SOTA model for presentation quality
    model_client = create_sota_model_client()

    return AssistantAgent(
        name="presentation_agent",
        model_client=model_client,
        description="Presentation specialist who formats complex multi-agent results into clear, actionable summaries",
        system_message=Prompts.get_presentation_agent_system_message()
    )