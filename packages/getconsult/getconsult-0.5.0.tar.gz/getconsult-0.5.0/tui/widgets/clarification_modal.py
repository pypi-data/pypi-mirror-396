"""
Clarification Modal widget for interactive Q&A before workflow execution.

Human-centered design principles:
1. Explain WHY clarification helps (builds trust)
2. Show progress clearly (reduces anxiety)
3. Provide immediate feedback on every action
4. Make it easy to skip if user prefers
5. Use familiar interaction patterns
"""

from typing import Dict, List, Any, Optional, Callable
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static, Input


class ClarificationQuestion(Vertical):
    """A single question with selectable options"""

    def __init__(
        self,
        question: str,
        options: List[str],
        question_index: int,
        total_questions: int,
        multi_select: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.question_text = question
        self.options = options
        self.question_index = question_index
        self.total_questions = total_questions
        self.multi_select = multi_select
        self.selected: List[int] = []
        self.custom_text: str = ""

    def compose(self) -> ComposeResult:
        # Question with clear numbering
        yield Static(
            f"[bold cyan]Q{self.question_index + 1}.[/bold cyan] {self.question_text}",
            classes="question-text"
        )

        for i, option in enumerate(self.options):
            key = str(i + 1)
            yield Static(
                f"    [hotkey]{key}[/hotkey]  {option}",
                id=f"option-{self.question_index}-{i}",
                classes="question-option"
            )

        # Custom text option
        yield Static(
            f"    [hotkey]o[/hotkey]  Other (type your own)",
            id=f"custom-{self.question_index}",
            classes="question-option custom-option"
        )

    def toggle_option(self, option_index: int) -> None:
        """Toggle selection of an option"""
        self.custom_text = ""  # Clear custom when selecting option
        if self.multi_select:
            if option_index in self.selected:
                self.selected.remove(option_index)
            else:
                self.selected.append(option_index)
        else:
            self.selected = [option_index]
        self._update_display()

    def set_custom_text(self, text: str) -> None:
        """Set custom text response"""
        self.custom_text = text
        self.selected = []
        self._update_display()

    def _update_display(self) -> None:
        """Update visual selection state with clear feedback"""
        for i, option in enumerate(self.options):
            try:
                option_widget = self.query_one(f"#option-{self.question_index}-{i}", Static)
                key = str(i + 1)

                if i in self.selected:
                    # Very obvious selection: green bullet, bold, green background hint
                    option_widget.update(f"  [bold green]→ {key}  ● {option}[/bold green]")
                    option_widget.add_class("selected")
                else:
                    option_widget.update(f"    [hotkey]{key}[/hotkey]  {option}")
                    option_widget.remove_class("selected")
            except Exception:
                pass

        # Update custom option
        try:
            custom_widget = self.query_one(f"#custom-{self.question_index}", Static)
            if self.custom_text:
                display_text = self.custom_text[:30] + "..." if len(self.custom_text) > 30 else self.custom_text
                custom_widget.update(f"  [bold green]→ o  ● {display_text}[/bold green]")
                custom_widget.add_class("selected")
            else:
                custom_widget.update(f"    [hotkey]o[/hotkey]  Other (type your own)")
                custom_widget.remove_class("selected")
        except Exception:
            pass

    def get_response(self) -> Any:
        """Get the user's response for this question"""
        if self.custom_text:
            return self.custom_text
        elif self.selected:
            if self.multi_select:
                return [self.options[i] for i in self.selected]
            else:
                return self.options[self.selected[0]]
        return None

    def is_answered(self) -> bool:
        """Check if this question has been answered"""
        return bool(self.custom_text) or bool(self.selected)


class ClarificationModal(Vertical):
    """Modal for displaying clarification questions and collecting responses.

    Designed with human-centered principles:
    - Clear explanation of purpose
    - Visual progress tracking
    - Immediate feedback on actions
    - Easy to skip or complete
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._questions: List[Dict[str, Any]] = []
        self._question_widgets: List[ClarificationQuestion] = []
        self._on_submit: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_skip: Optional[Callable[[], None]] = None
        self._custom_input_active: bool = False
        self._custom_input_question: Optional[int] = None
        self._focused_question: int = 0

    def compose(self) -> ComposeResult:
        # Header
        yield Static(
            "[bold cyan]━━━ ❓ CLARIFICATION ━━━[/bold cyan]",
            classes="clarification-header"
        )

        # Explanation of WHY this helps
        yield Static(
            "[dim]These quick questions help experts understand your needs.[/dim]",
            classes="clarification-why"
        )
        yield Static(
            "[dim italic]Better context → more accurate solutions[/dim italic]",
            classes="clarification-why"
        )

        # Progress indicator
        yield Static(
            "",
            id="progress-indicator",
            classes="progress-indicator"
        )

        # Questions container
        yield VerticalScroll(id="questions-container")

        # Custom input area (hidden by default)
        yield Static("", id="custom-input-prompt", classes="custom-input-prompt")
        yield Input(placeholder="Type your response and press Enter...", id="custom-input", classes="hidden")

        # Footer with status and instructions
        yield Static(
            "",
            id="footer-status",
            classes="footer-status"
        )
        yield Static(
            "[dim]────────────────────────────────────────────────[/dim]",
            classes="footer-divider"
        )
        yield Static(
            "[hotkey]1-4[/hotkey] select  [hotkey]↑↓[/hotkey] navigate  [hotkey]o[/hotkey] custom  [hotkey]Enter[/hotkey] submit  [hotkey]ESC[/hotkey] skip",
            classes="clarification-footer"
        )

    def show_questions(
        self,
        questions: List[Dict[str, Any]],
        on_submit: Callable[[Dict[str, Any]], None],
        on_skip: Callable[[], None]
    ) -> None:
        """Display questions and set callbacks"""
        self._questions = questions
        self._on_submit = on_submit
        self._on_skip = on_skip
        self._question_widgets = []
        self._focused_question = 0

        container = self.query_one("#questions-container", VerticalScroll)
        container.remove_children()

        total = len(questions)
        for i, q in enumerate(questions):
            question_widget = ClarificationQuestion(
                question=q["question"],
                options=q["options"],
                question_index=i,
                total_questions=total,
                multi_select=q.get("multi_select", False)
            )
            # Ensure clean state
            question_widget.selected = []
            question_widget.custom_text = ""

            container.mount(question_widget)
            self._question_widgets.append(question_widget)
            if i == 0:
                question_widget.add_class("focused")

        # Show the modal first, then update progress after a moment
        self.add_class("show")

        # Update progress and status (all should be 0 initially)
        self._update_progress()
        self._update_footer_status()

    def hide(self) -> None:
        """Hide the modal"""
        self.remove_class("show")
        self._custom_input_active = False
        try:
            self.query_one("#custom-input", Input).add_class("hidden")
            self.query_one("#custom-input-prompt", Static).update("")
        except Exception:
            pass

    def _update_progress(self) -> None:
        """Update the progress indicator"""
        try:
            progress = self.query_one("#progress-indicator", Static)
            total = len(self._question_widgets)
            answered = sum(1 for w in self._question_widgets if w.is_answered())

            if total == 0:
                return

            # Progress bar
            bar_width = 20
            filled = int(bar_width * answered / total)
            bar = "█" * filled + "░" * (bar_width - filled)

            if answered == total:
                progress.update(f"[bold green]Progress: [{bar}] {answered}/{total} ✓ Ready to submit![/bold green]")
            elif answered > 0:
                progress.update(f"[cyan]Progress: [{bar}] {answered}/{total}[/cyan]")
            else:
                progress.update(f"[dim]Progress: [{bar}] {answered}/{total}[/dim]")
        except Exception:
            pass

    def _update_footer_status(self) -> None:
        """Update the footer status message"""
        try:
            status = self.query_one("#footer-status", Static)
            answered = sum(1 for w in self._question_widgets if w.is_answered())
            total = len(self._question_widgets)

            if total == 0:
                status.update("")
            elif answered == total:
                status.update("[bold green]✓ All questions answered! Press Enter to continue.[/bold green]")
            elif answered > 0:
                remaining = total - answered
                status.update(f"[cyan]{answered}/{total} answered[/cyan] — [yellow]{remaining} remaining[/yellow]")
            else:
                status.update(f"[dim]Answer the {total} question{'s' if total > 1 else ''} above, or press ESC to skip[/dim]")
        except Exception:
            pass

    def process_key(self, key: str) -> bool:
        """Process key press, return True if handled"""
        if not self.has_class("show"):
            return False

        # Handle custom input mode
        if self._custom_input_active:
            if key == "escape":
                self._cancel_custom_input()
                return True
            elif key == "enter":
                self._submit_custom_input()
                return True
            return False  # Let input widget handle other keys

        # Handle option selection (1-4 for options, o for Other)
        if key in "1234":
            option_idx = int(key) - 1
            self._select_option_for_focused(option_idx)
            return True
        elif key == "o":
            self._activate_custom_input(self._focused_question)
            return True
        elif key in ("up", "k"):
            self._focus_previous_question()
            return True
        elif key in ("down", "j", "tab"):
            self._focus_next_question()
            return True
        elif key == "escape":
            self.hide()
            if self._on_skip:
                self._on_skip()
            return True
        elif key == "enter":
            self._submit_responses()
            return True

        return False

    def _select_option_for_focused(self, option_idx: int) -> None:
        """Select an option for the currently focused question"""
        if not self._question_widgets:
            return

        if self._focused_question < len(self._question_widgets):
            question = self._question_widgets[self._focused_question]
            if option_idx < len(question.options):
                question.toggle_option(option_idx)
                # Update progress and status immediately
                self._update_progress()
                self._update_footer_status()
                # Auto-advance to next unanswered question
                self._advance_to_next_unanswered()

    def _advance_to_next_unanswered(self) -> None:
        """Move focus to the next unanswered question, or stay if all answered"""
        for i in range(self._focused_question + 1, len(self._question_widgets)):
            if not self._question_widgets[i].is_answered():
                self._focused_question = i
                self._update_focus_display()
                return
        # All remaining are answered, check earlier ones
        for i in range(0, self._focused_question):
            if not self._question_widgets[i].is_answered():
                self._focused_question = i
                self._update_focus_display()
                return
        # All answered - stay on current

    def _focus_previous_question(self) -> None:
        """Move focus to previous question"""
        if self._focused_question > 0:
            self._focused_question -= 1
            self._update_focus_display()

    def _focus_next_question(self) -> None:
        """Move focus to next question"""
        if self._focused_question < len(self._question_widgets) - 1:
            self._focused_question += 1
            self._update_focus_display()

    def _update_focus_display(self) -> None:
        """Update visual indication of focused question"""
        for i, widget in enumerate(self._question_widgets):
            if i == self._focused_question:
                widget.add_class("focused")
            else:
                widget.remove_class("focused")

    def _activate_custom_input(self, question_idx: int) -> None:
        """Activate custom text input for a question"""
        if question_idx >= len(self._question_widgets):
            return

        self._custom_input_active = True
        self._custom_input_question = question_idx

        question = self._question_widgets[question_idx]
        prompt = self.query_one("#custom-input-prompt", Static)
        prompt.update(f"[bold cyan]Your answer for Q{question_idx + 1}:[/bold cyan]")

        input_widget = self.query_one("#custom-input", Input)
        input_widget.remove_class("hidden")
        input_widget.value = question.custom_text
        input_widget.focus()

    def _submit_custom_input(self) -> None:
        """Submit the custom text input"""
        if self._custom_input_question is None:
            return

        input_widget = self.query_one("#custom-input", Input)
        text = input_widget.value.strip()

        if text and self._custom_input_question < len(self._question_widgets):
            self._question_widgets[self._custom_input_question].set_custom_text(text)
            self._update_progress()
            self._update_footer_status()

        self._cancel_custom_input()
        self._advance_to_next_unanswered()

    def _cancel_custom_input(self) -> None:
        """Cancel custom text input"""
        self._custom_input_active = False
        self._custom_input_question = None

        try:
            input_widget = self.query_one("#custom-input", Input)
            input_widget.add_class("hidden")
            input_widget.value = ""

            prompt = self.query_one("#custom-input-prompt", Static)
            prompt.update("")
        except Exception:
            pass

    def _submit_responses(self) -> None:
        """Submit all responses"""
        if not self._on_submit:
            return

        responses = {}
        for i, widget in enumerate(self._question_widgets):
            response = widget.get_response()
            if response is not None:
                responses[self._questions[i]["question"]] = response

        self.hide()
        self._on_submit(responses)
