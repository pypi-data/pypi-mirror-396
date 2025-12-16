"""
Workflow constants - no more magic numbers
"""

class WorkflowConstants:
    """Clean constants for workflow behavior"""
    
    # Timing constants
    # Higher value ensures long agent responses aren't truncated mid-stream
    AGENT_RESPONSE_TIMEOUT_MESSAGES = 4
    CLEANUP_DELAY_SECONDS = 0.2
    EXTENDED_CLEANUP_DELAY_SECONDS = 0.3
    
    # State tracking
    POST_COMPROMISE_ITERATION_OFFSET = 0.5
    
    # String parsing constants
    FINAL_STANCE_MARKER = "**NEW FINAL STANCE:**"
    FINAL_STANCE_OLD_MARKER = "**FINAL STANCE:**"
    SCORING_RATIONALE_MARKER = "**SCORING RATIONALE:**"
    
    # Solution truncation
    MAX_SOLUTION_PREVIEW_LENGTH = 200
    TRUNCATION_SUFFIX = "..."
    
    # Display formatting
    SEPARATOR_LENGTH = 60
    FEEDBACK_SEPARATOR_LENGTH = 40
    ORCHESTRATOR_SEPARATOR_LENGTH = 50