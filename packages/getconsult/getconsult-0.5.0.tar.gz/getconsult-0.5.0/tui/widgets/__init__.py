"""
Consult TUI Custom Widgets

Collapsible workflow visualization components for multi-agent orchestration.
"""

from .status_header import StatusHeader
from .phase_container import PhaseContainer, PhaseStatus
from .agent_card import AgentCard, ThinkingIndicator
from .feedback_group import FeedbackGroup, FeedbackItem, IterationContainer
from .workflow_view import WorkflowView, SystemMessages
from .detail_pane import (
    DetailPane,
    ConsensusTrendChart,
    AgentSelector,
    JourneyPhase,
    JourneyView,
    FeedbackReceivedCard,
)
from .query_display import QueryDisplay
from .clarification_modal import ClarificationModal, ClarificationQuestion

__all__ = [
    "StatusHeader",
    "PhaseContainer",
    "PhaseStatus",
    "AgentCard",
    "ThinkingIndicator",
    "FeedbackGroup",
    "FeedbackItem",
    "IterationContainer",
    "WorkflowView",
    "SystemMessages",
    "DetailPane",
    "ConsensusTrendChart",
    "AgentSelector",
    "JourneyPhase",
    "JourneyView",
    "FeedbackReceivedCard",
    "QueryDisplay",
    "ClarificationModal",
    "ClarificationQuestion",
]
