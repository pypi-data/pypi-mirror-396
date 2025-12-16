#!/usr/bin/env python3
"""
Feature Gating System
Controls access to advanced features based on trial/paid status and Advanced Mode
"""

from typing import Set, List
from dataclasses import dataclass

from lmapp.utils.logging import logger


@dataclass
class FeatureTier:
    """Feature access control for each tier"""
    
    # Free tier features
    FREE_FEATURES = {
        "chat_basic",
        "backend_ollama",
        "cli_interface",
        "status_command",
        "help_command",
        "config_basic",
    }
    
    # Features requiring Advanced Mode (trial/paid)
    ADVANCED_FEATURES = {
        "chat_advanced",  # Multi-backend chat
        "backend_llamafile",
        "backend_mistral",
        "backend_openai",
        "backend_anthropic",
        "backend_groq",
        "backend_cohere",
        "backend_replicate",
        "rag_system",
        "plugin_system",
        "batch_processing",
        "web_ui",
        "sessions",
        "system_prompts",
        "advanced_config",
    }
    
    ALL_FEATURES = FREE_FEATURES | ADVANCED_FEATURES


class FeatureGate:
    """Manages feature access based on user tier"""
    
    def __init__(self, is_trial_active: bool, is_paid_active: bool = False):
        """
        Initialize feature gate
        
        Args:
            is_trial_active: Whether user has active trial
            is_paid_active: Whether user has paid subscription (future)
        """
        self.is_trial_active = is_trial_active
        self.is_paid_active = is_paid_active
    
    def is_advanced_mode_allowed(self) -> bool:
        """Check if Advanced Mode can be enabled"""
        return self.is_trial_active or self.is_paid_active
    
    def get_allowed_features(self, advanced_mode_enabled: bool) -> Set[str]:
        """
        Get set of features user has access to
        
        Args:
            advanced_mode_enabled: Whether Advanced Mode is currently enabled
        
        Returns:
            Set of feature flags user can access
        """
        features = set(FeatureTier.FREE_FEATURES)
        
        if advanced_mode_enabled and self.is_advanced_mode_allowed():
            features.update(FeatureTier.ADVANCED_FEATURES)
        
        return features
    
    def has_feature(self, feature: str, advanced_mode_enabled: bool) -> bool:
        """
        Check if user has access to specific feature
        
        Args:
            feature: Feature name to check
            advanced_mode_enabled: Current Advanced Mode status
        
        Returns:
            True if feature is accessible
        """
        allowed = self.get_allowed_features(advanced_mode_enabled)
        return feature in allowed
    
    def get_restricted_features(self, advanced_mode_enabled: bool) -> Set[str]:
        """Get features user does NOT have access to"""
        all_features = FeatureTier.ALL_FEATURES
        allowed = self.get_allowed_features(advanced_mode_enabled)
        return all_features - allowed
    
    def enforce_feature_access(self, feature: str, advanced_mode_enabled: bool) -> bool:
        """
        Enforce feature access - logs warning if feature is restricted
        
        Args:
            feature: Feature attempting to access
            advanced_mode_enabled: Current Advanced Mode status
        
        Returns:
            True if feature is allowed, False otherwise
        """
        if not self.has_feature(feature, advanced_mode_enabled):
            logger.warning(
                f"Feature '{feature}' requires Advanced Mode (trial or paid subscription)"
            )
            return False
        return True
    
    @staticmethod
    def get_feature_descriptions() -> dict:
        """Get human-readable descriptions of features"""
        return {
            # Free tier
            "chat_basic": "Chat with Ollama",
            "backend_ollama": "Ollama backend support",
            "cli_interface": "Command-line interface",
            "status_command": "System status command",
            "help_command": "Help command",
            "config_basic": "Basic configuration",
            
            # Advanced tier
            "chat_advanced": "Chat with multiple backends",
            "backend_llamafile": "LlamaFile backend support",
            "backend_mistral": "Mistral backend support",
            "backend_openai": "OpenAI backend support",
            "backend_anthropic": "Anthropic backend support",
            "backend_groq": "Groq backend support",
            "backend_cohere": "Cohere backend support",
            "backend_replicate": "Replicate backend support",
            "rag_system": "Retrieval-Augmented Generation (document search)",
            "plugin_system": "Community plugins support",
            "batch_processing": "Batch processing for multiple inputs",
            "web_ui": "Web-based user interface",
            "sessions": "Save and restore conversations",
            "system_prompts": "Custom system prompts library",
            "advanced_config": "Advanced configuration options",
        }


class FeatureGatingMiddleware:
    """
    Middleware for enforcing feature access in CLI commands
    """
    
    def __init__(self, gate: FeatureGate):
        """Initialize middleware with feature gate"""
        self.gate = gate
    
    def require_feature(self, feature: str, advanced_mode_enabled: bool):
        """
        Decorator for CLI commands that require specific feature
        
        Usage:
            @middleware.require_feature("rag_system", config.advanced_mode)
            def cmd_rag_add():
                ...
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.gate.enforce_feature_access(feature, advanced_mode_enabled):
                    raise FeatureAccessDenied(feature)
                return func(*args, **kwargs)
            return wrapper
        return decorator


class FeatureAccessDenied(Exception):
    """Raised when user tries to access restricted feature"""
    
    def __init__(self, feature: str):
        self.feature = feature
        super().__init__(
            f"Feature '{feature}' requires Advanced Mode "
            "(30-day trial or paid subscription)"
        )


# Example usage/testing functions

def create_gate_for_user(is_trial: bool = False, is_paid: bool = False) -> FeatureGate:
    """Factory function for creating feature gates"""
    return FeatureGate(is_trial_active=is_trial, is_paid_active=is_paid)


def display_feature_matrix():
    """Display feature access matrix for all tiers"""
    print("\n" + "="*60)
    print("LMAPP Feature Access Matrix")
    print("="*60 + "\n")
    
    descriptions = FeatureGate.get_feature_descriptions()
    
    # Create gates for each tier
    free = create_gate_for_user(is_trial=False, is_paid=False)
    trial = create_gate_for_user(is_trial=True, is_paid=False)
    paid = create_gate_for_user(is_trial=False, is_paid=True)
    
    print(f"{'Feature':<35} {'Free':<8} {'Trial':<8} {'Paid':<8}")
    print("-" * 60)
    
    for feature in sorted(FeatureTier.ALL_FEATURES):
        desc = descriptions.get(feature, feature)[:33]
        free_access = "✓" if free.has_feature(feature, False) else "-"
        trial_access = "✓" if trial.has_feature(feature, True) else "-"
        paid_access = "✓" if paid.has_feature(feature, True) else "-"
        
        print(f"{desc:<35} {free_access:<8} {trial_access:<8} {paid_access:<8}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Test/display feature matrix
    display_feature_matrix()
