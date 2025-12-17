"""
TUI Event Handler - renders workflow events to collapsible widget structure.

This handler receives structured events from workflows and delegates to
WorkflowRenderer for widget-based visualization with progressive disclosure.

The activity log is designed to be CHATTY and ENGAGING - keeping fidgety users
informed with real-time insights, contextual explanations, and personality.
"""

import time
import random
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from rich.text import Text
from rich.panel import Panel
from textual.widgets import RichLog

from src.workflows.base.events import EventListener, WorkflowEvent, EventTypes

if TYPE_CHECKING:
    from .workflow_renderer import WorkflowRenderer
    from .widgets.status_header import StatusHeader
    from .widgets.workflow_view import WorkflowView


class TUIEventHandler(EventListener):
    """Event listener that renders workflow events to collapsible widgets.

    Activity log philosophy: Be the knowledgeable narrator that explains
    what's happening, why it matters, and what to expect next.
    """

    # Contextual tips shown during different phases
    PHASE1_TIPS = [
        "Each expert analyzes your query from their unique perspective",
        "Initial responses tend to be comprehensive - refinement comes later",
        "Diverse viewpoints lead to better final answers",
        "Experts don't see each other's initial responses yet",
    ]

    FEEDBACK_TIPS = [
        "Peer review helps catch blind spots and biases",
        "Constructive criticism improves solution quality",
        "Experts learn from each other's perspectives",
        "This mirrors real-world collaborative problem solving",
    ]

    REFINEMENT_TIPS = [
        "Experts incorporate valid feedback into their positions",
        "Refinement doesn't mean abandoning core insights",
        "Good ideas survive peer scrutiny and become stronger",
        "Watch for convergence - similar conclusions from different angles",
    ]

    def __init__(
        self,
        workflow_view: "WorkflowView",
        status_header: Optional["StatusHeader"] = None,
        system_messages: Optional[RichLog] = None
    ):
        """
        Initialize the event handler.

        Args:
            workflow_view: The main WorkflowView widget
            status_header: Optional StatusHeader widget for status updates
            system_messages: Optional RichLog for system/error messages
        """
        self.workflow_view = workflow_view
        self.status_header = status_header
        self.system_messages = system_messages

        # Track state for richer logging
        self._workflow_start_time: float = 0
        self._current_phase: int = 0
        self._current_iteration: int = 0
        self._agents_responded: List[str] = []
        self._total_agents: int = 0
        self._feedback_count: int = 0
        self._shown_tips: set = set()

        # Import here to avoid circular imports
        from .workflow_renderer import WorkflowRenderer
        self.renderer = WorkflowRenderer(workflow_view, status_header)

    def _update_status(self, phase: str) -> None:
        """Update status bar with current phase (no-op, status bar removed)."""
        pass

    # === Activity Log Helpers ===

    def _log(self, message: Text | str, style: str = "") -> None:
        """Write a timestamped message to the activity log."""
        if not self.system_messages:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        text = Text()
        text.append(f"[{timestamp}] ", style="dim")

        if isinstance(message, str):
            text.append(message, style=style)
        else:
            text.append_text(message)

        self.system_messages.write(text)

    def _log_header(self, icon: str, title: str, style: str = "bold") -> None:
        """Log a prominent header line."""
        text = Text()
        text.append(f"{icon} ", style=style)
        text.append(title, style=style)
        self._log(text)

    def _log_detail(self, message: str, style: str = "dim") -> None:
        """Log an indented detail line."""
        text = Text()
        text.append("   ", style="dim")
        text.append(message, style=style)
        self._log(text)

    def _log_progress(self, current: int, total: int, what: str) -> None:
        """Log a progress indicator."""
        bar_width = 10
        filled = int(bar_width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)

        text = Text()
        text.append("   ", style="dim")
        text.append(f"[{bar}] ", style="cyan")
        text.append(f"{current}/{total} {what}", style="dim cyan")
        self._log(text)

    def _log_tip(self, tips: List[str], category: str) -> None:
        """Show a contextual tip (once per category per workflow)."""
        if category in self._shown_tips:
            return
        self._shown_tips.add(category)

        tip = random.choice(tips)
        text = Text()
        text.append("   💡 ", style="dim yellow")
        text.append(tip, style="dim italic yellow")
        self._log(text)

    def _format_agent(self, name: str) -> str:
        """Format agent name for display."""
        return name.replace('_', ' ').title().replace('Team ', '')

    def _elapsed(self) -> str:
        """Get elapsed time since workflow start."""
        if self._workflow_start_time == 0:
            return "0s"
        secs = int(time.time() - self._workflow_start_time)
        if secs < 60:
            return f"{secs}s"
        mins, secs = divmod(secs, 60)
        return f"{mins}m {secs}s"

    def on_event(self, event: WorkflowEvent) -> None:
        """Route event to appropriate handler."""
        handler_name = f'_handle_{event.event_type}'
        handler = getattr(self, handler_name, None)
        if handler:
            handler(event.data)

    # === Workflow Lifecycle ===

    def _handle_workflow_start(self, data: dict) -> None:
        """Initialize workflow visualization."""
        problem = data.get('problem', '')
        agents = data.get('agents', [])
        mode = data.get('mode', 'single')
        threshold = data.get('consensus_threshold', 0.8)
        max_iter = data.get('max_iterations', 1)

        # Reset state tracking
        self._workflow_start_time = time.time()
        self._current_phase = 0
        self._current_iteration = 0
        self._agents_responded = []
        self._total_agents = len(agents)
        self._feedback_count = 0
        self._shown_tips = set()

        # Initialize the workflow view
        self.workflow_view.start_workflow(problem)

        # Chatty workflow start
        self._log_header("🚀", "WORKFLOW INITIATED", "bold green")

        # Show the assembled team
        agent_names = [self._format_agent(a) for a in agents]
        self._log_detail(f"Assembled {len(agents)} experts:", "cyan")
        for name in agent_names:
            self._log_detail(f"  • {name}", "dim cyan")

        # Show configuration
        self._log_detail(f"Consensus threshold: {int(threshold*100)}%", "dim")
        self._log_detail(f"Max iterations: {max_iter}", "dim")

        # Set expectations
        text = Text()
        text.append("   Each expert will independently analyze your query, ", style="dim")
        text.append("then they'll critique each other ", style="dim")
        text.append("and refine their positions until consensus.", style="dim")
        self._log(text)

        # Delegate to renderer
        self.renderer.on_workflow_start(data)
        self._update_status("INITIALIZING")

    def _handle_workflow_complete(self, data: dict) -> None:
        """Handle workflow completion."""
        self.renderer.on_workflow_complete(data)
        self._update_status("COMPLETE")

        success = data.get('success', True)
        consensus_reached = data.get('consensus_reached', False)
        final_score = data.get('final_consensus_score', 0.0)
        duration = data.get('duration', 0)

        # Visual separator
        self._log("━" * 50, "dim")

        # Completion header
        if success:
            self._log_header("✅", "WORKFLOW COMPLETE", "bold green")
        else:
            self._log_header("⚠️", "WORKFLOW FINISHED WITH ISSUES", "bold yellow")

        # Resolution method with context
        if consensus_reached:
            pct = int(final_score * 100) if final_score else 0
            self._log_detail(f"Resolution: EXPERT CONSENSUS ({pct}%)", "green")
            self._log_detail("All experts aligned on the solution", "dim green")
            self._log_detail("This indicates high confidence in the answer", "dim green")
        else:
            self._log_detail("Resolution: ORCHESTRATOR SYNTHESIS", "yellow")
            self._log_detail("Experts had different perspectives (this is normal!)", "dim yellow")
            self._log_detail("Orchestrator analyzed all positions and created balanced answer", "dim")
            self._log_detail("Different viewpoints were weighed by expertise relevance", "dim")

        # Duration and stats
        mins, secs = divmod(int(duration), 60)
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
        self._log_detail(f"Duration: {time_str}", "dim cyan")
        self._log_detail(f"Phases completed: {self._current_phase}/3", "dim")
        if self._current_iteration > 0:
            self._log_detail(f"Refinement iterations: {self._current_iteration}", "dim")

        # Closing guidance
        self._log_detail("Press [D] to explore each expert's reasoning trace", "dim italic")

    def _handle_error(self, data: dict) -> None:
        """Handle and display error."""
        message = data.get('message', 'Unknown error')
        agent = data.get('agent_name', '')

        self.renderer.on_error(data)

        # Detailed error logging
        if agent:
            self._log_header("❌", f"ERROR from {self._format_agent(agent)}", "bold red")
        else:
            self._log_header("❌", "ERROR OCCURRED", "bold red")

        self._log_detail(message, "red")
        self._log_detail("The workflow will attempt to continue...", "dim yellow")

    # === Phase Events ===

    def _handle_phase_start(self, data: dict) -> None:
        """Handle phase start."""
        phase_num = data.get('phase_num', 0)
        phase_name = data.get('phase_name', '')

        self._current_phase = phase_num
        self._agents_responded = []  # Reset for new phase

        self.renderer.on_phase_start(data)

        # Visual separator between phases
        if phase_num > 1:
            self._log("─" * 40, "dim")

        # Phase-specific chatty messages
        phase_info = {
            1: {
                "name": "INITIAL ANALYSIS",
                "icon": "🔍",
                "style": "bold cyan",
                "desc": "Each expert analyzes your query independently",
                "what_next": "Experts are thinking... responses will appear shortly"
            },
            2: {
                "name": "PEER REVIEW & REFINEMENT",
                "icon": "🔄",
                "style": "bold yellow",
                "desc": "Experts critique and learn from each other",
                "what_next": "This is where the magic happens - diverse perspectives converge"
            },
            3: {
                "name": "RESOLUTION",
                "icon": "✨",
                "style": "bold green",
                "desc": "Synthesizing final answer from expert positions",
                "what_next": "Almost done! Creating the comprehensive response"
            }
        }

        info = phase_info.get(phase_num, {
            "name": phase_name,
            "icon": "▶",
            "style": "bold",
            "desc": "",
            "what_next": ""
        })

        self._log_header(info["icon"], f"PHASE {phase_num}: {info['name']}", info["style"])
        if info["desc"]:
            self._log_detail(info["desc"], "dim")
        if info["what_next"]:
            self._log_detail(info["what_next"], "dim italic")

        # Phase-specific tips
        if phase_num == 1:
            self._log_tip(self.PHASE1_TIPS, "phase1")

        # Update status based on phase
        if phase_num == 1:
            self._update_status("EXPERTS ANALYZING")
        elif phase_num == 2:
            self._update_status("PEER REVIEW")
        else:
            self._update_status("RESOLVING")

    def _handle_iteration_start(self, data: dict) -> None:
        """Handle iteration start."""
        iteration = data.get('iteration', 1)
        max_iter = data.get('max_iterations', 3)

        self._current_iteration = iteration
        self._agents_responded = []
        self._feedback_count = 0

        self.renderer.on_iteration_start(data)

        # Iteration context
        self._log_header("🔁", f"ITERATION {iteration}", "bold cyan")

        if iteration == 1:
            self._log_detail("First pass: Experts share initial critiques", "dim")
        elif iteration == max_iter:
            self._log_detail("Final iteration: Last chance to reach consensus", "dim yellow")
        else:
            self._log_detail(f"Refinement round {iteration}: Positions evolving", "dim")

    # === Agent Events ===

    def _handle_agent_thinking(self, data: dict) -> None:
        """Handle agent thinking indicator."""
        agent = data.get('agent_name', '')
        action = data.get('action', 'thinking')

        self.renderer.on_agent_thinking(data)

        # Chatty thinking status
        agent_display = self._format_agent(agent)

        # Different messages based on context
        if "presentation" in agent.lower():
            self._update_status("SYNTHESIZING ANSWER")
            self._log_detail(f"🎯 {agent_display} is preparing the final synthesis...", "magenta")
        elif self._current_phase == 1:
            self._log_detail(f"💭 {agent_display} is formulating their analysis...", "dim cyan")
        elif self._current_phase == 2:
            if "feedback" in action.lower() or "critiq" in action.lower():
                self._log_detail(f"🔎 {agent_display} is reviewing peer solutions...", "dim yellow")
            else:
                self._log_detail(f"📝 {agent_display} is refining their position...", "dim cyan")
        else:
            self._log_detail(f"⚙️ {agent_display} working...", "dim")

    def _handle_agent_response(self, data: dict) -> None:
        """Handle agent response."""
        agent = data.get('agent_name', '')
        response_type = data.get('response_type', '')

        self.renderer.on_agent_response(data)

        # Track responses and show progress
        agent_display = self._format_agent(agent)

        if agent not in self._agents_responded:
            self._agents_responded.append(agent)

        # Response-type specific messages
        if response_type == "Initial Analysis":
            self._log_detail(f"✓ {agent_display} submitted their analysis", "green")
            self._log_progress(len(self._agents_responded), self._total_agents, "experts responded")
        elif "Refined" in response_type:
            self._log_detail(f"✓ {agent_display} updated their position", "cyan")
            self._log_progress(len(self._agents_responded), self._total_agents, "experts refined")
        elif response_type == "Final Answer":
            self._log_header("📋", f"Final answer ready from {agent_display}", "bold green")

    def _handle_parallel_progress(self, data: dict) -> None:
        """Handle parallel execution progress."""
        completed = data.get('completed', 0)
        total = data.get('total', 0)
        agent = data.get('agent_name', '')

        if completed > 0 and total > 0:
            self._log_progress(completed, total, "parallel tasks")

    # === Feedback Events ===

    def _handle_feedback_phase_start(self, data: dict) -> None:
        """Handle feedback phase start."""
        self.renderer.on_feedback_phase_start(data)
        self._update_status("EXCHANGING FEEDBACK")
        self._feedback_count = 0

        self._log_header("💬", "FEEDBACK EXCHANGE", "bold yellow")
        self._log_detail("Experts now read and critique each other's work", "dim")
        self._log_detail("Constructive criticism helps refine solutions", "dim italic")
        self._log_tip(self.FEEDBACK_TIPS, "feedback")

    def _handle_feedback_exchange(self, data: dict) -> None:
        """Handle individual feedback exchange."""
        self.renderer.on_feedback_exchange(data)

        from_agent = self._format_agent(data.get('from_agent', ''))
        to_agent = self._format_agent(data.get('to_agent', ''))

        self._feedback_count += 1

        # Show feedback flow with context
        text = Text()
        text.append("   ", style="dim")
        text.append(f"{from_agent}", style="cyan")
        text.append(" → ", style="dim yellow")
        text.append(f"{to_agent}", style="cyan")
        text.append(f" [critique #{self._feedback_count}]", style="dim")
        self._log(text)

    # === Refinement Events ===

    def _handle_refinement_phase_start(self, data: dict) -> None:
        """Handle refinement phase start."""
        self.renderer.on_refinement_phase_start(data)
        self._update_status("REFINING SOLUTIONS")
        self._agents_responded = []  # Reset for refinement tracking

        self._log_header("📝", "REFINEMENT PHASE", "bold cyan")
        self._log_detail("Experts incorporate feedback into updated positions", "dim")
        self._log_detail("Watch for positions converging toward agreement", "dim italic")
        self._log_tip(self.REFINEMENT_TIPS, "refinement")

    # === Consensus Events ===

    def _handle_consensus_evaluation_start(self, data: dict) -> None:
        """Handle consensus evaluation start with clear explanation."""
        self.renderer.on_consensus_evaluation_start(data)
        self._update_status("CROSS-EXPERT APPROVAL")

        self._log_header("📊", "CROSS-EXPERT APPROVAL", "bold magenta")
        self._log_detail("Question: Would I sign off on THEIR solution for production?", "dim italic")
        self._log("")
        self._log_detail("✅ APPROVE    ⚠️ CONCERNS    ❌ OBJECT", "dim")
        self._log("")

    def _handle_cross_expert_approval(self, data: dict) -> None:
        """Handle individual pairwise approval result.

        Activity log shows brief verdict only - main view shows full details.
        """
        # Pass to renderer for main view accumulation
        self.renderer.on_cross_expert_approval(data)

        evaluator = self._format_agent(data.get('evaluator', ''))
        target = self._format_agent(data.get('target', ''))
        verdict = data.get('verdict', 'UNKNOWN')
        score = data.get('score', 0.0)

        # Verdict icons and styles
        verdict_styles = {
            'APPROVE': ('✅', 'green'),
            'APPROVE_WITH_CONCERNS': ('⚠️', 'yellow'),
            'CONCERNS': ('⚠️', 'yellow'),
            'OBJECT': ('❌', 'red'),
            'ERROR': ('💥', 'red'),
            'UNKNOWN': ('❓', 'dim')
        }
        icon, style = verdict_styles.get(verdict.upper(), ('❓', 'dim'))
        score_pct = int(score * 100)

        # Brief verdict line only - reasoning shown in main view
        text = Text()
        text.append(f"  {icon} ", style=style)
        text.append(f"{evaluator}", style="cyan")
        text.append(" → ", style="dim")
        text.append(f"{target}", style="cyan")
        text.append(f": {score_pct}%", style=f"dim {style}")
        self._log(text)

    def _handle_consensus_check(self, data: dict) -> None:
        """Handle consensus check results with transparent math."""
        self.renderer.on_consensus_check(data)

        score = data.get('score', data.get('final_score', 0.0))
        threshold = data.get('threshold', 0.8)
        interpretation = data.get('interpretation', '')
        individual_scores = data.get('individual_scores', [])

        # IMPORTANT: Validate 'reached' against actual score vs threshold
        # Don't blindly trust event data - it may be inconsistent
        actually_reached = score >= threshold
        reached = data.get('reached', actually_reached)

        # If there's a mismatch, trust the math
        if reached != actually_reached:
            reached = actually_reached

        pct = int(score * 100)
        threshold_pct = int(threshold * 100)

        # Show the calculation transparently in the log
        if individual_scores:
            num_reviews = len(individual_scores)
            score_sum = sum(individual_scores)
            self._log_detail(f"Math: ({score_sum:.1f}) / {num_reviews} reviews = {pct}%", "dim")

        if reached:
            self._log_header("✅", f"CONSENSUS: {pct}% ≥ {threshold_pct}% threshold", "bold green")
            if interpretation:
                self._log_detail(f"{interpretation}", "dim green")
            self._log_detail("Proceeding to final synthesis", "dim")
        else:
            self._log_header("⚠️", f"APPROVAL: {pct}% < {threshold_pct}% threshold", "bold yellow")
            if interpretation:
                self._log_detail(f"{interpretation}", "dim yellow")

            remaining_gap = threshold_pct - pct
            if remaining_gap > 20:
                self._log_detail("Significant objections - another iteration needed", "dim")
            else:
                self._log_detail("Close to approval! One more round might achieve consensus", "dim")

    # === Orchestrator Events ===

    def _handle_orchestrator_intervention(self, data: dict) -> None:
        """Handle orchestrator intervention."""
        self.renderer.on_orchestrator_intervention(data)
        self._update_status("ORCHESTRATOR DECIDING")

        reason = data.get('reason', 'max iterations reached')

        self._log("─" * 40, "dim")
        self._log_header("⚖️", "ORCHESTRATOR INTERVENTION", "bold magenta")
        self._log_detail(f"Trigger: {reason}", "magenta")
        self._log_detail("This is normal when experts have legitimately different perspectives", "dim")
        self._log_detail("The orchestrator will:", "dim")
        self._log_detail("  1. Analyze each expert's reasoning", "dim cyan")
        self._log_detail("  2. Identify areas of agreement & disagreement", "dim cyan")
        self._log_detail("  3. Synthesize a balanced answer honoring all valid points", "dim cyan")
        self._log_detail("Result: A comprehensive answer that no single expert could provide", "dim italic")

    def _handle_expert_compromise_responses(self, data: dict) -> None:
        """Handle expert responses to orchestrator's proposal."""
        responses = data.get('responses', [])

        if responses:
            self._log_detail("Experts reviewing orchestrator's synthesis:", "dim")

        for resp in responses:
            agent = self._format_agent(resp.get('agent_name', ''))
            decision = resp.get('decision', '')

            if 'accept' in decision.lower() or 'agree' in decision.lower():
                self._log_detail(f"  ✓ {agent}: Accepts synthesis", "green")
            elif 'reject' in decision.lower() or 'disagree' in decision.lower():
                self._log_detail(f"  ✗ {agent}: Has reservations", "yellow")
            else:
                self._log_detail(f"  • {agent}: {decision[:30]}...", "dim")

            self.renderer.on_agent_response({
                'agent_name': resp.get('agent_name', ''),
                'content': f"**Decision:** {resp.get('decision', '')}\n\n{resp.get('reasoning', '')}",
                'response_type': 'Compromise Response'
            })

    # === Clarification Events ===

    def _handle_clarification_analyzing(self, data: dict) -> None:
        """Handle clarification analysis starting."""
        self._log_header("🔍", "ANALYZING QUERY", "bold cyan")
        self._log_detail("Checking if clarification would help...", "dim italic")

    def _handle_clarification_needed(self, data: dict) -> None:
        """Handle clarification needed event - show questions to user."""
        questions = data.get('questions', [])
        reasoning = data.get('reasoning', '')

        self._log_header("❓", "CLARIFICATION NEEDED", "bold cyan")
        self._log_detail(f"Found {len(questions)} question(s) to help experts understand your needs", "dim")
        if reasoning:
            self._log_detail(f"Reason: {reasoning}", "dim italic")

        self._log_detail("Answer questions in the panel →", "dim yellow")

        # The modal display is handled by the app
        if hasattr(self, '_on_clarification_needed') and self._on_clarification_needed:
            self._on_clarification_needed(questions)

    def _handle_clarification_response(self, data: dict) -> None:
        """Handle user's clarification responses."""
        responses = data.get('responses', {})

        self._log_header("✓", "CLARIFICATIONS RECEIVED", "bold green")
        for question, answer in responses.items():
            q_short = question[:40] + "..." if len(question) > 40 else question
            if isinstance(answer, list):
                answer_str = ", ".join(answer)
            else:
                answer_str = str(answer)
            self._log_detail(f"{q_short}: {answer_str}", "dim cyan")

        self._log_detail("Proceeding with enhanced context...", "dim")

    def _handle_clarification_skipped(self, data: dict) -> None:
        """Handle user skipping clarification."""
        reason = data.get('reason', 'user_skipped')

        if reason == "timeout":
            self._log_header("⏱️", "CLARIFICATION TIMED OUT", "bold yellow")
            self._log_detail("Proceeding with original query", "dim")
        else:
            self._log_header("⏭️", "CLARIFICATION SKIPPED", "bold yellow")
            self._log_detail("Proceeding with original query", "dim")

    def set_clarification_callback(self, callback) -> None:
        """Set callback for when clarification is needed.

        Args:
            callback: Function that receives list of questions and shows modal
        """
        self._on_clarification_needed = callback

    # === Utility Methods ===

    def reset(self) -> None:
        """Reset for new workflow."""
        self._workflow_start_time = 0
        self._current_phase = 0
        self._current_iteration = 0
        self._agents_responded = []
        self._total_agents = 0
        self._feedback_count = 0
        self._shown_tips = set()
        self.renderer.reset()

    def scroll_to_current(self) -> None:
        """Scroll to current active section."""
        self.renderer.scroll_to_current()

    def collapse_all(self) -> None:
        """Collapse all expanded sections."""
        self.renderer.collapse_all()

    def expand_current(self) -> None:
        """Expand current active section."""
        self.renderer.expand_current()
