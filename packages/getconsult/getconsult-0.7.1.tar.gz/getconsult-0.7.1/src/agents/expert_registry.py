"""
Expert Agent Registry - Central configuration for all expert types
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from ..prompts.prompts import Prompts


@dataclass
class ExpertConfig:
    """Configuration for an expert agent"""
    name: str
    description: str
    base_message: str
    expertise_areas: List[str]
    
    def __post_init__(self):
        """Validate expert configuration"""
        if not self.name:
            raise ValueError("Expert name cannot be empty")
        if not self.description:
            raise ValueError("Expert description cannot be empty")
        if not self.base_message:
            raise ValueError("Expert base_message cannot be empty")


class ExpertRegistry:
    """Registry for managing expert agent configurations"""
    
    def __init__(self):
        self._experts: Dict[str, ExpertConfig] = {}
        self._expert_sets: Dict[str, List[str]] = {}
        self._register_default_experts()
    
    def register_expert(self, expert: ExpertConfig) -> None:
        """Register a new expert type"""
        self._experts[expert.name] = expert
    
    def register_expert_set(self, set_name: str, expert_names: List[str]) -> None:
        """Register a predefined set of experts"""
        # Validate all experts exist
        for name in expert_names:
            if name not in self._experts:
                raise ValueError(f"Unknown expert type: {name}")
        self._expert_sets[set_name] = expert_names
    
    def get_expert(self, name: str) -> ExpertConfig:
        """Get expert configuration by name"""
        if name not in self._experts:
            raise ValueError(f"Unknown expert type: {name}")
        return self._experts[name]
    
    def get_expert_set(self, set_name: str) -> List[str]:
        """Get predefined expert set"""
        if set_name not in self._expert_sets:
            raise ValueError(f"Unknown expert set: {set_name}")
        return self._expert_sets[set_name]
    
    def list_experts(self) -> List[str]:
        """List all available expert types"""
        return list(self._experts.keys())
    
    def list_expert_sets(self) -> List[str]:
        """List all available expert sets"""
        return list(self._expert_sets.keys())
    
    def _register_default_experts(self) -> None:
        """Register default expert types"""
        
        # Get centralized base messages
        base_messages = Prompts.get_expert_base_messages()
        
        # Technical Infrastructure Experts
        self.register_expert(ExpertConfig(
            name="database_expert",
            description="Database expert specializing in chat applications and real-time systems.",
            base_message=base_messages["database_expert"],
            expertise_areas=["database technology", "data modeling", "consistency guarantees", "performance optimization"]
        ))
        
        self.register_expert(ExpertConfig(
            name="backend_expert",
            description="Backend engineer with expertise in system architecture and scalability.",
            base_message=base_messages["backend_expert"],
            expertise_areas=["API design", "service architecture", "scalability patterns", "integration strategies"]
        ))
        
        self.register_expert(ExpertConfig(
            name="infrastructure_expert",
            description="Infrastructure expert focusing on deployment, monitoring, and operational concerns.",
            base_message=base_messages["infrastructure_expert"],
            expertise_areas=["deployment strategies", "monitoring solutions", "cost optimization", "operational excellence"]
        ))
        
        # Architecture & Design Experts
        self.register_expert(ExpertConfig(
            name="software_architect",
            description="Expert in system design, architecture patterns, and scalability",
            base_message=base_messages["software_architect"],
            expertise_areas=["system design", "architecture patterns", "scalability", "maintainability"]
        ))
        
        self.register_expert(ExpertConfig(
            name="cloud_engineer",
            description="Expert in cloud infrastructure, DevOps, and deployment strategies",
            base_message=base_messages["cloud_engineer"],
            expertise_areas=["cloud platforms", "DevOps", "containerization", "infrastructure as code"]
        ))
        
        # Security & Performance Experts
        self.register_expert(ExpertConfig(
            name="security_expert",
            description="Cybersecurity expert specializing in application and infrastructure security",
            base_message=base_messages["security_expert"],
            expertise_areas=["threat modeling", "secure coding", "authentication", "compliance"]
        ))
        
        self.register_expert(ExpertConfig(
            name="performance_expert",
            description="Performance engineering expert focusing on optimization and scalability",
            base_message=base_messages["performance_expert"],
            expertise_areas=["performance profiling", "load testing", "caching strategies", "optimization"]
        ))
        
        # Frontend & UX Experts  
        self.register_expert(ExpertConfig(
            name="frontend_expert",
            description="Frontend engineer with expertise in user interfaces and client-side architecture",
            base_message=base_messages["frontend_expert"],
            expertise_areas=["responsive design", "frontend performance", "accessibility", "UI frameworks"]
        ))
        
        self.register_expert(ExpertConfig(
            name="ux_expert",
            description="User experience expert focusing on usability and design principles",
            base_message=base_messages["ux_expert"],
            expertise_areas=["user research", "information architecture", "interaction design", "accessibility"]
        ))
        
        # Data & AI Experts
        self.register_expert(ExpertConfig(
            name="data_expert",
            description="Data engineering expert specializing in data pipelines and analytics",
            base_message=base_messages["data_expert"],
            expertise_areas=["data modeling", "ETL processes", "streaming", "data quality"]
        ))
        
        self.register_expert(ExpertConfig(
            name="ml_expert", 
            description="Machine learning expert focusing on AI/ML system design and implementation",
            base_message=base_messages["ml_expert"],
            expertise_areas=["model selection", "training pipelines", "MLOps", "model monitoring"]
        ))
        
        # Register predefined expert sets
        self.register_expert_set("essentials", [
            "backend_expert", "frontend_expert"
        ])

        self.register_expert_set("default", [
            "database_expert", "backend_expert", "infrastructure_expert"
        ])
        
        self.register_expert_set("architecture", [
            "software_architect", "database_expert", "cloud_engineer"
        ])
        
        self.register_expert_set("full_stack", [
            "backend_expert", "frontend_expert", "database_expert", "infrastructure_expert"
        ])
        
        self.register_expert_set("security_focused", [
            "security_expert", "backend_expert", "infrastructure_expert"
        ])
        
        self.register_expert_set("performance", [
            "performance_expert", "backend_expert", "database_expert"
        ])
        
        self.register_expert_set("data_platform", [
            "data_expert", "backend_expert", "infrastructure_expert"
        ])
        
        self.register_expert_set("ai_system", [
            "ml_expert", "backend_expert", "data_expert", "infrastructure_expert"
        ])
        
        self.register_expert_set("user_focused", [
            "ux_expert", "frontend_expert", "backend_expert"
        ])


# Global registry instance
expert_registry = ExpertRegistry()


# Convenience functions for easy registration
def register_expert(name: str, description: str, base_message: str, expertise_areas: List[str]) -> None:
    """Easy way to register a new expert type"""
    expert = ExpertConfig(
        name=name,
        description=description,
        base_message=base_message,
        expertise_areas=expertise_areas
    )
    expert_registry.register_expert(expert)


def register_expert_set(set_name: str, expert_names: List[str]) -> None:
    """Easy way to register a new expert set"""
    expert_registry.register_expert_set(set_name, expert_names)


def get_expert_config(name: str) -> ExpertConfig:
    """Get expert configuration"""
    return expert_registry.get_expert(name)


def get_expert_set(set_name: str) -> List[str]:
    """Get predefined expert set"""
    return expert_registry.get_expert_set(set_name)


def list_available_experts() -> List[str]:
    """List all available expert types"""
    return expert_registry.list_experts()


def list_available_expert_sets() -> List[str]:
    """List all available expert sets"""
    return expert_registry.list_expert_sets()