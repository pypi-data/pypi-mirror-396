"""
StatusHeader Widget - Persistent status bar showing workflow state.

Always visible at top of main content area, providing zero-scroll orientation.
"""

import time
from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text


class StatusHeader(Static):
    """Persistent header showing current workflow state."""

    # Reactive attributes for automatic updates
    phase_info = reactive("--")
    iteration_info = reactive("--")
    consensus_value = reactive(0.0)
    current_action = reactive("Ready")
    is_active = reactive(False)
    elapsed_seconds = reactive(0)

    DEFAULT_CSS = """
    StatusHeader {
        height: 2;
        background: #001a00;
        border-bottom: solid #003311;
        padding: 0 1;
    }

    StatusHeader.active {
        background: #0a0f00;
        border-bottom: solid #00ff41;
    }

    StatusHeader .status-line {
        height: 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._start_time: float = 0
        self._timer = None

    def compose(self) -> ComposeResult:
        yield Static(id="status-line-1", classes="status-line")
        yield Static(id="status-line-2", classes="status-line")

    def on_mount(self) -> None:
        self._update_display()

    def _start_timer(self) -> None:
        """Start the elapsed time timer."""
        self._start_time = time.time()
        self._timer = self.set_interval(1.0, self._tick)

    def _stop_timer(self) -> None:
        """Stop the elapsed time timer."""
        if self._timer:
            self._timer.stop()
            self._timer = None

    def _tick(self) -> None:
        """Update elapsed time every second."""
        if self._start_time > 0:
            self.elapsed_seconds = int(time.time() - self._start_time)

    def _format_elapsed(self) -> str:
        """Format elapsed time as mm:ss or hh:mm:ss."""
        secs = self.elapsed_seconds
        if secs < 3600:
            mins, secs = divmod(secs, 60)
            return f"{mins:02d}:{secs:02d}"
        else:
            hours, remainder = divmod(secs, 3600)
            mins, secs = divmod(remainder, 60)
            return f"{hours}:{mins:02d}:{secs:02d}"

    def watch_elapsed_seconds(self, value: int) -> None:
        self._update_display()

    def watch_phase_info(self, value: str) -> None:
        self._update_display()

    def watch_iteration_info(self, value: str) -> None:
        self._update_display()

    def watch_consensus_value(self, value: float) -> None:
        self._update_display()

    def watch_current_action(self, value: str) -> None:
        self._update_display()

    def watch_is_active(self, value: bool) -> None:
        if value:
            self.add_class("active")
        else:
            self.remove_class("active")
        self._update_display()

    def _update_display(self) -> None:
        """Update the status header display."""
        try:
            line1 = self.query_one("#status-line-1", Static)
            line2 = self.query_one("#status-line-2", Static)
        except Exception:
            return

        # Line 1: Status with clear labels
        text1 = Text()

        if self.is_active:
            # Running indicator with spinner
            spinner_chars = ["◐", "◓", "◑", "◒"]
            spinner = spinner_chars[self.elapsed_seconds % 4]
            text1.append(f" {spinner} ", style="bold green")

            # Phase with label
            text1.append("Phase ", style="dim")
            text1.append(self.phase_info, style="bold green")

            # Separator
            text1.append("  │  ", style="dim")

            # Iteration with label
            text1.append("Iter ", style="dim")
            text1.append(self.iteration_info, style="bold cyan")

            # Separator
            text1.append("  │  ", style="dim")

            # Consensus with label and bar
            text1.append("Consensus ", style="dim")
            consensus_pct = int(self.consensus_value * 100)
            if consensus_pct > 0:
                if self.consensus_value >= 0.8:
                    cons_style = "bold green"
                elif self.consensus_value >= 0.6:
                    cons_style = "bold yellow"
                else:
                    cons_style = "bold red"
                text1.append(f"{consensus_pct}%", style=cons_style)

                # Mini visual bar
                text1.append(" ", style="dim")
                bar_width = 8
                filled = int(bar_width * self.consensus_value)
                text1.append("█" * filled, style=cons_style)
                text1.append("░" * (bar_width - filled), style="dim")
            else:
                text1.append("--", style="dim")

            # Separator and elapsed time
            text1.append("  │  ", style="dim")
            text1.append("Elapsed ", style="dim")
            text1.append(self._format_elapsed(), style="bold cyan")
        else:
            text1.append(" ● ", style="dim green")
            text1.append("READY", style="bold green")
            text1.append("  │  Awaiting query...", style="dim")

        line1.update(text1)

        # Line 2: Current action with animated indicator
        text2 = Text()
        if self.is_active and self.current_action:
            # Animated dots based on elapsed time
            dots = "." * ((self.elapsed_seconds % 3) + 1)
            dots = dots.ljust(3)  # Pad to prevent jumping
            text2.append("   → ", style="yellow")
            text2.append(self.current_action, style="yellow")
            text2.append(dots, style="dim yellow")
        else:
            text2.append("   Enter a query and press Ctrl+Enter to start", style="dim")

        line2.update(text2)

    def update_from_tracker(self, tracker_state: dict) -> None:
        """Update from ProgressTracker state dict."""
        self.phase_info = tracker_state.get("phase", "--")
        self.iteration_info = tracker_state.get("iteration", "--")
        self.consensus_value = tracker_state.get("consensus", 0.0) or 0.0
        self.current_action = tracker_state.get("action", "")
        self.is_active = tracker_state.get("is_active", False)

    def set_workflow_active(self, active: bool = True) -> None:
        """Mark workflow as active/inactive."""
        self.is_active = active
        if active:
            self._start_timer()
        else:
            self._stop_timer()
            self.current_action = f"Complete ({self._format_elapsed()})"

    def set_phase(self, current: int, total: int) -> None:
        """Update phase display."""
        self.phase_info = f"{current}/{total}"

    def set_iteration(self, current: int, total: int) -> None:
        """Update iteration display."""
        self.iteration_info = f"{current}/{total}"

    def set_consensus(self, value: float) -> None:
        """Update consensus value (0.0 to 1.0)."""
        self.consensus_value = value

    def set_action(self, action: str) -> None:
        """Update current action text."""
        self.current_action = action
