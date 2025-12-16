"""
Git Flow Helper Plugin for LMAPP v0.2.5.

Provides Git Flow branching and workflow automation.
Simplifies feature, release, and hotfix branch management.

Features:
- Feature branch creation/completion
- Release branch management
- Hotfix branch automation
- Commit message formatting
- Pull request workflow guidance
- Branch naming conventions

Usage:
    plugin = GitFlowPlugin()
    plugin.initialize({"repo_path": "/path/to/repo"})
    result = plugin.execute(action="feature-start", name="AUTH")
    # Returns: {"status": "success", "branch": "feature/AUTH", "message": "..."}

Supported Actions:
- feature-start: Create feature branch
- feature-finish: Merge feature branch
- release-start: Create release branch
- release-finish: Close release branch
- hotfix-start: Create hotfix branch
- hotfix-finish: Close hotfix branch
"""

from typing import Dict, Optional, Any, Callable, List
from dataclasses import dataclass, field
import re

from .plugin_manager import BasePlugin, PluginMetadata


@dataclass
class GitFlowState:
    """Represents Git Flow state and history."""

    current_branch: str = "main"
    last_feature: Optional[str] = None
    last_release: Optional[str] = None
    last_hotfix: Optional[str] = None
    created_branches: List[str] = field(default_factory=list)
    completed_branches: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_branch": self.current_branch,
            "last_feature": self.last_feature,
            "last_release": self.last_release,
            "last_hotfix": self.last_hotfix,
            "created_branches": self.created_branches,
            "completed_branches": self.completed_branches,
        }


@dataclass
class BranchTemplate:
    """Template for Git Flow branches."""

    name: str
    prefix: str
    base_branch: str
    description: str
    merge_target: str

    def create_branch_name(self, feature_name: str) -> str:
        """Create branch name from template."""
        # Sanitize feature name
        clean_name = re.sub(r"[^a-zA-Z0-9_-]", "", feature_name.upper())
        return f"{self.prefix}/{clean_name}"


class GitFlowPlugin(BasePlugin):
    """
    Git Flow plugin for automated branch management.

    Implements Git Flow workflow with feature, release, and hotfix branches.
    """

    # Branch templates
    TEMPLATES = {
        "feature": BranchTemplate(
            name="Feature",
            prefix="feature",
            base_branch="develop",
            description="Feature development branch",
            merge_target="develop",
        ),
        "release": BranchTemplate(
            name="Release",
            prefix="release",
            base_branch="develop",
            description="Release preparation branch",
            merge_target="main",
        ),
        "hotfix": BranchTemplate(
            name="Hotfix",
            prefix="hotfix",
            base_branch="main",
            description="Production hotfix branch",
            merge_target="main",
        ),
    }

    # Commit message templates
    COMMIT_TEMPLATES = {
        "feature_start": "feat: start {name} feature",
        "feature_finish": "feat: complete {name} feature",
        "release_start": "release: start {version} release",
        "release_finish": "release: finalize {version}",
        "hotfix_start": "hotfix: start {version} hotfix",
        "hotfix_finish": "hotfix: complete {version} hotfix",
    }

    def __init__(self):
        """Initialize Git Flow plugin."""
        self._metadata = PluginMetadata(
            name="git-flow",
            version="0.1.0",
            description="Git Flow branch and workflow automation",
            author="LMAPP Team",
            license="MIT",
            dependencies=[],
            entry_point="example_git_flow:GitFlowPlugin",
            tags=["git", "git-flow", "branching", "workflow", "devops"],
        )
        self.repo_path = None
        self.state = GitFlowState()
        self.stats = {
            "features_created": 0,
            "features_completed": 0,
            "releases_created": 0,
            "hotfixes_created": 0,
        }

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return self._metadata

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Git Flow plugin.

        Args:
            config: Configuration dict with keys:
                - repo_path: Path to git repository
        """
        if config:
            self.repo_path = config.get("repo_path")

    def _validate_branch_name(self, name: str) -> tuple[bool, str]:
        """
        Validate branch name.

        Returns:
            (is_valid, error_message)
        """
        if not name or len(name) < 1:
            return False, "Branch name cannot be empty"

        if len(name) > 50:
            return False, "Branch name must be less than 50 characters"

        # Allow dots for version numbers, alphanumeric, hyphens, underscores
        if not re.match(r"^[a-zA-Z0-9_.\-]+$", name):
            return (
                False,
                "Branch name can only contain letters, numbers, hyphens, dots, and underscores",
            )

        return True, ""

    def _create_feature_branch(self, name: str) -> Dict[str, Any]:
        """Create a feature branch."""
        is_valid, error = self._validate_branch_name(name)
        if not is_valid:
            return {"status": "error", "message": error}

        template = self.TEMPLATES["feature"]
        branch_name = template.create_branch_name(name)
        commit_msg = self.COMMIT_TEMPLATES["feature_start"].format(name=name)

        # Track state
        self.state.last_feature = branch_name
        self.state.created_branches.append(branch_name)
        self.state.current_branch = branch_name
        self.stats["features_created"] += 1

        return {
            "status": "success",
            "action": "feature-start",
            "branch": branch_name,
            "base_branch": template.base_branch,
            "merge_target": template.merge_target,
            "commit_message": commit_msg,
            "instructions": f"Created feature branch '{branch_name}' from '{template.base_branch}'",
        }

    def _create_release_branch(self, version: str) -> Dict[str, Any]:
        """Create a release branch."""
        is_valid, error = self._validate_branch_name(version)
        if not is_valid:
            return {"status": "error", "message": error}

        template = self.TEMPLATES["release"]
        branch_name = f"{template.prefix}/{version}"
        commit_msg = self.COMMIT_TEMPLATES["release_start"].format(version=version)

        # Track state
        self.state.last_release = branch_name
        self.state.created_branches.append(branch_name)
        self.state.current_branch = branch_name
        self.stats["releases_created"] += 1

        return {
            "status": "success",
            "action": "release-start",
            "branch": branch_name,
            "base_branch": template.base_branch,
            "merge_target": template.merge_target,
            "version": version,
            "commit_message": commit_msg,
            "instructions": f"Created release branch '{branch_name}' for version {version}",
        }

    def _create_hotfix_branch(self, version: str) -> Dict[str, Any]:
        """Create a hotfix branch."""
        is_valid, error = self._validate_branch_name(version)
        if not is_valid:
            return {"status": "error", "message": error}

        template = self.TEMPLATES["hotfix"]
        branch_name = f"{template.prefix}/{version}"
        commit_msg = self.COMMIT_TEMPLATES["hotfix_start"].format(version=version)

        # Track state
        self.state.last_hotfix = branch_name
        self.state.created_branches.append(branch_name)
        self.state.current_branch = branch_name
        self.stats["hotfixes_created"] += 1

        return {
            "status": "success",
            "action": "hotfix-start",
            "branch": branch_name,
            "base_branch": template.base_branch,
            "merge_target": template.merge_target,
            "version": version,
            "commit_message": commit_msg,
            "instructions": f"Created hotfix branch '{branch_name}' for version {version}",
        }

    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute Git Flow action.

        Args:
            action: Git Flow action (feature-start, release-start, hotfix-start, etc.)
            name: Feature/version name

        Returns:
            Dict with action results
        """
        action = kwargs.get("action", "")
        name = kwargs.get("name", "")

        if not action:
            return {
                "status": "error",
                "message": "action parameter required",
                "available_actions": [
                    "feature-start",
                    "feature-finish",
                    "release-start",
                    "release-finish",
                    "hotfix-start",
                    "hotfix-finish",
                ],
            }

        if not name:
            return {"status": "error", "message": "name/version parameter required"}

        # Route to appropriate handler
        if action == "feature-start":
            return self._create_feature_branch(name)
        elif action == "release-start":
            return self._create_release_branch(name)
        elif action == "hotfix-start":
            return self._create_hotfix_branch(name)
        elif action == "feature-finish":
            return self._complete_branch("feature", name)
        elif action == "release-finish":
            return self._complete_release(name)
        elif action == "hotfix-finish":
            return self._complete_hotfix(name)
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}",
                "available_actions": [
                    "feature-start",
                    "feature-finish",
                    "release-start",
                    "release-finish",
                    "hotfix-start",
                    "hotfix-finish",
                ],
            }

    def _complete_branch(self, branch_type: str, name: str) -> Dict[str, Any]:
        """Complete a feature/hotfix branch."""
        self.stats["features_completed"] += 1
        self.state.completed_branches.append(f"{branch_type}/{name}")

        return {
            "status": "success",
            "action": f"{branch_type}-finish",
            "branch": f"{branch_type}/{name}",
            "message": f"Completed {branch_type} branch '{name}'",
        }

    def _complete_release(self, version: str) -> Dict[str, Any]:
        """Complete a release."""
        commit_msg = self.COMMIT_TEMPLATES["release_finish"].format(version=version)

        return {
            "status": "success",
            "action": "release-finish",
            "branch": f"release/{version}",
            "version": version,
            "commit_message": commit_msg,
            "message": f"Completed release {version}",
        }

    def _complete_hotfix(self, version: str) -> Dict[str, Any]:
        """Complete a hotfix."""
        commit_msg = self.COMMIT_TEMPLATES["hotfix_finish"].format(version=version)

        return {
            "status": "success",
            "action": "hotfix-finish",
            "branch": f"hotfix/{version}",
            "version": version,
            "commit_message": commit_msg,
            "message": f"Completed hotfix {version}",
        }

    def cleanup(self) -> None:
        """Cleanup when plugin is unloaded."""
        self.state = GitFlowState()
        self.stats = {
            "features_created": 0,
            "features_completed": 0,
            "releases_created": 0,
            "hotfixes_created": 0,
        }

    def get_commands(self) -> Dict[str, Callable]:
        """Get CLI commands provided by this plugin."""
        return {
            "feature": self._feature_command,
            "release": self._release_command,
            "hotfix": self._hotfix_command,
            "git-flow-status": self._status_command,
        }

    def _feature_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: manage feature branches."""
        subcommand = kwargs.get("subcommand", "start")
        name = kwargs.get("name", "")

        if subcommand == "start":
            return self._create_feature_branch(name)
        elif subcommand == "finish":
            return self._complete_branch("feature", name)
        else:
            return {"error": "Unknown subcommand"}

    def _release_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: manage release branches."""
        subcommand = kwargs.get("subcommand", "start")
        version = kwargs.get("version", "")

        if subcommand == "start":
            return self._create_release_branch(version)
        elif subcommand == "finish":
            return self._complete_release(version)
        else:
            return {"error": "Unknown subcommand"}

    def _hotfix_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: manage hotfix branches."""
        subcommand = kwargs.get("subcommand", "start")
        version = kwargs.get("version", "")

        if subcommand == "start":
            return self._create_hotfix_branch(version)
        elif subcommand == "finish":
            return self._complete_hotfix(version)
        else:
            return {"error": "Unknown subcommand"}

    def _status_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: show Git Flow status."""
        return {
            "state": self.state.to_dict(),
            "stats": self.stats.copy(),
        }


# Export for marketplace registration
__all__ = ["GitFlowPlugin", "GitFlowState", "BranchTemplate"]


# Marketplace registration metadata
PLUGIN_MANIFEST = {
    "name": "git-flow",
    "version": "0.1.0",
    "author": "LMAPP Team",
    "description": "Git Flow branch and workflow automation",
    "repository": "https://github.com/nabaznyl/lmapp/tree/mother/src/lmapp/plugins",
    "install_url": "https://github.com/nabaznyl/lmapp/raw/mother/src/lmapp/plugins/example_git_flow.py",
    "tags": ["git", "git-flow", "branching", "workflow", "devops"],
    "dependencies": [],
    "license": "MIT",
}
