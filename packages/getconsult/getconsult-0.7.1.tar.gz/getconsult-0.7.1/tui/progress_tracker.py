"""
Progress Tracker - Tracks workflow state for visualization.

Maintains the state needed to render the sidebar progress section
and updates based on workflow events.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Callable
from enum import Enum


class PhaseStatus(Enum):
    """Status of a workflow phase."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"


@dataclass
class ProgressState:
    """Current state of workflow progress."""

    # Main phases
    analysis_status: PhaseStatus = PhaseStatus.PENDING
    peer_review_status: PhaseStatus = PhaseStatus.PENDING
    resolution_status: PhaseStatus = PhaseStatus.PENDING
    synthesis_status: PhaseStatus = PhaseStatus.PENDING

    # Sub-phases within peer review
    feedback_status: PhaseStatus = PhaseStatus.PENDING
    refinement_status: PhaseStatus = PhaseStatus.PENDING
    consensus_status: PhaseStatus = PhaseStatus.PENDING

    # Iteration tracking
    current_iteration: int = 0
    max_iterations: int = 1

    # Consensus tracking
    consensus_history: List[float] = field(default_factory=list)
    consensus_threshold: float = 0.8

    # Current action
    current_action: str = ""

    # Workflow metadata
    experts: List[str] = field(default_factory=list)
    is_active: bool = False


class ProgressTracker:
    """Tracks workflow progress and notifies listeners of changes."""

    def __init__(self):
        self.state = ProgressState()
        self._listeners: List[Callable[[ProgressState], None]] = []

    def add_listener(self, callback: Callable[[ProgressState], None]) -> None:
        """Register a callback to be notified on state changes."""
        self._listeners.append(callback)

    def _notify_listeners(self) -> None:
        """Notify all listeners of state change."""
        for listener in self._listeners:
            try:
                listener(self.state)
            except Exception:
                pass  # Don't let listener errors break tracking

    def reset(self) -> None:
        """Reset tracker for new workflow."""
        self.state = ProgressState()
        self._notify_listeners()

    # === Event Handlers ===

    def on_workflow_start(self, experts: List[str], max_iterations: int, threshold: float) -> None:
        """Handle workflow start event."""
        self.state = ProgressState(
            experts=experts,
            max_iterations=max_iterations,
            consensus_threshold=threshold,
            is_active=True,
            current_action="Initializing workflow..."
        )
        self._notify_listeners()

    def on_phase_start(self, phase_num: int, phase_name: str) -> None:
        """Handle phase start event."""
        if phase_num == 1:
            self.state.analysis_status = PhaseStatus.ACTIVE
            self.state.current_action = "Experts analyzing problem..."
        elif phase_num == 2:
            self.state.analysis_status = PhaseStatus.COMPLETE
            self.state.peer_review_status = PhaseStatus.ACTIVE
            self.state.current_action = "Starting peer review..."
        self._notify_listeners()

    def on_iteration_start(self, iteration: int) -> None:
        """Handle iteration start event."""
        self.state.current_iteration = iteration
        # Reset sub-phase statuses for new iteration
        self.state.feedback_status = PhaseStatus.PENDING
        self.state.refinement_status = PhaseStatus.PENDING
        self.state.consensus_status = PhaseStatus.PENDING
        self.state.current_action = f"Iteration {iteration}/{self.state.max_iterations}"
        self._notify_listeners()

    def on_feedback_phase_start(self) -> None:
        """Handle feedback phase start."""
        self.state.feedback_status = PhaseStatus.ACTIVE
        self.state.current_action = "Experts providing feedback..."
        self._notify_listeners()

    def on_refinement_phase_start(self) -> None:
        """Handle refinement phase start."""
        self.state.feedback_status = PhaseStatus.COMPLETE
        self.state.refinement_status = PhaseStatus.ACTIVE
        self.state.current_action = "Refining solutions..."
        self._notify_listeners()

    def on_consensus_evaluation_start(self) -> None:
        """Handle consensus evaluation start."""
        self.state.refinement_status = PhaseStatus.COMPLETE
        self.state.consensus_status = PhaseStatus.ACTIVE
        self.state.current_action = "Evaluating consensus..."
        self._notify_listeners()

    def on_consensus_check(self, score: float, reached: bool) -> None:
        """Handle consensus check result."""
        self.state.consensus_history.append(score)
        self.state.consensus_status = PhaseStatus.COMPLETE

        if reached:
            self.state.peer_review_status = PhaseStatus.COMPLETE
            self.state.resolution_status = PhaseStatus.COMPLETE
            self.state.current_action = f"Consensus reached: {int(score * 100)}%"
        else:
            self.state.current_action = f"Consensus: {int(score * 100)}% (need {int(self.state.consensus_threshold * 100)}%)"
        self._notify_listeners()

    def on_orchestrator_intervention(self) -> None:
        """Handle orchestrator intervention."""
        self.state.peer_review_status = PhaseStatus.COMPLETE
        self.state.resolution_status = PhaseStatus.ACTIVE
        self.state.current_action = "Orchestrator making decision..."
        self._notify_listeners()

    def on_agent_thinking(self, agent_name: str, action: str) -> None:
        """Handle agent thinking event."""
        # Check if this is the presentation agent - triggers synthesis phase
        if "presentation" in agent_name.lower():
            self.on_synthesis_start()
            return

        # Format agent name for display
        display_name = agent_name.replace("_", " ").title()
        if display_name.startswith("Team "):
            display_name = display_name.split("Team ", 1)[-1]
        self.state.current_action = f"{display_name}: {action}"
        self._notify_listeners()

    def on_synthesis_start(self) -> None:
        """Handle final synthesis/presentation start."""
        self.state.resolution_status = PhaseStatus.COMPLETE
        self.state.synthesis_status = PhaseStatus.ACTIVE
        self.state.current_action = "Synthesizing final answer..."
        self._notify_listeners()

    def on_workflow_complete(self, success: bool) -> None:
        """Handle workflow completion."""
        self.state.synthesis_status = PhaseStatus.COMPLETE
        self.state.is_active = False
        self.state.current_action = "Complete!" if success else "Completed with issues"
        self._notify_listeners()

    # === Display Helpers ===

    def get_consensus_trend_string(self) -> str:
        """Get formatted consensus trend string."""
        if not self.state.consensus_history:
            return "No data yet"

        percentages = [f"{int(s * 100)}%" for s in self.state.consensus_history]
        return " → ".join(percentages)

    def get_latest_consensus(self) -> Optional[float]:
        """Get the most recent consensus score."""
        if self.state.consensus_history:
            return self.state.consensus_history[-1]
        return None

    def get_progress_bar(self, width: int = 10) -> str:
        """Get a text-based progress bar for consensus."""
        score = self.get_latest_consensus()
        if score is None:
            return "░" * width

        filled = int(width * score)
        return "█" * filled + "░" * (width - filled)

    def get_status_display(self) -> dict:
        """Return data for StatusHeader widget."""
        current_phase = 0
        if self.state.analysis_status == PhaseStatus.ACTIVE:
            current_phase = 1
        elif self.state.peer_review_status == PhaseStatus.ACTIVE:
            current_phase = 2
        elif self.state.resolution_status == PhaseStatus.ACTIVE:
            current_phase = 3
        elif self.state.synthesis_status == PhaseStatus.ACTIVE:
            current_phase = 3
        elif self.state.synthesis_status == PhaseStatus.COMPLETE:
            current_phase = 3

        return {
            "phase": f"{current_phase}/3",
            "iteration": f"{self.state.current_iteration}/{self.state.max_iterations}",
            "consensus": self.get_latest_consensus(),
            "action": self.state.current_action,
            "is_active": self.state.is_active,
        }

    def get_phase_status(self, phase_num: int) -> str:
        """Get the status of a specific phase."""
        if phase_num == 1:
            return self.state.analysis_status.value
        elif phase_num == 2:
            return self.state.peer_review_status.value
        elif phase_num == 3:
            if self.state.synthesis_status != PhaseStatus.PENDING:
                return self.state.synthesis_status.value
            return self.state.resolution_status.value
        return "pending"
