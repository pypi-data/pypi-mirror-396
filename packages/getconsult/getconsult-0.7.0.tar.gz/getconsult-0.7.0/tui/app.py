#!/usr/bin/env python3
"""
Consult TUI - Main Application
Expert Panel Consensus Terminal Interface

Features collapsible workflow visualization for reduced cognitive load.
"""

import os
from datetime import datetime
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Button, Static, TextArea, RichLog
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on

from .styles import APP_CSS
from .workers import WorkerMixin
from .handlers import HandlerMixin
from .helpers import HelperMixin, is_supported_file
from .widgets import StatusHeader, WorkflowView, ClarificationModal
from .widgets.detail_pane import DetailPane

from src.core.license import get_current_tier, get_current_limits, Tier, get_license_manager
from src.core.rate_limiter import check_can_query, record_query, get_rate_limiter
from src.core.paths import ensure_consult_structure, get_logs_dir
from src.core.security import get_contextual_logger, set_session_context
from src.core.identity import get_user_id, generate_session_id
from src.core.feature_gate import require_tui, require_attachments, require_team_mode, check_feature
from src.core.exceptions import FeatureGatedError


class ChatTUI(WorkerMixin, HandlerMixin, HelperMixin, App):
    """Consult - Expert Panel Consensus"""

    TITLE = " Consult"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("n", "new_session", "New Session"),
        ("y", "copy_solution", "Copy Solution"),
        ("f", "browse_files", "Browse Files"),
        ("x", "clear_attachments", "Clear Files"),
        ("d", "toggle_detail", "Toggle Detail"),
        ("l", "toggle_log", "Toggle Log"),
        ("u", "toggle_input", "Toggle Input"),
        ("g", "goto_current", "Go to Current"),
        ("c", "compact_memory", "Compact Memory"),
        ("escape", "collapse_all", "Collapse All"),
        ("?", "show_help", "Help"),
    ]

    CSS = APP_CSS

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Settings Sidebar
            with Vertical(id="sidebar"):
                yield Static("CONFIGURATION", classes="main-header")

                yield Static("  MODEL", classes="section-header")
                yield Static("[setting-value]claude-sonnet-4-20250514[/setting-value]", id="model-display", classes="setting")
                yield Static("[dim]Single AI team[/dim]", id="mode-display", classes="setting")
                yield Static("[hotkey]P[/hotkey][dim]=model [/dim][hotkey]M[/hotkey][dim]=mode[/dim]", classes="key-hint")

                yield Static("  ANALYSIS", classes="section-header")
                yield Static("[setting-value]2[/setting-value] [dim]thinking rounds[/dim]", id="iterations-display", classes="setting")
                yield Static("[setting-value]80%[/setting-value] [dim]agreement needed[/dim]", id="threshold-display", classes="setting")
                yield Static("[setting-value]3[/setting-value] [dim]experts (default)[/dim]", id="experts-display", classes="setting")
                yield Static("[hotkey]I[/hotkey][dim]=rounds [/dim][hotkey]T[/hotkey][dim]=agree [/dim][hotkey]E[/hotkey][dim]=experts[/dim]", classes="key-hint")

                yield Static("  OUTPUT", classes="section-header")
                yield Static("[dim]Markdown:[/dim] [toggle-off]OFF[/toggle-off]", id="markdown-display", classes="setting")
                yield Static("[hotkey]O[/hotkey][dim]=toggle[/dim]", classes="key-hint")

                yield Static("  MEMORY", classes="section-header")
                yield Static("[setting-value]0%[/setting-value] [dim]used[/dim]", id="memory-usage", classes="setting")
                yield Static("[dim]No prior context[/dim]", id="memory-context", classes="setting")
                yield Static("[setting-value]0[/setting-value] [dim]messages[/dim]", id="memory-messages", classes="setting")
                yield Static("[hotkey]C[/hotkey][dim]=compact [/dim][hotkey]N[/hotkey][dim]=new[/dim]", classes="key-hint")

                yield Static("  FILES", classes="section-header")
                yield Static("[dim]None attached[/dim]", id="attachments-display", classes="setting")
                yield Static("[hotkey]F[/hotkey][dim]=browse [/dim][hotkey]X[/hotkey][dim]=clear[/dim]", classes="key-hint")

            # Chat area with new collapsible workflow view
            with Vertical(id="chat-area"):
                # Title bar
                yield Static(
                    "[bold]CONSULT[/bold] [dim]│ Many Experts, One Answer[/dim]",
                    id="title-bar"
                )

                # Status header - always visible workflow state
                yield StatusHeader(id="status-header")

                # Main workflow view - collapsible structure
                yield WorkflowView(id="workflow-view")

                # Activity Log - chatty real-time insights (full history preserved)
                yield RichLog(
                    id="system-messages",
                    auto_scroll=True,
                    max_lines=None,  # No limit - preserve full lineage
                    markup=True,
                    wrap=True
                )

                # Collapsed indicator (hidden by default, shown when log is collapsed)
                yield Static(
                    "─── [bold green]ACTIVITY LOG[/bold green] [dim]collapsed ─── press[/dim] [bold yellow]L[/bold yellow] [dim]to expand ───[/dim]",
                    id="log-collapsed-bar"
                )

                # Input section - cohesive bordered unit
                with Vertical(id="input-section"):
                    with Horizontal(id="input-area"):
                        yield TextArea(id="chat-input")
                        yield Button("► Send", id="send-btn", variant="success")

                # Collapsed input indicator (hidden by default)
                yield Static(
                    "─── [bold cyan]INPUT[/bold cyan] [dim]collapsed ─── press[/dim] [bold yellow]U[/bold yellow] [dim]to expand ───[/dim]",
                    id="input-collapsed-bar"
                )

        # Modals
        with Container(id="expert-modal"):
            yield Container(id="expert-selection", classes="expert-container")

        with Container(id="file-modal"):
            yield Container(id="file-browser", classes="file-container")

        # Clarification modal (right-dock, shown when clarification needed)
        with Container(id="clarification-modal"):
            yield ClarificationModal(id="clarification-content")

        # Detail pane (optional - toggle with D key)
        with Container(id="detail-pane"):
            yield DetailPane(id="detail-content")

        yield Footer()

    def on_mount(self):
        # Ensure Consult home directory exists
        ensure_consult_structure()

        # Initialize contextual logging with user/session IDs
        license_key = get_license_manager().get_license_key()
        user_id = get_user_id(license_key) if license_key else "anonymous"
        session_id = generate_session_id()
        set_session_context(user_id=user_id, session_id=session_id)

        log_file = get_logs_dir() / "consult.log"
        self.logger = get_contextual_logger("consult.tui", log_file=str(log_file))
        self.logger.info("Consult TUI started")

        self.provider = "anthropic"
        self.mode = "single"
        self.markdown = False
        self.max_iterations = 2
        self.consensus_threshold = 0.8
        self.experts = "default"

        self.current_status = "READY"
        self.current_status_type = "ready"

        self.attachments = []
        self.markdown_content = []
        self.current_output_buffer = []

        # Event handler reference (set by workers when workflow runs)
        self._event_handler = None
        # Renderer reference (persists after workflow completes for detail pane)
        self._last_renderer = None
        # Clarification handler reference (set by workers when workflow runs)
        self._clarification_handler = None
        # Track if workflow is running (locks configuration)
        self._workflow_active = False

        from src.memory.memory_persistence import MemoryPersistence
        self.memory_persistence = MemoryPersistence()
        self.memory_persistence.load_state()

        # Initialize model display with actual model name
        from src.config import Config
        model_name = Config.get_model_for_provider(self.provider)
        self.query_one("#model-display").update(f"[setting-value]{model_name}[/setting-value]")

        self._update_memory_display()

        self.expert_sets = []
        self.all_experts = []
        self.custom_experts = []
        self._load_expert_data()

        # Show welcome info in system messages
        self._show_log_welcome()

        # Set up input section as cohesive unit - welcoming for first-time users
        input_section = self.query_one("#input-section")
        input_section.border_title = "Ask anything... experts will analyze and discuss"
        input_section.border_subtitle = "U to hide │ Shift+Enter to send"

        self.query_one("#chat-input").focus()

    def _show_log_welcome(self):
        """Show engaging welcome state in the activity log."""
        from rich.text import Text
        system_messages = self.query_one("#system-messages", RichLog)

        welcome = Text()
        welcome.append("─── ACTIVITY LOG ─── ", style="bold green")
        welcome.append("[", style="dim")
        welcome.append("L", style="bold yellow")
        welcome.append("] collapse\n", style="dim")
        welcome.append("Real-time insights as your expert panel works\n\n", style="dim")
        welcome.append("⌨️  ", style="dim")
        welcome.append("[D]", style="bold yellow")
        welcome.append(" reasoning trace  ", style="dim")
        welcome.append("[E]", style="bold yellow")
        welcome.append(" experts  ", style="dim")
        welcome.append("[?]", style="bold yellow")
        welcome.append(" all hotkeys\n", style="dim")
        system_messages.write(welcome)

    # Event handlers - must be defined on App class directly for Textual to find them
    @on(Button.Pressed, "#send-btn")
    def handle_send_button(self):
        """Handle send button press"""
        # Check if workflow is running (button shows "Stop" when processing)
        send_btn = self.query_one("#send-btn")
        is_processing = send_btn.has_class("processing")

        if is_processing:
            # Stop workflow
            self.workers.cancel_all()
            system_messages = self.query_one("#system-messages", RichLog)
            system_messages.write("[bold red]⏹ Workflow stopped by user[/bold red]")
            self._unlock_config()
            self.reset_send_button()
        else:
            input_widget = self.query_one("#chat-input", TextArea)
            question = input_widget.text.strip()

            if not question:
                return

            system_messages = self.query_one("#system-messages", RichLog)

            # Check quota before running
            can_query, quota_error = check_can_query()
            if not can_query:
                tier = get_current_tier()
                limits = get_current_limits()
                system_messages.write(f"[bold red]Query limit reached[/bold red]")
                system_messages.write(f"[red]{quota_error}[/red]")
                system_messages.write(f"[dim]Tier: {tier.value} ({limits.queries_per_day}/day, {limits.queries_per_hour}/hour)[/dim]")
                system_messages.write("[dim]Upgrade at: https://getconsult.sysapp.dev[/dim]")
                return

            # Check for quota warning
            rate_limiter = get_rate_limiter()
            warning = rate_limiter.show_quota_warning()
            if warning:
                system_messages.write(f"[yellow]Note: {warning}[/yellow]")

            time_str = datetime.now().strftime("%H:%M")
            system_messages.write(f"[dim]{time_str}[/dim] [bold blue] Query submitted[/bold blue]")

            input_widget.clear()

            send_btn = self.query_one("#send-btn")
            send_btn.label = "■ Stop"
            send_btn.add_class("processing")

            # Freeze input area during processing
            input_section = self.query_one("#input-section")
            input_section.add_class("processing")
            input_section.border_title = "⏳ PROCESSING"
            input_section.border_subtitle = "\\[■] stop"
            chat_input = self.query_one("#chat-input", TextArea)
            chat_input.disabled = True

            self.update_system_status("processing", "PROCESSING...")

            self.run_command(question)

    def on_key(self, event):
        """Handle global key presses"""
        # Check clarification modal first (highest priority)
        clarification_modal = self.query_one("#clarification-content", ClarificationModal)
        if clarification_modal.has_class("show"):
            if clarification_modal.process_key(event.key):
                event.prevent_default()
                return

        # Check expert modal
        modal = self.query_one("#expert-modal")
        if "show" in modal.classes:
            if event.key == "escape":
                self.hide_expert_selection()
                event.prevent_default()
                return
            elif event.key == "enter":
                self.hide_expert_selection()
                event.prevent_default()
                return

        # Check file browser modal
        file_modal = self.query_one("#file-modal")
        if "show" in file_modal.classes:
            if event.key == "escape":
                self.hide_file_browser()
                event.prevent_default()
                return

        # Only handle settings keys when NOT in textarea
        textarea = self.query_one("#chat-input", TextArea)
        if not textarea.has_focus:
            # Config keys - only work when workflow is not active
            if event.key == "p":
                if not self._workflow_active:
                    self.cycle_provider()
                event.prevent_default()
            elif event.key == "m":
                if not self._workflow_active:
                    self.cycle_mode()
                event.prevent_default()
            elif event.key == "o":
                # Markdown toggle is safe during workflow
                self.toggle_markdown()
                event.prevent_default()
            elif event.key == "t":
                if not self._workflow_active:
                    self.cycle_threshold()
                event.prevent_default()
            elif event.key == "i":
                if not self._workflow_active:
                    self.cycle_iterations()
                event.prevent_default()
            elif event.key == "e":
                if not self._workflow_active:
                    self.cycle_experts()
                event.prevent_default()
            elif event.key == "c":
                if not self._workflow_active:
                    self.action_compact_memory()
                event.prevent_default()
            elif event.key == "f":
                if not self._workflow_active:
                    self.action_browse_files()
                event.prevent_default()
            elif event.key == "x":
                if not self._workflow_active:
                    self.action_clear_attachments()
                event.prevent_default()
            elif event.key == "n":
                if not self._workflow_active:
                    self.action_new_session()
                event.prevent_default()
            elif event.key == "d":
                self.action_toggle_detail()
                event.prevent_default()
            elif event.key == "l":
                self.action_toggle_log()
                event.prevent_default()
            elif event.key == "u":
                self.action_toggle_input()
                event.prevent_default()
            elif event.key in ("plus", "equal", "minus"):
                self.action_expand_input()
                event.prevent_default()
            elif event.key == "g":
                self.action_goto_current()
                event.prevent_default()
            elif event.key in "123456789":
                # If detail pane is visible, use numbers to select agents
                detail_pane_container = self.query_one("#detail-pane")
                if "show" in detail_pane_container.classes:
                    detail_pane = self.query_one("#detail-content", DetailPane)
                    detail_pane.select_agent_by_number(int(event.key))
                else:
                    self.toggle_expert_by_number(int(event.key))
                event.prevent_default()
            elif event.key in "abdghijklmop":
                idx = ord(event.key) - ord('a') + 10
                self.toggle_expert_by_number(idx)
                event.prevent_default()

        # Shift+Enter to send - works everywhere, cross-platform
        if event.key == "shift+enter":
            self.handle_send_button()
            event.prevent_default()
            event.stop()

    def on_click(self, event):
        """Handle clicks on file items"""
        if hasattr(event.widget, 'file_path') and hasattr(event.widget, 'file_type'):
            if event.widget.file_type == "directory":
                self.show_file_browser(event.widget.file_path)
            elif event.widget.file_type == "supported":
                self._select_file(event.widget.file_path)
                self.hide_file_browser()

    # Action methods
    def action_show_help(self):
        """Show keyboard shortcuts in system messages"""
        system_messages = self.query_one("#system-messages", RichLog)
        system_messages.write("")
        system_messages.write("[bold green] KEYBOARD SHORTCUTS[/bold green]")
        system_messages.write("[dim]─────────────────────────────────────[/dim]")
        system_messages.write("[yellow]Model:[/yellow] P=switch model  M=single/team mode")
        system_messages.write("[yellow]Analysis:[/yellow] I=rounds  T=agreement  E=experts")
        system_messages.write("[yellow]Output:[/yellow] O=markdown  Y=copy solution")
        system_messages.write("[yellow]View:[/yellow] D=detail  L=log  G=goto  ESC=collapse")
        system_messages.write("[yellow]Memory:[/yellow] C=compact  N=new session")
        system_messages.write("[yellow]Files:[/yellow] F=browse  X=clear")
        system_messages.write("[yellow]General:[/yellow] ?=help  Ctrl+Enter=send  Q=quit")
        system_messages.write("[dim]─────────────────────────────────────[/dim]")
        system_messages.write("")

    def action_copy_solution(self):
        """Copy the last solution to clipboard"""
        system_messages = self.query_one("#system-messages", RichLog)

        # Check if we have a result to copy
        if not hasattr(self, '_last_result') or not self._last_result:
            system_messages.write("[yellow]No solution to copy yet. Run a query first.[/yellow]")
            return

        # Import and use the clipboard function from CLI
        from src.cli import copy_to_clipboard

        solution = self._last_result.final_solution
        if copy_to_clipboard(solution):
            system_messages.write("[green]✓ Solution copied to clipboard[/green]")
        else:
            system_messages.write("[yellow]Could not copy to clipboard. Try selecting text manually.[/yellow]")

    def action_compact_memory(self):
        """Handle memory compaction via keyboard command"""
        system_messages = self.query_one("#system-messages", RichLog)
        system_messages.write("[bold yellow] Compacting memory...[/bold yellow]")
        self._do_compact_memory()

    def action_new_session(self):
        """Start a new session"""
        # Cancel any running workers first
        self.workers.cancel_all()
        self._do_new_session()

    def action_browse_files(self):
        """Show the file browser panel"""
        try:
            self.show_file_browser()
        except Exception as e:
            system_messages = self.query_one("#system-messages", RichLog)
            system_messages.write(f"[red] Error opening file browser: {str(e)}[/red]")

    def action_clear_attachments(self):
        """Clear all attachments"""
        if self.attachments:
            self.attachments = []
            self.update_attachments_display()
            system_messages = self.query_one("#system-messages", RichLog)
            system_messages.write("[dim]Files cleared[/dim]")

    def action_toggle_detail(self):
        """Toggle the detail pane visibility"""
        detail_pane_container = self.query_one("#detail-pane")
        detail_pane_container.toggle_class("show")

        # If showing, connect renderer and refresh
        if "show" in detail_pane_container.classes:
            detail_pane = self.query_one("#detail-content", DetailPane)
            # Use current event handler's renderer, or fall back to last renderer
            renderer = None
            if self._event_handler and hasattr(self._event_handler, 'renderer'):
                renderer = self._event_handler.renderer
            elif self._last_renderer:
                renderer = self._last_renderer

            if renderer:
                detail_pane.set_renderer(renderer)
                detail_pane.refresh_view()

    def action_toggle_log(self):
        """Toggle the activity log visibility for more reading space"""
        log = self.query_one("#system-messages", RichLog)
        collapsed_bar = self.query_one("#log-collapsed-bar", Static)

        # Toggle: when log visible -> hide log, show bar
        #         when log hidden -> show log, hide bar
        log.toggle_class("collapsed")
        collapsed_bar.toggle_class("show")

    def action_toggle_input(self):
        """Toggle the input area visibility for more reading space"""
        input_section = self.query_one("#input-section")
        collapsed_bar = self.query_one("#input-collapsed-bar", Static)

        input_section.toggle_class("collapsed")
        collapsed_bar.toggle_class("show")

    def action_expand_input(self):
        """Toggle expanded input area for longer queries"""
        input_section = self.query_one("#input-section")
        input_section.toggle_class("expanded")

        # Update subtitle to show current state
        if "expanded" in input_section.classes:
            input_section.border_subtitle = "\\[U] hide  \\[-] shrink"
        else:
            input_section.border_subtitle = "\\[U] hide  \\[+] expand"

    def action_goto_current(self):
        """Scroll to and expand current active section"""
        if self._event_handler:
            self._event_handler.scroll_to_current()

    def action_collapse_all(self):
        """Collapse all expanded sections"""
        # Try current event handler first
        if self._event_handler:
            self._event_handler.collapse_all()
        # Fall back to last renderer (for after workflow completes)
        elif self._last_renderer:
            self._last_renderer.collapse_all()

        # Also collapse detail pane phases if visible
        try:
            detail_pane = self.query_one("#detail-pane")
            if detail_pane.display:
                journey_view = detail_pane.query_one("#journey-view")
                for phase in journey_view._phases.values():
                    phase.collapsed = True
        except Exception:
            pass

    def action_quit(self):
        """Quit the app cleanly"""
        # Cancel any running workers
        self.workers.cancel_all()
        self.exit()

    # Expert selection methods
    def show_expert_selection(self):
        """Show the expert selection panel"""
        try:
            modal = self.query_one("#expert-modal")
            container = self.query_one("#expert-selection")

            container.remove_children()
            modal.add_class("show")

            selected_count = len(self.custom_experts)
            total_count = len(self.all_experts)
            container.mount(Static(f"[bold cyan]SELECT AGENTS ({selected_count}/{total_count})[/bold cyan]", classes="expert-header"))
            container.mount(Static(f"[bold green] {selected_count} selected[/bold green] [dim]• Min: 2 experts[/dim]", classes="key-hint"))
            container.mount(Static("[bold yellow]ESC/Enter to close[/bold yellow] [dim]• Toggle: 1-9, a-z[/dim]", classes="key-hint"))
            container.mount(Static("", classes=""))

            categories = {
                "Core": ["backend_expert", "frontend_expert", "database_expert", "infrastructure_expert"],
                "Advanced": ["ml_expert", "ai_expert", "security_expert", "cloud_expert"],
                "Specialized": []
            }

            categorized = set()
            for category_experts in categories.values():
                categorized.update(category_experts)

            for expert in self.all_experts:
                if expert not in categorized:
                    categories["Specialized"].append(expert)

            for category, experts in categories.items():
                category_experts = [e for e in experts if e in self.all_experts]
                if category_experts:
                    container.mount(Static(f"[bold green] {category}[/bold green]", classes="section-header"))

                    for expert in category_experts:
                        i = self.all_experts.index(expert)
                        if i < 9:
                            key = str(i + 1)
                        else:
                            key = chr(ord('a') + i - 9)

                        clean_name = expert.replace("_expert", "").replace("_", " ").title()

                        if expert in self.custom_experts:
                            container.mount(Static(f" [hotkey]{key}[/hotkey] [bold green][/bold green] {clean_name}", classes="expert-item selected"))
                        else:
                            container.mount(Static(f" [hotkey]{key}[/hotkey]   {clean_name}", classes="expert-item unselected"))

                    container.mount(Static("", classes=""))

        except Exception as e:
            print(f"Expert selection error: {e}")
            self.hide_expert_selection()

    def hide_expert_selection(self):
        """Hide the expert selection panel"""
        modal = self.query_one("#expert-modal")
        container = self.query_one("#expert-selection")
        container.remove_children()
        modal.remove_class("show")

    def toggle_expert_by_number(self, num_or_idx):
        """Toggle expert by number"""
        if self.experts != "custom":
            return

        if num_or_idx >= 10:
            idx = num_or_idx - 1
        else:
            idx = num_or_idx - 1

        if idx >= len(self.all_experts) or idx < 0:
            return

        expert = self.all_experts[idx]

        if expert in self.custom_experts:
            if len(self.custom_experts) > 2:
                self.custom_experts.remove(expert)
        else:
            self.custom_experts.append(expert)

        self.show_expert_selection()
        count = len(self.custom_experts)
        self.query_one("#experts-display").update(f"[setting-label]Agents:[/setting-label] [setting-value active]CUSTOM({count})[/setting-value active]")

    # File browser methods
    def show_file_browser(self, path=None):
        """Show the file browser panel"""
        if path is None:
            path = os.getcwd()

        try:
            modal = self.query_one("#file-modal")
            container = self.query_one("#file-browser")

            container.remove_children()
            modal.add_class("show")

            container.mount(Static(" SELECT FILE", classes="file-header"))
            container.mount(Static(f"[dim]{path}[/dim]", classes="file-path"))

            path_obj = Path(path)
            entries = []

            if path_obj.parent != path_obj:
                entries.append((".. (parent)", "directory", str(path_obj.parent)))

            try:
                for item in sorted(path_obj.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                    if item.is_dir():
                        entries.append((f" {item.name}/", "directory", str(item)))
                    elif is_supported_file(item.name):
                        size_mb = item.stat().st_size / (1024 * 1024)
                        if size_mb < 20:
                            entries.append((f" {item.name}", "supported", str(item)))
                        else:
                            entries.append((f" {item.name} [dim](too large)[/dim]", "file", str(item)))
                    else:
                        entries.append((f" {item.name}", "file", str(item)))
            except PermissionError:
                entries.append(("[red]Permission denied[/red]", "error", ""))

            for display_name, file_type, full_path in entries:
                item = Static(display_name, classes=f"file-item {file_type}")
                item.file_path = full_path
                item.file_type = file_type
                container.mount(item)

            container.mount(Static("", classes="file-item"))
            container.mount(Static("[dim]Click to select • ESC to close[/dim]", classes="file-item"))

        except Exception as e:
            print(f"File browser error: {e}")
            self.hide_file_browser()

    def hide_file_browser(self):
        """Hide the file browser panel"""
        modal = self.query_one("#file-modal")
        container = self.query_one("#file-browser")
        container.remove_children()
        modal.remove_class("show")

    # Workflow state management
    def _lock_config(self):
        """Lock configuration panel during workflow - visual feedback only"""
        self._workflow_active = True
        # Add locked class to sidebar for visual dimming
        try:
            sidebar = self.query_one("#sidebar")
            sidebar.add_class("locked")
        except Exception:
            pass

    def _unlock_config(self):
        """Unlock configuration panel after workflow completes"""
        self._workflow_active = False
        # Remove locked class from sidebar
        try:
            sidebar = self.query_one("#sidebar")
            sidebar.remove_class("locked")
        except Exception:
            pass

    # Clarification methods
    def show_clarification_modal(self, questions):
        """Show the clarification modal with questions"""
        modal_container = self.query_one("#clarification-modal")
        clarification_modal = self.query_one("#clarification-content", ClarificationModal)

        modal_container.add_class("show")
        clarification_modal.show_questions(
            questions=questions,
            on_submit=self._on_clarification_submit,
            on_skip=self._on_clarification_skip
        )

    def hide_clarification_modal(self):
        """Hide the clarification modal"""
        modal_container = self.query_one("#clarification-modal")
        clarification_modal = self.query_one("#clarification-content", ClarificationModal)

        modal_container.remove_class("show")
        clarification_modal.hide()

    def _on_clarification_submit(self, responses):
        """Handle clarification responses from modal"""
        self.hide_clarification_modal()

        if self._clarification_handler:
            self._clarification_handler.receive_response(responses)

        system_messages = self.query_one("#system-messages", RichLog)
        system_messages.write("[bold green] Clarifications received[/bold green]")

    def _on_clarification_skip(self):
        """Handle clarification skip"""
        self.hide_clarification_modal()

        if self._clarification_handler:
            self._clarification_handler.skip_clarification()

        system_messages = self.query_one("#system-messages", RichLog)
        system_messages.write("[dim] Clarification skipped[/dim]")

    def _select_file(self, file_path):
        """Select a file for attachment"""
        system_messages = self.query_one("#system-messages", RichLog)

        # Check attachments feature access
        try:
            require_attachments()
        except FeatureGatedError as e:
            system_messages.write(f"[red]{e.user_message()}[/red]")
            return

        try:
            # Check for duplicate
            for existing in self.attachments:
                if hasattr(existing, 'original_path') and existing.original_path == file_path:
                    filename = file_path.split('/')[-1]
                    system_messages.write(f"[yellow]⚠ File already attached: {filename}[/yellow]")
                    return

            from src.models.attachments import AttachmentProcessor
            attachment = AttachmentProcessor.load_from_path(file_path)
            self.attachments.append(attachment)
            attachment.original_path = file_path

            filename = file_path.split('/')[-1]
            system_messages.write(f"[green]📎 Added file: {filename}[/green]")

            self.update_attachments_display()

        except FileNotFoundError:
            system_messages.write(f"[red] File not found: {file_path}[/red]")
        except Exception as e:
            system_messages.write(f"[red] Error adding file: {str(e)}[/red]")


def main():
    # Check TUI access BEFORE launching (Pro tier required)
    # This runs before Textual takes over the terminal
    try:
        require_tui()
    except FeatureGatedError as e:
        print(e.user_message())
        return

    app = ChatTUI()
    app.run()


if __name__ == "__main__":
    main()
