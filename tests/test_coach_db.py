"""
Tests for src/coach/lib/db.py
"""
import pytest
import os
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_firestore_db_class():
    """Mock FirestoreDb class."""
    with patch('src.coach.lib.db.FirestoreDb') as mock:
        mock_instance = MagicMock()
        mock_instance.project_id = "test-project-id"
        mock.return_value = mock_instance
        yield mock


def test_get_firestore_db_default_project(mock_firestore_db_class):
    """Test get_firestore_db with default project ID."""
    from src.coach.lib.db import get_firestore_db
    
    # Remove env var if exists
    if 'AGENT_PROJECT_ID' in os.environ:
        del os.environ['AGENT_PROJECT_ID']
    
    db = get_firestore_db()
    
    # Verify FirestoreDb was called with default project
    mock_firestore_db_class.assert_called_once_with(project_id="agno-os-test")
    assert db is not None


def test_get_firestore_db_custom_project(mock_firestore_db_class):
    """Test get_firestore_db with custom project ID from environment."""
    from src.coach.lib.db import get_firestore_db
    
    os.environ['AGENT_PROJECT_ID'] = 'custom-project-id'
    
    db = get_firestore_db()
    
    # Verify FirestoreDb was called with custom project
    mock_firestore_db_class.assert_called_once_with(project_id="custom-project-id")
    assert db is not None


def test_get_firestore_db_logs_info(mock_firestore_db_class, caplog):
    """Test that get_firestore_db logs the project ID."""
    import logging
    from src.coach.lib.db import get_firestore_db
    
    os.environ['AGENT_PROJECT_ID'] = 'test-logging-project'
    
    with caplog.at_level(logging.INFO):
        db = get_firestore_db()
    
    # Check that logging occurred
    assert "Setting firestore test-logging-project" in caplog.text


def test_project_id_constant():
    """Test that PROJECT_ID constant is set correctly."""
    from src.coach.lib.db import PROJECT_ID
    
    # Should use environment variable or default
    expected = os.environ.get("AGENT_PROJECT_ID", "agno-os-test")
    assert PROJECT_ID == expected

# Made with Bob
