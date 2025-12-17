"""
Simple state management for consensus workflow
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class WorkflowState:
    """Clean state management for workflow - no business logic, just data"""

    # Core solutions
    current_solutions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    initial_solutions: Dict[str, str] = field(default_factory=dict)

    # Feedback tracking
    evaluation_history: Dict[str, Dict[int, Dict[str, Dict[str, str]]]] = field(default_factory=dict)

    # Meta Reviewer feedback (stored separately for easy access by presentation/orchestrator)
    # Structure: {iteration: {target_name: feedback}}
    meta_reviewer_feedback: Dict[int, Dict[str, str]] = field(default_factory=dict)

    # Workflow progress
    iteration_count: int = 0
    start_time: Optional[float] = None

    # Attachments
    attachments: List = field(default_factory=list)
    
    def store_initial_solution(self, agent_name: str, solution: str):
        """Store initial solution for agent"""
        self.initial_solutions[agent_name] = solution
        self.current_solutions[agent_name] = {
            "answer": solution,
            "iteration": 0
        }
    
    def update_solution(self, agent_name: str, solution: str, iteration: int):
        """Update agent's current solution"""
        self.current_solutions[agent_name] = {
            "answer": solution,
            "iteration": iteration
        }
    
    def get_received_feedback(self, agent_name: str, iteration: int) -> Dict[str, str]:
        """Get feedback received by agent in specific iteration - cleaner access"""
        return (
            self.evaluation_history
            .get(agent_name, {})
            .get(iteration, {})
            .get('feedback_received', {})
        )
    
    def store_feedback_batch(self, feedback_collection: Dict[str, Dict[str, str]], iteration: int):
        """Store complete feedback batch - extracted from main class"""
        # Initialize structure for all agents if needed
        for evaluator_name in feedback_collection.keys():
            if evaluator_name not in self.evaluation_history:
                self.evaluation_history[evaluator_name] = {}
            if iteration not in self.evaluation_history[evaluator_name]:
                self.evaluation_history[evaluator_name][iteration] = {
                    'feedback_given': {},
                    'feedback_received': {}
                }
        
        # Store given and received feedback
        for evaluator_name, feedback_dict in feedback_collection.items():
            if evaluator_name in self.evaluation_history:
                self.evaluation_history[evaluator_name][iteration]['feedback_given'] = feedback_dict
            
            for target_name, feedback_content in feedback_dict.items():
                if target_name in self.evaluation_history:
                    if target_name not in self.evaluation_history:
                        self.evaluation_history[target_name] = {}
                    if iteration not in self.evaluation_history[target_name]:
                        self.evaluation_history[target_name][iteration] = {
                            'feedback_given': {},
                            'feedback_received': {}
                        }
                    self.evaluation_history[target_name][iteration]['feedback_received'][evaluator_name] = feedback_content
    
    def store_meta_reviewer_feedback(self, iteration: int, target_name: str, feedback: str) -> None:
        """Store Meta Reviewer feedback for a target agent."""
        if iteration not in self.meta_reviewer_feedback:
            self.meta_reviewer_feedback[iteration] = {}
        self.meta_reviewer_feedback[iteration][target_name] = feedback

    def get_all_meta_reviewer_feedback(self) -> Dict[str, str]:
        """Get all Meta Reviewer feedback across all iterations (latest per target)."""
        all_feedback = {}
        # Iterate through iterations in order to get latest feedback per target
        for iteration in sorted(self.meta_reviewer_feedback.keys()):
            for target_name, feedback in self.meta_reviewer_feedback[iteration].items():
                all_feedback[target_name] = feedback
        return all_feedback

    def get_all_current_solutions(self) -> Dict[str, str]:
        """Get just the answer strings from all current solutions"""
        return {name: data['answer'] for name, data in self.current_solutions.items()}

    def get_all_current_solutions_detailed(self) -> Dict[str, Dict[str, Any]]:
        """Get all current solutions with detailed information"""
        return self.current_solutions.copy()