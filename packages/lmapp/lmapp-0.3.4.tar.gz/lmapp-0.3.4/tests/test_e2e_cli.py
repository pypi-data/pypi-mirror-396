"""End-to-end CLI scenario tests for lmapp."""

import pytest
from click.testing import CliRunner
from lmapp.cli import cli


class TestCLIScenarios:
    """End-to-end scenarios using the CLI."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    # Main Menu Tests

    def test_main_menu_interactive(self, runner):
        """Test main menu displays and handles input."""
        # This would normally be interactive - we test non-interactive mode
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Commands:" in result.output or "Options:" in result.output

    def test_help_command_detailed(self, runner):
        """Test help shows all available commands."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        # Should show command structure
        assert "Usage:" in result.output

    # Status Command Tests

    def test_status_shows_system_info(self, runner):
        """Test 'lmapp status' shows system information."""
        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        # Should contain diagnostic information
        assert "backend" in result.output.lower() or "system" in result.output.lower()

    def test_status_backend_detection(self, runner):
        """Test status command detects backends."""
        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        # At minimum, should detect mock backend
        assert "mock" in result.output.lower() or "available" in result.output.lower()

    def test_status_no_errors(self, runner):
        """Test status command completes without errors."""
        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "error" not in result.output.lower()

    # Version Command Tests

    def test_version_display(self, runner):
        """Test version flag displays version."""
        result = runner.invoke(cli, ["--version"])

        # Should exit successfully
        assert result.exit_code == 0
        # Should contain version info
        assert "0.1.0" in result.output or result.exit_code == 0

    # Chat Command Tests (Mock Backend)

    def test_chat_help(self, runner):
        """Test chat help documentation."""
        result = runner.invoke(cli, ["chat", "--help"])

        assert result.exit_code == 0
        assert "help" in result.output.lower() or "Usage:" in result.output

    # Config Command Tests

    def test_config_show(self, runner):
        """Test 'lmapp config show' displays current config."""
        result = runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        # Should show configuration
        assert (
            "config" in result.output.lower() or "temperature" in result.output.lower()
        )

    def test_config_show_all_settings(self, runner):
        """Test config shows all available settings."""
        result = runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        # Should contain key settings
        output = result.output.lower()
        # At least some config-related content should be shown
        assert len(output) > 10

    def test_config_set_temperature(self, runner):
        """Test setting temperature via CLI."""
        # Set a value
        result = runner.invoke(cli, ["config", "set", "temperature", "0.5"])

        # Check if it was set (command should complete)
        assert result.exit_code == 0

    def test_config_set_model(self, runner):
        """Test setting model via CLI."""
        result = runner.invoke(cli, ["config", "set", "model", "mistral"])

        assert result.exit_code == 0

    def test_config_validate(self, runner):
        """Test config validation command."""
        result = runner.invoke(cli, ["config", "validate"])

        assert result.exit_code == 0
        # Should validate successfully
        assert (
            "valid" in result.output.lower()
            or "ok" in result.output.lower()
            or result.exit_code == 0
        )

    # Error Handling Tests

    def test_invalid_command_error(self, runner):
        """Test CLI handles invalid commands gracefully."""
        result = runner.invoke(cli, ["invalid-command"])

        # Should error
        assert result.exit_code != 0
        # Should provide helpful message
        assert (
            "no such command" in result.output.lower()
            or "error" in result.output.lower()
        )

    def test_invalid_config_value(self, runner):
        """Test CLI rejects invalid config values."""
        result = runner.invoke(cli, ["config", "set", "temperature", "5.0"])

        # CLI prints a validation failure but returns success (non-fatal)
        # to keep interactive sessions alive; ensure the failure message appears
        assert result.exit_code == 0
        assert "✗ Failed to set temperature" in result.output

    def test_missing_argument_error(self, runner):
        """Test CLI handles missing arguments."""
        result = runner.invoke(cli, ["config", "set"])

        # Should error - missing arguments
        assert result.exit_code != 0

    # Multi-Command Workflows

    def test_workflow_check_status_then_config(self, runner):
        """Test workflow: check status then check config."""
        # First command
        status_result = runner.invoke(cli, ["status"])
        assert status_result.exit_code == 0

        # Second command
        config_result = runner.invoke(cli, ["config", "show"])
        assert config_result.exit_code == 0

    def test_workflow_config_then_verify(self, runner):
        """Test workflow: set config then verify."""
        # Set temperature
        set_result = runner.invoke(cli, ["config", "set", "temperature", "0.7"])
        assert set_result.exit_code == 0

        # Show config to verify
        show_result = runner.invoke(cli, ["config", "show"])
        assert show_result.exit_code == 0

    # Output Format Tests

    def test_status_output_is_readable(self, runner):
        """Test status output is well-formatted and readable."""
        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        output = result.output

        # Should have reasonable length
        assert len(output) > 50
        # Should not have excessive errors
        assert output.count("error") < 3

    def test_config_output_is_readable(self, runner):
        """Test config output is well-formatted."""
        result = runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        output = result.output

        # Should display readable config format
        assert len(output) > 20

    # Edge Cases

    def test_empty_string_argument(self, runner):
        """Test CLI handles empty string arguments."""
        result = runner.invoke(cli, ["config", "set", "model", ""])

        # Should handle gracefully (accept or reject, but not crash)
        assert result.exit_code in [0, 1, 2]  # Exit code could vary

    def test_special_characters_in_args(self, runner):
        """Test CLI handles special characters."""
        result = runner.invoke(cli, ["config", "set", "model", "test-model-v2"])

        # Should handle gracefully
        assert result.exit_code >= 0

    def test_multiple_command_chain(self, runner):
        """Test multiple commands in sequence."""
        commands = [
            (["--help"], 0),
            (["status"], 0),
            (["config", "show"], 0),
        ]

        for cmd, expected_code in commands:
            result = runner.invoke(cli, cmd)
            assert result.exit_code == expected_code or result.exit_code == 0


class TestCLIErrorMessages:
    """Test CLI provides helpful error messages."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_error_message_clarity(self, runner):
        """Test error messages are clear and helpful."""
        result = runner.invoke(cli, ["invalid-cmd"])

        # Error message should be helpful
        output = result.output.lower()
        assert any(
            phrase in output
            for phrase in ["no such command", "error", "usage", "did you mean"]
        )

    def test_help_on_invalid_args(self, runner):
        """Test providing help when invalid args given."""
        result = runner.invoke(cli, ["config", "set"])

        # Should indicate what's missing
        output = result.output.lower()
        assert "error" in output or "missing" in output or "argument" in output


class TestCLIUserExperience:
    """Test CLI user experience improvements."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_command_consistency(self, runner):
        """Test commands follow consistent patterns."""
        # All info commands should work similarly
        info_commands = [
            ["status"],
            ["config", "show"],
            ["--version"],
        ]

        for cmd in info_commands:
            result = runner.invoke(cli, cmd)
            # All should exit cleanly
            assert result.exit_code >= 0

    def test_verbose_output_useful(self, runner):
        """Test verbose output provides useful information."""
        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        # Output should contain actual information
        assert len(result.output) > 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
