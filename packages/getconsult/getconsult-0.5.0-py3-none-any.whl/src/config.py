"""
Configuration management for Consult

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.

API keys are loaded from:
1. Environment variables (highest priority)
2. Project .env file
3. ~/.consult/.env (fallback for user-wide configuration)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Literal, Optional
from .core.exceptions import MissingAPIKeyError, InvalidProviderError
from .core.paths import get_env_path


def _load_env_files():
    """Load .env files in priority order.

    Priority (highest first):
    1. Environment variables already set
    2. Project-level .env file
    3. ~/.consult/.env (user-wide fallback)
    """
    # Load project .env first (this doesn't override existing env vars)
    load_dotenv()

    # Load ~/.consult/.env as fallback (also doesn't override)
    consult_env = get_env_path()
    if consult_env.exists():
        load_dotenv(consult_env)


# Load environment files
_load_env_files()

# Type definitions for configuration
ProviderType = Literal["openai", "anthropic", "google"]
ModeType = Literal["single", "team"]

class Config:
    """Configuration management for single provider and multi-team modes"""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration (with .env overrides)
    # Defaults optimized for cost/quality balance (Dec 2025)
    # - Haiku 4.5: 73% SWE-bench, extended thinking, $1/$5 per 1M tokens
    # - GPT-4o-mini: 82% MMLU, 87% HumanEval, $0.15/$0.60 per 1M tokens
    # - Gemini 2.5 Flash-Lite: fastest/cheapest in 2.5 family, $0.10/$0.40 per 1M tokens
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    # State-of-the-Art Model for Distinguished Engineer meta-reviewer
    # Update this when switching to newer frontier models
    SOTA_MODEL = os.getenv("SOTA_MODEL", "claude-opus-4-5-20251101")
    SOTA_PROVIDER: ProviderType = "anthropic"  # Opus 4.5 is Anthropic
    
    # Default Configuration
    DEFAULT_MODE: ModeType = "single"
    DEFAULT_SINGLE_PROVIDER: ProviderType = "anthropic" 
    
    # Team Configuration
    TEAM_PROVIDERS = ["openai", "anthropic", "google"]
    ORCHESTRATOR_PROVIDER = "anthropic"  # Always Claude for orchestrator
    
    @classmethod
    def validate_config(cls, mode: ModeType = "single", provider: Optional[ProviderType] = None) -> bool:
        """Validate configuration based on mode and provider"""
        if mode == "single":
            # For single mode, validate the specified provider or default
            target_provider = provider or cls.DEFAULT_SINGLE_PROVIDER
            return cls._validate_provider(target_provider)
        
        elif mode == "team":
            # For team mode, validate all team providers are available
            available_providers = []
            for team_provider in cls.TEAM_PROVIDERS:
                if cls._validate_provider(team_provider):
                    available_providers.append(team_provider)
            
            # Need at least 2 providers for meaningful team competition
            return len(available_providers) >= 2
        
        return False
    
    @classmethod
    def _validate_provider(cls, provider: ProviderType) -> bool:
        """Validate a specific provider has API key"""
        if provider == "openai":
            return bool(cls.OPENAI_API_KEY)
        elif provider == "anthropic":
            return bool(cls.ANTHROPIC_API_KEY)
        elif provider == "google":
            return bool(cls.GOOGLE_API_KEY)
        return False
    
    @classmethod
    def get_available_providers(cls) -> list[ProviderType]:
        """Get list of providers with valid API keys"""
        available = []
        for provider in ["anthropic", "openai", "google"]:
            if cls._validate_provider(provider):
                available.append(provider)
        return available
    
    @classmethod
    def get_team_providers(cls) -> list[ProviderType]:
        """Get list of available providers for team mode"""
        available_teams = []
        for provider in cls.TEAM_PROVIDERS:
            if cls._validate_provider(provider):
                available_teams.append(provider)
        return available_teams
    
    @classmethod
    def get_model_for_provider(cls, provider: ProviderType) -> str:
        """Get the model name for a specific provider"""
        if provider == "openai":
            return cls.OPENAI_MODEL
        elif provider == "anthropic":
            return cls.ANTHROPIC_MODEL
        elif provider == "google":
            return cls.GEMINI_MODEL
        else:
            available_providers = ["openai", "anthropic", "google"]
            raise InvalidProviderError(provider, available_providers)