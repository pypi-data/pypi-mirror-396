"""
PhaseContainer Widget - Collapsible container for workflow phases.

Each phase (Analysis, Peer Review, Resolution) is represented by a PhaseContainer
that can be expanded/collapsed. Shows status icons and contains child widgets.
"""

from typing import Optional
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text


class PhaseStatus:
    """Phase status constants."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"


class PhaseContainer(Static):
    """Collapsible container for a workflow phase."""

    # Reactive attributes
    collapsed = reactive(True)
    status = reactive(PhaseStatus.PENDING)
    phase_title = reactive("")
    phase_num = reactive(0)
    elapsed_time = reactive("")

    DEFAULT_CSS = """
    PhaseContainer {
        height: auto;
        margin: 0 0 1 0;
        border-left: thick #336633;
        padding: 0;
    }

    PhaseContainer.active {
        border-left: thick #ffcc00;
        background: #050a00;
    }

    PhaseContainer.complete {
        border-left: thick #00ff41;
    }

    PhaseContainer.pending {
        border-left: thick #333333;
    }

    PhaseContainer .phase-header {
        height: 1;
        padding: 0 1;
        background: #001100;
    }

    PhaseContainer .phase-header:hover {
        background: #002200;
    }

    PhaseContainer.active .phase-header {
        background: #0a0f00;
    }

    PhaseContainer .phase-content {
        padding: 0 0 0 2;
        height: auto;
        min-height: 1;
    }

    PhaseContainer.-collapsed .phase-content {
        display: none;
    }

    #phase-content {
        height: auto;
        min-height: 1;
    }
    """

    class Toggled(Message):
        """Message sent when phase is toggled."""
        def __init__(self, phase_container: "PhaseContainer", collapsed: bool):
            self.phase_container = phase_container
            self.collapsed = collapsed
            super().__init__()

    def __init__(
        self,
        phase_num: int,
        title: str,
        status: str = PhaseStatus.PENDING,
        collapsed: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.phase_num = phase_num
        self.phase_title = title
        self.status = status
        self.collapsed = collapsed
        self._content_container: Optional[Vertical] = None
        self._pending_children = []  # Queue children added before mount
        self._mounted = False

    def compose(self) -> ComposeResult:
        yield Static(id="phase-header", classes="phase-header")
        yield Vertical(id="phase-content", classes="phase-content")

    def on_mount(self) -> None:
        # Get reference to content container after mount
        try:
            self._content_container = self.query_one("#phase-content", Vertical)
        except Exception:
            pass
        self._update_header()
        self._apply_status_class()
        # Apply initial collapsed state
        if self.collapsed:
            self.add_class("-collapsed")
        else:
            self.remove_class("-collapsed")

        # Mount any children that were added before widget was mounted
        if self._content_container and self._pending_children:
            for child in self._pending_children:
                self._content_container.mount(child)
            self._pending_children.clear()

        self._mounted = True

    def watch_collapsed(self, value: bool) -> None:
        if value:
            self.add_class("-collapsed")
        else:
            self.remove_class("-collapsed")
        # Update header to show correct expand/collapse indicator
        self._update_header()

    def watch_status(self, value: str) -> None:
        self._apply_status_class()
        self._update_header()

    def watch_phase_title(self, value: str) -> None:
        self._update_header()

    def watch_elapsed_time(self, value: str) -> None:
        self._update_header()

    def _apply_status_class(self) -> None:
        """Apply the appropriate CSS class based on status."""
        self.remove_class("pending", "active", "complete")
        self.add_class(self.status)

    def _update_header(self) -> None:
        """Update the header display."""
        try:
            header = self.query_one("#phase-header", Static)
        except Exception:
            return

        text = Text()

        # Expand/collapse indicator
        if self.collapsed:
            text.append("[+] ", style="bold green")
        else:
            text.append("[-] ", style="bold green")

        # Phase number and title
        text.append(f"Phase {self.phase_num}: ", style="bold")
        text.append(self.phase_title, style="bold white")

        # Status icon
        if self.status == PhaseStatus.COMPLETE:
            text.append("  ", style="green")
        elif self.status == PhaseStatus.ACTIVE:
            text.append("  ", style="yellow")
        else:
            text.append("  ", style="dim")

        # Elapsed time if available
        if self.elapsed_time:
            text.append(f" ({self.elapsed_time})", style="dim")

        header.update(text)

    def on_click(self, event) -> None:
        """Handle click to toggle collapse state."""
        # Check if click was on header
        try:
            header = self.query_one("#phase-header", Static)
            # Toggle if clicking on the phase container or header
            self.toggle()
            event.stop()
        except Exception:
            pass

    def toggle(self) -> None:
        """Toggle the collapsed state."""
        self.collapsed = not self.collapsed
        self.post_message(self.Toggled(self, self.collapsed))

    def set_expanded(self, expanded: bool = True) -> None:
        """Set the expanded/collapsed state."""
        self.collapsed = not expanded

    def set_status(self, status: str) -> None:
        """Update the phase status."""
        self.status = status
        # Auto-expand when becoming active
        if status == PhaseStatus.ACTIVE:
            self.collapsed = False

    def set_elapsed(self, elapsed: str) -> None:
        """Set elapsed time display."""
        self.elapsed_time = elapsed

    def add_child(self, widget) -> None:
        """Add a child widget to the content area.

        This method handles the async nature of Textual mounting by
        queuing widgets added before mount and mounting directly after.
        """
        if self._mounted and self._content_container:
            # Widget is fully mounted, mount child directly
            try:
                self._content_container.mount(widget)
            except Exception:
                pass
        else:
            # Queue for mounting when widget is fully mounted
            self._pending_children.append(widget)

    def clear_children(self) -> None:
        """Remove all child widgets from content area."""
        if self._content_container:
            self._content_container.remove_children()

    @property
    def content(self) -> Optional[Vertical]:
        """Get the content container."""
        return self._content_container
