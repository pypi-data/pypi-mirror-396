"""
AI-powered conversation compaction agent for intelligent memory management.
Similar to Claude Code's compaction system.
"""

from typing import List, Dict, Any
from autogen_agentchat.agents import AssistantAgent
from ..agents.agents import create_model_client


class ConversationCompactor:
    """AI-powered conversation compaction system."""
    
    def __init__(self):
        """Initialize the compaction agent."""
        self.model_client = create_model_client()
        self.compactor_agent = self._create_compactor_agent()
    
    def _create_compactor_agent(self) -> AssistantAgent:
        """Create the specialized compaction agent."""
        from ..prompts.prompts import Prompts
        
        return AssistantAgent(
            name="conversation_compactor",
            model_client=self.model_client,
            description="Intelligent conversation summarization specialist",
            system_message=Prompts.get_compaction_agent_system_message()
        )
    
    async def compact_conversation(self, 
                                 original_question: str,
                                 conversation_history: List[Dict[str, Any]],
                                 final_solution: str = None) -> str:
        """
        Intelligently compact a conversation using AI.
        
        Args:
            original_question: The user's original question
            conversation_history: List of conversation messages to compact
            final_solution: The final solution if available
            
        Returns:
            AI-generated intelligent summary
        """
        # Prepare the conversation for compaction
        conversation_text = self._format_conversation_for_compaction(
            original_question, conversation_history, final_solution
        )
        
        # Create compaction prompt
        compaction_prompt = f"""Please compact this expert conversation intelligently:

{conversation_text}

Generate a comprehensive but concise summary that preserves all key information while reducing verbosity. Focus on decisions, recommendations, and context that might be referenced in future questions."""

        try:
            # Get AI-powered summary
            from ..workflows.base.agent_communicator import AgentCommunicator
            communicator = AgentCommunicator()
            
            summary = await communicator.get_response(
                self.compactor_agent, 
                compaction_prompt,
                max_messages=3
            )
            
            return summary
            
        except Exception as e:
            # Fallback to basic summary if AI fails
            return self._create_fallback_summary(original_question, conversation_history, final_solution)
    
    def _format_conversation_for_compaction(self, 
                                          original_question: str,
                                          conversation_history: List[Dict[str, Any]], 
                                          final_solution: str = None) -> str:
        """Format conversation history for AI compaction."""
        
        parts = [f"ORIGINAL QUESTION: {original_question}"]
        parts.append("")
        parts.append("EXPERT DISCUSSION:")
        
        # Group by expert and conversation flow
        current_discussion = []
        for msg in conversation_history:
            expert = msg.get("expert", "Unknown")
            message = msg.get("message", "")
            msg_type = msg.get("type", "discussion")
            
            if expert == "USER":
                parts.append(f"\nUSER FOLLOW-UP: {message}")
            elif expert == "SYSTEM" and msg_type == "final_solution":
                parts.append(f"\nFINAL SOLUTION: {message[:500]}...")
            elif expert != "SYSTEM":
                # Truncate very long messages but keep key parts
                if len(message) > 1000:
                    message = message[:800] + "... [truncated]"
                parts.append(f"\n{expert}: {message}")
        
        if final_solution:
            parts.append(f"\nFINAL AGREED SOLUTION: {final_solution[:500]}...")
            
        return "\n".join(parts)
    
    def _create_fallback_summary(self, 
                                original_question: str,
                                conversation_history: List[Dict[str, Any]],
                                final_solution: str = None) -> str:
        """Create a fallback summary if AI compaction fails."""
        
        # Count expert contributions
        expert_counts = {}
        key_insights = []
        
        for msg in conversation_history:
            expert = msg.get("expert", "Unknown")
            message = msg.get("message", "")
            
            if expert != "SYSTEM" and expert != "USER":
                expert_counts[expert] = expert_counts.get(expert, 0) + 1
                
                # Extract first sentence as key insight
                first_sentence = message.split('.')[0]
                if len(first_sentence) > 20 and len(first_sentence) < 200:
                    key_insights.append(f"- {expert}: {first_sentence}")
        
        summary_parts = [
            "## Conversation Summary",
            f"**Original Question**: {original_question}",
            "",
            "**Key Expert Insights**:",
        ]
        
        summary_parts.extend(key_insights[:5])  # Top 5 insights
        
        if final_solution:
            summary_parts.extend([
                "",
                f"**Final Solution**: {final_solution[:300]}..."
            ])
        
        summary_parts.extend([
            "",
            f"**Experts Consulted**: {', '.join(expert_counts.keys())}",
            f"**Total Messages Compacted**: {len(conversation_history)}"
        ])
        
        return "\n".join(summary_parts)