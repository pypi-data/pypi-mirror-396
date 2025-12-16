"""Memory persistence layer for maintaining context across subprocess calls.

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime, timezone
from .memory_manager import MemoryManager
from src.core.paths import get_sessions_dir
from src.core.identity import generate_session_id, get_timestamp, get_iso_timestamp
from src.core.license import get_license_manager
from src.core.security import redact_secrets


class MemoryPersistence:
    """Handles saving and loading memory state to disk for TUI continuity.

    Sessions are stored in ~/.consult/sessions/ with traceable filenames.
    """

    def __init__(self, session_file: Optional[str] = None, user_id: Optional[str] = None):
        """Initialize memory persistence.

        Args:
            session_file: Path to session file. If None, creates new session in ~/.consult/sessions/
            user_id: User ID for session tracking. If None, uses license manager.
        """
        self._user_id = user_id or get_license_manager().get_user_id()
        self._session_id = generate_session_id()

        if session_file:
            self.session_file = Path(session_file)
        else:
            # Use ~/.consult/sessions/ with traceable filename
            sessions_dir = get_sessions_dir()
            filename = f"session_{get_timestamp()}_u{self._user_id}_s{self._session_id}.json"
            self.session_file = sessions_dir / filename

        self.memory_manager = MemoryManager()

    @property
    def user_id(self) -> str:
        """Get user ID for this session."""
        return self._user_id

    @property
    def session_id(self) -> str:
        """Get session ID."""
        return self._session_id
        
    def save_state(self) -> None:
        """Save current memory state to disk.

        Session files include metadata for traceability and never contain API keys.
        """
        from src import __version__
        from src.core.license import get_current_tier

        state = {
            # Metadata for traceability
            "meta": {
                "user_id": self._user_id,
                "session_id": self._session_id,
                "created_at": get_iso_timestamp(),
                "updated_at": get_iso_timestamp(),
                "tier": get_current_tier().value,
                "version": __version__,
            },
            # Memory state
            "memory": {
                "original_question": self.memory_manager.original_question,
                "final_solution": self.memory_manager.final_solution,
                "conversation_history": self.memory_manager.conversation_history,
                "is_compacted": self.memory_manager.is_compacted,
                "compaction_summary": self.memory_manager.compaction_summary,
                "conversation_count": self.memory_manager.conversation_count,
            },
            # Legacy field for backward compatibility
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Redact any secrets before saving
        state_json = json.dumps(state, indent=2)
        state_json = redact_secrets(state_json)

        with open(self.session_file, 'w') as f:
            f.write(state_json)
            
    def load_state(self) -> bool:
        """Load memory state from disk.

        Supports both new format (with meta/memory structure) and legacy format.

        Returns:
            True if state was loaded, False if no state file exists.
        """
        if not self.session_file.exists():
            return False

        try:
            with open(self.session_file, 'r') as f:
                state = json.load(f)

            # Handle new format with meta/memory structure
            if "memory" in state and "meta" in state:
                memory = state["memory"]
                meta = state["meta"]
                # Restore user/session IDs from file
                if meta.get("user_id"):
                    self._user_id = meta["user_id"]
                if meta.get("session_id"):
                    self._session_id = meta["session_id"]
            else:
                # Legacy format - memory fields at top level
                memory = state

            self.memory_manager.original_question = memory.get("original_question")
            self.memory_manager.final_solution = memory.get("final_solution")
            self.memory_manager.conversation_history = memory.get("conversation_history", [])
            self.memory_manager.is_compacted = memory.get("is_compacted", False)
            self.memory_manager.compaction_summary = memory.get("compaction_summary")
            self.memory_manager.conversation_count = memory.get("conversation_count", 0)

            return True
        except Exception as e:
            print(f"Error loading memory state: {e}")
            return False
            
    async def add_question(self, question: str) -> None:
        """Add question and save state."""
        await self.memory_manager.add_question(question)
        self.save_state()
        
    async def add_solution(self, solution: str) -> None:
        """Add solution and save state."""
        await self.memory_manager.add_solution(solution)
        self.save_state()
        
    async def add_conversation(self, expert_name: str, message: str, message_type: str = "discussion") -> None:
        """Add conversation and save state."""
        await self.memory_manager.add_conversation(expert_name, message, message_type)
        self.save_state()
        
    async def compact_memory(self) -> str:
        """Compact memory and save state."""
        result = await self.memory_manager.compact_memory()
        self.save_state()
        return result
        
    async def get_expert_context(self) -> Dict[str, Any]:
        """Get expert context from memory."""
        return await self.memory_manager.get_expert_context()
        
    def get_memory_usage(self) -> float:
        """Get memory usage percentage."""
        return self.memory_manager.get_memory_usage()
        
    async def clear_session(self) -> None:
        """Clear current session and delete session file."""
        await self.memory_manager.clear()
        if self.session_file.exists():
            self.session_file.unlink()
            
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about current session."""
        return {
            "session_file": str(self.session_file),
            "has_context": self.memory_manager.final_solution is not None,
            "is_compacted": self.memory_manager.is_compacted,
            "memory_usage": self.get_memory_usage(),
            "conversation_count": self.memory_manager.conversation_count
        }