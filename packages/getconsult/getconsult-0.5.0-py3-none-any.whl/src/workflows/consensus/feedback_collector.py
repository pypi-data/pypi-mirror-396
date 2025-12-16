"""
Feedback collection component - extracted from ConsensusWorkflow
"""

import asyncio
import time
from typing import List, Dict, Optional
from autogen_agentchat.agents import AssistantAgent

from ..base.agent_communicator import AgentCommunicator
from ..base.workflow_state import WorkflowState
from ..base.workflow_constants import WorkflowConstants
from ..base.events import EventEmitter, EventTypes
from ...prompts.prompts import Prompts
from ...agents.expert_registry import get_expert_config
from ...core.paths import get_logs_dir
from ...core.security import get_contextual_logger

# Module logger
_logger = None


def _get_logger():
    """Get or create the feedback collector logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.feedback", log_file=str(log_file))
    return _logger


class FeedbackCollector:
    """Handles peer feedback collection between agents"""

    def __init__(self, communicator: AgentCommunicator, emitter: EventEmitter):
        self.communicator = communicator
        self.emitter = emitter
        self.logger = _get_logger()

    async def collect_feedback(self, agents: List[AssistantAgent], state: WorkflowState,
                             problem: str, iteration_count: int,
                             attachments: Optional[List] = None,
                             meta_reviewer: Optional[AssistantAgent] = None) -> None:
        """Collect feedback from each agent about others (PARALLELIZED)

        Also collects cross-cutting feedback from Meta Reviewer
        to all experts if provided.
        """
        feedback_start = time.time()
        num_peers = len(agents) * (len(agents) - 1)
        num_meta = len(agents) if meta_reviewer else 0
        self.logger.info(f"Feedback collection starting | {num_peers} peer reviews + {num_meta} meta reviews")

        # Emit feedback phase start
        self.emitter.emit(EventTypes.FEEDBACK_PHASE_START)

        # Show all agents starting feedback collection
        for evaluator in agents:
            self.emitter.emit(
                EventTypes.AGENT_THINKING,
                agent_name=evaluator.name,
                action="providing feedback to peers"
            )

        # Show Meta Reviewer starting if present
        if meta_reviewer:
            self.emitter.emit(
                EventTypes.AGENT_THINKING,
                agent_name=meta_reviewer.name,
                action="cross-cutting review across all expert perspectives"
            )

        # Create all feedback tasks for parallel execution
        feedback_tasks = []
        task_info = []  # Track which task corresponds to which evaluator->target

        # Peer-to-peer feedback (existing behavior)
        for evaluator in agents:
            for target in agents:
                if target.name == evaluator.name:
                    continue

                target_solution = state.current_solutions[target.name]['answer']
                task = self._get_feedback_for_target(evaluator, target, problem, target_solution, attachments)
                feedback_tasks.append(task)
                task_info.append((evaluator.name, target.name))

        # Meta Reviewer feedback to ALL experts (runs in parallel with peer feedback)
        if meta_reviewer:
            all_solutions = {name: data['answer'] for name, data in state.current_solutions.items()}
            for target in agents:
                target_solution = state.current_solutions[target.name]['answer']
                task = self._get_meta_reviewer_feedback_for_target(
                    meta_reviewer, target, problem, target_solution, all_solutions, attachments
                )
                feedback_tasks.append(task)
                task_info.append((meta_reviewer.name, target.name))

        # Execute all feedback collection in parallel
        feedback_results = await asyncio.gather(*feedback_tasks, return_exceptions=True)

        # Organize results back into the expected structure
        feedback_collection = {}
        for evaluator in agents:
            feedback_collection[evaluator.name] = {}

        # Add Meta Reviewer to feedback collection if present
        if meta_reviewer:
            feedback_collection[meta_reviewer.name] = {}

        error_count = 0
        for i, ((evaluator_name, target_name), result) in enumerate(zip(task_info, feedback_results)):
            if isinstance(result, Exception):
                feedback_response = f"Error collecting feedback: {str(result)}"
                error_count += 1
                self.logger.error(f"Feedback FAILED: {evaluator_name} → {target_name} | {type(result).__name__}: {result}")
                self.emitter.emit(
                    EventTypes.WORKFLOW_ERROR,
                    message=f"Error in feedback {evaluator_name} → {target_name}: {result}"
                )
            else:
                feedback_response = result

            feedback_collection[evaluator_name][target_name] = feedback_response

            # Store Meta Reviewer feedback separately for presentation/orchestrator context
            if meta_reviewer and evaluator_name == meta_reviewer.name:
                if not feedback_response.startswith("Error"):
                    state.store_meta_reviewer_feedback(iteration_count, target_name, feedback_response)

            # Show feedback for transparency
            if feedback_response and not feedback_response.startswith("Error"):
                # Show clear feedback direction: who → who
                self.emitter.emit(
                    EventTypes.FEEDBACK_EXCHANGE,
                    from_agent=evaluator_name,
                    to_agent=target_name,
                    feedback=feedback_response
                )

        # Store feedback in clean state management
        state.store_feedback_batch(feedback_collection, iteration_count)

        feedback_elapsed = time.time() - feedback_start
        success_count = len(feedback_results) - error_count
        self.logger.info(f"Feedback collection complete | {feedback_elapsed:.1f}s | "
                        f"{success_count} succeeded, {error_count} failed")
    
    def _get_expertise_areas(self, agent_name: str) -> Optional[List[str]]:
        """Extract expertise areas for an agent from registry"""
        # Handle prefixed names (e.g., "team_openai_database_expert" -> "database_expert")
        for expert_type in ["database_expert", "backend_expert", "infrastructure_expert",
                           "software_architect", "cloud_engineer", "security_expert",
                           "performance_expert", "frontend_expert", "ux_expert",
                           "data_expert", "ml_expert"]:
            if expert_type in agent_name:
                try:
                    config = get_expert_config(expert_type)
                    return config.expertise_areas
                except ValueError:
                    pass
        return None

    async def _get_feedback_for_target(self, evaluator: AssistantAgent, target: AssistantAgent,
                                     problem: str, target_solution: str,
                                     attachments: Optional[List] = None) -> str:
        """Get feedback from evaluator about target's solution"""
        # Get evaluator's expertise areas for domain-lens anchoring
        expertise_areas = self._get_expertise_areas(evaluator.name)

        feedback_prompt = Prompts.peer_feedback_prompt(
            problem=problem,
            evaluator_name=evaluator.name,
            target_name=target.name,
            target_solution=target_solution,
            evaluator_expertise_areas=expertise_areas
        )

        return await self.communicator.get_response(
            evaluator, feedback_prompt, attachments=attachments
        )

    async def _get_meta_reviewer_feedback_for_target(self, meta_reviewer: AssistantAgent, target: AssistantAgent,
                                                      problem: str, target_solution: str,
                                                      all_solutions: Dict[str, str],
                                                      attachments: Optional[List] = None) -> str:
        """Get Meta Reviewer cross-cutting feedback for a target's solution.

        Meta Reviewer reviews each expert's solution with full context of all solutions,
        providing cross-cutting critique that surfaces integration issues and
        blindspots that domain experts miss.
        """
        feedback_prompt = Prompts.meta_reviewer_feedback_prompt(
            problem=problem,
            target_name=target.name,
            target_solution=target_solution,
            all_solutions=all_solutions
        )

        return await self.communicator.get_response(
            meta_reviewer, feedback_prompt, attachments=attachments
        )