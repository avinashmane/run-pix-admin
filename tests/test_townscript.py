"""
Tests for src/townscript.py
"""
import pytest
import os
from unittest.mock import MagicMock, patch
import json


@pytest.fixture
def sample_config():
    """Sample configuration for Townscript."""
    return {
        'api': {
            'base': 'https://www.townscript.com/api'
        }
    }


@pytest.fixture
def townscript_instance(sample_config):
    """Create a Townscript instance for testing."""
    from src.townscript import Townscript
    return Townscript(sample_config)


def test_townscript_init(sample_config):
    """Test Townscript initialization."""
    from src.townscript import Townscript
    
    ts = Townscript(sample_config)
    
    assert ts.cfg == sample_config


@patch('src.townscript.requests.post')
def test_tstoken_success(mock_post, townscript_instance):
    """Test TSToken successful authentication."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'test_token_123'}
    mock_post.return_value = mock_response
    
    # Set environment variables
    os.environ['TOWNSCRIPT_USER'] = 'test@example.com'
    os.environ['TOWNSCRIPT_PASS'] = 'test_password'
    
    townscript_instance.TSToken()
    
    # Verify token was set
    assert townscript_instance.token == 'test_token_123'
    
    # Verify request was made correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert 'loginwithtownscript' in call_args[0][0]


@patch('src.townscript.requests.post')
def test_tstoken_failure(mock_post, townscript_instance):
    """Test TSToken with failed authentication."""
    # Mock failed response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_post.return_value = mock_response
    
    os.environ['TOWNSCRIPT_USER'] = 'test@example.com'
    os.environ['TOWNSCRIPT_PASS'] = 'wrong_password'
    
    # Should not raise exception, but token won't be set
    townscript_instance.TSToken()
    
    assert not hasattr(townscript_instance, 'token')


@patch('src.townscript.requests.get')
def test_tsget_success(mock_get, townscript_instance):
    """Test TSget with successful response."""
    townscript_instance.token = 'test_token'
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'test_data'}
    mock_get.return_value = mock_response
    
    result = townscript_instance.TSget('/test/endpoint')
    
    assert result == {'data': 'test_data'}
    
    # Verify headers included token (note the typo in original code)
    call_args = mock_get.call_args
    headers = call_args[1]['headers']
    assert 'Authotization' in headers  # Original code has typo


@patch('src.townscript.requests.get')
def test_tsget_failure(mock_get, townscript_instance):
    """Test TSget with failed response."""
    townscript_instance.token = 'test_token'
    
    # Mock failed response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    with pytest.raises(Exception) as exc_info:
        townscript_instance.TSget('/test/endpoint')
    
    assert "Status code 404" in str(exc_info.value)


@patch('src.townscript.Townscript._getAPI')
def test_get_events_success(mock_get_api, townscript_instance):
    """Test getEvents with successful response."""
    # Mock response
    mock_response = MagicMock()
    event_data = {'eventCode': 'TEST2024', 'name': 'Test Event'}
    mock_response.json.return_value = {'data': json.dumps(event_data)}
    mock_get_api.return_value = mock_response
    
    result = townscript_instance.getEvents('TEST2024')
    
    assert result == event_data
    assert townscript_instance.event == event_data


@patch('src.townscript.Townscript._getAPI')
def test_get_events_failure(mock_get_api, townscript_instance, capsys):
    """Test getEvents with failed response."""
    # Mock failed response
    mock_get_api.side_effect = Exception("API Error")
    
    result = townscript_instance.getEvents('TEST2024')
    
    # Should print error and return None
    captured = capsys.readouterr()
    assert "Error:" in captured.out
    assert result is None


@patch('src.townscript.Townscript._getAPI')
def test_get_data_success(mock_get_api, townscript_instance):
    """Test getData with successful response."""
    # Mock response
    mock_response = MagicMock()
    registration_data = [{'registrationId': 1, 'userName': 'Test User'}]
    mock_response.json.return_value = {'data': json.dumps(registration_data)}
    mock_get_api.return_value = mock_response
    
    result = townscript_instance.getData('TEST2024')
    
    assert result == registration_data


@patch('src.townscript.Townscript._getAPI')
def test_get_page_data_success(mock_get_api, townscript_instance):
    """Test getPageData with successful response."""
    # Mock response
    mock_response = MagicMock()
    page_data = {'title': 'Test Event Page', 'description': 'Test Description'}
    mock_response.json.return_value = {'data': json.dumps(page_data)}
    mock_get_api.return_value = mock_response
    
    result = townscript_instance.getPageData('TEST2024')
    
    assert result == page_data


@patch('src.townscript.requests.get')
def test_getapi_success(mock_get, townscript_instance):
    """Test _getAPI with successful request."""
    townscript_instance.token = 'test_token'
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    result = townscript_instance._getAPI('https://api.example.com/test')
    
    assert result == mock_response
    
    # Verify headers
    call_args = mock_get.call_args
    headers = call_args[1]['headers']
    assert headers['Authorization'] == 'test_token'
    assert headers['accept'] == 'application/json'


@patch('src.townscript.requests.get')
def test_getapi_exception(mock_get, townscript_instance, capsys):
    """Test _getAPI with exception."""
    townscript_instance.token = 'test_token'
    
    mock_get.side_effect = Exception("Network Error")
    
    result = townscript_instance._getAPI('https://api.example.com/test')
    
    # Should print error and return None
    captured = capsys.readouterr()
    assert "Error:" in captured.out
    assert result is None


def test_townscript_api_base_url(townscript_instance):
    """Test that API base URL is correctly set from config."""
    assert townscript_instance.cfg['api']['base'] == 'https://www.townscript.com/api'

# Made with Bob
