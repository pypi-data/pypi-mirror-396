"""
Structured data models for agent responses using Pydantic
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class ExpertAnalysis(BaseModel):
    """Structured output for expert initial analysis"""
    recommendation: str = Field(description="The expert's recommended solution")
    key_reasoning: List[str] = Field(description="Key facts and reasoning supporting the recommendation")
    confidence_level: float = Field(ge=0.0, le=1.0, description="Confidence level between 0.0 and 1.0")
    
    @field_validator('confidence_level')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence level must be between 0.0 and 1.0')
        return v


class FeedbackPoint(BaseModel):
    """Individual feedback point from one expert to another"""
    category: Literal["strength", "concern", "suggestion"] = Field(description="Type of feedback")
    content: str = Field(description="The specific feedback content")
    technical_justification: str = Field(description="Technical evidence or reasoning")
    priority: Literal["critical", "important", "minor"] = Field(description="Priority level of this feedback")


class PeerFeedback(BaseModel):
    """Structured feedback from one expert to another"""
    from_expert: str = Field(description="Name of the expert giving feedback")
    to_expert: str = Field(description="Name of the expert receiving feedback")
    technical_strengths: List[FeedbackPoint] = Field(description="Identified technical strengths")
    technical_concerns: List[FeedbackPoint] = Field(description="Technical concerns and risks")
    improvement_suggestions: List[FeedbackPoint] = Field(description="Actionable improvement suggestions")
    critical_priorities: List[str] = Field(description="Most critical points to address")


class FeedbackResponse(BaseModel):
    """How an expert responds to feedback"""
    feedback_point: str = Field(description="The specific feedback being addressed")
    response_type: Literal["accept", "modify", "reject"] = Field(description="How the expert responds")
    justification: str = Field(description="Technical justification for the response")
    changes_made: Optional[str] = Field(None, description="Specific changes made if accepting/modifying")


class EvolvedSolution(BaseModel):
    """Expert's evolved solution after feedback"""
    expert_name: str = Field(description="Name of the expert")
    iteration: int = Field(description="Iteration number")
    final_solution: str = Field(description="The evolved solution incorporating feedback")
    feedback_responses: List[FeedbackResponse] = Field(description="How each feedback point was addressed")
    changes_summary: str = Field(description="Summary of all changes made")
    confidence_evolution: str = Field(description="How confidence changed and why")
    final_confidence: float = Field(ge=0.0, le=1.0, description="Final confidence level")


class ConsensusEvaluation(BaseModel):
    """Consensus evaluation by an expert (legacy - use CrossExpertApproval)"""
    evaluator: str = Field(description="Expert performing the evaluation")
    consensus_score: float = Field(ge=0.0, le=1.0, description="Consensus score")
    breakdown: str = Field(description="Explanation of alignment/disagreement factors")
    key_alignments: List[str] = Field(description="Key areas of agreement")
    key_disagreements: List[str] = Field(description="Key areas of disagreement")


class DimensionApproval(BaseModel):
    """Approval assessment for a single dimension"""
    dimension: Literal["requirements", "approach", "tradeoffs", "architecture", "implementation"]
    verdict: Literal["APPROVE", "CONCERNS", "OBJECT"]
    score: float = Field(ge=0.0, le=1.0, description="Weighted score for this dimension")
    reasoning: str = Field(description="Brief reasoning for verdict")


class CrossExpertApproval(BaseModel):
    """Structured cross-expert approval: Expert A evaluates Expert B's solution

    TRUE CONSENSUS: Not "how similar are we?" but "Would I sign off on THIS for production?"

    Deterministic output - no regex parsing needed.
    """
    evaluator: str = Field(description="Expert giving the approval")
    target: str = Field(description="Expert whose solution is being evaluated")

    # Dimensional assessments with production-blocking weights
    requirements: DimensionApproval = Field(description="Requirements alignment (30% weight)")
    approach: DimensionApproval = Field(description="Technical approach (25% weight)")
    tradeoffs: DimensionApproval = Field(description="Trade-off reasoning (20% weight)")
    architecture: DimensionApproval = Field(description="Architecture quality (15% weight)")
    implementation: DimensionApproval = Field(description="Implementation feasibility (10% weight)")

    # Final verdict
    overall_verdict: Literal["APPROVE", "APPROVE_WITH_CONCERNS", "OBJECT"] = Field(
        description="Overall production approval verdict"
    )
    approval_score: float = Field(
        ge=0.0, le=1.0,
        description="Weighted approval score (0.0-1.0)"
    )

    # Supporting details
    endorsements: List[str] = Field(description="Specific aspects being endorsed")
    concerns: List[str] = Field(default=[], description="Concerns that don't block approval")
    objections: List[str] = Field(default=[], description="Blocking issues (only if OBJECT)")

    @field_validator('approval_score')
    def validate_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Approval score must be between 0.0 and 1.0')
        return v


class ProposalEvaluation(BaseModel):
    """Expert evaluation of orchestrator proposal"""
    expert_name: str = Field(description="Expert evaluating the proposal")
    acceptance_level: Literal["accept", "accept_with_modifications", "neutral", "reject_with_counter", "reject"]
    technical_assessment: str = Field(description="Technical analysis of the proposal")
    suggested_modifications: Optional[List[str]] = Field(None, description="Specific modifications suggested")
    confidence_in_compromise: float = Field(ge=0.0, le=1.0, description="Confidence in the compromise")


class OrchestratorDecision(BaseModel):
    """Structured orchestrator decision"""
    disagreement_analysis: Dict[str, str] = Field(description="Analysis of each disagreement area")
    consensus_points: List[str] = Field(description="Identified areas of agreement")
    technical_synthesis: str = Field(description="How conflicting recommendations are resolved")
    final_solution: str = Field(description="Complete technical solution")
    expert_resolution_log: Dict[str, str] = Field(description="How each expert's view was incorporated")
    implementation_plan: List[str] = Field(description="Step-by-step implementation guidance")
    validation_criteria: List[str] = Field(description="Success metrics and validation criteria")


class WorkflowResult(BaseModel):
    """Final workflow result with complete metadata"""
    problem_statement: str
    resolution_method: Literal["democratic_consensus", "orchestrator_facilitated", "orchestrator_authority"]
    final_solution: str
    consensus_achieved: bool
    consensus_score: Optional[float] = None
    iterations_completed: int
    orchestrator_rounds: Optional[int] = None
    total_duration_seconds: float
    expert_solutions: Dict[str, str] = Field(description="Final solution from each expert")
    resolution_metadata: Dict[str, Any] = Field(description="Additional metadata about the resolution")
    technical_details: Optional[str] = Field(None, description="Technical details for debugging/transparency")