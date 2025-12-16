"""
System prompt management for LMAPP.

Allows users to customize AI behavior with system prompts.
Prompts are stored in ~/.lmapp/system_prompt.txt (user) and default prompts by role.
"""

from pathlib import Path
from typing import Optional, Dict
import os


class SystemPromptManager:
    """Manages system prompts for different roles and use cases."""
    
    # Default system prompts for different contexts
    DEFAULT_PROMPTS = {
        "default": """You are LMAPP, a helpful local AI assistant. You provide clear, concise, and accurate answers.
You prioritize user privacy and work entirely offline without telemetry.
Always be honest about your capabilities and limitations.
Format your responses clearly with appropriate markdown when needed.""",
        
        "code": """You are an expert programmer assistant. You help with:
- Code review and suggestions
- Debugging and troubleshooting
- Best practices and design patterns
- Explaining code concepts

Always provide clear code examples with proper formatting.
Specify the programming language when showing code.
Explain the reasoning behind suggestions.""",
        
        "analysis": """You are an analytical assistant skilled in data interpretation and reasoning.
You help with:
- Breaking down complex problems
- Finding patterns and insights
- Logical analysis and critical thinking
- Research and fact-finding

Organize your responses with clear structure and evidence.""",
        
        "creative": """You are a creative writing assistant. You help with:
- Story ideas and plot development
- Character creation
- Writing style and tone
- Creative brainstorming

Be imaginative while maintaining quality and coherence.""",
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize SystemPromptManager.
        
        Args:
            config_dir: Config directory (default: ~/.lmapp/)
        """
        if config_dir is None:
            home = Path.home()
            config_dir = home / ".lmapp"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.custom_prompt_file = self.config_dir / "system_prompt.txt"
    
    def get_prompt(self, role: str = "default") -> str:
        """
        Get system prompt for a given role.
        
        Returns custom prompt if set, otherwise returns default for role.
        
        Args:
            role: Prompt role/context (default, code, analysis, creative)
        
        Returns:
            System prompt string
        """
        # Check for user custom prompt first
        if self.custom_prompt_file.exists():
            try:
                return self.custom_prompt_file.read_text().strip()
            except IOError:
                pass
        
        # Return default for role
        return self.DEFAULT_PROMPTS.get(role, self.DEFAULT_PROMPTS["default"])
    
    def set_custom_prompt(self, prompt: str) -> None:
        """Set a custom system prompt (overwrites all roles)."""
        self.custom_prompt_file.write_text(prompt.strip())
    
    def get_custom_prompt(self) -> Optional[str]:
        """Get the current custom prompt, or None if not set."""
        if self.custom_prompt_file.exists():
            try:
                content = self.custom_prompt_file.read_text().strip()
                return content if content else None
            except IOError:
                return None
        return None
    
    def clear_custom_prompt(self) -> None:
        """Clear the custom prompt and revert to defaults."""
        try:
            self.custom_prompt_file.unlink()
        except FileNotFoundError:
            pass
    
    def get_default_prompt(self, role: str = "default") -> str:
        """Get the default prompt for a role (ignoring custom prompts)."""
        return self.DEFAULT_PROMPTS.get(role, self.DEFAULT_PROMPTS["default"])
    
    def list_available_roles(self) -> list:
        """List available default prompt roles."""
        return list(self.DEFAULT_PROMPTS.keys())
    
    def show_prompt(self, role: str = "default") -> Dict[str, str]:
        """Get detailed prompt information."""
        prompt = self.get_prompt(role)
        is_custom = self.get_custom_prompt() is not None
        
        return {
            "role": role,
            "is_custom": is_custom,
            "prompt": prompt,
            "length": len(prompt),
        }


# Global instance
_prompt_manager: Optional[SystemPromptManager] = None


def get_prompt_manager(config_dir: Optional[Path] = None) -> SystemPromptManager:
    """Get or create the global SystemPromptManager instance."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = SystemPromptManager(config_dir)
    return _prompt_manager
