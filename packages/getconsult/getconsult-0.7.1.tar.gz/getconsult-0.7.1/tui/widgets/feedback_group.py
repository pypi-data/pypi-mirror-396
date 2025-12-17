"""
FeedbackGroup Widget - Collapsible group for feedback exchanges.

Groups multiple feedback exchanges into a single collapsible container
showing "N feedback exchanges" when collapsed.
Includes copy-to-clipboard functionality for each feedback item.
"""

from typing import List, Tuple
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel

from src.cli import copy_to_clipboard


class FeedbackItem(Static):
    """Individual feedback exchange display with copy button."""

    DEFAULT_CSS = """
    FeedbackItem {
        height: auto;
        margin: 0 0 1 0;
        padding: 0;
    }

    FeedbackItem .feedback-row {
        height: auto;
    }

    FeedbackItem .feedback-panel {
        width: 1fr;
    }

    FeedbackItem .copy-btn {
        width: 3;
        height: 1;
        background: transparent;
        border: none;
        color: #666666;
        padding: 0;
        margin: 0 0 0 1;
        dock: right;
    }

    FeedbackItem .copy-btn:hover {
        color: #ffcc00;
        background: #1a1a00;
    }

    FeedbackItem .copy-btn.-copied {
        color: #00ff00;
    }
    """

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        feedback: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._from_agent = self._format_agent_name(from_agent)
        self._to_agent = self._format_agent_name(to_agent)
        self._feedback = feedback
        self._panel_widget = None

    def _format_agent_name(self, name: str) -> str:
        display = name.replace("_", " ").title()
        if display.startswith("Team "):
            display = display[5:]
        return display

    def compose(self) -> ComposeResult:
        with Horizontal(classes="feedback-row"):
            yield Static("", id="feedback-panel", classes="feedback-panel")
            yield Button("📋", id="copy-btn", classes="copy-btn")

    def on_mount(self) -> None:
        self._panel_widget = self.query_one("#feedback-panel", Static)
        self._update_display()

    def _update_display(self) -> None:
        """Update the feedback item display."""
        if not self._panel_widget:
            return

        try:
            content = Markdown(self._feedback)
        except Exception:
            content = Text(self._feedback)

        # Format title with subtitle for Meta Reviewer
        if "meta" in self._from_agent.lower() and "reviewer" in self._from_agent.lower():
            title = f"FEEDBACK: {self._from_agent} → {self._to_agent}"
            subtitle = "Cross-cutting review across all expert perspectives"
        else:
            title = f"FEEDBACK: {self._from_agent} → {self._to_agent}"
            subtitle = None

        panel = Panel(
            content,
            title=title,
            subtitle=subtitle,
            border_style="yellow",
            padding=(0, 1)
        )
        self._panel_widget.update(panel)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle copy button press."""
        if event.button.id == "copy-btn":
            self._copy_content()
            event.stop()

    def _copy_content(self) -> None:
        """Copy feedback content to clipboard."""
        # Include context in copied text
        header = f"FEEDBACK: {self._from_agent} → {self._to_agent}\n\n"
        if copy_to_clipboard(header + self._feedback):
            try:
                btn = self.query_one("#copy-btn", Button)
                btn.label = "✓"
                btn.add_class("-copied")
                self.set_timer(1.5, self._reset_copy_button)
            except Exception:
                pass

    def _reset_copy_button(self) -> None:
        """Reset copy button to original state."""
        try:
            btn = self.query_one("#copy-btn", Button)
            btn.label = "📋"
            btn.remove_class("-copied")
        except Exception:
            pass


class FeedbackGroup(Static):
    """Collapsible group of feedback exchanges."""

    # Reactive attributes
    collapsed = reactive(True)
    feedback_count = reactive(0)

    DEFAULT_CSS = """
    FeedbackGroup {
        height: auto;
        margin: 0 0 0 1;
        border: solid #333300;
        padding: 0;
    }

    FeedbackGroup .feedback-header {
        height: 1;
        padding: 0 1;
        background: #0a0a00;
    }

    FeedbackGroup .feedback-header:hover {
        background: #151500;
    }

    FeedbackGroup .feedback-content {
        padding: 1;
        height: auto;
    }

    FeedbackGroup.-collapsed .feedback-content {
        display: none;
    }
    """

    class Toggled(Message):
        """Message sent when group is toggled."""
        def __init__(self, feedback_group: "FeedbackGroup", collapsed: bool):
            self.feedback_group = feedback_group
            self.collapsed = collapsed
            super().__init__()

    def __init__(self, title: str = "Feedback Exchange", **kwargs):
        super().__init__(**kwargs)
        self._title = title
        self._feedback_items: List[Tuple[str, str, str]] = []
        self._content_container = None
        self._mounted = False  # Track whether widget is fully mounted

    def compose(self) -> ComposeResult:
        yield Static(id="feedback-header", classes="feedback-header")
        self._content_container = Vertical(classes="feedback-content")
        yield self._content_container

    def on_mount(self) -> None:
        self._update_header()
        if self.collapsed:
            self.add_class("-collapsed")

        # Mount any feedback items that were added before widget was mounted
        if self._content_container and self._feedback_items:
            for from_agent, to_agent, feedback in self._feedback_items:
                item = FeedbackItem(from_agent, to_agent, feedback)
                self._content_container.mount(item)

        # Mark as fully mounted - future add_feedback calls can mount directly
        self._mounted = True

    def watch_collapsed(self, value: bool) -> None:
        if value:
            self.add_class("-collapsed")
        else:
            self.remove_class("-collapsed")
        # Update header to show correct expand/collapse indicator
        self._update_header()

    def watch_feedback_count(self, value: int) -> None:
        self._update_header()

    def _update_header(self) -> None:
        """Update the header display."""
        try:
            header = self.query_one("#feedback-header", Static)
        except Exception:
            return

        text = Text()

        # Expand/collapse indicator
        if self.collapsed:
            text.append("[>] ", style="bold yellow")
        else:
            text.append("[v] ", style="bold yellow")

        # Title with count
        text.append("", style="yellow")
        text.append(f" {self._title} ", style="bold yellow")
        text.append(f"({self.feedback_count} items)", style="dim yellow")

        header.update(text)

    def on_click(self, event) -> None:
        """Handle click to toggle collapse state."""
        self.toggle()
        event.stop()

    def toggle(self) -> None:
        """Toggle the collapsed state."""
        self.collapsed = not self.collapsed
        self.post_message(self.Toggled(self, self.collapsed))

    def expand(self) -> None:
        """Expand this group."""
        self.collapsed = False

    def collapse(self) -> None:
        """Collapse this group."""
        self.collapsed = True

    def add_feedback(self, from_agent: str, to_agent: str, feedback: str) -> None:
        """Add a feedback exchange to the group."""
        self._feedback_items.append((from_agent, to_agent, feedback))
        self.feedback_count = len(self._feedback_items)

        # Only mount directly if widget is fully mounted
        # Otherwise, on_mount will handle mounting all pending items
        if self._mounted and self._content_container:
            item = FeedbackItem(from_agent, to_agent, feedback)
            self._content_container.mount(item)

    def clear_feedback(self) -> None:
        """Remove all feedback items."""
        self._feedback_items.clear()
        self.feedback_count = 0
        if self._content_container:
            self._content_container.remove_children()


class IterationContainer(Static):
    """Container for an iteration's content (feedback + refinements + consensus)."""

    # Reactive attributes
    collapsed = reactive(True)
    iteration_num = reactive(0)
    status = reactive("pending")  # pending, active, complete
    consensus_score = reactive(0.0)

    DEFAULT_CSS = """
    IterationContainer {
        height: auto;
        margin: 0 0 0 1;
        border-left: solid #333333;
        padding: 0;
    }

    IterationContainer.active {
        border-left: solid #ffcc00;
    }

    IterationContainer.complete {
        border-left: solid #00ff41;
    }

    IterationContainer .iteration-header {
        height: 1;
        padding: 0 1;
        background: #050505;
    }

    IterationContainer .iteration-header:hover {
        background: #101010;
    }

    IterationContainer .iteration-content {
        padding: 0 0 0 1;
        height: auto;
    }

    IterationContainer.-collapsed .iteration-content {
        display: none;
    }
    """

    def __init__(self, iteration_num: int, **kwargs):
        super().__init__(**kwargs)
        self.iteration_num = iteration_num
        self._content_container = None
        self._pending_children = []  # Queue children added before mount
        self._mounted = False

    def compose(self) -> ComposeResult:
        yield Static(id="iteration-header", classes="iteration-header")
        self._content_container = Vertical(classes="iteration-content")
        yield self._content_container

    def on_mount(self) -> None:
        self._update_header()
        self._apply_status()
        if self.collapsed:
            self.add_class("-collapsed")

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
        self._apply_status()
        self._update_header()

    def watch_consensus_score(self, value: float) -> None:
        self._update_header()

    def _apply_status(self) -> None:
        self.remove_class("pending", "active", "complete")
        self.add_class(self.status)

    def _update_header(self) -> None:
        """Update the header display."""
        try:
            header = self.query_one("#iteration-header", Static)
        except Exception:
            return

        text = Text()

        # Expand/collapse indicator
        if self.collapsed:
            text.append("[>] ", style="bold cyan")
        else:
            text.append("[v] ", style="bold cyan")

        # Iteration number
        text.append(f"Iteration {self.iteration_num}", style="bold")

        # Status icon
        if self.status == "complete":
            text.append("  ", style="green")
            if self.consensus_score > 0:
                pct = int(self.consensus_score * 100)
                text.append(f" ({pct}%)", style="dim green")
        elif self.status == "active":
            text.append("  ", style="yellow")
        else:
            text.append("  ", style="dim")

        header.update(text)

    def on_click(self, event) -> None:
        """Handle click to toggle collapse state."""
        self.toggle()
        event.stop()

    def toggle(self) -> None:
        """Toggle the collapsed state."""
        self.collapsed = not self.collapsed

    def set_status(self, status: str) -> None:
        """Update status (pending, active, complete)."""
        self.status = status
        if status == "active":
            self.collapsed = False

    def set_consensus(self, score: float) -> None:
        """Set the consensus score for this iteration."""
        self.consensus_score = score

    def add_child(self, widget) -> None:
        """Add a child widget to the content area."""
        if self._mounted and self._content_container:
            self._content_container.mount(widget)
        else:
            # Queue for mounting when widget is fully mounted
            self._pending_children.append(widget)

    @property
    def content(self):
        """Get the content container."""
        return self._content_container
