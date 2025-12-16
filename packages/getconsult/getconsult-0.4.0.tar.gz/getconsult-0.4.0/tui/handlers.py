"""
Event handlers and key bindings for the Consult TUI
"""

import os
from datetime import datetime
from pathlib import Path
from textual.widgets import Static, TextArea, RichLog

from src.core.feature_gate import check_feature, require_team_mode, require_export
from src.core.exceptions import FeatureGatedError


class HandlerMixin:
    """Mixin class providing event handlers for ChatTUI"""

    def on_key(self, event):
        """Handle global key presses"""
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
            if event.key == "p":
                self.cycle_provider()
                event.prevent_default()
            elif event.key == "m":
                self.cycle_mode()
                event.prevent_default()
            elif event.key == "o":
                self.toggle_markdown()
                event.prevent_default()
            elif event.key == "t":
                self.cycle_threshold()
                event.prevent_default()
            elif event.key == "i":
                self.cycle_iterations()
                event.prevent_default()
            elif event.key == "e":
                self.cycle_experts()
                event.prevent_default()
            elif event.key == "c":
                self.action_compact_memory()
                event.prevent_default()
            elif event.key == "f":
                self.action_browse_files()
                event.prevent_default()
            elif event.key == "x":
                self.action_clear_attachments()
                event.prevent_default()
            elif event.key == "n":
                self.action_new_session()
                event.prevent_default()
            elif event.key in "123456789":
                self.toggle_expert_by_number(int(event.key))
                event.prevent_default()
            elif event.key in "abdghijklmop":
                idx = ord(event.key) - ord('a') + 10
                self.toggle_expert_by_number(idx)
                event.prevent_default()

        if event.key == "ctrl+enter":
            self.send_message()
            event.prevent_default()

    def on_click(self, event):
        """Handle clicks on file items"""
        if hasattr(event.widget, 'file_path') and hasattr(event.widget, 'file_type'):
            if event.widget.file_type == "directory":
                self.show_file_browser(event.widget.file_path)
            elif event.widget.file_type == "supported":
                self._select_file(event.widget.file_path)
                self.hide_file_browser()

    # Settings cycling methods
    def cycle_provider(self):
        """Cycle between providers/models"""
        from src.config import Config

        display = self.query_one("#model-display")
        display.add_class("changing")

        if self.mode == "team":
            display.update("[setting-value]Multiple models[/setting-value]")
            self.set_timer(0.5, lambda: display.remove_class("changing"))
            return

        providers = ["anthropic", "openai", "google"]
        idx = providers.index(self.provider)
        self.provider = providers[(idx + 1) % len(providers)]

        model_name = Config.get_model_for_provider(self.provider)
        display.update(f"[setting-value active]{model_name}[/setting-value active]")
        self.set_timer(0.5, lambda: display.remove_class("changing"))

    def cycle_mode(self):
        """Cycle between modes"""
        from src.config import Config

        mode_display = self.query_one("#mode-display")
        model_display = self.query_one("#model-display")

        mode_display.add_class("changing")
        model_display.add_class("changing")

        if self.mode == "single":
            # Check if team mode is allowed before switching
            try:
                require_team_mode()
                self.mode = "team"
            except FeatureGatedError as e:
                system_messages = self.query_one("#system-messages", RichLog)
                system_messages.write(f"[red]{e.user_message()}[/red]")
                mode_display.remove_class("changing")
                model_display.remove_class("changing")
                return
        else:
            self.mode = "single"

        if self.mode == "team":
            mode_display.update("[dim active]Competing AI teams[/dim active]")
            model_display.update("[setting-value]Multiple models[/setting-value]")
        else:
            mode_display.update("[dim active]Single AI team[/dim active]")
            model_name = Config.get_model_for_provider(self.provider)
            model_display.update(f"[setting-value]{model_name}[/setting-value]")

        self.set_timer(0.5, lambda: (mode_display.remove_class("changing"), model_display.remove_class("changing")))

    def toggle_markdown(self):
        """Toggle markdown output"""
        from textual.widgets import RichLog
        display = self.query_one("#markdown-display")
        system_messages = self.query_one("#system-messages", RichLog)

        # Check if enabling (need to check export permission)
        if not self.markdown:
            try:
                require_export()
            except FeatureGatedError as e:
                system_messages.write(f"[red]{e.user_message()}[/red]")
                return

        display.add_class("changing")
        self.markdown = not self.markdown

        if self.markdown:
            display.update("[setting-label]Markdown:[/setting-label] [toggle-on]ON[/toggle-on]")
            system_messages.write("[dim]📝 Markdown output enabled - will save to ~/.consult/outputs/ on completion[/dim]")
        else:
            display.update("[setting-label]Markdown:[/setting-label] [toggle-off]OFF[/toggle-off]")
            system_messages.write("[dim]📝 Markdown output disabled[/dim]")

        self.set_timer(0.5, lambda: display.remove_class("changing"))

    def cycle_threshold(self):
        """Cycle consensus threshold"""
        display = self.query_one("#threshold-display")
        display.add_class("changing")

        thresholds = [0.6, 0.7, 0.8, 0.9, 0.95]
        try:
            idx = thresholds.index(self.consensus_threshold)
            self.consensus_threshold = thresholds[(idx + 1) % len(thresholds)]
        except ValueError:
            self.consensus_threshold = 0.8

        percentage = int(self.consensus_threshold * 100)
        display.update(f"[setting-value active]{percentage}%[/setting-value active] [dim]agreement needed[/dim]")
        self.set_timer(0.5, lambda: display.remove_class("changing"))

    def cycle_iterations(self):
        """Cycle max iterations"""
        display = self.query_one("#iterations-display")
        display.add_class("changing")

        iterations = [1, 2, 3, 5]
        try:
            idx = iterations.index(self.max_iterations)
            self.max_iterations = iterations[(idx + 1) % len(iterations)]
        except ValueError:
            self.max_iterations = 2

        label = "round" if self.max_iterations == 1 else "rounds"
        display.update(f"[setting-value active]{self.max_iterations}[/setting-value active] [dim]thinking {label}[/dim]")
        self.set_timer(0.5, lambda: display.remove_class("changing"))

    def cycle_experts(self):
        """Cycle through expert sets"""
        display = self.query_one("#experts-display")
        display.add_class("changing")

        if self.experts == "default":
            self.experts = "custom"
            count = len(self.custom_experts)
            display.update(f"[setting-value active]{count}[/setting-value active] [dim]experts (custom)[/dim]")
            self.show_expert_selection()
        else:
            self.experts = "default"
            display.update("[setting-value active]3[/setting-value active] [dim]experts (default)[/dim]")
            self.hide_expert_selection()

        self.set_timer(0.5, lambda: display.remove_class("changing"))
