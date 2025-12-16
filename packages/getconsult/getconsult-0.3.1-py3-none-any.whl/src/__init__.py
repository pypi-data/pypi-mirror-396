"""
Consult - Multi-Agent Problem Solving System

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.
"""

from .agents import (
    create_expert_agents,
    create_solution_agent,
    create_model_client
)
from .workflows import ConsensusWorkflow
from .config import Config

__version__ = "0.1.0"
__license__ = "Proprietary - See LICENSE file"
__all__ = [
    "create_expert_agents",
    "create_solution_agent",
    "create_model_client",
    "ConsensusWorkflow",
    "Config"
]