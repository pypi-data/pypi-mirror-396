"""
Workflow orchestration component - coordinates consensus workflow phases
"""

import time
import asyncio
from typing import List, Optional, Tuple
from autogen_agentchat.agents import AssistantAgent

from ...core.exceptions import ConsensusTimeoutError, AgentResponseError, AgentTimeoutError
from ...core.paths import get_logs_dir
from ...core.security import get_contextual_logger

from .initial_analysis_handler import InitialAnalysisHandler
from .feedback_collector import FeedbackCollector
from .solution_refiner import SolutionRefiner
from .consensus_evaluator import ConsensusEvaluator
from ..base.agent_communicator import AgentCommunicator
from ..base.workflow_state import WorkflowState
from ..base.workflow_constants import WorkflowConstants
from ..base.response_parser import ResponseParser
from ..base.events import EventEmitter, EventTypes
from ...prompts.prompts import Prompts

# Module logger
_logger = None


def _get_logger():
    """Get or create the orchestrator logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.orchestrator", log_file=str(log_file))
    return _logger


class WorkflowOrchestrator:
    """Orchestrates the consensus workflow phases using focused components"""

    def __init__(self, communicator: AgentCommunicator, emitter: EventEmitter,
                 memory_manager=None, meta_reviewer: Optional[AssistantAgent] = None):
        self.communicator = communicator
        self.emitter = emitter
        self.memory_manager = memory_manager
        self.meta_reviewer = meta_reviewer
        self.logger = _get_logger()

        # Initialize specialized components with emitter
        self.initial_handler = InitialAnalysisHandler(communicator, emitter, memory_manager)
        self.feedback_collector = FeedbackCollector(communicator, emitter)
        self.solution_refiner = SolutionRefiner(communicator, emitter)
        self.consensus_evaluator = ConsensusEvaluator(communicator, emitter)
    
    async def run_consensus_phases(self, agents: List[AssistantAgent], state: WorkflowState,
                                 orchestrator: AssistantAgent, problem: str,
                                 consensus_threshold: float, max_iterations: int) -> Tuple[str, str, int]:
        """Run the complete consensus workflow phases

        Returns:
            Tuple of (final_solution, resolution_method, orchestrator_rounds)
        """
        agent_names = [a.name for a in agents]
        self.logger.info(f"Phase 1: Initial Analysis | {len(agents)} experts: {agent_names}")

        # Phase 1: Initial answers
        self.emitter.emit(
            EventTypes.PHASE_START,
            phase_num=1,
            phase_name="Initial Analysis",
            description="Each expert provides independent solution"
        )
        phase1_start = time.time()
        await self.initial_handler.collect_initial_answers(agents, state, problem)
        self.logger.info(f"Phase 1 complete | {time.time() - phase1_start:.1f}s")

        # Phase 2: Peer feedback and refinement
        self.logger.info(f"Phase 2: Peer Feedback | max_iterations={max_iterations}, threshold={consensus_threshold}")
        self.emitter.emit(
            EventTypes.PHASE_START,
            phase_num=2,
            phase_name="Peer Feedback",
            description="Cross-evaluation and refinement"
        )

        consensus_reached = False
        consensus_score = 0.0

        while state.iteration_count < max_iterations and not consensus_reached:
            state.iteration_count += 1
            elapsed = time.time() - state.start_time

            self.logger.info(f"Iteration {state.iteration_count}/{max_iterations} starting | elapsed={elapsed:.1f}s")

            self.emitter.emit(
                EventTypes.ITERATION_START,
                iteration=state.iteration_count,
                elapsed_seconds=elapsed
            )

            # Cross-evaluate and refine
            iter_start = time.time()
            await self._run_feedback_and_refinement_iteration(agents, state, problem)

            # Check for consensus (evaluator emits CONSENSUS_CHECK event with full data)
            consensus_score = await self.consensus_evaluator.evaluate_consensus(
                agents, state, threshold=consensus_threshold
            )

            iter_elapsed = time.time() - iter_start
            self.logger.info(f"Iteration {state.iteration_count} complete | {iter_elapsed:.1f}s | "
                           f"consensus={consensus_score:.2f} vs threshold={consensus_threshold}")

            if consensus_score >= consensus_threshold:
                consensus_reached = True
                self.logger.info(f"Consensus REACHED at iteration {state.iteration_count}")

        # Phase 3: Orchestrator intervention if needed
        if consensus_reached:
            final_solution = self._format_consensus_solution(agents, state, consensus_threshold)
            return final_solution, "democratic_consensus", 0
        else:
            self.logger.warning(f"Consensus NOT reached after {max_iterations} iterations | "
                              f"final_score={consensus_score:.2f} < threshold={consensus_threshold}")
            # This would call orchestrator intervention logic
            # For now, return a placeholder to maintain interface
            orchestrator_solution = "Orchestrator intervention needed - not implemented in this component"
            return orchestrator_solution, "orchestrator_authority", 1
    
    async def _run_feedback_and_refinement_iteration(self, agents: List[AssistantAgent],
                                                   state: WorkflowState, problem: str) -> None:
        """Run a single iteration of feedback collection and solution refinement"""
        # Get attachments from state so reviewers can reference original documents
        attachments = state.attachments if hasattr(state, 'attachments') else None

        # Step 1: Collect feedback (with attachments for document reference)
        # Meta Reviewer provides cross-cutting feedback to all experts
        await self.feedback_collector.collect_feedback(
            agents, state, problem, state.iteration_count,
            attachments=attachments,
            meta_reviewer=self.meta_reviewer
        )

        # Step 2: Refine solutions (with attachments for re-examination)
        await self.solution_refiner.refine_solutions(
            agents, state, problem, state.iteration_count, attachments=attachments
        )
    
    def _format_consensus_solution(self, agents: List[AssistantAgent], state: WorkflowState, 
                                 consensus_threshold: float) -> str:
        """Format consensus solution in structured, readable format"""
        
        # Extract key information from each solution
        formatted_solutions = []
        
        for name, data in state.current_solutions.items():
            agent_display = ResponseParser.format_agent_display_name(name)
            solution = data['answer']
            
            # Use clean parser for final stance extraction
            final_stance = ResponseParser.extract_final_stance(solution)
            formatted_solutions.append(f"### {agent_display}\n{final_stance}")
        
        return f"""# 🎯 CONSENSUS SOLUTION

## Resolution Status
✅ **Democratic consensus achieved** ({consensus_threshold*100:.0f}%+ agreement)  
🔄 **Iterations completed:** {state.iteration_count}  
👥 **Expert participants:** {len(agents)}  

## Expert Recommendations

{chr(10).join(formatted_solutions)}

## Summary
All experts reached consensus through structured peer feedback and iterative refinement. The solution represents the collective wisdom of specialized domain experts."""