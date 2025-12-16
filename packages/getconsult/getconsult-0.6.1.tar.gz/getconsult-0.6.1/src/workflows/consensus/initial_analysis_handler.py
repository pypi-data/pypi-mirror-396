"""
Initial analysis handling component - extracted from ConsensusWorkflow
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
    """Get or create the initial analysis handler logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.initial", log_file=str(log_file))
    return _logger


class InitialAnalysisHandler:
    """Handles the initial analysis phase where agents provide their first solutions"""

    def __init__(self, communicator: AgentCommunicator, emitter: EventEmitter,
                 memory_manager=None):
        self.communicator = communicator
        self.emitter = emitter
        self.memory_manager = memory_manager
        self.logger = _get_logger()
    
    async def collect_initial_answers(self, agents: List[AssistantAgent], state: WorkflowState,
                                    problem: str) -> None:
        """Phase 1: Each agent provides initial answer (PARALLELIZED)"""
        analysis_start = time.time()
        agent_names = [a.name for a in agents]
        self.logger.info(f"Initial analysis starting | {len(agents)} agents in parallel: {agent_names}")

        # Show all agents starting simultaneously
        for agent in agents:
            self.emitter.emit(
                EventTypes.AGENT_THINKING,
                agent_name=agent.name,
                action="analyzing the problem"
            )

        # Create tasks for parallel execution with progress tracking
        tasks = []
        agent_task_map = {}  # Map tasks to agents for proper ordering
        for agent in agents:
            task = asyncio.create_task(self._get_initial_answer(agent, problem, state.attachments))
            tasks.append(task)
            agent_task_map[task] = agent

        # Execute with progress updates
        completed = 0
        total = len(agents)
        results_map = {}  # Map agents to results
        pending = set(tasks)

        # Show initial progress
        self.emitter.emit(
            EventTypes.PARALLEL_PROGRESS,
            completed=completed,
            total=total,
            action="Experts analyzing"
        )

        # Execute all initial analyses in parallel with progress using wait()
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

            for task in done:
                agent = agent_task_map[task]
                try:
                    result = task.result()
                except Exception as e:
                    result = e

                results_map[agent.name] = result
                completed += 1
                self.emitter.emit(
                    EventTypes.PARALLEL_PROGRESS,
                    completed=completed,
                    total=total,
                    action="Experts analyzing"
                )

        # Process results in original agent order and display responses
        error_count = 0
        for agent in agents:
            result = results_map.get(agent.name)
            if isinstance(result, Exception):
                answer = f"Error during initial analysis: {str(result)}"
                error_count += 1
                self.logger.error(f"Initial analysis FAILED: {agent.name} | {type(result).__name__}: {result}")
                self.emitter.emit(
                    EventTypes.WORKFLOW_ERROR,
                    agent_name=agent.name,
                    error=str(result)
                )
            else:
                answer = result

            # Use clean state management
            state.store_initial_solution(agent.name, answer)

            # Store in memory if available
            if self.memory_manager and answer and not answer.startswith("Error"):
                await self.memory_manager.add_conversation(agent.name, answer[:500], "initial_analysis")

            self.emitter.emit(
                EventTypes.AGENT_RESPONSE,
                agent_name=agent.name,
                content=answer,
                response_type="Initial Analysis"
            )

        analysis_elapsed = time.time() - analysis_start
        success_count = len(agents) - error_count
        self.logger.info(f"Initial analysis complete | {analysis_elapsed:.1f}s | "
                        f"{success_count} succeeded, {error_count} failed")
    
    async def _get_initial_answer(self, agent: AssistantAgent, problem: str, 
                                attachments: Optional[List] = None) -> str:
        """Get initial answer from a single agent"""
        prompt = Prompts.initial_analysis_prompt(problem)
        
        return await self.communicator.get_response(
            agent, prompt, max_messages=WorkflowConstants.AGENT_RESPONSE_TIMEOUT_MESSAGES,
            attachments=attachments
        )