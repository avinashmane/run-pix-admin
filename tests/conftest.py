"""
Shared pytest fixtures and configuration for all tests.
"""
import pytest
import sys
import os
import yaml
import json
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, "./src")

# Set up test environment variables
TEST_ENV = {
    "CONFIG_FILE": "./src/config.yaml",
    "APP_ROOT": "./src",
    "AGENT_PROJECT_ID": "test-project-id",
    "CMS_PROJECT_ID": "test-cms-project",
    "TOWNSCRIPT_USER": "test@example.com",
    "TOWNSCRIPT_PASS": "test_password",
    "EVENT": "TEST_EVENT",
    "TIMEIT": "END",
}

for key, value in TEST_ENV.items():
    os.environ[key] = value


@pytest.fixture
def mock_service_account():
    """Mock SERVICE_ACCOUNT credentials."""
    return {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test.iam.gserviceaccount.com"
    }


@pytest.fixture
def mock_firestore_db():
    """Mock Firestore database."""
    mock_db = MagicMock()
    mock_db.project_id = "test-project"
    return mock_db


@pytest.fixture
def sample_config():
    """Load sample configuration."""
    config_path = os.environ.get("CONFIG_FILE", "./src/config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {
        "version": "1.0.0",
        "api": {"base": "https://api.example.com"},
        "certificates": {},
        "sheet": {"url": "https://docs.google.com/spreadsheets/test"}
    }


@pytest.fixture
def mock_agent():
    """Mock Agno Agent."""
    mock = MagicMock()
    mock.id = "test-agent"
    mock.model = MagicMock()
    mock.db = MagicMock()
    return mock


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment after each test."""
    yield
    # Cleanup can be added here if needed

# Made with Bob
