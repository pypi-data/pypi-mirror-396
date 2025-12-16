"""
Meta Reviewer agent.

Cross-cutting review across all expert perspectives.
Uses the state-of-the-art model (Config.SOTA_MODEL) to identify
integration issues and blindspots that domain experts miss.
"""
from autogen_agentchat.agents import AssistantAgent

from .agents import create_sota_model_client
from ..prompts.prompts import Prompts


def create_meta_reviewer() -> AssistantAgent:
    """Create the Meta Reviewer agent.

    Cross-cutting review across all expert perspectives.
    Uses the state-of-the-art model (configured in Config.SOTA_MODEL)
    to surface integration issues and blindspots that domain experts miss.

    Returns:
        AssistantAgent configured as Meta Reviewer
    """
    # Use shared SOTA model client
    model_client = create_sota_model_client()

    return AssistantAgent(
        name="meta_reviewer",
        model_client=model_client,
        description="Cross-cutting review across all expert perspectives",
        system_message=Prompts.get_meta_reviewer_base_message()
    )
