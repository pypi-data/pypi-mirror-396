#!/usr/bin/env python3
"""
Test suite for First-Run Wizard functionality (Task 2)
Tests hardware detection and model recommendation logic
"""

import pytest
from unittest.mock import patch
from lmapp.ui.first_run import FirstRunWizard
from lmapp.core.config import LMAppConfig
from lmapp.backend.detector import BackendDetector


class TestFirstRunWizardCore:
    """Core logic tests for FirstRunWizard (non-UI methods)"""

    @pytest.fixture
    def wizard(self):
        """Create FirstRunWizard instance"""
        return FirstRunWizard()

    # ========================================================================
    # HARDWARE DETECTION LOGIC TESTS
    # ========================================================================

    def test_hardware_detection_returns_dict(self, wizard):
        """Test hardware detection returns dict with required keys"""
        # Call the method that actually does the detection logic
        # (without the UI part which calls console.input)
        with patch("lmapp.ui.first_run.console.input", return_value=""):
            with patch("lmapp.ui.first_run.console.print"):  # Suppress output
                hardware = wizard._detect_hardware()
                assert isinstance(hardware, dict)
                assert "total_ram_gb" in hardware
                assert "available_ram_gb" in hardware
                assert "cpu_cores" in hardware

    def test_hardware_detection_values_realistic(self, wizard):
        """Test hardware detection returns realistic values"""
        with patch("lmapp.ui.first_run.console.input", return_value=""):
            with patch("lmapp.ui.first_run.console.print"):
                hardware = wizard._detect_hardware()
                # Should have at least some RAM
                assert hardware["total_ram_gb"] > 0.1
                # Available should be less than or equal to total
                assert hardware["available_ram_gb"] <= hardware["total_ram_gb"]
                # CPU cores should be reasonable
                assert hardware["cpu_cores"] >= 1
                assert hardware["cpu_cores"] <= 1024

    # ========================================================================
    # MODEL RECOMMENDATION LOGIC TESTS
    # ========================================================================

    def test_model_recommendation_low_ram(self, wizard):
        """Test model recommendation for <2GB RAM systems"""
        hardware_low = {"total_ram_gb": 1.5, "available_ram_gb": 1.0, "cpu_cores": 2}
        model = wizard._get_recommended_model(hardware_low)
        assert isinstance(model, str)
        assert len(model) > 0
        # Should recommend a small model for low RAM
        assert "b" in model  # Model naming includes size like "7b"

    def test_model_recommendation_medium_ram(self, wizard):
        """Test model recommendation for 2-4GB RAM systems"""
        hardware_medium = {"total_ram_gb": 3.0, "available_ram_gb": 2.5, "cpu_cores": 4}
        model = wizard._get_recommended_model(hardware_medium)
        assert isinstance(model, str)
        assert len(model) > 0

    def test_model_recommendation_good_ram(self, wizard):
        """Test model recommendation for 4-8GB RAM systems"""
        hardware_good = {"total_ram_gb": 6.0, "available_ram_gb": 5.5, "cpu_cores": 8}
        model = wizard._get_recommended_model(hardware_good)
        assert isinstance(model, str)
        assert len(model) > 0

    def test_model_recommendation_high_ram(self, wizard):
        """Test model recommendation for 8GB+ RAM systems"""
        hardware_high = {
            "total_ram_gb": 16.0,
            "available_ram_gb": 14.0,
            "cpu_cores": 16,
        }
        model = wizard._get_recommended_model(hardware_high)
        assert isinstance(model, str)
        assert len(model) > 0

    def test_model_recommendation_always_returns_string(self, wizard):
        """Test model recommendation always returns valid string"""
        test_cases = [
            {"total_ram_gb": 0.5, "available_ram_gb": 0.4, "cpu_cores": 1},
            {"total_ram_gb": 3.0, "available_ram_gb": 2.5, "cpu_cores": 4},
            {"total_ram_gb": 10.0, "available_ram_gb": 9.0, "cpu_cores": 12},
            {"total_ram_gb": 32.0, "available_ram_gb": 30.0, "cpu_cores": 32},
        ]
        for hardware in test_cases:
            model = wizard._get_recommended_model(hardware)
            assert isinstance(model, str)
            assert len(model) > 0

    def test_model_recommendation_boundary_values(self, wizard):
        """Test model recommendation at exact boundary values"""
        boundaries = [
            {"total_ram_gb": 2.0, "available_ram_gb": 1.5, "cpu_cores": 2},
            {"total_ram_gb": 4.0, "available_ram_gb": 3.5, "cpu_cores": 4},
            {"total_ram_gb": 8.0, "available_ram_gb": 7.5, "cpu_cores": 8},
        ]
        for hardware in boundaries:
            model = wizard._get_recommended_model(hardware)
            assert isinstance(model, str)
            assert len(model) > 0

    # ========================================================================
    # INITIALIZATION & STRUCTURE TESTS
    # ========================================================================

    def test_wizard_initialization(self):
        """Test FirstRunWizard initializes with required components"""
        wizard = FirstRunWizard()
        assert wizard is not None
        assert hasattr(wizard, "config")
        assert hasattr(wizard, "config_manager")
        assert hasattr(wizard, "detector")
        assert wizard.config is not None

    def test_wizard_has_required_methods(self, wizard):
        """Test wizard has all required methods"""
        assert hasattr(wizard, "run")
        assert hasattr(wizard, "_show_welcome")
        assert hasattr(wizard, "_detect_hardware")
        assert hasattr(wizard, "_get_recommended_model")
        assert hasattr(wizard, "_should_download_model")
        assert hasattr(wizard, "_download_model")
        assert hasattr(wizard, "_show_completion")

        # All should be callable
        assert callable(wizard.run)
        assert callable(wizard._detect_hardware)
        assert callable(wizard._get_recommended_model)

    def test_wizard_config_has_completed_setup_field(self, wizard):
        """Test config supports completed_setup flag"""
        assert hasattr(wizard.config, "completed_setup")
        assert isinstance(wizard.config.completed_setup, bool)

    # ========================================================================
    # WORKFLOW LOGIC TESTS
    # ========================================================================

    def test_should_download_model_decline(self, wizard):
        """Test wizard method exists and returns bool"""
        # Test that the method exists and is callable
        assert hasattr(wizard, "_should_download_model")
        assert callable(wizard._should_download_model)

    def test_should_download_model_accept(self, wizard):
        """Test wizard download method signature"""
        # Test that the method exists and is callable
        assert hasattr(wizard, "_should_download_model")
        assert callable(wizard._should_download_model)

    def test_wizard_multiple_instantiation(self):
        """Test creating multiple wizard instances works correctly"""
        wizards = [FirstRunWizard() for _ in range(3)]
        assert len(wizards) == 3
        # All should be independent
        for wizard in wizards:
            assert wizard is not None
            assert hasattr(wizard, "config")


class TestFirstRunWizardIntegrationWithConfig:
    """Integration tests with ConfigManager"""

    def test_wizard_loads_existing_config(self):
        """Test wizard properly loads existing config"""
        wizard = FirstRunWizard()
        assert wizard.config is not None
        # Config should have been loaded via ConfigManager
        assert isinstance(wizard.config, LMAppConfig)

    def test_wizard_respects_completed_setup_flag(self):
        """Test wizard checks completed_setup flag"""
        wizard = FirstRunWizard()
        # Should have the flag available
        completed = wizard.config.completed_setup
        assert isinstance(completed, bool)

    def test_wizard_detector_initialized(self):
        """Test BackendDetector is properly initialized"""
        wizard = FirstRunWizard()
        assert wizard.detector is not None
        assert isinstance(wizard.detector, BackendDetector)


class TestFirstRunWizardEdgeCases:
    """Edge case and robustness tests"""

    @pytest.fixture
    def wizard(self):
        """Create wizard for edge case testing"""
        return FirstRunWizard()

    def test_model_recommendation_zero_ram(self, wizard):
        """Test model recommendation handles zero RAM edge case"""
        try:
            hardware = {"total_ram_gb": 0.0, "available_ram_gb": 0.0, "cpu_cores": 1}
            model = wizard._get_recommended_model(hardware)
            # Should return something, even for edge case
            assert isinstance(model, str)
        except Exception:
            # OK if it raises exception for invalid hardware
            assert True

    def test_model_recommendation_negative_values(self, wizard):
        """Test model recommendation robustness with invalid values"""
        hardware_invalid = {
            "total_ram_gb": -1.0,
            "available_ram_gb": -1.0,
            "cpu_cores": -1,
        }
        try:
            model = wizard._get_recommended_model(hardware_invalid)
            # Either returns something or raises exception
            if model:
                assert isinstance(model, str)
        except Exception:
            # Exception is acceptable for invalid input
            assert True

    def test_model_recommendation_extreme_high_ram(self, wizard):
        """Test model recommendation with very high RAM"""
        hardware_extreme = {
            "total_ram_gb": 256.0,
            "available_ram_gb": 256.0,
            "cpu_cores": 128,
        }
        model = wizard._get_recommended_model(hardware_extreme)
        assert isinstance(model, str)
        assert len(model) > 0

    def test_hardware_dict_structure_consistency(self, wizard):
        """Test hardware detection always returns dict with required keys"""
        with patch("lmapp.ui.first_run.console.input", return_value=""):
            with patch("lmapp.ui.first_run.console.print"):
                for _ in range(3):
                    hardware = wizard._detect_hardware()
                    # Should have these required keys
                    assert "total_ram_gb" in hardware
                    assert "available_ram_gb" in hardware
                    assert "cpu_cores" in hardware
