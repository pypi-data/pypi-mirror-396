#!/usr/bin/env python3
"""
Trial & Freemium System
Manages 30-day trial period with auto-renewal and feature gating
"""

import json
import hashlib
import platform
import socket
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict

from lmapp.utils.logging import logger


@dataclass
class TrialState:
    """Trial state tracking"""
    trial_id: str
    start_date: str
    renewal_count: int = 0
    last_renewal: str = ""
    status: str = "active"
    version: int = 1


class TrialManager:
    """Manages trial period and freemium features"""
    
    # Paths for trial tracker storage
    PRIMARY_PATH = Path.home() / ".lmapp" / "trial_tracker.json"
    BACKUP_PATH = Path.home() / ".lmapp_backup" / "trial_tracker.json"
    SYSTEM_PATH = Path("/var/lmapp/trial_tracker.json")
    
    TRIAL_DURATION_DAYS = 30
    
    def __init__(self):
        """Initialize trial manager"""
        self.trial_state = self._load_trial_state()
        self._ensure_backup()
    
    @staticmethod
    def _generate_machine_id() -> str:
        """
        Generate unique machine ID from hostname + MAC address
        Used to identify machine for trial persistence
        """
        try:
            hostname = socket.gethostname()
            mac = get_mac_address()
            combined = f"{hostname}:{mac}"
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
        except Exception as e:
            logger.warning(f"Could not generate machine ID: {e}, using fallback")
            return hashlib.sha256(platform.node().encode()).hexdigest()[:16]
    
    def _load_trial_state(self) -> TrialState:
        """
        Load trial state from primary, backup, or system location
        Returns existing state or creates new trial
        """
        # Try primary location
        if self.PRIMARY_PATH.exists():
            return self._load_from_file(self.PRIMARY_PATH)
        
        # Try backup location
        if self.BACKUP_PATH.exists():
            logger.info("Trial tracker not found, restoring from backup")
            state = self._load_from_file(self.BACKUP_PATH)
            self._save_to_file(self.PRIMARY_PATH, state)
            return state
        
        # Try system location (Linux)
        if self.SYSTEM_PATH.exists() and platform.system() == "Linux":
            logger.info("Trial tracker not found, restoring from system backup")
            try:
                state = self._load_from_file(self.SYSTEM_PATH)
                self._save_to_file(self.PRIMARY_PATH, state)
                return state
            except Exception as e:
                logger.warning(f"Could not load system trial tracker: {e}")
        
        # Create new trial
        logger.info("Starting new 30-day trial period")
        return self._create_new_trial()
    
    @staticmethod
    def _load_from_file(path: Path) -> TrialState:
        """Load trial state from JSON file"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return TrialState(**data)
        except Exception as e:
            logger.error(f"Error loading trial state from {path}: {e}")
            raise
    
    @staticmethod
    def _save_to_file(path: Path, state: TrialState) -> None:
        """Save trial state to JSON file"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(asdict(state), f, indent=2)
            logger.debug(f"Trial state saved to {path}")
        except Exception as e:
            logger.error(f"Error saving trial state to {path}: {e}")
            raise
    
    def _create_new_trial(self) -> TrialState:
        """Create new trial state"""
        now = datetime.now().isoformat()
        state = TrialState(
            trial_id=self._generate_machine_id(),
            start_date=now,
            last_renewal=now,
            status="active",
            renewal_count=0,
        )
        self._save_trial_state(state)
        return state
    
    def _ensure_backup(self) -> None:
        """Ensure backup copy of trial tracker exists"""
        try:
            if self.PRIMARY_PATH.exists():
                self._save_to_file(self.BACKUP_PATH, self.trial_state)
                
                # Linux: also save to system location if possible
                if platform.system() == "Linux":
                    try:
                        self._save_to_file(self.SYSTEM_PATH, self.trial_state)
                    except PermissionError:
                        logger.debug("No permission to save system trial tracker")
                    except Exception as e:
                        logger.debug(f"Could not save system trial tracker: {e}")
        except Exception as e:
            logger.warning(f"Could not ensure backup: {e}")
    
    def _save_trial_state(self, state: TrialState) -> None:
        """Save trial state to all locations"""
        self._save_to_file(self.PRIMARY_PATH, state)
        self._ensure_backup()
    
    def is_trial_active(self) -> bool:
        """Check if trial is currently active"""
        if self.trial_state.status != "active":
            return False
        
        return self._days_remaining() > 0
    
    def _days_remaining(self) -> int:
        """Calculate days remaining in trial"""
        last_renewal = datetime.fromisoformat(self.trial_state.last_renewal)
        days_elapsed = (datetime.now() - last_renewal).days
        return max(0, self.TRIAL_DURATION_DAYS - days_elapsed)
    
    def get_days_remaining(self) -> int:
        """Get days remaining in trial (0 if expired)"""
        if not self.is_trial_active():
            return 0
        return self._days_remaining()
    
    def renew_trial(self) -> bool:
        """
        Renew trial for another 30 days
        This happens automatically or can be called manually
        """
        if self.trial_state.status != "active":
            logger.warning("Cannot renew inactive trial")
            return False
        
        self.trial_state.last_renewal = datetime.now().isoformat()
        self.trial_state.renewal_count += 1
        self._save_trial_state(self.trial_state)
        logger.info(f"Trial renewed. Renewal count: {self.trial_state.renewal_count}")
        return True
    
    def check_and_renew(self) -> None:
        """
        Check if trial needs renewal and renew if necessary
        Called on application startup
        """
        if self.trial_state.status != "active":
            return
        
        if self._days_remaining() <= 0:
            self.renew_trial()
    
    def get_trial_info(self) -> Dict[str, Any]:
        """Get complete trial information"""
        return {
            "is_active": self.is_trial_active(),
            "days_remaining": self.get_days_remaining(),
            "status": self.trial_state.status,
            "start_date": self.trial_state.start_date,
            "last_renewal": self.trial_state.last_renewal,
            "renewal_count": self.trial_state.renewal_count,
            "trial_id": self.trial_state.trial_id[:8] + "...",  # Partial ID for display
        }
    
    def reset_trial(self) -> None:
        """
        Reset trial to new 30-day period
        Intended for testing or user request
        """
        logger.warning("Resetting trial period")
        self.trial_state = self._create_new_trial()
        self._ensure_backup()


def get_mac_address() -> str:
    """Get MAC address of primary network interface"""
    try:
        import uuid
        mac = uuid.getnode()
        return ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
    except Exception:
        return "unknown"


# Global trial manager instance
_trial_manager: Optional[TrialManager] = None


def init_trial_system() -> TrialManager:
    """Initialize global trial manager"""
    global _trial_manager
    if _trial_manager is None:
        _trial_manager = TrialManager()
        _trial_manager.check_and_renew()
    return _trial_manager


def get_trial_manager() -> TrialManager:
    """Get global trial manager (must call init_trial_system first)"""
    global _trial_manager
    if _trial_manager is None:
        return init_trial_system()
    return _trial_manager


def is_trial_active() -> bool:
    """Check if trial is active"""
    return get_trial_manager().is_trial_active()


def get_trial_info() -> Dict[str, Any]:
    """Get trial info"""
    return get_trial_manager().get_trial_info()
