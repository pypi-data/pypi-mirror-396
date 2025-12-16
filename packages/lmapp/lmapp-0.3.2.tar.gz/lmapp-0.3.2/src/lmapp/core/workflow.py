"""
Workflow Calibration Manager
Handles user preferences for AI behavior, tools, and operating rules.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.prompt import Confirm, Prompt, IntPrompt
from rich.panel import Panel

from lmapp.core.config import get_config_manager

console = Console()

class WorkflowManager:
    def __init__(self):
        self.config_dir = Path(os.path.expanduser("~/.config/lmapp"))
        self.rules_file = self.config_dir / "workflow_rules.json"
        self.config_manager = get_config_manager()
        
        # Default rules structure
        self.default_rules = {
            "ask_first": True,
            "minimal_changes": True,
            "tools": [
                "vscode", "github copilot", "agent", "edit", "execute", 
                "read", "search", "todo", "web", "gitkraken", 
                "pylance mcp server", "python"
            ],
            "custom_instructions": ""
        }

    def load_rules(self) -> Dict:
        """Load rules from disk or return defaults."""
        if self.rules_file.exists():
            try:
                return json.loads(self.rules_file.read_text())
            except json.JSONDecodeError:
                return self.default_rules
        return self.default_rules

    def save_rules(self, rules: Dict):
        """Save rules to disk."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.rules_file.write_text(json.dumps(rules, indent=2))

    def should_prompt(self) -> bool:
        """Check if we should prompt the user for setup."""
        config = self.config_manager.get()
        return (not config.workflow_setup_completed) and (not config.suppress_workflow_prompt)

    def run_setup_wizard(self):
        """Interactive wizard to configure workflow."""
        console.print(Panel("[bold cyan]Roles & Workflows Setup[/bold cyan]\n\nLet's configure how your AI assistant behaves.", border_style="cyan"))
        
        rules = self.load_rules()
        
        # 1. Operating Mode
        console.print("\n[bold]1. Operating Mode[/bold]")
        rules["ask_first"] = Confirm.ask(
            "Should the AI ask clarifying questions before implementing changes?", 
            default=rules.get("ask_first", True)
        )
        
        rules["minimal_changes"] = Confirm.ask(
            "Should the AI make minimal, targeted changes (vs. comprehensive refactors)?", 
            default=rules.get("minimal_changes", True)
        )

        # 2. Tools
        console.print("\n[bold]2. Tool Awareness[/bold]")
        console.print(f"[dim]Current tools: {', '.join(rules.get('tools', []))}[/dim]")
        if Confirm.ask("Would you like to edit the list of available tools?", default=False):
            tools_str = Prompt.ask("Enter tools (comma separated)", default=", ".join(rules.get("tools", [])))
            rules["tools"] = [t.strip() for t in tools_str.split(",") if t.strip()]

        # 3. Custom Instructions
        console.print("\n[bold]3. Custom Instructions[/bold]")
        rules["custom_instructions"] = Prompt.ask(
            "Any specific instructions? (e.g., 'Always explain why')", 
            default=rules.get("custom_instructions", "")
        )

        # Save
        self.save_rules(rules)
        
        # Update Config
        self.config_manager.update(workflow_setup_completed=True)
        
        console.print("\n[bold green]✓ Roles & Workflows Setup Complete![/bold green]")
        console.print(f"Rules saved to: {self.rules_file}")

    def generate_system_prompt(self) -> str:
        """Generate the system prompt based on current rules."""
        rules = self.load_rules()
        
        prompt = """You are a calibrated AI assistant.
Your core operating rules are:
"""
        if rules.get("ask_first"):
            prompt += "1. Ask specific clarifying questions before implementing changes.\n"
            prompt += "2. Treat exploratory discussion as exploration, not authorization.\n"
        
        if rules.get("minimal_changes"):
            prompt += "3. Make minimal, targeted changes (do exactly what is asked, no more).\n"
            prompt += "4. Never assume the user wants a comprehensive fix if they ask for a specific detail.\n"
            
        if rules.get("custom_instructions"):
            prompt += f"\nUser Instructions: {rules['custom_instructions']}\n"
            
        if rules.get("tools"):
            prompt += "\nYou have access to the following tools:\n"
            for tool in rules["tools"]:
                prompt += f"- {tool}\n"
                
        return prompt
