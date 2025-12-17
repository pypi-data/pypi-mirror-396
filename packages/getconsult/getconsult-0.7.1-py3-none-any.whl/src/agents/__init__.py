"""
Agent implementations for Consult
"""

from .agents import (
    create_expert_agents,
    create_team_expert_agents,
    create_solution_agent,
    create_model_client,
    create_model_client_for_provider,
    StructuredAgentFactory
)
from .expert_manager import (
    ExpertManager,
    create_experts,
    create_teams,
    add_expert,
    list_configurations
)
from .distinguished_engineer import create_meta_reviewer

__all__ = [
    "create_expert_agents",
    "create_team_expert_agents",
    "create_solution_agent",
    "create_model_client",
    "create_model_client_for_provider",
    "StructuredAgentFactory",
    "ExpertManager",
    "create_experts",
    "create_teams",
    "add_expert",
    "list_configurations",
    "create_meta_reviewer"
]