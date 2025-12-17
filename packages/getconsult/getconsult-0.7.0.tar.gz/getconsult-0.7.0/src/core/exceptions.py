"""
Custom exceptions for Consult
Provides structured error handling with domain-specific error types
"""

from typing import Optional, Dict, Any


class ConsultError(Exception):
    """Base exception for all Consult errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context
        }


# Workflow Exceptions
class WorkflowError(ConsultError):
    """Base class for workflow-related errors"""
    pass


class ConsensusTimeoutError(WorkflowError):
    """Raised when consensus cannot be reached within specified iterations"""
    
    def __init__(self, iterations: int, consensus_score: float, threshold: float, 
                 agent_count: int, context: Optional[Dict[str, Any]] = None):
        message = (f"Consensus not reached after {iterations} iterations. "
                  f"Final score: {consensus_score:.3f}, Threshold: {threshold:.3f}, "
                  f"Agents: {agent_count}")
        super().__init__(message, "CONSENSUS_TIMEOUT", context)
        self.iterations = iterations
        self.consensus_score = consensus_score
        self.threshold = threshold
        self.agent_count = agent_count


class WorkflowInitializationError(WorkflowError):
    """Raised when workflow cannot be properly initialized"""
    pass


class OrchestratorError(WorkflowError):
    """Raised when orchestrator intervention fails"""
    pass


# Agent Communication Exceptions
class AgentCommunicationError(ConsultError):
    """Base class for agent communication errors"""
    pass


class AgentResponseError(AgentCommunicationError):
    """Raised when an agent fails to provide a valid response"""
    
    def __init__(self, agent_name: str, prompt: str, original_error: Optional[Exception] = None,
                 context: Optional[Dict[str, Any]] = None):
        message = f"Agent '{agent_name}' failed to respond properly"
        if original_error:
            message += f": {str(original_error)}"
        
        error_context = context or {}
        error_context.update({
            "agent_name": agent_name,
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "original_error": str(original_error) if original_error else None
        })
        
        super().__init__(message, "AGENT_RESPONSE_FAILED", error_context)
        self.agent_name = agent_name
        self.original_error = original_error


class AgentTimeoutError(AgentCommunicationError):
    """Raised when an agent response times out"""
    
    def __init__(self, agent_name: str, timeout_seconds: float, context: Optional[Dict[str, Any]] = None):
        message = f"Agent '{agent_name}' timed out after {timeout_seconds}s"
        error_context = context or {}
        error_context.update({
            "agent_name": agent_name,
            "timeout_seconds": timeout_seconds
        })
        
        super().__init__(message, "AGENT_TIMEOUT", error_context)
        self.agent_name = agent_name
        self.timeout_seconds = timeout_seconds


class MultimodalProcessingError(AgentCommunicationError):
    """Raised when multimodal content processing fails"""
    
    def __init__(self, attachment_type: str, filename: Optional[str] = None, 
                 original_error: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None):
        message = f"Failed to process {attachment_type} attachment"
        if filename:
            message += f" '{filename}'"
        if original_error:
            message += f": {str(original_error)}"
            
        error_context = context or {}
        error_context.update({
            "attachment_type": attachment_type,
            "filename": filename,
            "original_error": str(original_error) if original_error else None
        })
        
        super().__init__(message, "MULTIMODAL_PROCESSING_FAILED", error_context)
        self.attachment_type = attachment_type
        self.filename = filename
        self.original_error = original_error


# Configuration Exceptions
class ConfigurationError(ConsultError):
    """Base class for configuration-related errors"""
    pass


class MissingAPIKeyError(ConfigurationError):
    """Raised when required API keys are not available"""
    
    def __init__(self, provider: str, context: Optional[Dict[str, Any]] = None):
        message = f"Missing API key for provider: {provider}"
        error_context = context or {}
        error_context.update({"provider": provider})
        
        super().__init__(message, "MISSING_API_KEY", error_context)
        self.provider = provider


class InvalidProviderError(ConfigurationError):
    """Raised when an unsupported provider is specified"""
    
    def __init__(self, provider: str, available_providers: list, context: Optional[Dict[str, Any]] = None):
        message = f"Invalid provider '{provider}'. Available: {', '.join(available_providers)}"
        error_context = context or {}
        error_context.update({
            "provider": provider,
            "available_providers": available_providers
        })
        
        super().__init__(message, "INVALID_PROVIDER", error_context)
        self.provider = provider
        self.available_providers = available_providers


class InvalidExpertConfigError(ConfigurationError):
    """Raised when expert configuration is invalid"""
    
    def __init__(self, config_value: str, available_experts: list, context: Optional[Dict[str, Any]] = None):
        message = f"Invalid expert configuration '{config_value}'"
        error_context = context or {}
        error_context.update({
            "config_value": config_value,
            "available_experts": available_experts
        })
        
        super().__init__(message, "INVALID_EXPERT_CONFIG", error_context)
        self.config_value = config_value
        self.available_experts = available_experts


# Memory and Storage Exceptions
class MemoryError(ConsultError):
    """Base class for memory-related errors"""
    pass


class MemoryStorageError(MemoryError):
    """Raised when memory storage operations fail"""
    pass


class MemoryRetrievalError(MemoryError):
    """Raised when memory retrieval operations fail"""
    pass


# Resource Management Exceptions
class ResourceError(ConsultError):
    """Base class for resource management errors"""
    pass


class ResourceExhaustionError(ResourceError):
    """Raised when system resources are exhausted"""
    
    def __init__(self, resource_type: str, limit: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        message = f"Resource exhaustion: {resource_type}"
        if limit:
            message += f" (limit: {limit})"
            
        error_context = context or {}
        error_context.update({
            "resource_type": resource_type,
            "limit": limit
        })
        
        super().__init__(message, "RESOURCE_EXHAUSTED", error_context)
        self.resource_type = resource_type
        self.limit = limit


class ResourceCleanupError(ResourceError):
    """Raised when resource cleanup fails"""
    pass


# Feature Gating Exceptions
class FeatureGatedError(ConsultError):
    """Raised when a user attempts to access a feature not available in their tier.

    Provides clear, actionable messaging for end users while logging
    detailed context for debugging.
    """

    # User-friendly feature names and upgrade messages
    FEATURE_INFO = {
        "team_mode": {
            "name": "Team Mode",
            "description": "Multi-provider comparison (OpenAI vs Anthropic vs Google)",
            "free_alternative": "Use single-provider mode with --provider flag",
        },
        "tui_enabled": {
            "name": "Terminal UI",
            "description": "Interactive terminal interface with real-time updates",
            "free_alternative": "Use CLI mode: consult -p 'your question'",
        },
        "sessions_enabled": {
            "name": "Sessions",
            "description": "Conversation persistence and follow-up queries",
            "free_alternative": "Each query is independent in free tier",
        },
        "attachments_enabled": {
            "name": "Attachments",
            "description": "Image and PDF file analysis",
            "free_alternative": "Describe the content in your query text",
        },
        "export_enabled": {
            "name": "Export",
            "description": "Markdown and structured output export",
            "free_alternative": "Copy output from terminal",
        },
        "custom_experts": {
            "name": "Custom Experts",
            "description": "Configure custom expert panels and personas",
            "free_alternative": "Use default expert sets",
        },
        "max_experts": {
            "name": "Expert Count",
            "description": "Number of experts per query",
            "free_alternative": "Use -e essentials (2 experts: backend + frontend)",
        },
        "max_iterations": {
            "name": "Consensus Iterations",
            "description": "Rounds of peer review for consensus",
            "free_alternative": None,
        },
    }

    def __init__(self, feature: str, current_tier: str, required_tier: str = "pro_byok",
                 context: Optional[Dict[str, Any]] = None):
        feature_info = self.FEATURE_INFO.get(feature, {"name": feature, "description": feature})

        # Build user-friendly message
        message = f"'{feature_info['name']}' requires Pro tier (current: {current_tier})"

        error_context = context or {}
        error_context.update({
            "feature": feature,
            "feature_name": feature_info["name"],
            "current_tier": current_tier,
            "required_tier": required_tier,
        })

        super().__init__(message, "FEATURE_GATED", error_context)
        self.feature = feature
        self.feature_name = feature_info["name"]
        self.feature_description = feature_info.get("description", "")
        self.free_alternative = feature_info.get("free_alternative")
        self.current_tier = current_tier
        self.required_tier = required_tier

    def user_message(self) -> str:
        """Get formatted message for end-user display."""
        lines = [
            f"⛔ {self.feature_name} is a Pro feature",
            f"",
            f"   {self.feature_description}",
            f"",
        ]

        if self.free_alternative:
            lines.append(f"   💡 Free alternative: {self.free_alternative}")
            lines.append("")

        lines.append(f"   🚀 Upgrade at: https://getconsult.sysapp.dev")

        return "\n".join(lines)