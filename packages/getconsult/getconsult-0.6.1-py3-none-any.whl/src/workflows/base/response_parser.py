"""
Clean response parsing logic - extracted from workflow
"""
from .workflow_constants import WorkflowConstants


class ResponseParser:
    """Clean response parsing - no fragile string manipulation in main workflow"""
    
    @staticmethod
    def extract_final_stance(response: str) -> str:
        """Extract final stance from response - moved from workflow"""
        # Try new format first
        if WorkflowConstants.FINAL_STANCE_MARKER in response:
            return ResponseParser._extract_section(response, WorkflowConstants.FINAL_STANCE_MARKER)
        
        # Try old format
        if WorkflowConstants.FINAL_STANCE_OLD_MARKER in response:
            return ResponseParser._extract_section(response, WorkflowConstants.FINAL_STANCE_OLD_MARKER)
        
        # Return full response if no structured section found
        return response
    
    @staticmethod
    def _extract_section(response: str, marker: str) -> str:
        """Extract section after marker"""
        section_start = response.find(marker)
        if section_start == -1:
            return response
            
        section_content = response[section_start:].replace(marker, '').strip()
        return section_content
    
    @staticmethod
    def truncate_solution_preview(solution: str) -> str:
        """Create clean preview of solution for orchestrator analysis"""
        if len(solution) <= WorkflowConstants.MAX_SOLUTION_PREVIEW_LENGTH:
            return solution
            
        return (solution[:WorkflowConstants.MAX_SOLUTION_PREVIEW_LENGTH] + 
                WorkflowConstants.TRUNCATION_SUFFIX)
    
    @staticmethod
    def format_agent_display_name(agent_name: str) -> str:
        """Convert agent_name to display format"""
        return agent_name.replace('_', ' ').title()