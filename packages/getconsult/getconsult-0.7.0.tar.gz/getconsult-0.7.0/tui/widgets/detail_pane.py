"""
DetailPane Widget - Agent Journey Visualization.

Shows how each agent evolved through the consensus workflow:
- Initial position
- Critiques received from peers
- Refinements made
- Final consensus position
- Cross-expert approvals received (how others evaluated this agent)
- Cross-expert approvals given (how this agent evaluated others)

History is retained across queries in the same session.
Toggle with 'D' key.
"""

from typing import Dict, List, Optional, TYPE_CHECKING
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical, VerticalScroll, Horizontal
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.markdown import Markdown

if TYPE_CHECKING:
    from ..workflow_renderer import WorkflowRenderer, AgentJourneyData, QueryJourney, ApprovalRecord


class ConsensusTrendChart(Static):
    """Shows consensus trend as ASCII sparkline - hidden until data exists."""

    DEFAULT_CSS = """
    ConsensusTrendChart {
        height: auto;
        margin: 1 0 0 0;
        padding: 0 1;
        border-top: solid #333300;
        background: #050500;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._history: List[float] = []

    def update_history(self, history: List[float]) -> None:
        """Update with new consensus history."""
        self._history = history
        self._update_display()

    def on_mount(self) -> None:
        # Hide initially - only show when we have data
        self.display = False

    def _update_display(self) -> None:
        # Hide if no data
        if not self._history:
            self.display = False
            return

        # Show and update
        self.display = True

        text = Text()
        text.append("GROUP CONSENSUS: ", style="bold yellow")

        # Create sparkline
        blocks = ['\u2581', '\u2582', '\u2583', '\u2584', '\u2585', '\u2586', '\u2587', '\u2588']
        min_val = min(self._history) if self._history else 0
        max_val = max(self._history) if self._history else 1
        range_val = max_val - min_val if max_val > min_val else 1

        sparkline = ""
        for val in self._history:
            normalized = (val - min_val) / range_val
            idx = min(int(normalized * 7), 7)
            sparkline += blocks[idx]

        # Color based on final value
        final_val = self._history[-1] if self._history else 0
        if final_val >= 0.8:
            style = "green"
        elif final_val >= 0.5:
            style = "yellow"
        else:
            style = "red"

        text.append(sparkline, style=f"bold {style}")

        # Show percentage progression
        text.append("  ", style="dim")
        for i, val in enumerate(self._history):
            text.append(f"{int(val * 100)}%", style=style if i == len(self._history) - 1 else "dim")
            if i < len(self._history) - 1:
                text.append(" > ", style="dim")

        self.update(text)


class AgentTab(Static):
    """Individual tab for agent selection."""

    DEFAULT_CSS = """
    AgentTab {
        height: 1;
        width: auto;
        min-width: 14;
        padding: 0 2;
        margin: 0 1 0 0;
        background: #333333;
        color: #cccccc;
        border: tall #555555;
        text-align: center;
    }

    AgentTab:hover {
        background: #444444;
        color: #ffffff;
        border: tall #00ff41;
    }

    AgentTab.selected {
        background: #004400;
        border: tall #00ff41;
        color: #00ff41;
        text-style: bold;
    }
    """

    def __init__(self, agent_name: str, **kwargs):
        super().__init__(**kwargs)
        self._agent_name = agent_name

    def on_mount(self) -> None:
        # Show shortened name for tab with visual emphasis
        short_name = self._agent_name.replace(" Expert", "")
        self.update(f"[ {short_name} ]")

    def on_click(self, event) -> None:
        """Handle click to select this agent."""
        event.stop()
        self.post_message(AgentSelector.AgentSelected(self._agent_name))


class AgentSelector(Static):
    """Single widget showing agent selection with keyboard hints."""

    DEFAULT_CSS = """
    AgentSelector {
        height: auto;
        min-height: 3;
        background: #001100;
        padding: 0 1;
        margin: 0 0 1 0;
        border: solid #003311;
    }
    """

    selected_agent = reactive("")

    class AgentSelected(Message):
        """Message sent when an agent is selected."""
        def __init__(self, agent_name: str):
            self.agent_name = agent_name
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agents: List[str] = []

    def on_mount(self) -> None:
        """Show initial state."""
        self._update_display()

    def set_agents(self, agents: List[str]) -> None:
        """Set the list of agents to display."""
        self._agents = agents
        self._update_display()

    def _update_display(self) -> None:
        """Update the display."""
        text = Text()
        text.append("SELECT AGENT:\n", style="bold green")

        if not self._agents:
            text.append("No agents yet - start a workflow", style="yellow italic")
            self.update(text)
            return

        # Build the display with numbered agents
        for i, agent in enumerate(self._agents):
            short_name = agent.replace(" Expert", "")
            is_selected = agent == self.selected_agent

            # Add separator
            if i > 0:
                text.append("  │  ", style="dim")

            # Number key hint
            text.append(f"[{i+1}]", style="bold yellow")
            text.append(" ", style="dim")

            # Agent name - highlighted if selected
            if is_selected:
                text.append(f"▶ {short_name}", style="bold green reverse")
            else:
                text.append(short_name, style="white")

        text.append("\n", style="dim")
        text.append("Press 1-9 to select agent", style="dim italic")

        self.update(text)

    def watch_selected_agent(self, value: str) -> None:
        self._update_display()

    def select_by_index(self, index: int) -> None:
        """Select agent by index (0-based)."""
        if 0 <= index < len(self._agents):
            self.selected_agent = self._agents[index]
            self.post_message(AgentSelector.AgentSelected(self._agents[index]))


class JourneyPhase(Vertical):
    """Collapsible section for a journey phase - simpler design."""

    collapsed = reactive(False)  # Start expanded by default
    phase_name = reactive("")
    phase_type = reactive("")

    DEFAULT_CSS = """
    JourneyPhase {
        height: auto;
        margin: 0 0 1 0;
        padding: 0;
    }

    JourneyPhase.initial {
        border-left: thick #00aaff;
    }

    JourneyPhase.feedback {
        border-left: thick #ffcc00;
    }

    JourneyPhase.refinement {
        border-left: thick #cc66ff;
    }

    JourneyPhase.consensus {
        border-left: thick #00ff41;
    }

    JourneyPhase .phase-header {
        height: 1;
        padding: 0 1;
        background: #001100;
    }

    JourneyPhase .phase-header:hover {
        background: #002200;
    }

    JourneyPhase .phase-content {
        padding: 0 1;
        height: auto;
    }

    JourneyPhase.-collapsed .phase-content {
        display: none;
    }
    """

    def __init__(self, phase_name: str, phase_type: str, content=None, collapsed: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.phase_name = phase_name
        self.phase_type = phase_type
        self._initial_content = content
        self._content_widgets: List = []
        self.collapsed = collapsed  # Set initial collapsed state

    def compose(self) -> ComposeResult:
        # Header with click to toggle
        yield Static(self._make_header_text(), classes="phase-header")
        # Content container
        with Vertical(classes="phase-content"):
            if self._initial_content:
                yield self._initial_content
            for widget in self._content_widgets:
                yield widget

    def _make_header_text(self) -> Text:
        text = Text()
        if self.collapsed:
            text.append("[>] ", style="bold cyan")
        else:
            text.append("[v] ", style="bold cyan")
        text.append(self.phase_name, style="bold white")
        return text

    def on_mount(self) -> None:
        self.add_class(self.phase_type)
        if self.collapsed:
            self.add_class("-collapsed")

    def watch_collapsed(self, value: bool) -> None:
        if value:
            self.add_class("-collapsed")
        else:
            self.remove_class("-collapsed")
        # Update header text
        try:
            header = self.query_one(".phase-header", Static)
            header.update(self._make_header_text())
        except Exception:
            pass

    def on_click(self, event) -> None:
        """Handle click to toggle collapse."""
        # Only toggle if clicking header area
        self.collapsed = not self.collapsed
        event.stop()

    def add_content_widget(self, widget) -> None:
        """Add content widget before compose."""
        self._content_widgets.append(widget)


class FeedbackReceivedCard(Static):
    """Shows feedback received from one peer."""

    DEFAULT_CSS = """
    FeedbackReceivedCard {
        height: auto;
        margin: 0 0 1 1;
        padding: 0;
    }
    """

    def __init__(self, from_agent: str, feedback: str, iteration: int, **kwargs):
        super().__init__(**kwargs)
        self._from_agent = from_agent
        self._feedback = feedback
        self._iteration = iteration

    def on_mount(self) -> None:
        self._update_display()

    def _update_display(self) -> None:
        """Render the feedback card - full content, no truncation."""
        try:
            content = Markdown(self._feedback)
        except Exception:
            content = Text(self._feedback)

        # Format title with subtitle for Meta Reviewer
        if "meta" in self._from_agent.lower() and "reviewer" in self._from_agent.lower():
            title = f"FEEDBACK: {self._from_agent} → (Iter {self._iteration})"
            subtitle = "Cross-cutting review across all expert perspectives"
        else:
            title = f"FEEDBACK: {self._from_agent} → (Iter {self._iteration})"
            subtitle = None

        panel = Panel(
            content,
            title=title,
            subtitle=subtitle,
            border_style="yellow",
            padding=(0, 1)
        )
        self.update(panel)


class ApprovalCard(Static):
    """Shows a cross-expert approval record (given or received)."""

    DEFAULT_CSS = """
    ApprovalCard {
        height: auto;
        margin: 0 0 1 1;
        padding: 0;
    }
    """

    def __init__(self, approval: "ApprovalRecord", direction: str, **kwargs):
        """
        Args:
            approval: The approval record
            direction: "given" (this agent reviewed someone) or "received" (someone reviewed this agent)
        """
        super().__init__(**kwargs)
        self._approval = approval
        self._direction = direction

    def on_mount(self) -> None:
        self._update_display()

    def _update_display(self) -> None:
        """Render the approval card with verdict, score, and reasoning."""
        approval = self._approval
        verdict = approval.verdict.upper()

        # Determine styling based on verdict
        if 'APPROVE' in verdict and 'CONCERN' not in verdict:
            icon, border_style, verdict_style = "✅", "green", "bold green"
        elif 'CONCERN' in verdict:
            icon, border_style, verdict_style = "⚠️", "yellow", "bold yellow"
        elif 'OBJECT' in verdict:
            icon, border_style, verdict_style = "❌", "red", "bold red"
        else:
            icon, border_style, verdict_style = "❓", "dim", "dim"

        # Format title based on direction
        evaluator = approval.evaluator.replace('_', ' ').title()
        target = approval.target.replace('_', ' ').title()
        score_pct = int(approval.score * 100)

        if self._direction == "given":
            title = f"{icon} REVIEWED: {target}"
        else:
            title = f"{icon} FROM: {evaluator}"

        # Build content
        content = Text()
        content.append(f"Verdict: {verdict} ", style=verdict_style)
        content.append(f"({score_pct}%)\n", style="dim")

        # Show endorsements
        if approval.endorsements:
            content.append("\n✓ Endorsements:\n", style="green")
            for e in approval.endorsements[:3]:  # Top 3
                content.append(f"  • {e}\n", style="dim green")

        # Show concerns
        if approval.concerns:
            content.append("\n⚠ Concerns:\n", style="yellow")
            for c in approval.concerns[:3]:  # Top 3
                content.append(f"  • {c}\n", style="dim yellow")

        # Show objections
        if approval.objections:
            content.append("\n✗ Objections:\n", style="red")
            for o in approval.objections[:3]:  # Top 3
                content.append(f"  • {o}\n", style="dim red")

        panel = Panel(
            content,
            title=title,
            border_style=border_style,
            padding=(0, 1)
        )
        self.update(panel)


class JourneyView(VerticalScroll):
    """Main container for displaying an agent's journey."""

    DEFAULT_CSS = """
    JourneyView {
        height: 1fr;
        padding: 0;
        background: #000500;
    }

    JourneyView .empty-state {
        padding: 2;
        text-align: center;
        color: #666666;
    }

    JourneyView .agent-title {
        height: 2;
        padding: 0 1;
        background: #002200;
        border-bottom: solid #00ff41;
        text-align: center;
    }

    JourneyView .content-preview {
        padding: 1;
        background: #001100;
        border: solid #003311;
        margin: 0 0 1 0;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._phases: Dict[str, JourneyPhase] = {}
        self._separator: Optional[Static] = None  # Track separator for cleanup
        self._current_agent: str = ""

    def compose(self) -> ComposeResult:
        yield Static(id="journey-agent-title", classes="agent-title")
        yield Static(id="journey-empty", classes="empty-state")

    def on_mount(self) -> None:
        self._show_empty()

    def _show_empty(self, agent_name: str = "") -> None:
        """Show empty state message."""
        try:
            # Show agent title even when waiting
            title = self.query_one("#journey-agent-title", Static)
            if agent_name:
                title_text = Text()
                title_text.append("VIEWING: ", style="dim")
                title_text.append(agent_name.upper(), style="bold green")
                title.update(title_text)
                title.display = True
            else:
                title.display = False
        except Exception:
            pass

        try:
            empty = self.query_one("#journey-empty", Static)
            text = Text()
            text.append("⏳ Waiting for data...\n\n", style="bold yellow")
            text.append("Journey details appear after agents complete analysis.\n\n", style="dim")
            text.append("For each query, you'll see:\n", style="dim")
            text.append("  💡 Initial Position\n", style="blue")
            text.append("  👥 Peer Reviews Received\n", style="yellow")
            text.append("  🔄 Revised Position\n", style="magenta")
            text.append("  ✅ Consensus Contribution\n\n", style="green")
            text.append("Press ", style="dim")
            text.append("D", style="bold green")
            text.append(" to close", style="dim")
            empty.update(text)
            empty.display = True
        except Exception:
            pass

    def _render_query_journey(self, query: str, journey_data, prefix: str = "", is_current: bool = True) -> None:
        """Render a single query's journey phases.

        Args:
            query: The query text
            journey_data: Either AgentJourneyData (current) or QueryJourney (history)
            prefix: Prefix for phase IDs to avoid collisions
            is_current: Whether this is the current query (affects styling)
        """
        # Query header
        query_text = Text()
        if is_current:
            query_text.append("❯ ", style="bold cyan")
        else:
            query_text.append("◦ ", style="dim")
        display_query = query[:300] + "..." if len(query) > 300 else query
        query_text.append(display_query, style="white" if is_current else "dim")

        query_widget = Static(Panel(
            query_text,
            title="Query" if is_current else "Previous Query",
            border_style="cyan" if is_current else "dim",
            padding=(0, 1)
        ))
        query_phase = JourneyPhase(
            "📋 QUERY" if is_current else "📋 QUERY",
            "initial",
            content=query_widget,
            collapsed=not is_current  # Collapse history queries
        )
        self.mount(query_phase)
        self._phases[f"{prefix}query"] = query_phase

        # Check for actual journey data
        has_data = (
            journey_data.initial_response or
            journey_data.feedback_received or
            journey_data.refinements or
            journey_data.final_response
        )

        if not has_data:
            return

        # 1. INITIAL POSITION - first take on the problem
        if journey_data.initial_response:
            try:
                content = Markdown(journey_data.initial_response)
            except Exception:
                content = Text(journey_data.initial_response)
            content_widget = Static(Panel(content, border_style="blue", padding=(0, 1)))
            phase = JourneyPhase("💡 INITIAL POSITION", "initial", content=content_widget, collapsed=not is_current)
            self.mount(phase)
            self._phases[f"{prefix}initial"] = phase

        # 2. PEER REVIEWS RECEIVED - feedback from other experts
        if journey_data.feedback_received:
            count = len(journey_data.feedback_received)
            phase = JourneyPhase(f"👥 PEER REVIEWS RECEIVED ({count})", "feedback", collapsed=not is_current)
            for from_agent, feedback, iteration in journey_data.feedback_received:
                card = FeedbackReceivedCard(from_agent, feedback, iteration)
                phase.add_content_widget(card)
            self.mount(phase)
            self._phases[f"{prefix}feedback"] = phase

        # 3. REVISED POSITION - updated answer after considering feedback
        if journey_data.refinements:
            count = len(journey_data.refinements)
            phase = JourneyPhase(f"🔄 REVISED POSITION ({count} updates)", "refinement", collapsed=not is_current)
            for iteration, ref_content in journey_data.refinements:
                try:
                    md_content = Markdown(ref_content)
                except Exception:
                    md_content = Text(ref_content)
                phase.add_content_widget(Static(
                    Panel(md_content, title=f"After Round {iteration}", border_style="magenta", padding=(0, 1))
                ))
            self.mount(phase)
            self._phases[f"{prefix}refinement"] = phase

        # 4. CONSENSUS CONTRIBUTION - final aligned position
        consensus_text = Text()
        if journey_data.consensus_score is not None:
            pct = int(journey_data.consensus_score * 100)
            if pct >= 80:
                consensus_text.append(f"✓ {pct}% ALIGNED ", style="bold green")
                consensus_text.append("with group consensus\n\n", style="green")
            elif pct >= 50:
                consensus_text.append(f"◐ {pct}% PARTIAL ", style="bold yellow")
                consensus_text.append("agreement\n\n", style="yellow")
            else:
                consensus_text.append(f"✗ {pct}% DIVERGENT ", style="bold red")
                consensus_text.append("from group\n\n", style="red")
        else:
            consensus_text.append("⏳ Awaiting consensus evaluation...\n\n", style="dim italic")

        if journey_data.final_response:
            try:
                # Try to render as markdown for rich formatting
                final_content = Markdown(journey_data.final_response)
                consensus_text.append_text(Text(journey_data.final_response))
            except Exception:
                consensus_text.append(journey_data.final_response, style="white")

        content_widget = Static(Panel(consensus_text, border_style="green", padding=(0, 1)))
        phase = JourneyPhase("✅ CONSENSUS CONTRIBUTION", "consensus", content=content_widget, collapsed=not is_current)
        self.mount(phase)
        self._phases[f"{prefix}consensus"] = phase

        # 5. APPROVALS RECEIVED - how other experts evaluated this agent's solution
        approvals_received = getattr(journey_data, 'approvals_received', [])
        if approvals_received:
            count = len(approvals_received)
            # Calculate average score received
            avg_score = sum(a.score for a in approvals_received) / count if count > 0 else 0
            avg_pct = int(avg_score * 100)
            phase = JourneyPhase(f"📥 APPROVALS RECEIVED ({count}, avg {avg_pct}%)", "consensus", collapsed=not is_current)
            for approval in approvals_received:
                card = ApprovalCard(approval, direction="received")
                phase.add_content_widget(card)
            self.mount(phase)
            self._phases[f"{prefix}approvals_received"] = phase

        # 6. APPROVALS GIVEN - how this agent evaluated others' solutions
        approvals_given = getattr(journey_data, 'approvals_given', [])
        if approvals_given:
            count = len(approvals_given)
            # Calculate average score given
            avg_score = sum(a.score for a in approvals_given) / count if count > 0 else 0
            avg_pct = int(avg_score * 100)
            phase = JourneyPhase(f"📤 APPROVALS GIVEN ({count}, avg {avg_pct}%)", "feedback", collapsed=True)  # Collapsed by default
            for approval in approvals_given:
                card = ApprovalCard(approval, direction="given")
                phase.add_content_widget(card)
            self.mount(phase)
            self._phases[f"{prefix}approvals_given"] = phase

    def show_journey(self, journey: "AgentJourneyData", current_query: str = "") -> None:
        """Display a complete agent journey with query context and history.

        Structure per query:
        - Query text
        - Initial Position (first take)
        - Peer Reviews Received (feedback from others)
        - Revised Position (after considering feedback)
        - Consensus Contribution (final aligned answer)
        """
        self._current_agent = journey.agent_name

        # Check if there's any actual data
        has_data = (
            journey.initial_response or
            journey.feedback_received or
            journey.refinements or
            journey.final_response
        )

        # If no data yet, show waiting message with agent name
        if not has_data and not journey.query_history:
            self.clear_journey()
            self._show_empty(journey.agent_name)
            return

        # Show agent title
        try:
            title = self.query_one("#journey-agent-title", Static)
            title_text = Text()
            title_text.append("VIEWING: ", style="dim")
            title_text.append(journey.agent_name.upper(), style="bold green")
            total_queries = 1 + len(journey.query_history) if has_data else len(journey.query_history)
            if total_queries > 1:
                title_text.append(f"  │  {total_queries} queries in session", style="dim italic")
            title.update(title_text)
            title.display = True
        except Exception:
            pass

        # Hide empty state
        try:
            empty = self.query_one("#journey-empty", Static)
            empty.display = False
        except Exception:
            pass

        # Clear existing phases
        self.clear_journey()

        # Render current query journey (expanded)
        if has_data or current_query:
            self._render_query_journey(
                query=current_query or "(current query)",
                journey_data=journey,
                prefix="current_",
                is_current=True
            )

        # Render history (collapsed, most recent first)
        if journey.query_history:
            # Add separator (only one)
            self._separator = Static(Text("─── PRIOR QUERIES ───", style="dim"), classes="history-separator")
            self.mount(self._separator)

            for i, hist in enumerate(journey.query_history):
                self._render_query_journey(
                    query=hist.query,
                    journey_data=hist,
                    prefix=f"hist{i}_",
                    is_current=False
                )

    def clear_journey(self) -> None:
        """Clear all journey content."""
        for phase in list(self._phases.values()):
            try:
                phase.remove()
            except Exception:
                pass
        self._phases.clear()

        # Remove separator if exists
        if self._separator:
            try:
                self._separator.remove()
            except Exception:
                pass
            self._separator = None

    def clear(self) -> None:
        """Clear and show empty state."""
        self.clear_journey()
        self._show_empty()


class DetailPane(VerticalScroll):
    """Agent Journey visualization pane."""

    selected_agent = reactive("")

    DEFAULT_CSS = """
    DetailPane {
        height: 100%;
        padding: 0;
        background: #000500;
    }

    DetailPane .detail-header {
        height: 1;
        background: #001a00;
        border-bottom: solid #00ff41;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._renderer: Optional["WorkflowRenderer"] = None
        self._consensus_chart: Optional[ConsensusTrendChart] = None
        self._agent_selector: Optional[AgentSelector] = None
        self._journey_view: Optional[JourneyView] = None

    def compose(self) -> ComposeResult:
        # Compact header - self-descriptive name
        header_text = Text()
        header_text.append("REASONING TRACE ", style="bold green")
        header_text.append("| 1-9 switch ", style="dim")
        header_text.append("[D close]", style="dim yellow")
        yield Static(header_text, id="detail-header", classes="detail-header")

        # Agent selector first (primary action)
        self._agent_selector = AgentSelector(id="agent-selector")
        yield self._agent_selector

        # Journey view (main content)
        self._journey_view = JourneyView(id="journey-view")
        yield self._journey_view

        # Consensus trend at bottom (supplementary - hidden until data)
        self._consensus_chart = ConsensusTrendChart(id="consensus-chart")
        yield self._consensus_chart

    def set_renderer(self, renderer: "WorkflowRenderer") -> None:
        """Set the workflow renderer reference for data access."""
        self._renderer = renderer

    def refresh_view(self) -> None:
        """Refresh the detail pane with current data."""
        if not self._renderer:
            return

        # Update consensus chart
        history = self._renderer.get_consensus_history()
        if self._consensus_chart:
            self._consensus_chart.update_history(history)

        # Update agent selector
        agents = self._renderer.get_all_agent_names()
        if self._agent_selector and agents:
            self._agent_selector.set_agents(agents)

            # If no agent selected, select first
            if not self.selected_agent and agents:
                self.selected_agent = agents[0]

        # Update journey view for selected agent
        self._update_journey()

    def watch_selected_agent(self, value: str) -> None:
        """Watch for agent selection changes."""
        if self._agent_selector:
            self._agent_selector.selected_agent = value
        self._update_journey()

    def _update_journey(self) -> None:
        """Update journey view for selected agent."""
        if not self._renderer or not self.selected_agent or not self._journey_view:
            return

        journey = self._renderer.get_agent_journey(self.selected_agent)
        current_query = self._renderer.get_current_query()
        self._journey_view.show_journey(journey, current_query)

    def on_agent_selector_agent_selected(self, event: AgentSelector.AgentSelected) -> None:
        """Handle agent selection from selector."""
        self.selected_agent = event.agent_name

    def select_agent_by_number(self, number: int) -> bool:
        """Select agent by number key (1-based). Returns True if handled."""
        if self._agent_selector and number >= 1:
            index = number - 1  # Convert to 0-based
            self._agent_selector.select_by_index(index)
            return True
        return False

    def on_data_update(self, event_type: str, agent_name: Optional[str] = None) -> None:
        """Handle notification that data has updated."""
        # Only refresh if pane is visible
        if self.display:
            self.refresh_view()

    def clear(self) -> None:
        """Clear all content."""
        if self._consensus_chart:
            self._consensus_chart.update_history([])
        if self._journey_view:
            self._journey_view.clear()
        self.selected_agent = ""
