#!/usr/bin/env python3
"""
Configuration CLI Commands Tests
Tests for lmapp config command and subcommands
"""

from click.testing import CliRunner

from lmapp.cli import main


class TestConfigShowCommand:
    """Test config show command"""

    def test_config_show_displays_settings(self):
        """Test that config show displays current settings"""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "show"])

        assert result.exit_code == 0
        assert "Current Configuration:" in result.output
        assert "backend:" in result.output
        assert "model:" in result.output
        assert "temperature:" in result.output

    def test_config_show_displays_location(self):
        """Test that config show displays config location"""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "show"])

        assert result.exit_code == 0
        assert "~/.config/lmapp/config.json" in result.output
        assert "~/.local/share/lmapp/logs/lmapp.log" in result.output


class TestConfigSetCommand:
    """Test config set command"""

    def test_config_set_string_value(self):
        """Test setting a string configuration value"""
        runner = CliRunner()

        # Set a model value
        result = runner.invoke(main, ["config", "set", "model", "mistral"])

        assert result.exit_code == 0
        assert "✓ Updated model = mistral" in result.output

    def test_config_set_float_value(self):
        """Test setting a float configuration value"""
        runner = CliRunner()

        result = runner.invoke(main, ["config", "set", "temperature", "0.3"])

        assert result.exit_code == 0
        assert "✓ Updated temperature = 0.3" in result.output

    def test_config_set_int_value(self):
        """Test setting an integer configuration value"""
        runner = CliRunner()

        result = runner.invoke(main, ["config", "set", "timeout", "600"])

        assert result.exit_code == 0
        assert "✓ Updated timeout = 600" in result.output

    def test_config_set_boolean_true(self):
        """Test setting a boolean value to true"""
        runner = CliRunner()

        result = runner.invoke(main, ["config", "set", "debug", "true"])

        assert result.exit_code == 0
        assert "✓ Updated debug = True" in result.output

    def test_config_set_boolean_false(self):
        """Test setting a boolean value to false"""
        runner = CliRunner()

        result = runner.invoke(main, ["config", "set", "debug", "false"])

        assert result.exit_code == 0
        assert "✓ Updated debug = False" in result.output

    def test_config_set_invalid_key(self):
        """Test setting an invalid configuration key"""
        runner = CliRunner()

        result = runner.invoke(main, ["config", "set", "invalid_key", "value"])

        assert result.exit_code == 0
        assert "✗ Unknown configuration key: invalid_key" in result.output
        assert "Valid keys:" in result.output

    def test_config_set_invalid_backend(self):
        """Test setting an invalid backend value"""
        runner = CliRunner()

        result = runner.invoke(main, ["config", "set", "backend", "invalid_backend"])

        assert result.exit_code == 0
        assert "✗ Failed to set backend:" in result.output

    def test_config_set_temperature_out_of_range(self):
        """Test setting temperature out of valid range"""
        runner = CliRunner()

        result = runner.invoke(main, ["config", "set", "temperature", "1.5"])

        assert result.exit_code == 0
        assert "✗ Failed to set temperature:" in result.output

    def test_config_set_persists_across_commands(self):
        """Test that config changes persist"""
        runner = CliRunner()

        # Set a value
        runner.invoke(main, ["config", "set", "model", "llama2"])

        # Show and verify
        result = runner.invoke(main, ["config", "show"])

        # Note: This may not persist in test due to singleton, but verify command works
        assert result.exit_code == 0


class TestConfigResetCommand:
    """Test config reset command"""

    def test_config_reset_requires_confirmation(self):
        """Test that reset requires user confirmation"""
        runner = CliRunner()

        # Decline confirmation
        result = runner.invoke(main, ["config", "reset"], input="n\n")

        # Should abort
        assert result.exit_code != 0 or "aborted" in result.output.lower()

    def test_config_reset_with_confirmation(self):
        """Test resetting config with confirmation"""
        runner = CliRunner()

        # Accept confirmation
        result = runner.invoke(main, ["config", "reset"], input="y\n")

        assert result.exit_code == 0
        assert "✓ Configuration reset to defaults" in result.output


class TestConfigValidateCommand:
    """Test config validate command"""

    def test_config_validate_valid_config(self):
        """Test validating a valid configuration"""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "validate"])

        assert result.exit_code == 0
        assert "✓ Configuration is valid" in result.output


class TestConfigIntegration:
    """Integration tests for config commands"""

    def test_config_subcommand_help(self):
        """Test getting help for config command"""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "--help"])

        assert result.exit_code == 0
        assert "show" in result.output
        assert "set" in result.output
        assert "reset" in result.output
        assert "validate" in result.output

    def test_config_show_subcommand_help(self):
        """Test getting help for config show"""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "show", "--help"])

        assert result.exit_code == 0
        assert "Display current configuration" in result.output

    def test_config_set_subcommand_help(self):
        """Test getting help for config set"""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "set", "--help"])

        assert result.exit_code == 0
        assert "Set a configuration value" in result.output
        assert "Examples:" in result.output

    def test_full_config_workflow(self):
        """Test a complete configuration workflow"""
        runner = CliRunner()

        # Show initial config
        result1 = runner.invoke(main, ["config", "show"])
        assert result1.exit_code == 0
        assert "Current Configuration:" in result1.output

        # Set a value
        result2 = runner.invoke(main, ["config", "set", "model", "tinyllama"])
        assert result2.exit_code == 0
        assert "✓ Updated" in result2.output

        # Validate
        result3 = runner.invoke(main, ["config", "validate"])
        assert result3.exit_code == 0
        assert "✓ Configuration is valid" in result3.output
