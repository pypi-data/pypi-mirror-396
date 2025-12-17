"""
Expert Manager - Easy interface for creating and managing expert agents
"""

from typing import List, Dict, Any, Optional
from .agents import create_expert_agents, create_team_expert_agents
from .expert_registry import (
    register_expert, register_expert_set, 
    list_available_experts, list_available_expert_sets,
    get_expert_set
)
from ..config import ProviderType


class ExpertManager:
    """High-level interface for expert agent management"""
    
    @staticmethod
    def create_experts(
        config: str = "default",
        provider: ProviderType = None
    ) -> List[Any]:
        """Create expert agents using a configuration
        
        Args:
            config: Either an expert set name or comma-separated expert names
            provider: Provider to use for all agents
            
        Examples:
            # Use predefined sets
            experts = ExpertManager.create_experts("full_stack")
            experts = ExpertManager.create_experts("security_focused")
            
            # Use specific experts
            experts = ExpertManager.create_experts("database_expert,security_expert,performance_expert")
        """
        # Check if it's a comma-separated list of experts
        if "," in config:
            expert_types = [name.strip() for name in config.split(",")]
            return create_expert_agents(expert_types=expert_types, provider=provider)
        
        # Otherwise treat as expert set
        return create_expert_agents(expert_set=config, provider=provider)
    
    @staticmethod 
    def create_teams(
        config: str = "default"
    ) -> Dict[str, List[Any]]:
        """Create expert teams using a configuration
        
        Args:
            config: Either an expert set name or comma-separated expert names
            
        Examples:
            # Use predefined sets
            teams = ExpertManager.create_teams("ai_system")
            teams = ExpertManager.create_teams("performance")
            
            # Use specific experts
            teams = ExpertManager.create_teams("ml_expert,data_expert,backend_expert")
        """
        # Check if it's a comma-separated list of experts
        if "," in config:
            expert_types = [name.strip() for name in config.split(",")]
            return create_team_expert_agents(expert_types=expert_types)
        
        # Otherwise treat as expert set
        return create_team_expert_agents(expert_set=config)
    
    @staticmethod
    def add_expert(
        name: str,
        description: str, 
        base_message: str,
        expertise_areas: List[str]
    ) -> None:
        """Add a new expert type
        
        Example:
            ExpertManager.add_expert(
                name="blockchain_expert",
                description="Blockchain and cryptocurrency expert",
                base_message="You are a blockchain expert...",
                expertise_areas=["smart contracts", "consensus algorithms", "tokenomics"]
            )
        """
        register_expert(name, description, base_message, expertise_areas)
    
    @staticmethod
    def add_expert_set(name: str, experts: List[str]) -> None:
        """Add a new expert set
        
        Example:
            ExpertManager.add_expert_set("web3", ["blockchain_expert", "security_expert", "backend_expert"])
        """
        register_expert_set(name, experts)
    
    @staticmethod
    def list_experts() -> List[str]:
        """List all available expert types"""
        return list_available_experts()
    
    @staticmethod
    def list_expert_sets() -> List[str]:
        """List all available expert sets"""
        return list_available_expert_sets()
    
    @staticmethod
    def describe_expert_set(set_name: str) -> Dict[str, Any]:
        """Get detailed information about an expert set"""
        from .expert_registry import get_expert_config
        
        expert_names = get_expert_set(set_name)
        return {
            "name": set_name,
            "experts": expert_names,
            "count": len(expert_names),
            "descriptions": {
                name: get_expert_config(name).description 
                for name in expert_names
            }
        }
    
    @staticmethod
    def print_available_configurations():
        """Print a nice overview of available configurations"""
        print("🚀 Available Expert Configurations\n")
        
        print("📋 Expert Sets:")
        for set_name in sorted(ExpertManager.list_expert_sets()):
            info = ExpertManager.describe_expert_set(set_name)
            experts_str = ", ".join(info["experts"])
            print(f"  • {set_name}: {experts_str}")
        
        print(f"\n👥 Individual Experts ({len(ExpertManager.list_experts())} available):")
        for expert in sorted(ExpertManager.list_experts()):
            try:
                from .expert_registry import get_expert_config
                config = get_expert_config(expert)
                print(f"  • {expert}: {config.description}")
            except:
                print(f"  • {expert}")
        
        print(f"\n💡 Usage Examples:")
        print(f"  ExpertManager.create_experts('security_focused')")
        print(f"  ExpertManager.create_experts('database_expert,security_expert')")
        print(f"  ExpertManager.create_teams('ai_system')")


# Convenience functions for easy imports
def create_experts(config: str = "default", provider: ProviderType = None):
    """Shortcut to create experts"""
    return ExpertManager.create_experts(config, provider)

def create_teams(config: str = "default"):
    """Shortcut to create teams"""
    return ExpertManager.create_teams(config)

def add_expert(name: str, description: str, base_message: str, expertise_areas: List[str]):
    """Shortcut to add expert"""
    return ExpertManager.add_expert(name, description, base_message, expertise_areas)

def list_configurations():
    """Shortcut to print configurations"""
    return ExpertManager.print_available_configurations()