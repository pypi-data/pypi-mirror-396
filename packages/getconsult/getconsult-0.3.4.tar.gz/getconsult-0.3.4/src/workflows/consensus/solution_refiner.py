"""
Solution refinement component - extracted from ConsensusWorkflow
"""

import asyncio
import time
from typing import List, Optional
from autogen_agentchat.agents import AssistantAgent

from ..base.agent_communicator import AgentCommunicator
from ..base.workflow_state import WorkflowState
from ..base.workflow_constants import WorkflowConstants
from ..base.events import EventEmitter, EventTypes
from ...prompts.prompts import Prompts
from ...core.paths import get_logs_dir
from ...core.security import get_contextual_logger

# Module logger
_logger = None


def _get_logger():
    """Get or create the solution refiner logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.refiner", log_file=str(log_file))
    return _logger


class SolutionRefiner:
    """Handles solution refinement based on peer feedback"""

    def __init__(self, communicator: AgentCommunicator, emitter: EventEmitter):
        self.communicator = communicator
        self.emitter = emitter
        self.logger = _get_logger()

    async def refine_solutions(self, agents: List[AssistantAgent], state: WorkflowState,
                             problem: str, iteration_count: int,
                             attachments: Optional[List] = None) -> None:
        """Integrate feedback and refine solutions (PARALLELIZED)"""
        refine_start = time.time()
        agent_names = [a.name for a in agents]
        self.logger.info(f"Solution refinement starting | {len(agents)} agents: {agent_names}")

        # Emit refinement phase start
        self.emitter.emit(EventTypes.REFINEMENT_PHASE_START)

        # Show all agents starting refinement
        for agent in agents:
            self.emitter.emit(
                EventTypes.AGENT_THINKING,
                agent_name=agent.name,
                action="integrating peer feedback"
            )

        # Create refinement tasks for parallel execution
        refinement_tasks = []
        for agent in agents:
            task = self._refine_agent_solution(agent, state, problem, iteration_count, attachments)
            refinement_tasks.append(task)

        # Execute all refinements in parallel
        refinement_results = await asyncio.gather(*refinement_tasks, return_exceptions=True)

        # Process results and update solutions
        error_count = 0
        for i, (agent, result) in enumerate(zip(agents, refinement_results)):
            if isinstance(result, Exception):
                refined_response = f"Error during refinement: {str(result)}"
                error_count += 1
                self.logger.error(f"Refinement FAILED: {agent.name} | {type(result).__name__}: {result}")
                self.emitter.emit(
                    EventTypes.WORKFLOW_ERROR,
                    message=f"Error refining {agent.name}: {result}"
                )
            else:
                refined_response = result

            # Use clean state management
            state.update_solution(agent.name, refined_response, iteration_count)

            self.emitter.emit(
                EventTypes.AGENT_RESPONSE,
                agent_name=agent.name,
                content=refined_response,
                response_type=f"Refined Solution (Iteration {iteration_count})"
            )

        refine_elapsed = time.time() - refine_start
        success_count = len(agents) - error_count
        self.logger.info(f"Solution refinement complete | {refine_elapsed:.1f}s | "
                        f"{success_count} succeeded, {error_count} failed")
    
    async def _refine_agent_solution(self, agent: AssistantAgent, state: WorkflowState,
                                   problem: str, iteration_count: int,
                                   attachments: Optional[List] = None) -> str:
        """Refine a single agent's solution based on feedback"""
        # Collect feedback for this agent with error handling
        try:
            received_feedback = state.get_received_feedback(agent.name, iteration_count)
        except (KeyError, AttributeError):
            received_feedback = {}

        if not received_feedback:
            # If no feedback available, return a message explaining this
            current_answer = state.current_solutions.get(agent.name, {}).get('answer', 'No solution available')
            return f"Unable to refine solution - no peer feedback received. Original solution stands: {current_answer}"

        current_solution = state.current_solutions[agent.name]['answer']

        refinement_prompt = Prompts.feedback_integration_prompt(
            problem=problem,
            agent_name=agent.name,
            current_solution=current_solution,
            all_feedback=received_feedback
        )

        return await self.communicator.get_response(
            agent, refinement_prompt, max_messages=WorkflowConstants.AGENT_RESPONSE_TIMEOUT_MESSAGES,
            attachments=attachments
        )