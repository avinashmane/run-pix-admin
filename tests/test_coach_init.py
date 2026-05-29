"""
Tests for src/coach/__init__.py
"""
import pytest
from unittest.mock import MagicMock, patch, call


def test_mount_coach_creates_fastapi_app_when_none():
    """Test that mount_coach creates a FastAPI app when none is provided."""
    with patch('src.coach.FastAPI') as mock_fastapi, \
         patch('src.coach.get_db') as mock_get_db, \
         patch('src.coach.get_basic_agent') as mock_get_agent, \
         patch('src.coach.AgentOS') as mock_agent_os:
        
        from src.coach import mount_coach
        
        # Setup mocks
        mock_app = MagicMock()
        mock_fastapi.return_value = mock_app
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_agent = MagicMock()
        mock_get_agent.return_value = mock_agent
        mock_os = MagicMock()
        mock_os.get_app.return_value = MagicMock()
        mock_agent_os.return_value = mock_os
        
        # Call without app
        result = mount_coach()
        
        # Verify FastAPI was created
        mock_fastapi.assert_called_once_with(
            title="API v1",
            description="Version 1 of the API"
        )


def test_mount_coach_uses_provided_app():
    """Test that mount_coach uses the provided app."""
    with patch('src.coach.get_db') as mock_get_db, \
         patch('src.coach.get_basic_agent') as mock_get_agent, \
         patch('src.coach.AgentOS') as mock_agent_os:
        
        from src.coach import mount_coach
        
        # Setup mocks
        provided_app = MagicMock()
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_agent = MagicMock()
        mock_get_agent.return_value = mock_agent
        mock_os = MagicMock()
        mock_os.get_app.return_value = MagicMock()
        mock_agent_os.return_value = mock_os
        
        # Call with app
        result = mount_coach(app=provided_app)
        
        # Verify the provided app was used (AgentOS should be created)
        assert mock_agent_os.called


def test_mount_coach_initializes_database():
    """Test that mount_coach initializes the database."""
    with patch('src.coach.FastAPI'), \
         patch('src.coach.get_db') as mock_get_db, \
         patch('src.coach.get_basic_agent') as mock_get_agent, \
         patch('src.coach.AgentOS') as mock_agent_os:
        
        from src.coach import mount_coach
        
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_agent = MagicMock()
        mock_get_agent.return_value = mock_agent
        mock_os = MagicMock()
        mock_os.get_app.return_value = MagicMock()
        mock_agent_os.return_value = mock_os
        
        # Call function
        mount_coach()
        
        # Verify get_db was called
        mock_get_db.assert_called_once()


def test_mount_coach_creates_basic_agent():
    """Test that mount_coach creates the basic agent with database."""
    with patch('src.coach.FastAPI'), \
         patch('src.coach.get_db') as mock_get_db, \
         patch('src.coach.get_basic_agent') as mock_get_agent, \
         patch('src.coach.AgentOS') as mock_agent_os:
        
        from src.coach import mount_coach
        
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_agent = MagicMock()
        mock_get_agent.return_value = mock_agent
        mock_os = MagicMock()
        mock_os.get_app.return_value = MagicMock()
        mock_agent_os.return_value = mock_os
        
        # Call function
        mount_coach()
        
        # Verify get_basic_agent was called with db
        mock_get_agent.assert_called_once_with(mock_db)


def test_mount_coach_creates_agent_os():
    """Test that mount_coach creates AgentOS with agents."""
    with patch('src.coach.FastAPI'), \
         patch('src.coach.get_db') as mock_get_db, \
         patch('src.coach.get_basic_agent') as mock_get_agent, \
         patch('src.coach.AgentOS') as mock_agent_os:
        
        from src.coach import mount_coach
        
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_agent = MagicMock()
        mock_get_agent.return_value = mock_agent
        mock_os = MagicMock()
        mock_os.get_app.return_value = MagicMock()
        mock_agent_os.return_value = mock_os
        
        # Call function
        mount_coach()
        
        # Verify AgentOS was created with agents list
        mock_agent_os.assert_called_once_with(agents=[mock_agent])


def test_mount_coach_returns_app():
    """Test that mount_coach returns the AgentOS app."""
    with patch('src.coach.FastAPI'), \
         patch('src.coach.get_db') as mock_get_db, \
         patch('src.coach.get_basic_agent') as mock_get_agent, \
         patch('src.coach.AgentOS') as mock_agent_os:
        
        from src.coach import mount_coach
        
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_agent = MagicMock()
        mock_get_agent.return_value = mock_agent
        mock_returned_app = MagicMock()
        mock_os = MagicMock()
        mock_os.get_app.return_value = mock_returned_app
        mock_agent_os.return_value = mock_os
        
        # Call function
        result = mount_coach()
        
        # Verify get_app was called and result is returned
        mock_os.get_app.assert_called_once()
        assert result == mock_returned_app

# Made with Bob
