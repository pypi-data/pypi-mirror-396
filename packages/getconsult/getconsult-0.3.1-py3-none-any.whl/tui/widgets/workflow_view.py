"""
WorkflowView Widget - Main container for collapsible workflow visualization.

Replaces RichLog as the main content area for workflow display.
"""

from typing import Optional, List
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import VerticalScroll, Vertical
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel

from .phase_container import PhaseContainer


class WorkflowView(VerticalScroll):
    """Main container widget for workflow visualization."""

    DEFAULT_CSS = """
    WorkflowView {
        height: 1fr;
        padding: 1;
        background: #000000;
    }

    WorkflowView .welcome-message {
        margin: 2;
        padding: 1;
    }

    WorkflowView .problem-display {
        margin: 0 0 1 0;
        padding: 1;
        border: solid #003311;
        background: #001100;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._phases: List[PhaseContainer] = []
        self._problem_widget: Optional[Static] = None
        self._welcome_shown = True

    def compose(self) -> ComposeResult:
        # Welcome message shown initially
        yield Static(id="welcome-container", classes="welcome-message")

    def on_mount(self) -> None:
        self._show_welcome()

    def _show_welcome(self) -> None:
        """Display welcome message."""
        try:
            container = self.query_one("#welcome-container", Static)
        except Exception:
            return

        welcome_text = Text()
        welcome_text.append("\n  CONSULT ", style="bold green")
        welcome_text.append("Expert Panel Consensus\n\n", style="dim")
        welcome_text.append("  Enter a query to begin.\n", style="dim")
        welcome_text.append("  Multiple experts will analyze your problem,\n", style="dim")
        welcome_text.append("  critique each other, and reach consensus.\n\n", style="dim")
        welcome_text.append("  Press ", style="dim")
        welcome_text.append("?", style="bold green")
        welcome_text.append(" for help.\n", style="dim")

        container.update(welcome_text)
        self._welcome_shown = True

    def clear(self) -> None:
        """Clear all workflow content and show welcome."""
        # Remove all phase containers
        for phase in self._phases:
            try:
                phase.remove()
            except Exception:
                pass
        self._phases.clear()

        # Remove problem display
        if self._problem_widget:
            try:
                self._problem_widget.remove()
            except Exception:
                pass
            self._problem_widget = None

        # Show welcome
        self._show_welcome()

    def start_workflow(self, problem: str) -> None:
        """Initialize for a new workflow - remove welcome message."""
        def do_start():
            # Remove welcome message completely
            try:
                container = self.query_one("#welcome-container", Static)
                container.remove()
                self._welcome_shown = False
            except Exception:
                pass

        # Handle thread safety - must happen on main thread
        try:
            self.app.call_from_thread(do_start)
        except RuntimeError:
            # Already on main thread
            do_start()

    def add_phase(self, phase: PhaseContainer) -> None:
        """Add a phase container to the workflow view."""
        self._phases.append(phase)
        self.mount(phase)

    def get_phase(self, phase_num: int) -> Optional[PhaseContainer]:
        """Get a phase container by number."""
        for phase in self._phases:
            if phase.phase_num == phase_num:
                return phase
        return None

    def expand_all(self) -> None:
        """Expand all phases and their contents."""
        for phase in self._phases:
            phase.collapsed = False

    def collapse_all(self) -> None:
        """Collapse all phases."""
        for phase in self._phases:
            phase.collapsed = True

    def scroll_to_phase(self, phase_num: int) -> None:
        """Scroll to a specific phase."""
        phase = self.get_phase(phase_num)
        if phase:
            phase.scroll_visible()


class SystemMessages(Static):
    """Container for system messages (errors, notifications)."""

    DEFAULT_CSS = """
    SystemMessages {
        height: auto;
        max-height: 10;
        padding: 0 1;
        background: #0a0000;
        border-top: solid #330000;
    }

    SystemMessages .message {
        height: 1;
    }

    SystemMessages .message.error {
        color: #ff6666;
    }

    SystemMessages .message.info {
        color: #666666;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._messages: List[str] = []
        self._max_messages = 5

    def add_message(self, message: str, level: str = "info") -> None:
        """Add a system message."""
        self._messages.append((message, level))
        if len(self._messages) > self._max_messages:
            self._messages.pop(0)
        self._render()

    def _render(self) -> None:
        """Render messages."""
        text = Text()
        for msg, level in self._messages:
            if level == "error":
                text.append(f" {msg}\n", style="red")
            else:
                text.append(f" {msg}\n", style="dim")
        self.update(text)

    def clear(self) -> None:
        """Clear all messages."""
        self._messages.clear()
        self.update("")
