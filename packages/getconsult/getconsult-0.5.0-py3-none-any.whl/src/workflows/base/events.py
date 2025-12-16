"""
Event-based architecture for workflow output.

This module provides a clean separation between workflow execution and output rendering.
Workflows emit events, and listeners (ConsoleDisplay, TUI) handle rendering independently.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Protocol, List, Optional
import time


@dataclass
class WorkflowEvent:
    """A structured event emitted by workflows.

    Events carry semantic meaning and typed data, enabling listeners
    to render them appropriately for their medium (CLI, TUI, web, etc.)
    """
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class EventListener(Protocol):
    """Protocol for event listeners.

    Implement this to receive workflow events.
    """
    def on_event(self, event: WorkflowEvent) -> None:
        """Handle a workflow event."""
        ...


class EventEmitter:
    """Emits events to registered listeners.

    Workflows use this to decouple execution from rendering.
    Multiple listeners can be registered (e.g., ConsoleDisplay + logger).
    """

    def __init__(self):
        self._listeners: List[EventListener] = []

    def add_listener(self, listener: EventListener) -> None:
        """Register a listener to receive events."""
        self._listeners.append(listener)

    def remove_listener(self, listener: EventListener) -> None:
        """Unregister a listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def emit(self, event_type: str, **data) -> None:
        """Emit an event to all listeners.

        Args:
            event_type: The type of event (e.g., 'agent_response', 'phase_start')
            **data: Event-specific payload data
        """
        event = WorkflowEvent(event_type=event_type, data=data)
        for listener in self._listeners:
            try:
                listener.on_event(event)
            except Exception:
                # Don't let listener errors break the workflow
                pass


# Event type constants for consistency
class EventTypes:
    """Constants for event types to avoid string typos."""

    # Workflow lifecycle
    WORKFLOW_START = "workflow_start"
    WORKFLOW_COMPLETE = "workflow_complete"
    WORKFLOW_ERROR = "error"

    # Phase events
    PHASE_START = "phase_start"
    ITERATION_START = "iteration_start"

    # Agent events
    AGENT_THINKING = "agent_thinking"
    AGENT_RESPONSE = "agent_response"
    PARALLEL_PROGRESS = "parallel_progress"

    # Feedback events
    FEEDBACK_PHASE_START = "feedback_phase_start"
    FEEDBACK_EXCHANGE = "feedback_exchange"

    # Refinement events
    REFINEMENT_PHASE_START = "refinement_phase_start"

    # Consensus events
    CONSENSUS_EVALUATION_START = "consensus_evaluation_start"
    CONSENSUS_CHECK = "consensus_check"
    CROSS_EXPERT_APPROVAL = "cross_expert_approval"  # Individual pairwise approval

    # Orchestrator events
    ORCHESTRATOR_INTERVENTION = "orchestrator_intervention"
    EXPERT_COMPROMISE_RESPONSES = "expert_compromise_responses"

    # Clarification events (Phase 0)
    CLARIFICATION_ANALYZING = "clarification_analyzing"
    CLARIFICATION_NEEDED = "clarification_needed"
    CLARIFICATION_RESPONSE = "clarification_response"
    CLARIFICATION_SKIPPED = "clarification_skipped"
