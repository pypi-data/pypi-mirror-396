"""
Centralized Orchestrator Factory - Single source for all orchestrator creation.

Uses SOTA model (Config.SOTA_MODEL) for authoritative decision-making.
"""

from autogen_agentchat.agents import AssistantAgent
from ..config import Config
from .agents import ResponseFormats, create_sota_model_client
from ..prompts.prompts import Prompts


class OrchestratorFactory:
    """Centralized factory for creating orchestrator agents.

    All orchestrators use SOTA model for high-quality authoritative decisions.
    """

    @staticmethod
    def create_single_mode_orchestrator() -> AssistantAgent:
        """Create orchestrator for single-provider mode.

        Uses SOTA model for authoritative decision-making.
        """
        # Use SOTA model for orchestrator quality
        model_client = create_sota_model_client()

        return AssistantAgent(
            name="orchestrator",
            model_client=model_client,
            description="Orchestrator who guides consensus when experts are deadlocked.",
            system_message=Prompts.get_single_mode_orchestrator_system_message(ResponseFormats.ORCHESTRATOR_INTERVENTION)
        )

    @staticmethod
    def create_team_mode_orchestrator() -> AssistantAgent:
        """Create orchestrator for team/multi-provider mode.

        Uses SOTA model for authoritative decision-making.
        """
        # Use SOTA model for orchestrator quality
        model_client = create_sota_model_client()

        return AssistantAgent(
            name="orchestrator",
            model_client=model_client,
            description="Orchestrator guiding multi-team consensus when deadlocked.",
            system_message=Prompts.get_team_mode_orchestrator_system_message(ResponseFormats.ORCHESTRATOR_INTERVENTION)
        )

    @staticmethod 
    def create_orchestrator(mode: str = "single") -> AssistantAgent:
        """Create appropriate orchestrator based on mode"""
        if mode == "team":
            return OrchestratorFactory.create_team_mode_orchestrator()
        else:
            return OrchestratorFactory.create_single_mode_orchestrator()


# Convenience functions for easy imports
def create_orchestrator(mode: str = "single") -> AssistantAgent:
    """Create orchestrator for specified mode"""
    return OrchestratorFactory.create_orchestrator(mode)


def create_single_orchestrator() -> AssistantAgent:
    """Create orchestrator for single mode"""
    return OrchestratorFactory.create_single_mode_orchestrator()


def create_team_orchestrator() -> AssistantAgent:
    """Create orchestrator for team mode"""
    return OrchestratorFactory.create_team_mode_orchestrator()