"""
Helper functions and utilities for the Consult TUI
"""

import sys
import os
from pathlib import Path
from textual.widgets import Static, RichLog

# Supported file extensions for attachments
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf", ".heic", ".heif"}


def is_supported_file(filename: str) -> bool:
    """Check if file is supported for attachments"""
    return any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)


class HelperMixin:
    """Mixin class providing helper methods for ChatTUI"""

    def reset_send_button(self):
        """Reset send button and input area to default state"""
        from textual.widgets import TextArea

        send_btn = self.query_one("#send-btn")
        send_btn.label = "► Send"
        send_btn.remove_class("processing")

        # Unfreeze input area - restore welcoming state
        input_section = self.query_one("#input-section")
        input_section.remove_class("processing")
        input_section.border_title = "Ask anything... experts will analyze and discuss"
        input_section.border_subtitle = "Shift+Enter to send"
        chat_input = self.query_one("#chat-input", TextArea)
        chat_input.disabled = False
        chat_input.focus()

        self.update_system_status("ready", "SYSTEM READY")

    def update_system_status(self, status_type: str, message: str):
        """Update the system status"""
        self.current_status_type = status_type

        if status_type == "ready":
            self.current_status = "READY"
        elif status_type == "processing":
            self.current_status = "ACTIVE"
        elif status_type == "error":
            self.current_status = "ERROR"
        else:
            self.current_status = "READY"

    def _update_memory_display(self):
        """Update memory status with visual feedback"""
        try:
            session_info = self.memory_persistence.get_session_info()

            memory_usage = self.query_one("#memory-usage", Static)
            usage_percent = self.memory_persistence.memory_manager.get_memory_usage()

            memory_usage.remove_class("memory-high")
            memory_usage.remove_class("memory-critical")

            if usage_percent >= 90:
                usage_text = f"[red bold]{int(usage_percent)}%[/red bold] [dim]CRITICAL[/dim]"
                memory_usage.add_class("memory-critical")
            elif usage_percent >= 70:
                usage_text = f"[yellow bold]{int(usage_percent)}%[/yellow bold] [dim]high[/dim]"
                memory_usage.add_class("memory-high")
            else:
                usage_text = f"[setting-value]{int(usage_percent)}%[/setting-value] [dim]used[/dim]"

            memory_usage.update(usage_text)

            memory_context = self.query_one("#memory-context", Static)
            if session_info["has_context"]:
                context_text = "[bold green]Has prior context[/bold green]"
            else:
                context_text = "[dim]No prior context[/dim]"
            memory_context.update(context_text)

            memory_messages = self.query_one("#memory-messages", Static)
            actual_count = len(self.memory_persistence.memory_manager.conversation_history)
            msg_label = "message" if actual_count == 1 else "messages"
            if session_info["is_compacted"]:
                messages_text = f"[setting-value]{actual_count}[/setting-value] [dim]{msg_label} (compacted)[/dim]"
            else:
                messages_text = f"[setting-value]{actual_count}[/setting-value] [dim]{msg_label}[/dim]"
            memory_messages.update(messages_text)
        except Exception:
            pass  # Memory widgets might not exist during initialization

    def update_attachments_display(self):
        """Update the attachments display in sidebar"""
        try:
            attachment_display = self.query_one("#attachments-display")
            count = len(self.attachments) if self.attachments else 0
            if count == 0:
                attachment_display.update("[dim]None attached[/dim]")
            elif count == 1:
                attachment_display.update("[setting-value]1[/setting-value] [dim]file attached[/dim]")
            else:
                attachment_display.update(f"[setting-value]{count}[/setting-value] [dim]files attached[/dim]")
        except Exception:
            pass  # Attachment display might not exist during initialization

    def _load_expert_data(self):
        """Load actual expert data from the system"""
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "main.py", "--list-experts"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                lines = result.stdout.split('\n')

                in_expert_sets = False
                in_individual_experts = False

                for line in lines:
                    line = line.strip()

                    if "📋 Expert Sets:" in line:
                        in_expert_sets = True
                        in_individual_experts = False
                        continue
                    elif "👥 Individual Experts" in line:
                        in_expert_sets = False
                        in_individual_experts = True
                        continue
                    elif "💡 Usage Examples:" in line:
                        break

                    if in_expert_sets and line.startswith("• "):
                        expert_set = line[2:].split(":")[0].strip()
                        if expert_set and expert_set not in self.expert_sets:
                            self.expert_sets.append(expert_set)

                    elif in_individual_experts and line.startswith("• "):
                        expert = line[2:].split(":")[0].strip()
                        if expert:
                            self.all_experts.append(expert)

                self.expert_sets = [e for e in self.expert_sets if e]

                if "default" in self.expert_sets:
                    self.expert_sets.remove("default")
                if "custom" in self.expert_sets:
                    self.expert_sets.remove("custom")

                self.expert_sets = ["default"] + self.expert_sets + ["custom"]

                if "database_expert" in self.all_experts and "backend_expert" in self.all_experts:
                    self.custom_experts = ["database_expert", "backend_expert", "infrastructure_expert"]
                else:
                    self.custom_experts = self.all_experts[:3] if len(self.all_experts) >= 3 else self.all_experts[:2] if len(self.all_experts) >= 2 else self.all_experts.copy()

        except Exception as e:
            self.expert_sets = ["default", "custom"]
            self.all_experts = ["backend_expert", "database_expert", "infrastructure_expert"]
            self.custom_experts = ["database_expert", "backend_expert", "infrastructure_expert"]
            print(f"Warning: Could not load expert data: {e}")
