#!/usr/bin/env python3
"""
Error Database Module
Manages a persistent log of errors and known solutions.
Acts as a "Fail-Safe" knowledge base.
"""

import json
import time
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

from lmapp.utils.logging import logger


@dataclass
class ErrorEntry:
    """Represents a single logged error"""

    timestamp: float
    error_type: str
    message: str
    context: str
    traceback: str
    solution: Optional[str] = None


class ErrorDB:
    """
    Manages the Error Database (JSONL).
    Stores past errors and provides solutions for known issues.
    """

    # Seed data for known issues (The "Knowledge Base")
    KNOWN_ISSUES = [
        {
            "pattern": "Connection refused.*11434",
            "solution": "Ollama service is not running. Try 'systemctl --user start ollama' or 'ollama serve'.",
        },
        {
            "pattern": "Max retries exceeded.*11434",
            "solution": "Ollama service is not running or unreachable. Check if 'ollama' is installed and running.",
        },
        {
            "pattern": "model '.*' not found",
            "solution": "The requested model is not installed. Run 'lmapp install' or 'ollama pull <model>'.",
        },
        {
            "pattern": "No backend detected",
            "solution": "No AI engine was found. Run 'lmapp install' to set one up.",
        },
    ]

    def __init__(self):
        import os

        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            self.data_dir = Path(xdg_data) / "lmapp"
        else:
            self.data_dir = Path.home() / ".local" / "share" / "lmapp"

        self.db_file = self.data_dir / "error_db.jsonl"
        self._ensure_db()

    def _ensure_db(self):
        """Ensure database file exists"""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)

        if not self.db_file.exists():
            self.db_file.touch()

    def _load_errors(self) -> List[Dict[str, Any]]:
        """Load errors from JSONL file"""
        errors = []
        try:
            if self.db_file.exists():
                with open(self.db_file, "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                errors.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Failed to load error DB: {e}")
        return errors

    def log_error(self, error: Exception, context: str = "") -> Optional[str]:
        """
        Log an error to the database and return a potential solution.
        """
        # Create entry
        entry = ErrorEntry(
            timestamp=time.time(),
            error_type=type(error).__name__,
            message=str(error),
            context=context,
            traceback=traceback.format_exc(),
        )

        # Check for known solution
        solution = self._find_solution(str(error))
        if solution:
            entry.solution = solution

        # Append to file
        try:
            with open(self.db_file, "a") as f:
                f.write(json.dumps(asdict(entry)) + "\n")

            # Try to log to global Failsafe DB
            try:
                from failsafe.core import FailsafeDB

                fs = FailsafeDB()
                fs.log(tool="lmapp", error=str(error), context=context)
            except ImportError:
                pass  # Failsafe not installed

        except Exception as e:
            logger.error(f"Failed to log error: {e}")

        return solution

    def _find_solution(self, error_msg: str) -> Optional[str]:
        """Find a solution based on error message patterns"""
        import re

        # Check built-in known issues
        for issue in self.KNOWN_ISSUES:
            if re.search(issue["pattern"], error_msg, re.IGNORECASE):
                return issue["solution"]

        return None

    def get_recent_errors(self, limit: int = 5) -> List[Dict]:
        """Get most recent errors"""
        errors = self._load_errors()
        return sorted(errors, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_history(self) -> List[Dict]:
        """Get full error history"""
        errors = self._load_errors()
        return sorted(errors, key=lambda x: x["timestamp"])


# Global instance
error_db = ErrorDB()
