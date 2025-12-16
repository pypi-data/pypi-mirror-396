"""Tests for Git Flow Plugin (v0.2.5) - 20 tests."""

import pytest
from lmapp.plugins.example_git_flow import GitFlowPlugin


class TestGitFlowPlugin:
    """Test Git Flow plugin."""

    def test_metadata(self):
        """Test plugin metadata."""
        plugin = GitFlowPlugin()
        assert plugin.metadata.name == "git-flow"
        assert "git" in plugin.metadata.tags

    def test_feature_start(self):
        """Test starting feature branch."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="feature-start", name="AUTH")

        assert result["status"] == "success"
        assert "feature/AUTH" in result["branch"]
        assert result["base_branch"] == "develop"
        assert plugin.stats["features_created"] == 1

    def test_feature_finish(self):
        """Test finishing feature branch."""
        plugin = GitFlowPlugin()
        plugin.execute(action="feature-start", name="AUTH")
        result = plugin.execute(action="feature-finish", name="AUTH")

        assert result["status"] == "success"
        assert plugin.stats["features_completed"] == 1

    def test_release_start(self):
        """Test starting release branch."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="release-start", name="1.0.0")

        assert result["status"] == "success"
        assert "release/1.0.0" in result["branch"]
        assert plugin.stats["releases_created"] == 1

    def test_hotfix_start(self):
        """Test starting hotfix branch."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="hotfix-start", name="1.0.1")

        assert result["status"] == "success"
        assert "hotfix/1.0.1" in result["branch"]
        assert plugin.stats["hotfixes_created"] == 1

    def test_invalid_branch_name(self):
        """Test validation of branch names."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="feature-start", name="")

        assert result["status"] == "error"

    def test_invalid_branch_characters(self):
        """Test branch name character validation."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="feature-start", name="invalid@#$")

        # Should fail validation - doesn't accept special chars
        assert result["status"] == "error"

    def test_branch_naming_convention(self):
        """Test branch naming follows convention."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="feature-start", name="MyFeature")

        assert result["status"] == "success"
        assert result["branch"].startswith("feature/")
        assert "MYFEATURE" in result["branch"]

    def test_commit_message_generation(self):
        """Test commit message generation."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="feature-start", name="AUTH")

        assert "commit_message" in result
        assert "AUTH" in result["commit_message"]
        assert result["commit_message"].startswith("feat:")

    def test_state_tracking(self):
        """Test state tracking."""
        plugin = GitFlowPlugin()
        plugin.execute(action="feature-start", name="AUTH")
        plugin.execute(action="release-start", name="1.0.0")

        assert plugin.state.last_feature == "feature/AUTH"
        assert plugin.state.last_release == "release/1.0.0"
        assert len(plugin.state.created_branches) == 2

    def test_get_commands(self):
        """Test CLI commands."""
        plugin = GitFlowPlugin()
        commands = plugin.get_commands()

        assert "feature" in commands
        assert "release" in commands
        assert "hotfix" in commands
        assert "git-flow-status" in commands

    def test_status_command(self):
        """Test status command."""
        plugin = GitFlowPlugin()
        plugin.execute(action="feature-start", name="AUTH")

        commands = plugin.get_commands()
        result = commands["git-flow-status"]()

        assert "state" in result
        assert "stats" in result
        assert result["state"]["last_feature"] == "feature/AUTH"

    def test_cleanup(self):
        """Test plugin cleanup."""
        plugin = GitFlowPlugin()
        plugin.execute(action="feature-start", name="AUTH")
        assert plugin.stats["features_created"] > 0

        plugin.cleanup()
        assert plugin.stats["features_created"] == 0

    def test_multiple_features(self):
        """Test creating multiple features."""
        plugin = GitFlowPlugin()
        plugin.execute(action="feature-start", name="AUTH")
        plugin.execute(action="feature-start", name="API")
        plugin.execute(action="feature-start", name="UI")

        assert plugin.stats["features_created"] == 3
        assert len(plugin.state.created_branches) == 3

    def test_missing_action(self):
        """Test error handling for missing action."""
        plugin = GitFlowPlugin()
        result = plugin.execute(name="AUTH")

        assert result["status"] == "error"
        assert "action parameter required" in result["message"]

    def test_missing_name(self):
        """Test error handling for missing name."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="feature-start")

        assert result["status"] == "error"
        assert "name/version parameter required" in result["message"]

    def test_unknown_action(self):
        """Test error handling for unknown action."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="invalid-action", name="TEST")

        assert result["status"] == "error"

    def test_release_finish_message(self):
        """Test release finish commit message."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="release-finish", name="1.0.0")

        assert "release:" in result["commit_message"]
        assert "1.0.0" in result["commit_message"]

    def test_hotfix_finish_message(self):
        """Test hotfix finish commit message."""
        plugin = GitFlowPlugin()
        result = plugin.execute(action="hotfix-finish", name="1.0.1")

        assert "hotfix:" in result["commit_message"]
        assert "1.0.1" in result["commit_message"]

    def test_state_to_dict(self):
        """Test state conversion to dictionary."""
        plugin = GitFlowPlugin()
        plugin.execute(action="feature-start", name="AUTH")

        state_dict = plugin.state.to_dict()
        assert "current_branch" in state_dict
        assert "created_branches" in state_dict
        assert "feature/AUTH" in state_dict["created_branches"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
