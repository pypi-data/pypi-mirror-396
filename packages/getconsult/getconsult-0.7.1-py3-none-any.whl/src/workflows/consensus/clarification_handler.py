"""
Clarification Handler for orchestrating the clarification flow.

This component integrates with ConsensusWorkflow to pause execution,
emit clarification questions to the TUI, and resume with enhanced context.
"""

import asyncio
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from ..base.events import EventEmitter, EventTypes
from ...agents.clarifier_agent import ClarifierAgent, ClarificationResult
from ...config import ProviderType
from ...core.paths import get_logs_dir
from ...core.security import get_contextual_logger

if TYPE_CHECKING:
    from ...memory.memory_manager import MemoryManager

# Module logger
_logger = None


def _get_logger():
    """Get or create the clarification handler logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.clarify", log_file=str(log_file))
    return _logger


class ClarificationHandler:
    """Orchestrates the clarification flow within a workflow"""

    def __init__(
        self,
        emitter: EventEmitter,
        provider: ProviderType = "anthropic",
        memory_manager: Optional["MemoryManager"] = None
    ):
        """Initialize clarification handler

        Args:
            emitter: Event emitter for workflow events
            provider: Provider to use for clarifier agent
            memory_manager: Optional memory manager for context
        """
        self.emitter = emitter
        self.provider = provider
        self.memory_manager = memory_manager
        self.logger = _get_logger()

        # Async coordination
        self._response_event = asyncio.Event()
        self._user_responses: Dict[str, Any] = {}
        self._skipped = False

        # Clarifier agent (lazy initialization)
        self._clarifier: Optional[ClarifierAgent] = None

    def _get_clarifier(self) -> ClarifierAgent:
        """Get or create the clarifier agent"""
        if self._clarifier is None:
            self._clarifier = ClarifierAgent(provider=self.provider)
        return self._clarifier

    async def maybe_clarify(self, query: str, attachments: Optional[List[str]] = None) -> str:
        """Analyze query and optionally get clarification from user

        This method:
        1. Analyzes the query for ambiguity
        2. If clarification needed, emits CLARIFICATION_NEEDED event
        3. Waits for user response (or skip)
        4. Returns enhanced query with clarifications incorporated

        Args:
            query: The original user query
            attachments: Optional list of attachment file paths

        Returns:
            Enhanced query with clarifications, or original if none needed/skipped
        """
        # Reset state for new clarification
        self._response_event.clear()
        self._user_responses = {}
        self._skipped = False

        query_preview = query[:80] + '...' if len(query) > 80 else query
        self.logger.info(f"Clarification check starting | query='{query_preview}'")

        # Get memory context if available
        context = None
        if self.memory_manager:
            try:
                memory_context = self.memory_manager.get_context()
                if memory_context:
                    context = self.memory_manager.format_context_for_prompt(memory_context)
            except Exception:
                pass  # Continue without memory context

        # Add attachment info to context so clarifier knows files are attached
        if attachments:
            import os
            attachment_info = "ATTACHED FILES:\n"
            for attachment in attachments:
                # Handle both attachment objects and string paths
                if hasattr(attachment, 'metadata') and hasattr(attachment.metadata, 'filename'):
                    filename = attachment.metadata.filename
                elif hasattr(attachment, 'original_path'):
                    filename = os.path.basename(attachment.original_path)
                elif isinstance(attachment, str):
                    filename = os.path.basename(attachment)
                else:
                    filename = str(attachment)
                attachment_info += f"- {filename}\n"
            attachment_info += "\nNote: The user has attached the above file(s) for analysis.\n"
            if context:
                context = attachment_info + "\n" + context
            else:
                context = attachment_info

        # Emit analyzing event so UI can show feedback
        self.emitter.emit(
            EventTypes.CLARIFICATION_ANALYZING,
            query=query
        )

        # Analyze the query
        try:
            clarifier = self._get_clarifier()
            result = await clarifier.analyze_query(query, context)
        except Exception as e:
            # On error, don't block - continue with original query
            self.logger.error(f"Clarification analysis FAILED | error={type(e).__name__}: {e}")
            self.emitter.emit(
                EventTypes.WORKFLOW_ERROR,
                error=f"Clarification analysis failed: {e}",
                recoverable=True
            )
            return query

        # If no clarification needed, return original
        if not result.needs_clarification or not result.questions:
            self.logger.info("Clarification not needed | query is clear")
            return query

        # Emit clarification needed event with questions
        questions_data = [
            {
                "question": q.question,
                "options": q.options,
                "multi_select": q.multi_select
            }
            for q in result.questions
        ]

        question_texts = [q.question for q in result.questions]
        self.logger.info(f"Clarification NEEDED | {len(result.questions)} questions: {question_texts}")

        self.emitter.emit(
            EventTypes.CLARIFICATION_NEEDED,
            questions=questions_data,
            reasoning=result.reasoning,
            original_query=query
        )

        # Wait for user response
        self.logger.info("Waiting for user response (300s timeout)")
        try:
            await asyncio.wait_for(self._response_event.wait(), timeout=300.0)  # 5 min timeout
        except asyncio.TimeoutError:
            # Timeout - continue with original query
            self.logger.warning("Clarification TIMEOUT after 300s | continuing with original query")
            self.emitter.emit(
                EventTypes.CLARIFICATION_SKIPPED,
                reason="timeout"
            )
            return query

        # Check if user skipped
        if self._skipped:
            self.logger.info("Clarification SKIPPED by user")
            self.emitter.emit(
                EventTypes.CLARIFICATION_SKIPPED,
                reason="user_skipped"
            )
            return query

        # Format enhanced query with responses
        self.logger.info(f"Clarification responses received | {len(self._user_responses)} answers")
        clarifier = self._get_clarifier()
        enhanced_query = clarifier.format_enhanced_query(query, self._user_responses)

        # Emit response event
        self.emitter.emit(
            EventTypes.CLARIFICATION_RESPONSE,
            responses=self._user_responses,
            enhanced_query=enhanced_query
        )

        self.logger.debug(f"Enhanced query: {enhanced_query[:100]}...")
        return enhanced_query

    def receive_response(self, responses: Dict[str, Any]) -> None:
        """Receive user responses to clarification questions

        Called by TUI when user submits answers.

        Args:
            responses: Dict mapping question text to user's answer(s)
        """
        self._user_responses = responses
        self._skipped = False
        self._response_event.set()

    def skip_clarification(self) -> None:
        """User chose to skip clarification

        Called by TUI when user presses Escape.
        """
        self._skipped = True
        self._response_event.set()
