"""
QueryDisplay Widget - Collapsible display for the original query.

Shows truncated query when collapsed, full query when expanded.
Always accessible at the top of the workflow view.
"""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical
from textual.reactive import reactive
from rich.text import Text
from rich.markdown import Markdown


class QueryDisplay(Static):
    """Collapsible display for the original query."""

    collapsed = reactive(True)

    DEFAULT_CSS = """
    QueryDisplay {
        height: auto;
        margin: 0 0 1 0;
        border: solid #004400;
        background: #001100;
        padding: 0;
    }

    QueryDisplay:hover {
        border: solid #006600;
    }

    QueryDisplay .query-header {
        height: 1;
        padding: 0 1;
        background: #002200;
    }

    QueryDisplay .query-header:hover {
        background: #003300;
    }

    QueryDisplay .query-content {
        padding: 1;
        height: auto;
        max-height: 20;
    }

    QueryDisplay.-collapsed .query-content {
        display: none;
    }
    """

    def __init__(self, query: str, **kwargs):
        super().__init__(**kwargs)
        self._full_query = query
        self._summary = self._create_summary(query)

    def _create_summary(self, query: str, max_length: int = 80) -> str:
        """Create a truncated summary of the query."""
        # Take first line or first N characters
        first_line = query.split('\n')[0].strip()
        if len(first_line) > max_length:
            return first_line[:max_length] + "..."
        elif len(query) > len(first_line):
            return first_line + "..."
        return first_line

    def compose(self) -> ComposeResult:
        yield Static(id="query-header", classes="query-header")
        with Vertical(classes="query-content"):
            yield Static(id="query-full")

    def on_mount(self) -> None:
        self._update_header()
        self._update_content()
        if self.collapsed:
            self.add_class("-collapsed")

    def watch_collapsed(self, value: bool) -> None:
        if value:
            self.add_class("-collapsed")
        else:
            self.remove_class("-collapsed")
        self._update_header()

    def _update_header(self) -> None:
        """Update the header display."""
        try:
            header = self.query_one("#query-header", Static)
        except Exception:
            return

        text = Text()

        # Expand/collapse indicator
        if self.collapsed:
            text.append("[>] ", style="bold green")
        else:
            text.append("[v] ", style="bold green")

        # Icon and label
        text.append(" ", style="cyan")
        text.append("YOUR QUERY", style="bold cyan")
        text.append(": ", style="dim")

        # Summary when collapsed
        if self.collapsed:
            text.append(self._summary, style="white")

        header.update(text)

    def _update_content(self) -> None:
        """Update the full content display."""
        try:
            content = self.query_one("#query-full", Static)
        except Exception:
            return

        # Display full query
        query_text = Text()
        query_text.append(self._full_query, style="white")
        content.update(query_text)

    def on_click(self, event) -> None:
        """Handle click to toggle collapse state."""
        self.toggle()
        event.stop()

    def toggle(self) -> None:
        """Toggle the collapsed state."""
        self.collapsed = not self.collapsed

    def expand(self) -> None:
        """Expand to show full query."""
        self.collapsed = False

    def collapse(self) -> None:
        """Collapse to show summary."""
        self.collapsed = True

    @property
    def query(self) -> str:
        """Get the full query text."""
        return self._full_query
