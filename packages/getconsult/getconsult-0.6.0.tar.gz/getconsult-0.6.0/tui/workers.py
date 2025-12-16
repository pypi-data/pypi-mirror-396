"""
Async background workers for the Consult TUI
Uses Textual's @work decorator for proper async execution
"""

import asyncio
import re
import traceback
from datetime import datetime
from textual import work
from textual.widgets import RichLog, TextArea
from rich.text import Text

from tui.event_handler import TUIEventHandler
from tui.widgets import WorkflowView, StatusHeader

from src.core.rate_limiter import record_query
from src.core.paths import get_logs_dir
from src.core.security import get_contextual_logger

# Module-level logger for TUI workers
_logger = None

def _get_logger():
    """Get or create the TUI worker logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.tui.worker", log_file=str(log_file))
    return _logger


class WorkerMixin:
    """Mixin class providing async worker methods for ChatTUI"""

    @work(exclusive=True)
    async def run_command(self, question: str) -> None:
        """Run workflow with collapsible widget-based visualization.

        This executes the workflow directly and receives structured events
        that the TUIEventHandler renders into collapsible widgets.
        """
        from src.workflows.consensus.consensus_workflow import ConsensusWorkflow

        # Get the new widget-based components
        workflow_view = self.query_one("#workflow-view", WorkflowView)
        status_header = self.query_one("#status-header", StatusHeader)
        system_messages = self.query_one("#system-messages", RichLog)

        # Create TUI event handler with new widget-based rendering
        event_handler = TUIEventHandler(
            workflow_view=workflow_view,
            status_header=status_header,
            system_messages=system_messages
        )

        # Transfer agent history from previous renderer (for follow-up queries)
        if self._last_renderer:
            # First, archive the previous renderer's current journeys to its history
            if hasattr(self._last_renderer, '_archive_current_journeys'):
                self._last_renderer._archive_current_journeys()

            # Then copy all history to the new renderer
            if hasattr(self._last_renderer, '_agent_history'):
                for agent, journeys in self._last_renderer._agent_history.items():
                    event_handler.renderer._agent_history[agent] = journeys.copy()

        # Store reference for keyboard shortcuts (G, ESC)
        self._event_handler = event_handler

        # Set up clarification callback so modal can be shown from events
        # @work runs on the main thread, so we can call methods directly
        event_handler.set_clarification_callback(self.show_clarification_modal)

        # Lock configuration during workflow
        self._lock_config()

        logger = _get_logger()

        try:
            current_time = datetime.now().strftime("%H:%M")
            system_messages.write(Text(f"[{current_time}]  Starting workflow...", style="dim"))

            # Log query start (truncate long queries)
            query_preview = question[:100] + "..." if len(question) > 100 else question
            logger.info(f"Workflow started: mode={self.mode}, provider={self.provider}, experts={self.experts}, query='{query_preview}'")

            # Determine expert configuration
            expert_config = "default"
            if self.experts == "custom" and self.custom_experts:
                expert_config = ",".join(self.custom_experts)
            elif self.experts and self.experts != "default":
                expert_config = self.experts

            # Prepare attachments - pass the actual attachment objects, not just paths
            attachment_list = self.attachments if self.attachments else None

            # Create workflow with TUI event handler
            workflow = ConsensusWorkflow(
                max_iterations=self.max_iterations,
                consensus_threshold=self.consensus_threshold,
                mode=self.mode,
                provider=self.provider if self.mode == "single" else None,
                expert_config=expert_config,
                memory_manager=self.memory_persistence.memory_manager,
                event_listener=event_handler  # TUI receives events directly!
            )

            # Store clarification handler reference so callbacks can reach it
            self._clarification_handler = workflow.clarification_handler

            import time
            start_time = time.time()

            try:
                # Run workflow - events flow to TUIEventHandler automatically
                result = await workflow.solve_problem(question, attachment_list)

                # Store result for copy functionality
                self._last_result = result

                elapsed = time.time() - start_time
                logger.info(f"Workflow completed successfully in {elapsed:.1f}s")

                # Auto-copy solution to clipboard
                from src.cli import copy_to_clipboard
                if copy_to_clipboard(result.final_solution):
                    system_messages.write("[green]✓ Solution copied to clipboard[/green] [dim](Y to copy again)[/dim]")

                # Record successful query for quota tracking
                quota_status = record_query()
                system_messages.write(
                    f"[dim]Queries remaining: {quota_status.remaining_today} today, "
                    f"{quota_status.remaining_this_hour} this hour[/dim]"
                )

                # Save session state after successful query
                self.memory_persistence.save_state()
                logger.debug("Session state saved")
                self._update_memory_display()

                # Save markdown if enabled
                if self.markdown and result:
                    try:
                        from src.utils.markdown_output import generate_document, slugify_query
                        from src.core.paths import get_outputs_dir

                        outputs_dir = get_outputs_dir()

                        # First query creates file, follow-ups append
                        if not hasattr(self, '_markdown_path') or not self._markdown_path:
                            slug = slugify_query(question)
                            self._markdown_path = str(outputs_dir / f"{slug}.md")
                            saved_path = generate_document(result, self._markdown_path, append=False)
                            system_messages.write(f"[bold green]📝 Saved:[/bold green] [dim]{saved_path}[/dim]")
                            logger.info(f"Output saved to {saved_path}")
                        else:
                            saved_path = generate_document(result, self._markdown_path, append=True)
                            system_messages.write(f"[bold green]📝 Appended:[/bold green] [dim]{saved_path}[/dim]")
                            logger.info(f"Output appended to {saved_path}")
                    except Exception as e:
                        system_messages.write(f"[yellow]⚠️ Markdown save failed: {e}[/yellow]")
                        logger.error(f"Markdown save failed: {e}")

            finally:
                # Cleanup workflow resources
                try:
                    await workflow.close()
                except Exception:
                    pass

        except asyncio.CancelledError:
            system_messages.write(Text(" Workflow cancelled", style="yellow"))
            logger.warning("Workflow cancelled by user")
        except Exception as e:
            # Show error with traceback
            error_msg = str(e)
            system_messages.write(Text(f" Error: {error_msg}", style="bold red"))
            tb = traceback.format_exc()
            system_messages.write(Text(tb, style="dim red"))
            logger.error(f"Workflow failed: {error_msg}\n{tb}")

        finally:
            # Preserve renderer for detail pane access after workflow completes
            if self._event_handler and hasattr(self._event_handler, 'renderer'):
                self._last_renderer = self._event_handler.renderer
            self._event_handler = None
            self._unlock_config()
            self.reset_send_button()

    @work(exclusive=True)
    async def _do_compact_memory(self) -> None:
        """Async worker for memory compaction"""
        system_messages = self.query_one("#system-messages", RichLog)

        try:
            result = await self.memory_persistence.compact_memory()

            if result is None:
                system_messages.write("[yellow] Compaction returned no result[/yellow]")
                return

            if "No compaction needed" in result:
                system_messages.write("[dim] No compaction needed - memory is small enough[/dim]")
            elif "Compacted" in result:
                numbers = re.findall(r'\d+', result)
                if len(numbers) >= 2:
                    compacted_count = numbers[0]
                    kept_count = numbers[1]
                    system_messages.write(f"[bold green] Compacted {compacted_count} messages into intelligent summary[/bold green]")
                    system_messages.write(f"[dim]   Kept {kept_count} recent messages for immediate context[/dim]")
                else:
                    system_messages.write(f"[bold green] {result}[/bold green]")
            else:
                system_messages.write(f"[bold cyan] Memory:[/bold cyan] {result}")

        except asyncio.CancelledError:
            system_messages.write("[yellow] Compaction cancelled[/yellow]")
        except Exception as e:
            system_messages.write(f"[red] Compaction failed: {str(e)}[/red]")
            system_messages.write("[dim]   Try again or continue without compaction[/dim]")

        self._update_memory_display()

    @work(exclusive=True)
    async def _do_new_session(self) -> None:
        """Async worker for new session creation"""
        system_messages = self.query_one("#system-messages", RichLog)

        try:
            await self.memory_persistence.clear_session()
        except Exception as e:
            system_messages.write(f"[red]Error clearing session: {e}[/red]")

        from src.memory.memory_persistence import MemoryPersistence
        self.memory_persistence = MemoryPersistence()
        self._update_memory_display()

        # Clear the workflow view and reset run counter
        workflow_view = self.query_one("#workflow-view", WorkflowView)
        workflow_view.clear()

        # Reset the global run counter for fresh IDs
        from tui.workflow_renderer import WorkflowRenderer
        WorkflowRenderer._global_run_counter = 0

        # Reset markdown path for new session
        self._markdown_path = None

        # Clear system messages
        system_messages.clear()

        # Reset status header
        status_header = self.query_one("#status-header", StatusHeader)
        status_header.set_workflow_active(False)

        input_widget = self.query_one("#chat-input", TextArea)
        input_widget.clear()

        self.reset_send_button()
        input_widget.focus()

        system_messages.write("[dim] New session started[/dim]")
