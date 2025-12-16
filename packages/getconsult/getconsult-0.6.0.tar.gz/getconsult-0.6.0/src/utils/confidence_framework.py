"""
Standardized Confidence Scoring Framework
"""

class ConfidenceFramework:
    """Standardized confidence scoring system used across all agents"""
    
    # Standard confidence levels with descriptions
    CONFIDENCE_LEVELS = {
        1.0: "Certain - Proven solution, widely adopted, extensive experience, minimal risk",
        0.9: "Very High - Strong evidence, established patterns, low risk",
        0.8: "High - Good evidence, proven approach, manageable risk",
        0.7: "Moderate-High - Solid approach with some unknowns",
        0.6: "Moderate - Reasonable approach but significant considerations", 
        0.5: "Medium - Viable but requires careful evaluation",
        0.4: "Low-Medium - Uncertain outcome, higher risk",
        0.3: "Low - Limited evidence, substantial unknowns",
        0.2: "Very Low - High uncertainty, experimental approach",
        0.1: "Minimal - Highly speculative, very high risk",
        0.0: "No Confidence - Approach not recommended"
    }
    
    @staticmethod
    def get_confidence_description(score: float) -> str:
        """Get description for confidence score"""
        # Round to nearest 0.1 for lookup
        rounded_score = round(score, 1)
        return ConfidenceFramework.CONFIDENCE_LEVELS.get(rounded_score, "Invalid confidence score")
    
    @staticmethod
    def get_framework_text() -> str:
        """Get the standard confidence framework text for prompts"""
        return """Confidence Level Framework:
• 1.0 (Certain): Proven solution, widely adopted, extensive experience, minimal risk
• 0.9 (Very High): Strong evidence, established patterns, low risk
• 0.8 (High): Good evidence, proven approach, manageable risk
• 0.7 (Moderate-High): Solid approach with some unknowns
• 0.6 (Moderate): Reasonable approach but significant considerations
• 0.5 (Medium): Viable but requires careful evaluation
• 0.4 (Low-Medium): Uncertain outcome, higher risk
• 0.3 (Low): Limited evidence, substantial unknowns
• 0.2 (Very Low): High uncertainty, experimental approach
• 0.1 (Minimal): Highly speculative, very high risk
• 0.0 (No Confidence): Approach not recommended

Use EXACT decimal scores (e.g., 0.8, not "high") with brief rationale."""
    
    @staticmethod
    def get_compact_framework_text() -> str:
        """Get compact version for inline use"""
        return "Use confidence scores: 1.0 (Certain), 0.8 (High), 0.6 (Moderate), 0.4 (Low), 0.2 (Very Low), 0.0 (No Confidence) with rationale."
    
    @staticmethod
    def validate_confidence_score(score: float) -> bool:
        """Validate confidence score is in valid range"""
        return 0.0 <= score <= 1.0
    
    @staticmethod
    def format_confidence_instruction(context: str = "solution") -> str:
        """Format confidence scoring instruction for specific context"""
        return f"""Provide your confidence in this {context} using the framework:
{ConfidenceFramework.get_framework_text()}"""


# Convenience function
def get_confidence_framework() -> str:
    """Get standardized confidence framework text"""
    return ConfidenceFramework.get_framework_text()


def format_confidence_instruction(context: str = "solution") -> str:
    """Format confidence instruction for context"""
    return ConfidenceFramework.format_confidence_instruction(context)