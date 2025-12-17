"""Memory management system for maintaining context across expert conversations."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType, MemoryQueryResult
import json


class MemoryManager:
    """Manages conversation memory with compaction support."""
    
    def __init__(self, compaction_threshold: int = 10, retention_count: int = 5):
        """Initialize the memory manager.
        
        Args:
            compaction_threshold: Number of conversation messages before auto-compaction
            retention_count: Number of recent messages to keep after compaction
        """
        self.memory = ListMemory()
        self.original_question: Optional[str] = None
        self.final_solution: Optional[str] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.compaction_threshold = compaction_threshold
        self.retention_count = retention_count
        self.conversation_count = 0
        self.is_compacted = False
        self.compaction_summary: Optional[str] = None
        
    async def add_question(self, question: str) -> None:
        """Store the original user question.
        
        Args:
            question: The user's original question
        """
        # Only store as original if we don't have one yet
        if self.original_question is None:
            self.original_question = question
            
            # Also add to memory for persistence
            content = MemoryContent(
                content=f"ORIGINAL_QUESTION: {question}",
                mime_type=MemoryMimeType.TEXT,
                metadata={"type": "original_question", "timestamp": datetime.now().isoformat()}
            )
            await self.memory.add(content)
        else:
            # This is a follow-up question, add it to conversation history
            await self.add_conversation("USER", question, "follow_up_question")
        
    async def add_solution(self, solution: str) -> None:
        """Store the final solution presented to the user.
        
        Args:
            solution: The final solution/answer
        """
        # Store the latest solution
        self.final_solution = solution
        
        # Add to conversation history for tracking
        await self.add_conversation("SYSTEM", f"Final Solution: {solution[:500]}...", "final_solution")
        
        # Add to memory
        content = MemoryContent(
            content=f"FINAL_SOLUTION: {solution}",
            mime_type=MemoryMimeType.TEXT,
            metadata={"type": "final_solution", "timestamp": datetime.now().isoformat()}
        )
        await self.memory.add(content)
        
    async def add_conversation(self, expert_name: str, message: str, message_type: str = "discussion") -> None:
        """Add a conversation message to history.
        
        Args:
            expert_name: Name of the expert
            message: The conversation message
            message_type: Type of message (discussion, consensus, etc.)
        """
        conversation_entry = {
            "expert": expert_name,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history.append(conversation_entry)
        self.conversation_count += 1
        
        # Add to memory
        content = MemoryContent(
            content=f"[{expert_name}]: {message}",
            mime_type=MemoryMimeType.TEXT,
            metadata=conversation_entry
        )
        await self.memory.add(content)
        
        # Check if we need to auto-compact
        if len(self.conversation_history) > self.compaction_threshold:
            await self.compact_memory()
            
    async def compact_memory(self) -> str:
        """Compact the conversation history to reduce size.
        
        Returns:
            Summary of the compaction operation
        """
        if len(self.conversation_history) <= self.retention_count:
            return "No compaction needed - history is small enough"
            
        # Get messages to summarize (all except recent ones)
        to_summarize = self.conversation_history[:-self.retention_count]
        recent_messages = self.conversation_history[-self.retention_count:]
        
        # Create a summary of older conversations
        summary = await self._create_summary(to_summarize)
        
        # Store the summary
        self.compaction_summary = summary
        self.is_compacted = True
        
        # Replace history with summary entry + recent messages
        summary_entry = {
            "expert": "SYSTEM",
            "message": f"[COMPACTED SUMMARY of {len(to_summarize)} messages]: {summary}",
            "type": "compaction",
            "timestamp": datetime.now().isoformat(),
            "compacted_count": len(to_summarize)
        }
        
        self.conversation_history = [summary_entry] + recent_messages
        
        # Update conversation count to reflect new reality
        self.conversation_count = len(self.conversation_history)
        
        return f"Compacted {len(to_summarize)} messages into summary. Kept {len(recent_messages)} recent messages."
        
    async def _create_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Create an AI-powered intelligent summary of conversation messages.
        
        Args:
            messages: List of messages to summarize
            
        Returns:
            A comprehensive AI-generated summary
        """
        try:
            # Use AI-powered compaction
            from .compaction_agent import ConversationCompactor
            compactor = ConversationCompactor()
            
            # Get intelligent summary
            summary = await compactor.compact_conversation(
                original_question=self.original_question or "Unknown question",
                conversation_history=messages,
                final_solution=self.final_solution
            )
            
            return summary
            
        except Exception as e:
            # Fallback to simple summary if AI compaction fails
            return self._create_fallback_summary(messages)
    
    def _create_fallback_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Fallback summary method if AI compaction fails."""
        # Group messages by expert
        expert_contributions = {}
        for msg in messages:
            expert = msg.get("expert", "Unknown")
            if expert not in expert_contributions:
                expert_contributions[expert] = []
            expert_contributions[expert].append(msg.get("message", ""))
            
        # Create summary
        summary_parts = []
        for expert, contributions in expert_contributions.items():
            if contributions:
                # Take first and last contribution from each expert as summary
                if len(contributions) > 2:
                    summary_parts.append(f"{expert} discussed: {contributions[0][:100]}... and concluded with: {contributions[-1][:100]}")
                else:
                    summary_parts.append(f"{expert}: {contributions[0][:200]}")
                    
        return " | ".join(summary_parts)
        
    async def get_expert_context(self) -> Dict[str, Any]:
        """Get the memory context for experts.
        
        Returns:
            Dictionary containing relevant memory context
        """
        context = {
            "original_question": self.original_question,
            "final_solution": self.final_solution,
            "is_follow_up": self.final_solution is not None,
            "conversation_summary": None,
            "recent_discussions": []
        }
        
        # Add conversation context
        if self.is_compacted and self.compaction_summary:
            context["conversation_summary"] = self.compaction_summary
            
        # Add recent discussions (last 3 non-system messages)
        recent = [msg for msg in self.conversation_history[-5:] 
                  if msg.get("expert") != "SYSTEM"][-3:]
        context["recent_discussions"] = recent
        
        return context
        
    def get_memory_usage(self) -> float:
        """Get the current memory usage as a percentage.
        
        Returns:
            Percentage of memory used (0-100)
        """
        # Estimate based on conversation count vs threshold
        current = len(self.conversation_history)
        return min(100.0, (current / self.compaction_threshold) * 100)
        
    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format memory context for inclusion in expert prompts.
        
        Args:
            context: The memory context dictionary
            
        Returns:
            Formatted string for prompt inclusion
        """
        parts = []
        
        if context.get("is_follow_up"):
            parts.append("=== CONTINUING CONVERSATION ===")
            parts.append("You are continuing a conversation. The user has already asked questions and received answers.")
            parts.append("")
            
            if context.get("original_question"):
                parts.append(f"ORIGINAL QUESTION: {context['original_question']}")
                parts.append("")
                
            if context.get("final_solution"):
                parts.append("PREVIOUS SOLUTION PROVIDED:")
                parts.append(context['final_solution'][:1000])
                if len(context['final_solution']) > 1000:
                    parts.append("...")
                parts.append("")
                
            if context.get("conversation_summary"):
                parts.append("CONVERSATION SUMMARY:")
                parts.append(context['conversation_summary'])
                parts.append("")
                
            # Look for follow-up questions in recent discussions
            if context.get("recent_discussions"):
                follow_ups = [d for d in context["recent_discussions"] if d.get("type") == "follow_up_question"]
                if follow_ups:
                    parts.append("USER'S FOLLOW-UP QUESTIONS:")
                    for q in follow_ups:
                        parts.append(f"  - {q.get('message', '')}")
                    parts.append("")
                    
            parts.append("IMPORTANT: Consider the above context when answering. Reference the previous solution if relevant.")
            parts.append("=== END CONTEXT ===\n")
            
        return "\n".join(parts) if parts else ""
        
    async def clear(self) -> None:
        """Clear all memory."""
        await self.memory.clear()
        self.original_question = None
        self.final_solution = None
        self.conversation_history = []
        self.conversation_count = 0
        self.is_compacted = False
        self.compaction_summary = None
        
    async def query_memory(self, query: str) -> List[str]:
        """Query the memory for specific information.
        
        Args:
            query: Search query
            
        Returns:
            List of relevant memory entries
        """
        result = await self.memory.query(query)
        
        if isinstance(result, MemoryQueryResult):
            return [content.content for content in result.results]
        return []