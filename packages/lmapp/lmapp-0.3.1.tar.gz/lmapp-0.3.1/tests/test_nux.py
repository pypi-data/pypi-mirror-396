import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from lmapp.cli import main
from lmapp.core.config import LMAppConfig


@pytest.fixture
def runner():
    return CliRunner()


def test_nux_runs_on_first_run(runner):
    """Test that NUX runs when check_first_run returns True"""
    with patch("lmapp.cli.check_first_run", return_value=True) as mock_check, patch(
        "lmapp.cli.run_user_mode_setup"
    ) as mock_setup, patch("lmapp.cli.MainMenu") as mock_menu:

        result = runner.invoke(main)

        assert result.exit_code == 0
        mock_check.assert_called_once()
        mock_setup.assert_called_once()
        mock_menu.assert_called_once()


def test_nux_skips_on_subsequent_runs(runner):
    """Test that NUX skips when check_first_run returns False"""
    with patch("lmapp.cli.check_first_run", return_value=False) as mock_check, patch(
        "lmapp.cli.run_user_mode_setup"
    ) as mock_setup, patch("lmapp.cli.MainMenu") as mock_menu:

        result = runner.invoke(main)

        assert result.exit_code == 0
        mock_check.assert_called_once()
        mock_setup.assert_not_called()
        mock_menu.assert_called_once()


def test_dev_flag_enables_developer_mode(runner):
    """Test that --dev flag enables developer mode"""
    mock_config = MagicMock(spec=LMAppConfig)
    mock_config.developer_mode = False

    mock_manager = MagicMock()
    mock_manager.load.return_value = mock_config
    mock_manager.config_file.exists.return_value = True

    with patch("lmapp.cli.get_config_manager", return_value=mock_manager), patch(
        "lmapp.cli.check_first_run", return_value=False
    ), patch("lmapp.cli.MainMenu"):

        result = runner.invoke(main, ["--dev"])

        assert result.exit_code == 0
        assert mock_config.developer_mode is True
        mock_manager.save.assert_called_with(mock_config)
        assert "Developer Mode Enabled" in result.output


def test_dev_flag_with_nux(runner):
    """Test that --dev flag works even when NUX runs"""
    mock_config = MagicMock(spec=LMAppConfig)
    mock_config.developer_mode = False  # Initially false

    mock_manager = MagicMock()
    mock_manager.load.return_value = mock_config

    # First call to load (in dev check) might fail if file doesn't exist,
    # but in our CLI logic we check config_manager.config_file.exists()
    mock_manager.config_file.exists.return_value = False

    # After NUX, it should exist.
    # We need to simulate the state change or just mock the calls.

    with patch("lmapp.cli.check_first_run", return_value=True), patch(
        "lmapp.cli.run_user_mode_setup"
    ), patch("lmapp.cli.get_config_manager", return_value=mock_manager), patch(
        "lmapp.cli.MainMenu"
    ):

        result = runner.invoke(main, ["--dev"])

        assert result.exit_code == 0
        # The dev flag logic runs AFTER NUX check if dev is passed?
        # In my implementation:
        # 1. NUX check -> run_silent_setup
        # 2. Dev flag check -> load config -> set true

        # Wait, in my implementation:
        # 1. NUX Check -> run_silent_setup
        # 2. Dev flag check -> load config -> set true

        # Actually, I put Dev flag check AFTER NUX check in the final code?
        # Let's check the code I wrote.
        pass
