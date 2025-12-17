"""
AgentCard Widget - Collapsible card showing agent response.

Shows agent name + summary in collapsed state, full markdown response when expanded.
Includes copy-to-clipboard functionality for easy content sharing.
"""

from typing import Optional
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.markdown import Markdown

from src.cli import copy_to_clipboard


class AgentCard(Static):
    """Collapsible card for displaying an agent's response."""

    # Reactive attributes
    collapsed = reactive(True)
    agent_name = reactive("")
    response_type = reactive("Response")
    summary = reactive("")
    full_content = reactive("")
    is_active = reactive(False)

    DEFAULT_CSS = """
    AgentCard {
        height: auto;
        margin: 0 0 0 1;
        border: solid #003311;
        padding: 0;
    }

    AgentCard.active {
        border: solid #ffcc00;
        background: #050800;
    }

    AgentCard .agent-header-row {
        height: 1;
        padding: 0 1;
        background: #001100;
    }

    AgentCard .agent-header-row:hover {
        background: #002200;
    }

    AgentCard.active .agent-header-row {
        background: #0a0800;
    }

    AgentCard .agent-header {
        width: 1fr;
    }

    AgentCard .copy-btn {
        min-width: 4;
        width: 4;
        height: 1;
        background: transparent;
        border: none;
        color: #666666;
        padding: 0;
        margin: 0;
    }

    AgentCard .copy-btn:hover {
        color: #00ff00;
        background: #002200;
    }

    AgentCard .copy-btn.-copied {
        color: #00ff00;
    }

    AgentCard .agent-content {
        padding: 1;
        height: auto;
    }

    AgentCard.-collapsed .agent-content {
        display: none;
    }
    """

    class Toggled(Message):
        """Message sent when card is toggled."""
        def __init__(self, agent_card: "AgentCard", collapsed: bool):
            self.agent_card = agent_card
            self.collapsed = collapsed
            super().__init__()

    def __init__(
        self,
        agent_name: str,
        content: str,
        response_type: str = "Response",
        collapsed: bool = True,
        **kwargs
    ):
        # Initialize _content_widget before super().__init__ to avoid
        # AttributeError when reactive watchers fire during initialization
        self._content_widget: Optional[Static] = None
        super().__init__(**kwargs)
        self.agent_name = self._format_agent_name(agent_name)
        self.response_type = response_type
        self.full_content = content
        self.summary = self._extract_summary(content)
        self.collapsed = collapsed

    def _format_agent_name(self, name: str) -> str:
        """Format agent name for display."""
        # Convert backend_expert -> Backend Expert
        display = name.replace("_", " ").title()
        # Remove "Team " prefix if present
        if display.startswith("Team "):
            display = display[5:]
        return display

    def _extract_summary(self, content: str, max_length: int = 60) -> str:
        """Extract a meaningful summary from content."""
        if not content:
            return "No content"

        # Try to find the first meaningful line
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Skip markdown headers and empty lines
            if line and not line.startswith('#') and not line.startswith('---'):
                # Clean up the line
                summary = line.strip('*_`')
                if len(summary) > max_length:
                    # Find a good break point
                    summary = summary[:max_length]
                    last_space = summary.rfind(' ')
                    if last_space > max_length // 2:
                        summary = summary[:last_space]
                    summary += "..."
                return summary

        # Fallback: use first characters
        clean = content.strip()[:max_length]
        if len(content) > max_length:
            clean += "..."
        return clean

    def compose(self) -> ComposeResult:
        with Horizontal(classes="agent-header-row"):
            yield Static(id="agent-header", classes="agent-header")
            yield Button("📋", id="copy-btn", classes="copy-btn")
        with Vertical(classes="agent-content"):
            yield Static("", id="agent-full-content")

    def on_mount(self) -> None:
        # Get reference to content widget after mount
        try:
            self._content_widget = self.query_one("#agent-full-content", Static)
        except Exception:
            pass
        self._update_header()
        self._update_content()
        if self.collapsed:
            self.add_class("-collapsed")
        if self.is_active:
            self.add_class("active")

    def watch_collapsed(self, value: bool) -> None:
        if value:
            self.add_class("-collapsed")
        else:
            self.remove_class("-collapsed")
        # Update header to show correct expand/collapse indicator
        self._update_header()

    def watch_is_active(self, value: bool) -> None:
        if value:
            self.add_class("active")
        else:
            self.remove_class("active")

    def watch_agent_name(self, value: str) -> None:
        self._update_header()

    def watch_summary(self, value: str) -> None:
        self._update_header()

    def watch_full_content(self, value: str) -> None:
        self._update_content()
        self.summary = self._extract_summary(value)

    def _update_header(self) -> None:
        """Update the header display."""
        try:
            header = self.query_one("#agent-header", Static)
        except Exception:
            return

        text = Text()

        # Expand/collapse indicator
        if self.collapsed:
            text.append("[>] ", style="bold green")
        else:
            text.append("[v] ", style="bold green")

        # Agent name with icon
        text.append("", style="cyan")
        text.append(f" {self.agent_name}", style="bold cyan")

        # Response type if not standard
        if self.response_type != "Response":
            text.append(f" ({self.response_type})", style="dim")

        text.append(": ", style="dim")

        # Summary
        text.append(self.summary, style="white")

        header.update(text)

    def _update_content(self) -> None:
        """Update the full content display."""
        if not self._content_widget:
            return

        try:
            # Render as markdown
            rendered = Markdown(self.full_content)
            self._content_widget.update(rendered)
        except Exception:
            # Fallback to plain text
            self._content_widget.update(self.full_content)

    def on_click(self, event) -> None:
        """Handle click to toggle collapse state (but not on copy button)."""
        # Don't toggle if clicking on copy button
        if hasattr(event, 'widget') and isinstance(event.widget, Button):
            return
        self.toggle()
        event.stop()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle copy button press."""
        if event.button.id == "copy-btn":
            self._copy_content()
            event.stop()

    def _copy_content(self) -> None:
        """Copy content to clipboard and show feedback."""
        if copy_to_clipboard(self.full_content):
            # Visual feedback - change button temporarily
            try:
                btn = self.query_one("#copy-btn", Button)
                btn.label = "✓"
                btn.add_class("-copied")
                # Reset after delay
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

    def toggle(self) -> None:
        """Toggle the collapsed state."""
        self.collapsed = not self.collapsed
        self.post_message(self.Toggled(self, self.collapsed))

    def expand(self) -> None:
        """Expand this card."""
        self.collapsed = False

    def collapse(self) -> None:
        """Collapse this card."""
        self.collapsed = True

    def set_active(self, active: bool) -> None:
        """Mark this card as active/processing."""
        self.is_active = active

    def update_content(self, content: str, response_type: Optional[str] = None) -> None:
        """Update the card content."""
        self.full_content = content
        if response_type:
            self.response_type = response_type


class ThinkingIndicator(Static):
    """Shows that an agent is currently thinking/processing."""

    DEFAULT_CSS = """
    ThinkingIndicator {
        height: 1;
        padding: 0 1 0 2;
        color: #ffcc00;
    }
    """

    def __init__(self, agent_name: str, action: str = "thinking", **kwargs):
        super().__init__(**kwargs)
        self._agent_name = self._format_agent_name(agent_name)
        self._action = action

    def _format_agent_name(self, name: str) -> str:
        display = name.replace("_", " ").title()
        if display.startswith("Team "):
            display = display[5:]
        return display

    def on_mount(self) -> None:
        self._update_display()

    def _update_display(self) -> None:
        text = Text()
        text.append("  ", style="yellow")  # Spinner
        text.append(f"{self._agent_name} ", style="bold yellow")
        text.append(f"{self._action}...", style="yellow")
        self.update(text)

    def set_action(self, action: str) -> None:
        """Update the action text."""
        self._action = action
        self._update_display()
