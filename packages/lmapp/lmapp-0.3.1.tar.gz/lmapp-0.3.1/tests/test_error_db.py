import pytest
import json
import os
from pathlib import Path
from lmapp.core.error_db import ErrorDB


def test_error_db_init(tmp_path):
    # Mock XDG_DATA_HOME
    os.environ["XDG_DATA_HOME"] = str(tmp_path)
    db = ErrorDB()
    assert db.db_file.parent.exists()
    assert db.db_file.name == "error_db.jsonl"


def test_log_error(tmp_path):
    os.environ["XDG_DATA_HOME"] = str(tmp_path)
    db = ErrorDB()

    try:
        1 / 0
    except ZeroDivisionError as e:
        solution = db.log_error(e)

    # Verify log
    with open(db.db_file) as f:
        lines = f.readlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["error_type"] == "ZeroDivisionError"
        assert "division by zero" in entry["message"]


def test_known_issue_matching(tmp_path):
    os.environ["XDG_DATA_HOME"] = str(tmp_path)
    db = ErrorDB()

    # Add a mock known issue
    db.KNOWN_ISSUES = [
        {"pattern": r"connection refused", "solution": "Check your internet connection"}
    ]

    class MockError(Exception):
        pass

    err = MockError("Error: connection refused by server")
    solution = db.log_error(err)

    assert solution == "Check your internet connection"
