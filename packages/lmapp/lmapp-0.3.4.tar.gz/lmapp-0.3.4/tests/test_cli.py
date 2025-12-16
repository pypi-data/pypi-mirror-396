"""Tests for CLI commands"""

from click.testing import CliRunner
from lmapp.cli import main


class TestCLIBasics:
    """Test basic CLI functionality"""

    def test_version_flag(self):
        """Test --version flag"""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "lmapp" in result.output
        assert "version" in result.output.lower()

    def test_help_command(self):
        """Test --help flag"""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_status_command(self):
        """Test status command"""
        runner = CliRunner()
        result = runner.invoke(main, ["status"])

        # Should show status table
        assert result.exit_code == 0
        assert "Backend" in result.output or "backend" in result.output.lower()


class TestChatCommand:
    """Test chat command"""

    def test_chat_no_backend(self):
        """Test chat command with no backend running"""
        runner = CliRunner()
        result = runner.invoke(main, ["chat"])

        # Should fail or warn about no backend
        # (depends on system state)
        assert result.exit_code != 0 or "backend" in result.output.lower()

    def test_chat_help(self):
        """Test chat help"""
        runner = CliRunner()
        result = runner.invoke(main, ["chat", "--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
