"""
Tests for src/coach/agents/basic_agent.py
"""
import pytest
from unittest.mock import MagicMock, patch


def test_get_basic_agent_creation(mock_firestore_db):
    """Test that get_basic_agent creates an agent with correct configuration."""
    with patch('src.coach.agents.basic_agent.Agent') as mock_agent_class, \
         patch('src.coach.agents.basic_agent.Gemini') as mock_gemini_class, \
         patch('src.coach.agents.basic_agent.DuckDuckGoTools') as mock_tools_class:
        
        from src.coach.agents.basic_agent import get_basic_agent
        
        # Setup mocks
        mock_model = MagicMock()
        mock_gemini_class.return_value = mock_model
        mock_tools = MagicMock()
        mock_tools_class.return_value = mock_tools
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        # Call function
        agent = get_basic_agent(mock_firestore_db)
        
        # Verify Gemini model was created with correct ID
        mock_gemini_class.assert_called_once_with(id="gemini-2.5-pro")
        
        # Verify DuckDuckGoTools was instantiated
        mock_tools_class.assert_called_once()
        
        # Verify Agent was created with correct parameters
        mock_agent_class.assert_called_once_with(
            id="basic-agent",
            model=mock_model,
            db=mock_firestore_db,
            tools=[mock_tools],
            add_history_to_context=True,
        )
        
        assert agent == mock_agent


def test_get_basic_agent_with_none_db():
    """Test that get_basic_agent handles None database."""
    with patch('src.coach.agents.basic_agent.Agent') as mock_agent_class, \
         patch('src.coach.agents.basic_agent.Gemini'), \
         patch('src.coach.agents.basic_agent.DuckDuckGoTools'):
        
        from src.coach.agents.basic_agent import get_basic_agent
        
        # Call with None db
        agent = get_basic_agent(None)
        
        # Verify Agent was called with None db
        call_kwargs = mock_agent_class.call_args[1]
        assert call_kwargs['db'] is None


def test_get_basic_agent_returns_agent_instance(mock_firestore_db):
    """Test that get_basic_agent returns an agent instance."""
    with patch('src.coach.agents.basic_agent.Agent') as mock_agent_class, \
         patch('src.coach.agents.basic_agent.Gemini'), \
         patch('src.coach.agents.basic_agent.DuckDuckGoTools'):
        
        from src.coach.agents.basic_agent import get_basic_agent
        
        mock_agent = MagicMock()
        mock_agent.id = "basic-agent"
        mock_agent_class.return_value = mock_agent
        
        agent = get_basic_agent(mock_firestore_db)
        
        assert agent is not None
        assert agent.id == "basic-agent"


def test_get_basic_agent_agent_id():
    """Test that the agent has the correct ID."""
    with patch('src.coach.agents.basic_agent.Agent') as mock_agent_class, \
         patch('src.coach.agents.basic_agent.Gemini'), \
         patch('src.coach.agents.basic_agent.DuckDuckGoTools'):
        
        from src.coach.agents.basic_agent import get_basic_agent
        
        get_basic_agent(MagicMock())
        
        # Check that agent was created with id="basic-agent"
        call_kwargs = mock_agent_class.call_args[1]
        assert call_kwargs['id'] == "basic-agent"


def test_get_basic_agent_has_history_context():
    """Test that the agent has history context enabled."""
    with patch('src.coach.agents.basic_agent.Agent') as mock_agent_class, \
         patch('src.coach.agents.basic_agent.Gemini'), \
         patch('src.coach.agents.basic_agent.DuckDuckGoTools'):
        
        from src.coach.agents.basic_agent import get_basic_agent
        
        get_basic_agent(MagicMock())
        
        # Check that add_history_to_context is True
        call_kwargs = mock_agent_class.call_args[1]
        assert call_kwargs['add_history_to_context'] is True

# Made with Bob
