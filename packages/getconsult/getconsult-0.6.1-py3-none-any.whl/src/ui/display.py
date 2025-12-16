"""
Clean, human-friendly terminal display inspired by best CLI tools.

ConsoleDisplay implements EventListener to receive workflow events
and render them appropriately for terminal output.
"""

import shutil
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..workflows.base.events import EventListener, WorkflowEvent, EventTypes


class DisplayTheme:
    """Standardized visual language for consistent, polished output"""

    # Status indicators - consistent visual vocabulary
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "💡"
    THINKING = "🧠"
    ROCKET = "🚀"
    TARGET = "🎯"
    CONSENSUS = "📊"
    TEAM = "👥"
    CONFIG = "⚙️"
    TIME = "⏱️"
    LOOP = "🔄"
    CELEBRATE = "🎉"

    # Section delimiters - visual hierarchy
    HEADER_CHAR = "═"
    SECTION_CHAR = "─"
    HEAVY_DIVIDER = "━"

    # Box drawing characters
    BOX_TOP_LEFT = "┌"
    BOX_TOP_RIGHT = "┐"
    BOX_BOTTOM_LEFT = "└"
    BOX_BOTTOM_RIGHT = "┘"
    BOX_HORIZONTAL = "─"
    BOX_VERTICAL = "│"

    # Progress bar elements
    PROGRESS_FILLED = "█"
    PROGRESS_EMPTY = "░"

    # Standard spacing
    INDENT = "  "

    # Rich colors for semantic meaning
    PRIMARY = "cyan"
    SUCCESS_COLOR = "green"
    WARNING_COLOR = "yellow"
    ERROR_COLOR = "red"
    MUTED = "dim"
    AGENT_COLOR = "bold cyan"
    PHASE_COLOR = "bold magenta"

    @classmethod
    def divider(cls, width: int = 60, style: str = "light") -> str:
        """Create a visual divider"""
        char = cls.HEAVY_DIVIDER if style == "heavy" else cls.SECTION_CHAR
        return char * width

    @classmethod
    def progress_bar(cls, current: int, total: int, width: int = 30) -> str:
        """Create a progress bar"""
        if total == 0:
            return cls.PROGRESS_EMPTY * width
        filled = int((current / total) * width)
        return cls.PROGRESS_FILLED * filled + cls.PROGRESS_EMPTY * (width - filled)


class ConsoleDisplay(EventListener):
    """
    Terminal display that implements EventListener.

    Receives workflow events and renders them with Rich formatting.
    Supports both direct terminal output and piped output modes.
    """

    def __init__(self, width: int = None):
        import sys
        self.is_piped = not sys.stdout.isatty()
        self.width = width or self._get_terminal_width()
        self.indent = "  "

        # Configure Rich Console based on output mode
        if self.is_piped:
            self.rich_console = Console(force_terminal=False, no_color=True)
        else:
            self.rich_console = Console(width=self.width, soft_wrap=True)

    def _get_terminal_width(self) -> int:
        """Get terminal width dynamically"""
        try:
            width = shutil.get_terminal_size().columns
            return max(80, width)
        except Exception:
            return 120

    # =========================================================================
    # EventListener Implementation
    # =========================================================================

    def on_event(self, event: WorkflowEvent) -> None:
        """
        Handle incoming workflow events.

        Routes events to specific handler methods based on event type.
        """
        handler_name = f'_handle_{event.event_type}'
        handler = getattr(self, handler_name, None)
        if handler:
            handler(event.data)

    # =========================================================================
    # Event Handlers
    # =========================================================================

    def _handle_workflow_start(self, data: dict) -> None:
        """Handle workflow_start event"""
        self._render_header(
            problem=data.get('problem', ''),
            expert_agents=data.get('agents', []),
            consensus_threshold=data.get('consensus_threshold', 0.8),
            max_iterations=data.get('max_iterations', 3),
            mode=data.get('mode', 'single'),
            teams=data.get('teams'),
            provider=data.get('provider')
        )

    def _handle_phase_start(self, data: dict) -> None:
        """Handle phase_start event"""
        self._render_phase_header(
            phase_num=data.get('phase_num', 1),
            phase_name=data.get('phase_name', ''),
            description=data.get('description', ''),
            total_phases=data.get('total_phases', 3)
        )

    def _handle_iteration_start(self, data: dict) -> None:
        """Handle iteration_start event"""
        self._render_iteration_header(
            iteration=data.get('iteration', 1),
            elapsed=data.get('elapsed', 0.0)
        )

    def _handle_agent_thinking(self, data: dict) -> None:
        """Handle agent_thinking event"""
        self._render_agent_thinking(
            agent_name=data.get('agent_name', ''),
            phase=data.get('phase', ''),
            estimated_seconds=data.get('estimated_seconds')
        )

    def _handle_agent_response(self, data: dict) -> None:
        """Handle agent_response event"""
        self._render_agent_response(
            agent_name=data.get('agent_name', ''),
            content=data.get('content', ''),
            response_type=data.get('response_type', 'response')
        )

    def _handle_parallel_progress(self, data: dict) -> None:
        """Handle parallel_progress event"""
        self._render_parallel_progress(
            completed=data.get('completed', 0),
            total=data.get('total', 0),
            operation=data.get('operation', '')
        )

    def _handle_feedback_phase_start(self, data: dict) -> None:
        """Handle feedback_phase_start event"""
        self._render_feedback_phase_start()

    def _handle_feedback_exchange(self, data: dict) -> None:
        """Handle feedback_exchange event"""
        self._render_feedback_exchange(
            from_agent=data.get('from_agent', ''),
            to_agent=data.get('to_agent', ''),
            feedback=data.get('feedback', '')
        )

    def _handle_refinement_phase_start(self, data: dict) -> None:
        """Handle refinement_phase_start event"""
        self._render_refinement_phase_start()

    def _handle_consensus_evaluation_start(self, data: dict) -> None:
        """Handle consensus_evaluation_start event"""
        self._render_consensus_evaluation_start()

    def _handle_cross_expert_approval(self, data: dict) -> None:
        """Handle cross_expert_approval event - individual pairwise approval"""
        self._render_cross_expert_approval(
            evaluator=data.get('evaluator', ''),
            target=data.get('target', ''),
            verdict=data.get('verdict', ''),
            score=data.get('score', 0.0),
            endorsements=data.get('endorsements', []),
            concerns=data.get('concerns', []),
            objections=data.get('objections', [])
        )

    def _handle_consensus_check(self, data: dict) -> None:
        """Handle consensus_check event"""
        self._render_consensus_check(
            score=data.get('final_score', data.get('score', 0.0)),
            threshold=data.get('threshold', 0.8),
            interpretation=data.get('interpretation', ''),
            approval_matrix=data.get('approval_matrix')
        )

    def _handle_orchestrator_intervention(self, data: dict) -> None:
        """Handle orchestrator_intervention event"""
        self._render_orchestrator_intervention_start(
            elapsed_time=data.get('elapsed_time', '')
        )

    def _handle_expert_compromise_responses(self, data: dict) -> None:
        """Handle expert_compromise_responses event"""
        self._render_expert_compromise_responses_start()

    def _handle_workflow_complete(self, data: dict) -> None:
        """Handle workflow_complete event"""
        self._render_completion_summary(
            consensus_reached=data.get('consensus_reached', False),
            duration=data.get('duration', 0.0),
            iteration_count=data.get('iteration_count', 0),
            max_iterations=data.get('max_iterations', 3)
        )

    def _handle_error(self, data: dict) -> None:
        """Handle error event"""
        message = data.get('message', 'Unknown error')
        print(f"\n{DisplayTheme.ERROR} Error: {message}\n")

    # =========================================================================
    # Render Methods (actual display logic)
    # =========================================================================

    def _render_header(self, problem: str, expert_agents: List[Any],
                       consensus_threshold: float, max_iterations: int,
                       mode: str = "single", teams: Dict[str, List[Any]] = None,
                       provider: str = None):
        """Render workflow header"""
        # Title
        header_text = Text()
        header_text.append(f"{DisplayTheme.ROCKET} ", style="bold")
        header_text.append("Consult", style="bold cyan")
        print("\n")
        self.rich_console.print(Panel(header_text, border_style=DisplayTheme.PRIMARY, padding=(0, 2)))
        print()

        # Compact info section
        from ..config import Config
        threshold_pct = int(consensus_threshold * 100)

        # Problem
        problem_short = problem[:80] + "..." if len(problem) > 80 else problem
        print(f"📋 **{problem_short}**")

        # Model/team info
        if mode == "team" and teams:
            team_names = ", ".join(sorted(teams.keys()))
            print(f"🤖 Teams: {team_names} | 👥 Experts per team: {len(list(teams.values())[0])}")
        else:
            actual_provider = provider or Config.DEFAULT_SINGLE_PROVIDER
            model_name = Config.get_model_for_provider(actual_provider)
            experts = [agent.name.replace('_', ' ').title() for agent in expert_agents]
            print(f"🤖 {model_name} | 👥 {', '.join(experts)}")

        # Config
        print(f"⚙️ Consensus: {threshold_pct}% | Max rounds: {max_iterations}")
        print()
        print("─" * 50)
        print()

    def _render_phase_header(self, phase_num: int, phase_name: str,
                             description: str, total_phases: int = 3):
        """Render phase header"""
        phase_emojis = {1: "🔍", 2: DisplayTheme.LOOP, 3: "🎭"}
        emoji = phase_emojis.get(phase_num, "📋")
        progress = DisplayTheme.progress_bar(phase_num, total_phases, width=20)
        percentage = int(phase_num / total_phases * 100)

        header_text = Text()
        header_text.append(f"{emoji} PHASE {phase_num}/{total_phases}: ", style="bold")
        header_text.append(phase_name.upper(), style=DisplayTheme.PHASE_COLOR)

        print("\n")
        self.rich_console.print(Panel(
            header_text,
            subtitle=f"[dim]{progress} {percentage}%[/dim]",
            border_style=DisplayTheme.PHASE_COLOR,
            padding=(0, 2)
        ))
        if description:
            print(f"{DisplayTheme.INDENT}[dim]{description}[/dim]")
        print()

    def _render_iteration_header(self, iteration: int, elapsed: float):
        """Render iteration header"""
        time_str = f"{elapsed:.0f}s" if elapsed >= 1 else f"{elapsed:.1f}s"
        print("\n\n")
        print("-" * 60)
        print(f"🔄 ITERATION {iteration} • Time Elapsed: {time_str}")
        print("-" * 60)
        print()

    def _render_agent_thinking(self, agent_name: str, phase: str,
                               estimated_seconds: int = None):
        """Render agent thinking indicator"""
        agent_display = agent_name.replace('_', ' ').title()
        time_hint = ""
        if estimated_seconds:
            if estimated_seconds < 60:
                time_hint = f" (~{estimated_seconds}s)"
            else:
                minutes = estimated_seconds // 60
                time_hint = f" (~{minutes}min)"
        print(f"🧠 {agent_display} {phase}...{time_hint}")

    def _render_agent_response(self, agent_name: str, content: str,
                               response_type: str = "response"):
        """Render agent response with Rich Panel"""
        agent_display = agent_name.replace('_', ' ').title()

        if not content or not content.strip():
            content = f"{DisplayTheme.WARNING} No response received from agent."

        response_emojis = {
            "initial analysis": "🔍",
            "refined solution": "✨",
            "response to orchestrator compromise": "🤝",
            "compromise proposal": DisplayTheme.TARGET
        }
        emoji = response_emojis.get(response_type.lower(), "💭")
        title = f"{emoji} {agent_display}"

        # Always use Rich Panel for proper rendering
        md_content = Markdown(content, code_theme="monokai", inline_code_theme="monokai")
        panel = Panel(
            md_content,
            title=title,
            title_align="left",
            border_style=DisplayTheme.PRIMARY,
            padding=(1, 2)
        )
        print()
        self.rich_console.print(panel)
        print()

    def _render_parallel_progress(self, completed: int, total: int, operation: str):
        """Render parallel operation progress"""
        percentage = int((completed / total) * 100) if total > 0 else 0
        filled_blocks = int((completed / total) * 10) if total > 0 else 0
        empty_blocks = 10 - filled_blocks
        progress_bar = "█" * filled_blocks + "░" * empty_blocks

        print(f"\r⚡ {operation}: {progress_bar} {completed}/{total} ({percentage}%)", end='', flush=True)
        if completed == total:
            print()

    def _render_feedback_phase_start(self):
        """Render feedback phase start"""
        print("\n")
        print("💬 Peer Feedback Exchange")
        print("─" * 40)
        print("Each expert reviews others' solutions")
        print()

    def _render_feedback_exchange(self, from_agent: str, to_agent: str, feedback: str):
        """Render feedback exchange"""
        from_display = from_agent.replace('_', ' ').title()
        to_display = to_agent.replace('_', ' ').title()

        print("\n\n")
        print("  " + "=" * 60)
        print(f"  💬 FEEDBACK: {from_display} → {to_display}")
        print("  " + "=" * 60)
        print()

        md = Markdown(feedback, code_theme="monokai", inline_code_theme="monokai")
        self.rich_console.print(md)
        print()

    def _render_refinement_phase_start(self):
        """Render refinement phase start"""
        print("\n")
        print("✨ Solution Refinement")
        print("─" * 40)
        print("Agents integrate feedback and improve solutions")
        print()

    def _render_consensus_evaluation_start(self):
        """Render consensus evaluation start with clear explanation"""
        print("\n")
        print("📊 Cross-Expert Approval")
        print("─" * 50)
        print("Question: Would I sign off on THEIR solution?")
        print()
        print("✅ APPROVE    ⚠️ CONCERNS    ❌ OBJECT")
        print("─" * 50)
        print()

    def _render_cross_expert_approval(self, evaluator: str, target: str,
                                       verdict: str, score: float,
                                       endorsements: list = None, concerns: list = None,
                                       objections: list = None):
        """Render individual pairwise approval result with reasoning"""
        evaluator_display = evaluator.replace('_', ' ').title()
        target_display = target.replace('_', ' ').title()
        endorsements = endorsements or []
        concerns = concerns or []
        objections = objections or []

        # Verdict icons
        verdict_icons = {
            'APPROVE': '✅',
            'APPROVE WITH CONCERNS': '⚠️',
            'CONCERNS': '⚠️',
            'OBJECT': '❌',
            'ERROR': '💥',
            'UNKNOWN': '❓'
        }
        icon = verdict_icons.get(verdict.upper(), '❓')
        score_pct = int(score * 100)

        print(f"  {icon} {evaluator_display} → {target_display}: {verdict} ({score_pct}%)")

        # Show reasoning
        for endorsement in endorsements[:2]:
            truncated = endorsement[:70] + '...' if len(endorsement) > 70 else endorsement
            print(f"      ✓ {truncated}")
        for concern in concerns[:2]:
            truncated = concern[:70] + '...' if len(concern) > 70 else concern
            print(f"      ⚠ {truncated}")
        for objection in objections[:2]:
            truncated = objection[:70] + '...' if len(objection) > 70 else objection
            print(f"      ✗ {truncated}")

    def _render_consensus_check(self, score: float, threshold: float,
                                 interpretation: str = '', approval_matrix: dict = None):
        """Render consensus check with transparent math explanation"""
        score_pct = int(score * 100)
        threshold_pct = int(threshold * 100)

        if score >= threshold:
            status_icon = DisplayTheme.SUCCESS
            status_text = "CONSENSUS REACHED"
            border_style = DisplayTheme.SUCCESS_COLOR
            outcome_text = "Experts approved each other's solutions → proceeding to final synthesis"
        else:
            status_icon = DisplayTheme.LOOP
            needed = threshold_pct - score_pct
            status_text = f"Need {needed}% more approval"
            border_style = DisplayTheme.WARNING_COLOR
            outcome_text = "Some experts objected → will iterate or orchestrator resolves"

        progress = DisplayTheme.progress_bar(score_pct, 100, width=30)

        content = Text()

        # Show the math transparently
        if approval_matrix:
            # Calculate totals for explanation
            all_scores = []
            pairwise_details = []
            for evaluator, targets in approval_matrix.items():
                for target, data in targets.items():
                    pair_score = data.get('score', 0.5)
                    verdict = data.get('verdict', 'UNKNOWN')
                    all_scores.append(pair_score)
                    # Format names nicely
                    ev_name = evaluator.replace('_', ' ').title()
                    tg_name = target.replace('_', ' ').title()
                    if 'Team ' in ev_name:
                        ev_name = ev_name.replace('Team ', '')
                    if 'Team ' in tg_name:
                        tg_name = tg_name.replace('Team ', '')
                    pairwise_details.append((ev_name, tg_name, pair_score, verdict))

            num_reviews = len(all_scores)
            if num_reviews > 0:
                # HOW IT'S CALCULATED section
                content.append("HOW THIS WAS CALCULATED\n", style="bold dim")
                content.append("─" * 40 + "\n", style="dim")

                # Show pairwise approvals as a compact list
                content.append(f"Each expert reviewed {num_reviews // (len(approval_matrix))} other solutions:\n\n", style="dim")

                for ev_name, tg_name, pair_score, verdict in pairwise_details:
                    # Verdict icon
                    if 'APPROVE' in verdict.upper() and 'CONCERN' not in verdict.upper():
                        icon = "✓"
                        style = "green"
                    elif 'CONCERN' in verdict.upper():
                        icon = "~"
                        style = "yellow"
                    else:
                        icon = "✗"
                        style = "red"

                    score_val = "1.0" if pair_score == 1.0 else f"{pair_score:.1f}"
                    content.append(f"  {icon} {ev_name[:15]:<15} → {tg_name[:15]:<15} = ", style=style)
                    content.append(f"{score_val}\n", style=f"bold {style}")

                content.append("\n", style="")

                # Show the formula
                score_sum = sum(all_scores)
                content.append("Formula: ", style="dim")
                content.append(f"({score_sum:.1f}) / {num_reviews} reviews = ", style="")
                content.append(f"{score_pct}%\n\n", style="bold")

        # Main result display
        content.append(f"[{progress}] {score_pct}% ", style="bold")
        content.append(f"(threshold: {threshold_pct}%)\n", style="dim")
        content.append(f"\n{status_icon} {status_text}\n", style="bold")
        content.append(f"{outcome_text}\n", style="dim")

        if interpretation:
            content.append(f"\n{interpretation}", style="dim italic")

        print()
        self.rich_console.print(Panel(
            content,
            title=f"{DisplayTheme.CONSENSUS} CONSENSUS RESULT",
            border_style=border_style,
            padding=(0, 2)
        ))
        print()

    def _render_orchestrator_intervention_start(self, elapsed_time: str):
        """Render orchestrator intervention header"""
        print("\n\n")
        print(f"🎭 Orchestrator Intervention • {elapsed_time}")
        print("─" * 50)
        print()

    def _render_expert_compromise_responses_start(self):
        """Render expert compromise responses header"""
        print(f"\n🎯 EXPERT RESPONSES TO COMPROMISE")
        print("─" * 60)

    def _render_completion_summary(self, consensus_reached: bool, duration: float,
                                   iteration_count: int, max_iterations: int):
        """Render workflow completion summary"""
        time_str = f"{duration:.0f}s" if duration >= 1 else f"{duration:.1f}s"
        result_text = "Democratic consensus achieved" if consensus_reached else "Orchestrator resolution"
        result_icon = DisplayTheme.SUCCESS if consensus_reached else "🎭"

        content = Text()
        content.append(f"{result_icon} Result:   ", style="bold")
        content.append(f"{result_text}\n",
                       style=DisplayTheme.SUCCESS_COLOR if consensus_reached else DisplayTheme.PRIMARY)
        content.append(f"{DisplayTheme.TIME}  Duration: ", style="bold")
        content.append(f"{time_str}\n")
        content.append(f"{DisplayTheme.LOOP} Rounds:   ", style="bold")
        content.append(f"{iteration_count}/{max_iterations}")

        print("\n")
        self.rich_console.print(Panel(
            content,
            title=f"{DisplayTheme.CELEBRATE} WORKFLOW COMPLETE",
            border_style=DisplayTheme.SUCCESS_COLOR if consensus_reached else DisplayTheme.PRIMARY,
            padding=(1, 2)
        ))
        print()

    # =========================================================================
    # Legacy API (for backward compatibility during migration)
    # These call the render methods directly. Remove after full migration.
    # =========================================================================

    def print_header(self, problem: str, expert_agents: List[Any],
                     consensus_threshold: float, max_iterations: int,
                     mode: str = "single", teams: Dict[str, List[Any]] = None,
                     provider: str = None):
        """Legacy method - delegates to render"""
        self._render_header(problem, expert_agents, consensus_threshold,
                            max_iterations, mode, teams, provider)

    def print_phase_header(self, phase_num: int, phase_name: str,
                           description: str, total_phases: int = 3):
        """Legacy method - delegates to render"""
        self._render_phase_header(phase_num, phase_name, description, total_phases)

    def print_iteration_header(self, iteration: int, elapsed: float):
        """Legacy method - delegates to render"""
        self._render_iteration_header(iteration, elapsed)

    def print_agent_thinking(self, agent_name: str, phase: str,
                             estimated_seconds: int = None):
        """Legacy method - delegates to render"""
        self._render_agent_thinking(agent_name, phase, estimated_seconds)

    def print_agent_response(self, agent_name: str, content: str,
                             response_type: str = "response"):
        """Legacy method - delegates to render"""
        self._render_agent_response(agent_name, content, response_type)

    def print_parallel_progress(self, completed: int, total: int, operation: str):
        """Legacy method - delegates to render"""
        self._render_parallel_progress(completed, total, operation)

    def print_feedback_phase_start(self):
        """Legacy method - delegates to render"""
        self._render_feedback_phase_start()

    def print_feedback_exchange(self, from_agent: str, to_agent: str, feedback: str):
        """Legacy method - delegates to render"""
        self._render_feedback_exchange(from_agent, to_agent, feedback)

    def print_refinement_phase_start(self):
        """Legacy method - delegates to render"""
        self._render_refinement_phase_start()

    def print_consensus_evaluation_start(self):
        """Legacy method - delegates to render"""
        self._render_consensus_evaluation_start()

    def print_consensus_check(self, score: float, threshold: float,
                               interpretation: str = '', approval_matrix: dict = None):
        """Legacy method - delegates to render"""
        self._render_consensus_check(score, threshold, interpretation, approval_matrix)

    def print_orchestrator_intervention_start(self, elapsed_time: str):
        """Legacy method - delegates to render"""
        self._render_orchestrator_intervention_start(elapsed_time)

    def print_expert_compromise_responses_start(self):
        """Legacy method - delegates to render"""
        self._render_expert_compromise_responses_start()

    def print_completion_summary(self, consensus_reached: bool, duration: float,
                                 iteration_count: int, max_iterations: int):
        """Legacy method - delegates to render"""
        self._render_completion_summary(consensus_reached, duration,
                                        iteration_count, max_iterations)

    def print_parallel_execution_start(self, operation_name: str):
        """Legacy method"""
        print(f"🚀 Running parallel {operation_name}...")
        print()
