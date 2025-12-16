"""
Refactored Consensus workflow using specialized components
Maintains exact same interface as original ConsensusWorkflow
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent

from ...agents.agents import (
    create_expert_agents, create_model_client,
    create_team_expert_agents,
    create_model_client_for_provider
)
from ...agents.orchestrator_factory import OrchestratorFactory
from ...agents.agents import ResponseFormats
from ...prompts.prompts import Prompts
from ...config import ModeType, ProviderType
from ...ui.display import ConsoleDisplay
from ...models.responses import WorkflowResult
from ...agents.presentation_agent import create_presentation_agent
from ...agents.distinguished_engineer import create_meta_reviewer
from ...core.paths import get_logs_dir
from ...core.security import get_contextual_logger, set_query_id, clear_query_id
import uuid

# Specialized components
from ..base.workflow_state import WorkflowState
from ..base.agent_communicator import AgentCommunicator
from ..base.workflow_constants import WorkflowConstants
from ..base.response_parser import ResponseParser
from ..base.events import EventEmitter, EventTypes, EventListener
from .workflow_orchestrator import WorkflowOrchestrator
from .clarification_handler import ClarificationHandler

# Module logger
_logger = None


def _get_logger():
    """Get or create the workflow logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.workflow", log_file=str(log_file))
    return _logger


class ConsensusWorkflow:
    """Consensus workflow using specialized components - maintains original interface"""

    def __init__(self, max_iterations: int = 1, consensus_threshold: float = 0.8,
                 mode: ModeType = "single", provider: Optional[ProviderType] = None, expert_config: str = "default",
                 memory_manager=None, event_listener: Optional[EventListener] = None):
        self.max_iterations = max_iterations
        self.consensus_threshold = consensus_threshold
        self.mode = mode
        self.provider = provider
        self.expert_config = expert_config
        self.memory_manager = memory_manager
        self.logger = _get_logger()

        self.logger.info(f"Workflow init | mode={mode}, provider={provider}, experts={expert_config}, "
                        f"max_iter={max_iterations}, threshold={consensus_threshold}")

        # Initialize event emitter with optional listener
        self.emitter = EventEmitter()

        # Initialize display (which is also a listener)
        self.display = ConsoleDisplay()
        self.emitter.add_listener(self.display)

        # Add custom listener if provided (e.g., TUI handler)
        if event_listener:
            self.emitter.add_listener(event_listener)

        # Initialize core components
        self.state = WorkflowState()
        self.communicator = AgentCommunicator()
        self.presentation_agent = create_presentation_agent()

        # Create Meta Reviewer (uses SOTA model)
        # Cross-cutting review across all expert perspectives
        self.meta_reviewer = create_meta_reviewer()

        # Initialize workflow orchestrator with emitter and meta reviewer
        self.orchestrator_component = WorkflowOrchestrator(
            self.communicator, self.emitter, memory_manager,
            meta_reviewer=self.meta_reviewer
        )

        # Initialize clarification handler
        self.clarification_handler = ClarificationHandler(
            emitter=self.emitter,
            provider=provider or "anthropic",
            memory_manager=memory_manager
        )
        
        # Don't get memory context during init - will get it when solving problem
        memory_context = None
        
        # Create agents based on mode with memory context
        if mode == "single":
            # Parse expert configuration - could be set name or comma-separated list
            if "," in expert_config:
                expert_types = [name.strip() for name in expert_config.split(",")]
                self.expert_agents = create_expert_agents(
                    expert_types=expert_types, 
                    provider=provider,
                    memory_context=memory_context
                )
            else:
                self.expert_agents = create_expert_agents(
                    expert_set=expert_config, 
                    provider=provider,
                    memory_context=memory_context
                )
            self.orchestrator = OrchestratorFactory.create_single_mode_orchestrator()
            self.teams = None  # No teams in single mode
            self.logger.info(f"Single mode | {len(self.expert_agents)} experts: {[a.name for a in self.expert_agents]}")
        elif mode == "team":
            # Parse expert configuration - could be set name or comma-separated list
            if "," in expert_config:
                expert_types = [name.strip() for name in expert_config.split(",")]
                self.teams = create_team_expert_agents(expert_types=expert_types)
            else:
                self.teams = create_team_expert_agents(expert_set=expert_config)
            # Flatten teams into expert_agents list for workflow compatibility
            self.expert_agents = []
            for team_name, team_agents in self.teams.items():
                self.expert_agents.extend(team_agents)
            self.orchestrator = OrchestratorFactory.create_team_mode_orchestrator()
            self.logger.info(f"Team mode | {len(self.teams)} teams, {len(self.expert_agents)} total experts: {list(self.teams.keys())}")
        else:
            self.logger.error(f"Unknown mode: {mode}")
            raise ValueError(f"Unknown mode: {mode}")
    
    async def solve_problem(self, problem: str, attachments: Optional[List] = None) -> WorkflowResult:
        """Main consensus-building workflow - delegated to orchestrator component"""
        from ...models.attachments import AttachmentManager, Attachment

        # Generate unique query ID for this workflow run
        query_id = uuid.uuid4().hex[:6]
        set_query_id(query_id)

        self.state.start_time = time.time()
        problem_preview = problem[:100] + '...' if len(problem) > 100 else problem
        self.logger.info(f"=== WORKFLOW START === query='{problem_preview}'")

        # Prepare attachments for the current provider using AttachmentManager
        # This centralizes provider-specific handling (native PDF vs image conversion)
        if attachments:
            provider = self.provider or "anthropic"  # Default to anthropic for team mode
            attachment_manager = AttachmentManager(provider)
            for att in attachments:
                if isinstance(att, Attachment):
                    attachment_manager.add_attachment(att)
                else:
                    # Handle legacy path strings
                    attachment_manager.add_attachment(att)
            # Get provider-ready attachments (PDFs converted for OpenAI, native for others)
            prepared_attachments = attachment_manager.prepare_for_provider()
            self.state.attachments = prepared_attachments
            self.logger.info(f"Attachments prepared | {len(prepared_attachments)} files for {provider}")
        else:
            self.state.attachments = []

        # Phase 0: Clarification - analyze query for ambiguity
        # Pass original attachments so clarifier knows what files are attached
        self.logger.debug("Phase 0: Clarification check")
        enhanced_problem = await self.clarification_handler.maybe_clarify(problem, attachments)

        # Handle memory context updates if needed (use enhanced problem)
        await self._update_memory_context_if_needed(enhanced_problem)

        # Emit workflow start event (use enhanced problem for display)
        self.emitter.emit(
            EventTypes.WORKFLOW_START,
            problem=enhanced_problem,
            agents=[a.name for a in self.expert_agents],
            consensus_threshold=self.consensus_threshold,
            max_iterations=self.max_iterations,
            mode=self.mode,
            teams=list(self.teams.keys()) if self.teams else None,
            provider=self.provider
        )

        # Delegate main workflow to orchestrator component (use enhanced problem)
        self.logger.info("Starting consensus phases")
        final_solution, resolution_method, orchestrator_rounds = await self.orchestrator_component.run_consensus_phases(
            self.expert_agents, self.state, self.orchestrator, enhanced_problem,
            self.consensus_threshold, self.max_iterations
        )
        self.logger.info(f"Consensus phases complete | method={resolution_method}")

        # Handle orchestrator intervention if consensus wasn't reached
        if resolution_method == "orchestrator_authority":
            self.logger.info("Orchestrator intervention required")
            final_solution, resolution_method, orchestrator_rounds = await self._handle_orchestrator_intervention(enhanced_problem)
        
        # Create user-friendly presentation (use enhanced problem)
        if resolution_method == "democratic_consensus":
            solution_type = "consensus"
        else:
            solution_type = "orchestrator"

        user_friendly_solution = await self._create_user_friendly_presentation(enhanced_problem, final_solution, solution_type)
        
        # Store final solution in memory if available
        if self.memory_manager:
            await self.memory_manager.add_solution(user_friendly_solution)

        # Calculate duration and emit completion
        duration = time.time() - self.state.start_time
        consensus_reached = (resolution_method == "democratic_consensus")

        self.logger.info(f"=== WORKFLOW COMPLETE === duration={duration:.1f}s | iterations={self.state.iteration_count} | "
                        f"consensus={'YES' if consensus_reached else 'NO'} | method={resolution_method}")

        self.emitter.emit(
            EventTypes.WORKFLOW_COMPLETE,
            success=True,
            consensus_reached=consensus_reached,
            duration=duration,
            iterations=self.state.iteration_count,
            max_iterations=self.max_iterations,
            resolution_method=resolution_method
        )

        # Ensure all agent operations are complete before returning
        await asyncio.sleep(WorkflowConstants.CLEANUP_DELAY_SECONDS)

        # Clear query ID after workflow completes
        clear_query_id()

        return self._create_workflow_result(
            enhanced_problem, resolution_method, user_friendly_solution,
            consensus_reached, 0.0, orchestrator_rounds, duration
        )
    
    async def _update_memory_context_if_needed(self, problem: str):
        """Update expert agents with memory context if this is a follow-up conversation"""
        if self.memory_manager:
            # Get memory context BEFORE adding new question
            memory_context = await self.memory_manager.get_expert_context()
            
            # Store the new question (will be follow-up if context exists)
            await self.memory_manager.add_question(problem)
            
            # Recreate experts with memory context if this is a follow-up
            if memory_context.get("is_follow_up"):
                if self.mode == "single":
                    # Parse expert configuration
                    if "," in self.expert_config:
                        expert_types = [name.strip() for name in self.expert_config.split(",")]
                        self.expert_agents = create_expert_agents(
                            expert_types=expert_types, 
                            provider=self.provider,
                            memory_context=memory_context
                        )
                    else:
                        self.expert_agents = create_expert_agents(
                            expert_set=self.expert_config, 
                            provider=self.provider,
                            memory_context=memory_context
                        )
    
    async def _handle_orchestrator_intervention(self, problem: str) -> tuple:
        """Handle orchestrator intervention for unresolved consensus"""
        elapsed = time.time() - self.state.start_time

        # Emit orchestrator intervention event
        self.emitter.emit(
            EventTypes.ORCHESTRATOR_INTERVENTION,
            elapsed_seconds=elapsed,
            iterations=self.state.iteration_count
        )

        # Prepare expert solutions for orchestrator decision
        all_solutions = {
            name: data['answer']
            for name, data in self.state.current_solutions.items()
        }

        # Get Meta Reviewer feedback for orchestrator context
        meta_reviewer_feedback = self.state.get_all_meta_reviewer_feedback()

        # Use centralized orchestrator decision prompt
        final_decision_prompt = Prompts.orchestrator_decision_prompt(
            problem=problem,
            all_solutions=all_solutions,
            iterations=self.state.iteration_count,
            consensus_threshold=self.consensus_threshold,
            meta_reviewer_feedback=meta_reviewer_feedback if meta_reviewer_feedback else None
        )

        self.emitter.emit(
            EventTypes.AGENT_THINKING,
            agent_name="orchestrator",
            action="making final authoritative decision"
        )
        
        # Get orchestrator's final decision
        final_decision = await self.communicator.get_response(
            self.orchestrator, final_decision_prompt, max_messages=WorkflowConstants.AGENT_RESPONSE_TIMEOUT_MESSAGES
        )
        
        final_solution = f"""# 🎭 ORCHESTRATOR FINAL AUTHORITY

## Resolution Status
⚡ **Orchestrator final authority invoked**  
🔄 **Iterations attempted:** {self.state.iteration_count}  
👥 **Expert perspectives analyzed:** {len(self.expert_agents)}  
🎯 **Consensus threshold:** {self.consensus_threshold*100:.0f}%  

## Final Authoritative Decision

{final_decision}

## Resolution Summary
After attempting to facilitate democratic consensus, the orchestrator exercised final authority. This decision synthesizes all expert input with complete transparency about tradeoffs and rationale."""
        
        return final_solution, "orchestrator_authority", 1
    
    async def _create_user_friendly_presentation(self, original_problem: str, raw_solution: str, solution_type: str) -> str:
        """Create clean, user-friendly presentation of the final result.

        Note: Meta Reviewer feedback is NOT passed to presentation agent because
        experts have already refined their solutions incorporating that feedback.
        Presentation Agent synthesizes the final refined expert solutions.
        """

        # Get all expert solutions for comprehensive analysis
        expert_solutions = self.state.get_all_current_solutions_detailed()

        presentation_prompt = Prompts.presentation_summary_prompt(
            original_problem=original_problem,
            expert_solutions=expert_solutions,
            solution_type=solution_type,
            consensus_score=None,
            iterations=self.state.iteration_count
        )

        # Always show presentation agent progress - this is a long operation (10-30s typically)
        self.emitter.emit(
            EventTypes.AGENT_THINKING,
            agent_name="presentation_agent",
            action="synthesizing final comprehensive summary",
            estimated_seconds=20
        )

        user_friendly_result = await self.communicator.get_response(
            self.presentation_agent,
            presentation_prompt,
            max_messages=WorkflowConstants.AGENT_RESPONSE_TIMEOUT_MESSAGES
        )

        # Emit the final answer as an agent response for display
        self.emitter.emit(
            EventTypes.AGENT_RESPONSE,
            agent_name="presentation_agent",
            content=user_friendly_result,
            response_type="Final Answer"
        )

        return user_friendly_result
    
    def _create_workflow_result(self, problem: str, resolution_method: str, 
                              final_solution: str, consensus_achieved: bool,
                              consensus_score: float, orchestrator_rounds: int,
                              duration: float) -> WorkflowResult:
        """Create structured workflow result"""
        
        # Use clean state management
        expert_solutions = self.state.get_all_current_solutions()
        
        return WorkflowResult(
            problem_statement=problem,
            resolution_method=resolution_method,
            final_solution=final_solution,
            consensus_achieved=consensus_achieved,
            consensus_score=consensus_score if consensus_achieved else None,
            iterations_completed=self.state.iteration_count,
            orchestrator_rounds=orchestrator_rounds if orchestrator_rounds > 0 else None,
            total_duration_seconds=duration,
            expert_solutions=expert_solutions,
            resolution_metadata={
                "consensus_threshold": self.consensus_threshold,
                "total_agents": len(self.expert_agents)
            },
            technical_details=getattr(self, '_technical_details', None)
        )
    
    async def close(self):
        """Close resources gracefully"""
        # Wait for any pending operations
        await asyncio.sleep(WorkflowConstants.EXTENDED_CLEANUP_DELAY_SECONDS)
        
        # Collect unique clients
        clients_to_close = set()
        
        for agent in self.expert_agents + [self.orchestrator, self.presentation_agent, self.meta_reviewer]:
            if hasattr(agent, 'model_client'):
                clients_to_close.add(agent.model_client)
        
        # Close each client gracefully
        for client in clients_to_close:
            try:
                if hasattr(client, 'close'):
                    await client.close()
                elif hasattr(client, 'aclose'):
                    await client.aclose()
            except Exception:
                # Continue closing other clients
                pass
        
        # Additional wait to ensure AutoGen cleanup
        await asyncio.sleep(WorkflowConstants.CLEANUP_DELAY_SECONDS)