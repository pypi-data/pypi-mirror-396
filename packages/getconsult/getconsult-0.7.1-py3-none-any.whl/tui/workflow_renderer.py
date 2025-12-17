"""
WorkflowRenderer - Bridges workflow events to UI widgets.

This class receives workflow events and updates the appropriate widgets,
managing the collapsible structure and state transitions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from textual.containers import VerticalScroll

from .widgets.status_header import StatusHeader
from .widgets.phase_container import PhaseContainer, PhaseStatus
from .widgets.agent_card import AgentCard, ThinkingIndicator
from .widgets.feedback_group import FeedbackGroup, IterationContainer
from .progress_tracker import ProgressTracker

if TYPE_CHECKING:
    from .widgets.workflow_view import WorkflowView


@dataclass
class ApprovalRecord:
    """Record of one pairwise cross-expert approval."""
    evaluator: str
    target: str
    verdict: str  # APPROVE, APPROVE_WITH_CONCERNS, OBJECT
    score: float
    endorsements: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    objections: List[str] = field(default_factory=list)


@dataclass
class QueryJourney:
    """Data for one agent's journey through a single query."""
    query: str
    initial_response: Optional[str] = None
    feedback_received: List[Tuple[str, str, int]] = field(default_factory=list)  # (from_agent, feedback, iteration)
    refinements: List[Tuple[int, str]] = field(default_factory=list)  # (iteration, content)
    final_response: Optional[str] = None
    consensus_score: Optional[float] = None
    # Cross-expert approvals
    approvals_given: List[ApprovalRecord] = field(default_factory=list)  # This agent reviewing others
    approvals_received: List[ApprovalRecord] = field(default_factory=list)  # Others reviewing this agent


@dataclass
class AgentJourneyData:
    """Data structure for an agent's complete journey across all queries."""
    agent_name: str
    # Current query data (for backward compatibility)
    initial_response: Optional[str] = None
    feedback_received: List[Tuple[str, str, int]] = field(default_factory=list)
    refinements: List[Tuple[int, str]] = field(default_factory=list)
    final_response: Optional[str] = None
    consensus_score: Optional[float] = None
    # Cross-expert approvals for current query
    approvals_given: List[ApprovalRecord] = field(default_factory=list)  # This agent reviewing others
    approvals_received: List[ApprovalRecord] = field(default_factory=list)  # Others reviewing this agent
    # History across queries (newest first)
    query_history: List[QueryJourney] = field(default_factory=list)


class WorkflowRenderer:
    """Manages workflow visualization state and widget updates."""

    # Class-level counter - persists across all instances
    _global_run_counter = 0

    def __init__(
        self,
        workflow_view: "WorkflowView",
        status_header: Optional[StatusHeader] = None
    ):
        self.workflow_view = workflow_view
        self.status_header = status_header
        self.progress_tracker = ProgressTracker()

        # Widget references
        self._phase_widgets: Dict[int, PhaseContainer] = {}
        self._iteration_widgets: Dict[int, IterationContainer] = {}
        self._agent_cards: Dict[str, AgentCard] = {}
        self._feedback_groups: Dict[int, FeedbackGroup] = {}
        self._thinking_indicators: Dict[str, ThinkingIndicator] = {}
        self._waiting_indicator = None  # Direct reference to waiting widget

        # Current state
        self._current_phase = 0
        self._current_iteration = 0
        self._max_iterations = 1
        self._experts: list = []
        self._problem = ""

        # Instance run ID (set on workflow start)
        self._workflow_run = 0

        # History tracking: agent_name -> list of QueryJourney (newest first)
        self._agent_history: Dict[str, List[QueryJourney]] = {}

        # Cross-expert approval storage for current query
        self._approval_records: List[ApprovalRecord] = []

        # Register progress tracker listener
        self.progress_tracker.add_listener(self._on_progress_update)

    def _on_progress_update(self, state) -> None:
        """Handle progress tracker state updates."""
        if self.status_header:
            self.status_header.update_from_tracker({
                "phase": f"{self._current_phase}/3",
                "iteration": f"{self._current_iteration}/{self._max_iterations}",
                "consensus": state.consensus_history[-1] if state.consensus_history else 0.0,
                "action": state.current_action,
                "is_active": state.is_active,
            })

    def reset(self) -> None:
        """Reset renderer state for new workflow.

        Note: Does NOT clear the workflow view - we preserve conversation history.
        Old widgets remain visible, new widgets stack below.
        Agent journey history is preserved for the detail pane.
        """
        # Archive current journeys before clearing
        self._archive_current_journeys()

        self._phase_widgets.clear()
        self._iteration_widgets.clear()
        self._agent_cards.clear()
        self._feedback_groups.clear()
        self._thinking_indicators.clear()
        self._waiting_indicator = None
        self._current_phase = 0
        self._current_iteration = 0
        self._approval_records.clear()
        self.progress_tracker.reset()
        # Don't clear workflow_view - preserve conversation history

    def _archive_current_journeys(self) -> None:
        """Archive current query's agent journeys to history before reset."""
        if not self._problem or not self._agent_cards:
            return

        # Get all agent names from current run
        agent_names = self.get_all_agent_names()

        for agent_name in agent_names:
            journey = self._extract_current_journey(agent_name)
            if journey.initial_response or journey.final_response:
                # Extract approvals for this agent
                normalized = self._normalize_agent_name(agent_name)
                approvals_given = []
                approvals_received = []
                for record in self._approval_records:
                    if self._normalize_agent_name(record.evaluator) == normalized:
                        approvals_given.append(record)
                    if self._normalize_agent_name(record.target) == normalized:
                        approvals_received.append(record)

                # Create QueryJourney from current data
                query_journey = QueryJourney(
                    query=self._problem,
                    initial_response=journey.initial_response,
                    feedback_received=journey.feedback_received.copy(),
                    refinements=journey.refinements.copy(),
                    final_response=journey.final_response,
                    consensus_score=journey.consensus_score,
                    approvals_given=approvals_given,
                    approvals_received=approvals_received
                )

                # Add to history (prepend - newest first)
                if normalized not in self._agent_history:
                    self._agent_history[normalized] = []
                self._agent_history[normalized].insert(0, query_journey)

    def _extract_current_journey(self, agent_name: str) -> AgentJourneyData:
        """Extract journey data for an agent from current workflow run only."""
        journey = AgentJourneyData(agent_name=agent_name)
        normalized_name = self._normalize_agent_name(agent_name)

        for card_id, card in self._agent_cards.items():
            parts = card_id.split("-")
            if len(parts) >= 4:
                card_agent = parts[2]
                card_phase = int(parts[3]) if parts[3].isdigit() else 0

                if self._normalize_agent_name(card_agent) == normalized_name:
                    if card_phase == 1:
                        journey.initial_response = card.full_content
                    elif card_phase == 2:
                        iteration = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 1
                        journey.refinements.append((iteration, card.full_content))
                    elif card_phase == 3:
                        journey.final_response = card.full_content

        for iteration, feedback_group in self._feedback_groups.items():
            for from_agent, to_agent, feedback in feedback_group._feedback_items:
                if self._normalize_agent_name(to_agent) == normalized_name:
                    journey.feedback_received.append((from_agent, feedback, iteration))

        journey.refinements.sort(key=lambda x: x[0])

        if self.progress_tracker.state.consensus_history:
            journey.consensus_score = self.progress_tracker.state.consensus_history[-1]

        return journey

    def _remove_waiting_indicator(self) -> None:
        """Remove the waiting indicator if present."""
        if self._waiting_indicator:
            try:
                self._waiting_indicator.remove()
            except Exception:
                pass
            self._waiting_indicator = None

    def _call_later(self, callback):
        """Schedule a callback to run on the main thread.

        Uses call_from_thread when called from worker thread,
        or call_later when on main thread.
        """
        try:
            app = self.workflow_view.app
            # Try call_from_thread - raises RuntimeError if on main thread
            app.call_from_thread(callback)
        except RuntimeError as e:
            if "different thread" in str(e):
                # On main thread - use call_later instead
                try:
                    app.call_later(callback)
                except Exception:
                    # Last resort: call directly
                    try:
                        callback()
                    except Exception:
                        pass
            else:
                # Other error - try direct call
                try:
                    callback()
                except Exception:
                    pass
        except Exception:
            # Any other exception - try direct call
            try:
                callback()
            except Exception:
                pass

    # === Event Handlers ===

    def on_workflow_start(self, data: dict) -> None:
        """Handle workflow start - create initial structure."""
        # Increment CLASS-LEVEL counter - persists across renderer instances
        WorkflowRenderer._global_run_counter += 1
        self._workflow_run = WorkflowRenderer._global_run_counter
        run = self._workflow_run

        self.reset()

        self._problem = data.get('problem', '')
        self._experts = data.get('agents', [])
        self._max_iterations = data.get('max_iterations', 1)
        threshold = data.get('consensus_threshold', 0.8)

        # Update progress tracker
        self.progress_tracker.on_workflow_start(self._experts, self._max_iterations, threshold)

        # Update status header - use set_workflow_active to start timer
        if self.status_header:
            self.status_header.set_workflow_active(True)
            self.status_header.set_action("Initializing workflow...")

        def create_phases():
            from textual.widgets import Static, Rule
            from rich.text import Text
            from rich.panel import Panel

            # Add separator before follow-up queries (not the first one)
            if run > 1:
                separator = Rule(line_style="dashed", id=f"separator-{run}")
                self.workflow_view.mount(separator)

            # Add the query display (unique ID per run)
            if self._problem:
                display = self._problem[:300] + "..." if len(self._problem) > 300 else self._problem
                query_text = Text()
                query_text.append("❯ ", style="bold green")
                query_text.append(display, style="white")

                query_widget = Static(
                    query_text,
                    id=f"query-display-{run}",
                    classes="query-display"
                )
                self.workflow_view.mount(query_widget)

            # Create phase containers with unique IDs (all collapsed except phase 1)
            phase1 = PhaseContainer(
                phase_num=1,
                title="Initial Analysis",
                status=PhaseStatus.PENDING,
                collapsed=False,  # Start expanded
                id=f"phase-1-{run}"
            )
            self._phase_widgets[1] = phase1
            self.workflow_view.add_phase(phase1)

            phase2 = PhaseContainer(
                phase_num=2,
                title="Peer Review & Refinement",
                status=PhaseStatus.PENDING,
                collapsed=True,
                id=f"phase-2-{run}"
            )
            self._phase_widgets[2] = phase2
            self.workflow_view.add_phase(phase2)

            phase3 = PhaseContainer(
                phase_num=3,
                title="Resolution",
                status=PhaseStatus.PENDING,
                collapsed=True,
                id=f"phase-3-{run}"
            )
            self._phase_widgets[3] = phase3
            self.workflow_view.add_phase(phase3)

            # Schedule waiting indicator after phases are mounted
            def add_waiting():
                if 1 in self._phase_widgets:
                    waiting_text = Text()
                    waiting_text.append("  ", style="yellow")
                    waiting_text.append("Waiting for experts to analyze...", style="dim yellow")
                    waiting_indicator = Static(waiting_text)
                    self._waiting_indicator = waiting_indicator  # Store direct reference
                    self._phase_widgets[1].add_child(waiting_indicator)

            # Use set_timer to allow mount to complete
            self.workflow_view.app.set_timer(0.1, add_waiting)

        self._call_later(create_phases)

    def on_workflow_complete(self, data: dict) -> None:
        """Handle workflow completion."""
        success = data.get('success', True)
        consensus_reached = data.get('consensus_reached', False)

        self.progress_tracker.on_workflow_complete(success)

        if self.status_header:
            self.status_header.set_workflow_active(False)

        def finalize():
            # Clear any remaining thinking indicators
            self._clear_all_thinking_indicators()

            # Mark all phases as complete and collapse them
            # This makes room for follow-up queries
            for phase in self._phase_widgets.values():
                if phase.status == PhaseStatus.ACTIVE:
                    phase.set_status(PhaseStatus.COMPLETE)
                # Collapse completed phases to save space
                phase.collapsed = True

        self._call_later(finalize)

    def on_phase_start(self, data: dict) -> None:
        """Handle phase start."""
        phase_num = data.get('phase_num', 0)
        phase_name = data.get('phase_name', '')

        self._current_phase = phase_num
        self.progress_tracker.on_phase_start(phase_num, phase_name)

        # Update status header
        if self.status_header:
            self.status_header.set_phase(phase_num, 3)

        def update_phases():
            # Mark previous phase as complete
            if phase_num > 1 and (phase_num - 1) in self._phase_widgets:
                prev_phase = self._phase_widgets[phase_num - 1]
                prev_phase.set_status(PhaseStatus.COMPLETE)
                prev_phase.collapsed = True

            # Activate current phase
            if phase_num in self._phase_widgets:
                current_phase = self._phase_widgets[phase_num]
                current_phase.set_status(PhaseStatus.ACTIVE)
                # Note: set_status already sets collapsed=False for ACTIVE

                # Remove waiting indicator if this is Phase 1
                if phase_num == 1:
                    self._remove_waiting_indicator()

        self._call_later(update_phases)

    def on_iteration_start(self, data: dict) -> None:
        """Handle iteration start within Phase 2."""
        iteration = data.get('iteration', 1)
        self._current_iteration = iteration

        self.progress_tracker.on_iteration_start(iteration)

        if self.status_header:
            self.status_header.set_iteration(iteration, self._max_iterations)

        def create_iteration():
            # Mark previous iteration as complete
            if iteration > 1 and (iteration - 1) in self._iteration_widgets:
                prev_iter = self._iteration_widgets[iteration - 1]
                prev_iter.set_status("complete")
                prev_iter.collapsed = True

            # Create new iteration container within Phase 2 (with unique ID per run)
            if 2 in self._phase_widgets:
                phase2 = self._phase_widgets[2]
                iter_container = IterationContainer(
                    iteration_num=iteration,
                    id=f"iteration-{self._workflow_run}-{iteration}"
                )
                iter_container.set_status("active")
                self._iteration_widgets[iteration] = iter_container
                phase2.add_child(iter_container)

        self._call_later(create_iteration)

    def on_agent_thinking(self, data: dict) -> None:
        """Handle agent thinking indicator."""
        agent_name = data.get('agent_name', '')
        action = data.get('action', 'thinking')

        self.progress_tracker.on_agent_thinking(agent_name, action)

        if self.status_header:
            display_name = agent_name.replace("_", " ").title()
            if display_name.startswith("Team "):
                display_name = display_name[5:]
            self.status_header.set_action(f"{display_name} {action}...")

        def add_indicator():
            # Remove "waiting" message from phase 1 - experts are now working
            self._remove_waiting_indicator()

            # Remove existing indicator for this agent if present
            if agent_name in self._thinking_indicators:
                try:
                    self._thinking_indicators[agent_name].remove()
                except Exception:
                    pass
                del self._thinking_indicators[agent_name]

            # Add thinking indicator to current context (no ID to avoid async removal race)
            indicator = ThinkingIndicator(agent_name, action)
            self._thinking_indicators[agent_name] = indicator

            # Add to appropriate container
            phase = self._current_phase if self._current_phase > 0 else 1
            if phase == 1:
                if 1 in self._phase_widgets:
                    self._phase_widgets[1].add_child(indicator)
            elif phase == 2:
                if self._current_iteration in self._iteration_widgets:
                    self._iteration_widgets[self._current_iteration].add_child(indicator)
            else:
                if 3 in self._phase_widgets:
                    self._phase_widgets[3].add_child(indicator)

        self._call_later(add_indicator)

    def on_agent_response(self, data: dict) -> None:
        """Handle agent response - create or update agent card."""
        agent_name = data.get('agent_name', '')
        content = data.get('content', '')
        response_type = data.get('response_type', 'Response')

        # Determine target phase based on response_type, not current phase
        # This handles async timing where phase may have advanced before response arrives
        target_phase = self._current_phase if self._current_phase > 0 else 1
        if response_type == "Initial Analysis":
            target_phase = 1
        elif (response_type.startswith("Refined Solution") or
              response_type in ("Refined Analysis", "Feedback", "Compromise Response")):
            target_phase = 2
        elif response_type == "Final Answer":
            target_phase = 3

        def add_response():
            # Remove thinking indicator if present
            if agent_name in self._thinking_indicators:
                try:
                    self._thinking_indicators[agent_name].remove()
                except Exception:
                    pass
                del self._thinking_indicators[agent_name]

            # Remove waiting indicator from phase 1 if this is an initial analysis response
            if target_phase == 1:
                self._remove_waiting_indicator()

            # Create agent card (with unique ID per workflow run)
            card_id = f"agent-{self._workflow_run}-{agent_name}-{target_phase}-{self._current_iteration}"
            card = AgentCard(
                agent_name=agent_name,
                content=content,
                response_type=response_type,
                collapsed=True,  # Start collapsed for progressive disclosure
                id=card_id
            )
            self._agent_cards[card_id] = card

            # Add to appropriate container based on target phase
            if target_phase == 1:
                if 1 in self._phase_widgets:
                    self._phase_widgets[1].add_child(card)
                else:
                    # Phase widget doesn't exist - mount directly to workflow_view
                    try:
                        self.workflow_view.mount(card)
                    except Exception:
                        pass
            elif target_phase == 2:
                # In Phase 2, responses go in iteration container
                if self._current_iteration in self._iteration_widgets:
                    self._iteration_widgets[self._current_iteration].add_child(card)
                elif 2 in self._phase_widgets:
                    # Fallback to phase 2 directly
                    self._phase_widgets[2].add_child(card)
            else:
                # Phase 3 - final answer
                if 3 in self._phase_widgets:
                    self._phase_widgets[3].add_child(card)
                    # Auto-expand final answer
                    if "presentation" in agent_name.lower() or response_type == "Final Answer":
                        card.collapsed = False
                else:
                    # Fallback
                    try:
                        self.workflow_view.mount(card)
                    except Exception:
                        pass

        self._call_later(add_response)

    def on_feedback_phase_start(self, data: dict) -> None:
        """Handle feedback phase start."""
        self.progress_tracker.on_feedback_phase_start()

        if self.status_header:
            self.status_header.set_action("Experts exchanging feedback...")

        # Feedback group will be created lazily on first exchange to ensure iteration exists

    def _ensure_feedback_group(self) -> None:
        """Ensure feedback group exists for current iteration."""
        if self._current_iteration not in self._feedback_groups:
            if self._current_iteration in self._iteration_widgets:
                feedback_group = FeedbackGroup(
                    title="Feedback Exchange",
                    id=f"feedback-{self._workflow_run}-{self._current_iteration}"
                )
                self._feedback_groups[self._current_iteration] = feedback_group
                self._iteration_widgets[self._current_iteration].add_child(feedback_group)

    def on_feedback_exchange(self, data: dict) -> None:
        """Handle individual feedback exchange."""
        from_agent = data.get('from_agent', '')
        to_agent = data.get('to_agent', '')
        feedback = data.get('feedback', '')

        def add_feedback():
            # Ensure feedback group exists (creates it lazily)
            self._ensure_feedback_group()

            # Add to feedback group
            if self._current_iteration in self._feedback_groups:
                self._feedback_groups[self._current_iteration].add_feedback(
                    from_agent, to_agent, feedback
                )

        self._call_later(add_feedback)

    def on_refinement_phase_start(self, data: dict) -> None:
        """Handle refinement phase start."""
        self.progress_tracker.on_refinement_phase_start()

        if self.status_header:
            self.status_header.set_action("Experts refining solutions...")

    def on_consensus_evaluation_start(self, data: dict) -> None:
        """Handle consensus evaluation start."""
        self.progress_tracker.on_consensus_evaluation_start()
        self._pending_approvals = []  # Accumulate approvals for main view

        if self.status_header:
            self.status_header.set_action("Cross-expert approval...")

    def on_cross_expert_approval(self, data: dict) -> None:
        """Accumulate individual approval for display in main view and detail pane."""
        if not hasattr(self, '_pending_approvals'):
            self._pending_approvals = []
        self._pending_approvals.append(data)

        # Store as ApprovalRecord for detail pane access
        record = ApprovalRecord(
            evaluator=data.get('evaluator', ''),
            target=data.get('target', ''),
            verdict=data.get('verdict', 'UNKNOWN'),
            score=data.get('score', 0.0),
            endorsements=data.get('endorsements', []),
            concerns=data.get('concerns', []),
            objections=data.get('objections', [])
        )
        self._approval_records.append(record)

    def _clear_all_thinking_indicators(self) -> None:
        """Remove all thinking indicators."""
        for agent_name, indicator in list(self._thinking_indicators.items()):
            try:
                indicator.remove()
            except Exception:
                pass
        self._thinking_indicators.clear()

    def on_consensus_check(self, data: dict) -> None:
        """Handle consensus check result with full transparency."""
        # Get all available data
        score = data.get('score', data.get('final_score', 0.0))
        threshold = data.get('threshold', 0.8)
        individual_scores = data.get('individual_scores', [])
        agent_evaluations = data.get('agent_evaluations', [])
        interpretation = data.get('interpretation', '')
        approval_matrix = data.get('approval_matrix', {})

        # IMPORTANT: Validate 'reached' against actual score vs threshold
        # Don't blindly trust event data - trust the math
        actually_reached = score >= threshold
        reached = data.get('reached', actually_reached)
        if reached != actually_reached:
            reached = actually_reached

        self.progress_tracker.on_consensus_check(score, reached)

        if self.status_header:
            self.status_header.set_consensus(score)

        def update_iteration():
            # Update iteration container with consensus score
            if self._current_iteration in self._iteration_widgets:
                iter_widget = self._iteration_widgets[self._current_iteration]
                iter_widget.set_consensus(score)

                if reached:
                    # Clear all thinking indicators - work is done
                    self._clear_all_thinking_indicators()

                    iter_widget.set_status("complete")
                    # Collapse iteration and phase 2
                    iter_widget.collapsed = True
                    if 2 in self._phase_widgets:
                        self._phase_widgets[2].set_status(PhaseStatus.COMPLETE)
                        self._phase_widgets[2].collapsed = True

                    # Activate Phase 3 with TRANSPARENT consensus breakdown
                    if 3 in self._phase_widgets:
                        from textual.widgets import Static
                        from rich.text import Text
                        from rich.panel import Panel

                        self._phase_widgets[3].set_status(PhaseStatus.ACTIVE)
                        self._phase_widgets[3].collapsed = False

                        # Build transparent explanation showing THE MATH
                        pct = int(score * 100)
                        threshold_pct = int(threshold * 100)
                        explanation = Text()

                        # HEADER
                        explanation.append("✓ CONSENSUS ACHIEVED\n\n", style="bold green")

                        # HOW IT'S CALCULATED - show the math transparently
                        explanation.append("HOW THIS WAS CALCULATED\n", style="bold dim")
                        explanation.append("─" * 35 + "\n", style="dim")

                        # Get pairwise scores from pending approvals or approval matrix
                        pending_approvals = getattr(self, '_pending_approvals', [])
                        all_scores = []

                        if pending_approvals:
                            num_experts = len(set(a.get('evaluator', '') for a in pending_approvals))
                            explanation.append(f"Each of {num_experts} experts reviewed others' solutions:\n\n", style="dim")

                            for approval in pending_approvals:
                                evaluator = approval.get('evaluator', '').replace('_', ' ').title()
                                target = approval.get('target', '').replace('_', ' ').title()
                                # Remove "Team " prefix if present
                                if evaluator.startswith('Team '):
                                    evaluator = evaluator[5:]
                                if target.startswith('Team '):
                                    target = target[5:]

                                verdict = approval.get('verdict', 'UNKNOWN')
                                appr_score = approval.get('score', 0)
                                all_scores.append(appr_score)

                                # Verdict styling
                                if 'APPROVE' in verdict.upper() and 'CONCERN' not in verdict.upper():
                                    icon, vstyle = "✓", "green"
                                elif 'CONCERN' in verdict.upper():
                                    icon, vstyle = "~", "yellow"
                                elif 'OBJECT' in verdict.upper():
                                    icon, vstyle = "✗", "red"
                                else:
                                    icon, vstyle = "?", "dim"

                                score_val = "1.0" if appr_score == 1.0 else f"{appr_score:.1f}"
                                explanation.append(f"  {icon} {evaluator[:12]:<12} → {target[:12]:<12} = ", style=vstyle)
                                explanation.append(f"{score_val}\n", style=f"bold {vstyle}")

                            explanation.append("\n", style="")

                            # Show the formula
                            if all_scores:
                                score_sum = sum(all_scores)
                                num_reviews = len(all_scores)
                                explanation.append("Formula: ", style="dim")
                                explanation.append(f"({score_sum:.1f}) / {num_reviews} = ", style="")
                                explanation.append(f"{pct}%\n", style="bold green")
                                explanation.append(f"Threshold: {threshold_pct}%  ", style="dim")
                                explanation.append("✓ Met\n\n", style="green")
                        else:
                            explanation.append(f"Aggregate approval: {pct}%\n", style="green")
                            explanation.append(f"Threshold: {threshold_pct}%\n\n", style="dim")

                        if interpretation:
                            explanation.append(f"{interpretation}\n\n", style="dim italic")

                        explanation.append("→ Proceeding to final synthesis", style="bold green")

                        context_widget = Static(
                            Panel(explanation, border_style="green", padding=(0, 1)),
                            id=f"consensus-context-{self._workflow_run}"
                        )
                        self._phase_widgets[3].add_child(context_widget)

        self._call_later(update_iteration)

    def on_orchestrator_intervention(self, data: dict) -> None:
        """Handle orchestrator intervention."""
        self.progress_tracker.on_orchestrator_intervention()
        reason = data.get('reason', 'Experts could not reach consensus')

        if self.status_header:
            self.status_header.set_action("Orchestrator making final decision...")

        def handle_intervention():
            from textual.widgets import Static
            from rich.text import Text
            from rich.panel import Panel

            # Clear all thinking indicators from previous phases
            self._clear_all_thinking_indicators()

            # Mark phase 2 complete, activate phase 3
            if 2 in self._phase_widgets:
                self._phase_widgets[2].set_status(PhaseStatus.COMPLETE)
                self._phase_widgets[2].collapsed = True

            if 3 in self._phase_widgets:
                self._phase_widgets[3].set_status(PhaseStatus.ACTIVE)
                self._phase_widgets[3].collapsed = False

                # Add explanatory context to Phase 3
                explanation = Text()
                explanation.append("⚖ ORCHESTRATOR SYNTHESIS\n", style="bold magenta")
                explanation.append(f"Reason: {reason}\n\n", style="yellow")
                explanation.append("The orchestrator is analyzing all expert positions to create a ", style="dim")
                explanation.append("balanced final answer", style="bold")
                explanation.append(" that incorporates the best insights from each expert.", style="dim")

                context_widget = Static(
                    Panel(explanation, border_style="magenta", padding=(0, 1)),
                    id=f"orchestrator-context-{self._workflow_run}"
                )
                self._phase_widgets[3].add_child(context_widget)

        self._call_later(handle_intervention)

    def on_error(self, data: dict) -> None:
        """Handle error event."""
        message = data.get('message', 'Unknown error')

        if self.status_header:
            self.status_header.set_action(f"Error: {message}")

    # === Utility Methods ===

    def expand_current(self) -> None:
        """Expand the current active section."""
        def do_expand():
            if self._current_phase in self._phase_widgets:
                self._phase_widgets[self._current_phase].collapsed = False

            if self._current_iteration in self._iteration_widgets:
                self._iteration_widgets[self._current_iteration].collapsed = False

        self._call_later(do_expand)

    def collapse_all(self) -> None:
        """Collapse all sections."""
        def do_collapse():
            for phase in self._phase_widgets.values():
                phase.collapsed = True

            for iteration in self._iteration_widgets.values():
                iteration.collapsed = True

            for card in self._agent_cards.values():
                card.collapsed = True

            for feedback in self._feedback_groups.values():
                feedback.collapsed = True

        self._call_later(do_collapse)

    def scroll_to_current(self) -> None:
        """Scroll to the current active section."""
        self.expand_current()
        # Let Textual handle the scroll
        def do_scroll():
            if self._current_phase in self._phase_widgets:
                self._phase_widgets[self._current_phase].scroll_visible()

        self._call_later(do_scroll)

    # === Detail Pane Data Methods ===

    def get_all_agent_names(self) -> List[str]:
        """Return list of expert names from the current workflow."""
        return [self._format_agent_name(name) for name in self._experts]

    def _format_agent_name(self, name: str) -> str:
        """Format agent name for display."""
        display = name.replace("_", " ").title()
        if display.startswith("Team "):
            display = display[5:]
        return display

    def _normalize_agent_name(self, name: str) -> str:
        """Normalize agent name for matching (lowercase, no spaces)."""
        return name.lower().replace(" ", "_").replace("team_", "")

    def get_consensus_history(self) -> List[float]:
        """Return consensus scores over iterations."""
        return list(self.progress_tracker.state.consensus_history)

    def get_agent_journey(self, agent_name: str) -> AgentJourneyData:
        """Extract complete journey for one agent.

        Args:
            agent_name: Display name of the agent (e.g., "Backend Expert")

        Returns:
            AgentJourneyData with all journey information
        """
        journey = AgentJourneyData(agent_name=agent_name)
        normalized_name = self._normalize_agent_name(agent_name)

        # Extract initial response (Phase 1)
        for card_id, card in self._agent_cards.items():
            # Card IDs are: agent-{workflow_run}-{agent_name}-{phase}-{iteration}
            parts = card_id.split("-")
            if len(parts) >= 4:
                card_agent = parts[2]  # Agent name part (after workflow_run)
                card_phase = int(parts[3]) if parts[3].isdigit() else 0

                if self._normalize_agent_name(card_agent) == normalized_name:
                    if card_phase == 1:
                        journey.initial_response = card.full_content
                    elif card_phase == 2:
                        # Refinement - get iteration from card_id
                        iteration = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 1
                        journey.refinements.append((iteration, card.full_content))
                    elif card_phase == 3:
                        journey.final_response = card.full_content

        # Extract feedback received (from feedback groups)
        for iteration, feedback_group in self._feedback_groups.items():
            for from_agent, to_agent, feedback in feedback_group._feedback_items:
                # Check if this feedback was directed TO our agent
                if self._normalize_agent_name(to_agent) == normalized_name:
                    journey.feedback_received.append((from_agent, feedback, iteration))

        # Sort refinements by iteration
        journey.refinements.sort(key=lambda x: x[0])

        # Get latest consensus score
        if self.progress_tracker.state.consensus_history:
            journey.consensus_score = self.progress_tracker.state.consensus_history[-1]

        # Extract cross-expert approvals for this agent
        for record in self._approval_records:
            evaluator_normalized = self._normalize_agent_name(record.evaluator)
            target_normalized = self._normalize_agent_name(record.target)

            if evaluator_normalized == normalized_name:
                # This agent gave an approval to someone else
                journey.approvals_given.append(record)
            if target_normalized == normalized_name:
                # This agent received an approval from someone else
                journey.approvals_received.append(record)

        # Attach historical journeys for this agent
        if normalized_name in self._agent_history:
            journey.query_history = self._agent_history[normalized_name].copy()

        return journey

    def get_current_query(self) -> str:
        """Return the current query being processed."""
        return self._problem
