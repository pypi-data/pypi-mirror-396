#!/usr/bin/env python3
"""
Unit tests for trial and freemium system
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import pytest

from lmapp.core.trial import TrialManager, TrialState, get_mac_address
from lmapp.core.feature_gate import FeatureGate, FeatureTier, FeatureAccessDenied


class TestTrialStateDataclass:
    """Test TrialState dataclass"""
    
    def test_trial_state_creation(self):
        """Test creating trial state"""
        state = TrialState(
            trial_id="test123",
            start_date="2025-12-11T00:00:00",
            status="active"
        )
        assert state.trial_id == "test123"
        assert state.renewal_count == 0
        assert state.status == "active"
    
    def test_trial_state_with_renewal(self):
        """Test trial state with renewal count"""
        state = TrialState(
            trial_id="test123",
            start_date="2025-12-11T00:00:00",
            renewal_count=5,
            last_renewal="2025-12-11T00:00:00",
            status="active"
        )
        assert state.renewal_count == 5


class TestTrialManager:
    """Test TrialManager functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    def test_machine_id_generation(self):
        """Test machine ID generation"""
        machine_id = TrialManager._generate_machine_id()
        assert isinstance(machine_id, str)
        assert len(machine_id) > 0
        
        # Same machine should always generate same ID
        machine_id2 = TrialManager._generate_machine_id()
        assert machine_id == machine_id2
    
    def test_trial_state_to_dict(self):
        """Test serialization of trial state"""
        state = TrialState(
            trial_id="abc123",
            start_date="2025-12-11T00:00:00",
            status="active"
        )
        from dataclasses import asdict
        data = asdict(state)
        assert data["trial_id"] == "abc123"
        assert "start_date" in data
        assert data["status"] == "active"
    
    def test_trial_state_json_roundtrip(self, temp_dir):
        """Test saving and loading trial state"""
        state = TrialState(
            trial_id="test_id",
            start_date="2025-12-11T00:00:00",
            renewal_count=3,
            status="active"
        )
        
        # Save
        path = Path(temp_dir) / "trial.json"
        from dataclasses import asdict
        with open(path, 'w') as f:
            json.dump(asdict(state), f)
        
        # Load
        with open(path, 'r') as f:
            data = json.load(f)
        loaded_state = TrialState(**data)
        
        assert loaded_state.trial_id == "test_id"
        assert loaded_state.renewal_count == 3
        assert loaded_state.status == "active"


class TestFeatureGate:
    """Test feature gating system"""
    
    def test_free_tier_features(self):
        """Test free tier has only basic features"""
        gate = FeatureGate(is_trial_active=False, is_paid_active=False)
        features = gate.get_allowed_features(advanced_mode_enabled=False)
        
        assert "chat_basic" in features
        assert "backend_ollama" in features
        assert "cli_interface" in features
        assert "rag_system" not in features
        assert "plugin_system" not in features
    
    def test_trial_tier_features(self):
        """Test trial tier has all features"""
        gate = FeatureGate(is_trial_active=True, is_paid_active=False)
        features = gate.get_allowed_features(advanced_mode_enabled=True)
        
        assert "rag_system" in features
        assert "plugin_system" in features
        assert "batch_processing" in features
        assert "web_ui" in features
        assert "backend_openai" in features
    
    def test_paid_tier_features(self):
        """Test paid tier has all features"""
        gate = FeatureGate(is_trial_active=False, is_paid_active=True)
        features = gate.get_allowed_features(advanced_mode_enabled=True)
        
        assert "rag_system" in features
        assert "plugin_system" in features
        assert "batch_processing" in features
    
    def test_advanced_mode_disabled_reverts_to_free(self):
        """Test disabling Advanced Mode restricts features"""
        gate = FeatureGate(is_trial_active=True, is_paid_active=False)
        
        # With Advanced Mode ON
        features_on = gate.get_allowed_features(advanced_mode_enabled=True)
        assert "rag_system" in features_on
        
        # With Advanced Mode OFF
        features_off = gate.get_allowed_features(advanced_mode_enabled=False)
        assert "rag_system" not in features_off
    
    def test_has_feature(self):
        """Test checking individual feature access"""
        gate = FeatureGate(is_trial_active=False, is_paid_active=False)
        
        assert gate.has_feature("chat_basic", advanced_mode_enabled=False)
        assert not gate.has_feature("rag_system", advanced_mode_enabled=False)
        assert not gate.has_feature("web_ui", advanced_mode_enabled=False)
    
    def test_enforce_feature_access(self):
        """Test feature enforcement returns correct boolean"""
        gate = FeatureGate(is_trial_active=False, is_paid_active=False)
        
        # Free user accessing free feature
        assert gate.enforce_feature_access("chat_basic", advanced_mode_enabled=False)
        
        # Free user accessing advanced feature
        assert not gate.enforce_feature_access("rag_system", advanced_mode_enabled=False)
    
    def test_restricted_features(self):
        """Test getting list of restricted features"""
        gate = FeatureGate(is_trial_active=False, is_paid_active=False)
        restricted = gate.get_restricted_features(advanced_mode_enabled=False)
        
        assert "rag_system" in restricted
        assert "plugin_system" in restricted
        assert "web_ui" in restricted
        assert "chat_basic" not in restricted
    
    def test_feature_descriptions(self):
        """Test feature descriptions exist"""
        descriptions = FeatureGate.get_feature_descriptions()
        
        assert "rag_system" in descriptions
        assert isinstance(descriptions["rag_system"], str)
        assert len(descriptions["rag_system"]) > 0
    
    def test_advanced_mode_allowed_when_trial_active(self):
        """Test Advanced Mode is allowed when trial is active"""
        gate = FeatureGate(is_trial_active=True, is_paid_active=False)
        assert gate.is_advanced_mode_allowed()
    
    def test_advanced_mode_not_allowed_when_free(self):
        """Test Advanced Mode is not allowed for free users"""
        gate = FeatureGate(is_trial_active=False, is_paid_active=False)
        assert not gate.is_advanced_mode_allowed()
    
    def test_advanced_mode_allowed_when_paid(self):
        """Test Advanced Mode is allowed when paid"""
        gate = FeatureGate(is_trial_active=False, is_paid_active=True)
        assert gate.is_advanced_mode_allowed()


class TestFeatureTierSets:
    """Test feature tier sets are consistent"""
    
    def test_no_overlap_between_free_and_advanced(self):
        """Test free and advanced features don't overlap"""
        overlap = FeatureTier.FREE_FEATURES & FeatureTier.ADVANCED_FEATURES
        assert len(overlap) == 0, f"Features in both tiers: {overlap}"
    
    def test_all_features_accounted_for(self):
        """Test all features are in either free or advanced"""
        all_features = FeatureTier.FREE_FEATURES | FeatureTier.ADVANCED_FEATURES
        assert all_features == FeatureTier.ALL_FEATURES
    
    def test_free_features_exist(self):
        """Test free tier has features"""
        assert len(FeatureTier.FREE_FEATURES) > 0
    
    def test_advanced_features_exist(self):
        """Test advanced tier has features"""
        assert len(FeatureTier.ADVANCED_FEATURES) > 0


class TestFeatureAccessDenied:
    """Test feature access exception"""
    
    def test_exception_creation(self):
        """Test creating access denied exception"""
        exc = FeatureAccessDenied("rag_system")
        assert "rag_system" in str(exc)
        assert "Advanced Mode" in str(exc)
    
    def test_exception_message(self):
        """Test exception has helpful message"""
        exc = FeatureAccessDenied("web_ui")
        message = str(exc)
        assert "web_ui" in message
        assert "requires" in message


class TestMacAddressGeneration:
    """Test MAC address generation"""
    
    def test_mac_address_format(self):
        """Test MAC address has valid format"""
        mac = get_mac_address()
        assert isinstance(mac, str)
        assert len(mac) > 0


# Integration tests
class TestTrialSystemIntegration:
    """Integration tests for trial system"""
    
    def test_free_user_cannot_access_advanced_features(self):
        """Test free user flow"""
        gate = FeatureGate(is_trial_active=False, is_paid_active=False)
        
        # Free user in free tier
        free_features = gate.get_allowed_features(advanced_mode_enabled=False)
        assert "chat_basic" in free_features
        assert "rag_system" not in free_features
        
        # Free user can't enable advanced mode
        assert not gate.is_advanced_mode_allowed()
    
    def test_trial_user_has_full_access(self):
        """Test trial user flow"""
        gate = FeatureGate(is_trial_active=True, is_paid_active=False)
        
        # Trial user with advanced mode on
        trial_features = gate.get_allowed_features(advanced_mode_enabled=True)
        
        # All features available
        for feature in FeatureTier.ALL_FEATURES:
            assert feature in trial_features
    
    def test_trial_expiry_flow(self):
        """Test trial expiry to free tier flow"""
        # User has active trial
        gate_trial = FeatureGate(is_trial_active=True, is_paid_active=False)
        trial_features = gate_trial.get_allowed_features(advanced_mode_enabled=True)
        assert "rag_system" in trial_features
        
        # Trial expires
        gate_free = FeatureGate(is_trial_active=False, is_paid_active=False)
        free_features = gate_free.get_allowed_features(advanced_mode_enabled=False)
        assert "rag_system" not in free_features


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
