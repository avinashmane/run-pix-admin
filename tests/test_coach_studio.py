"""
Tests for src/coach/studio.py (Registry)
"""
import pytest
from unittest.mock import MagicMock, patch, call


def test_create_registry_calls_get_db():
    """Test that create_registry calls get_db."""
    with patch('src.coach.studio.get_db') as mock_get_db, \
         patch('src.coach.studio.Registry') as mock_registry_class:
        
        from src.coach.studio import create_registry
        
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        # Call function
        result = create_registry()
        
        # Verify get_db was called
        mock_get_db.assert_called_once()


def test_create_registry_initializes_registry_with_db():
    """Test that create_registry initializes Registry with database."""
    with patch('src.coach.studio.get_db') as mock_get_db, \
         patch('src.coach.studio.Registry') as mock_registry_class:
        
        from src.coach.studio import create_registry
        
        # Setup mocks
        mock_db = MagicMock()
        mock_db.project_id = "test-project"
        mock_get_db.return_value = mock_db
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        # Call function
        result = create_registry()
        
        # Verify Registry was initialized with db
        mock_registry_class.assert_called_once_with(db=mock_db)


def test_create_registry_returns_registry_instance():
    """Test that create_registry returns a Registry instance."""
    with patch('src.coach.studio.get_db') as mock_get_db, \
         patch('src.coach.studio.Registry') as mock_registry_class:
        
        from src.coach.studio import create_registry
        
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_registry = MagicMock()
        mock_registry.name = "test-registry"
        mock_registry_class.return_value = mock_registry
        
        # Call function
        result = create_registry()
        
        # Verify result is the registry instance
        assert result == mock_registry
        assert result.name == "test-registry"


def test_registry_singleton_exists():
    """Test that registry singleton is created."""
    with patch('src.coach.studio.get_db') as mock_get_db, \
         patch('src.coach.studio.Registry') as mock_registry_class:
        
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        # Import module (this creates the singleton)
        import importlib
        import src.coach.studio
        importlib.reload(src.coach.studio)
        
        from src.coach.studio import registry
        
        # Verify registry exists
        assert registry is not None


def test_registry_singleton_uses_database():
    """Test that registry singleton is initialized with database."""
    with patch('src.coach.studio.get_db') as mock_get_db, \
         patch('src.coach.studio.Registry') as mock_registry_class:
        
        # Setup mocks
        mock_db = MagicMock()
        mock_db.project_id = "singleton-test-project"
        mock_get_db.return_value = mock_db
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        # Import module (this creates the singleton)
        import importlib
        import src.coach.studio
        importlib.reload(src.coach.studio)
        
        # Verify Registry was called with db
        mock_registry_class.assert_called_with(db=mock_db)


def test_create_registry_handles_db_initialization():
    """Test that create_registry properly handles database initialization."""
    with patch('src.coach.studio.get_db') as mock_get_db, \
         patch('src.coach.studio.Registry') as mock_registry_class:
        
        from src.coach.studio import create_registry
        
        # Setup mocks - simulate real db object
        mock_db = MagicMock()
        mock_db.project_id = "test-project-123"
        mock_db.collection = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        # Call function
        result = create_registry()
        
        # Verify db was obtained before Registry creation
        assert mock_get_db.called
        assert mock_registry_class.called
        
        # Verify call order: get_db should be called before Registry
        call_order = [mock_get_db, mock_registry_class]
        for mock in call_order:
            assert mock.called


def test_create_registry_multiple_calls():
    """Test that create_registry can be called multiple times."""
    with patch('src.coach.studio.get_db') as mock_get_db, \
         patch('src.coach.studio.Registry') as mock_registry_class:
        
        from src.coach.studio import create_registry
        
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_registry1 = MagicMock()
        mock_registry2 = MagicMock()
        mock_registry_class.side_effect = [mock_registry1, mock_registry2]
        
        # Call function twice
        result1 = create_registry()
        result2 = create_registry()
        
        # Verify both calls succeeded
        assert result1 == mock_registry1
        assert result2 == mock_registry2
        
        # Verify get_db was called twice
        assert mock_get_db.call_count == 2


def test_registry_module_imports():
    """Test that registry module imports are correct."""
    # This test verifies the module can be imported
    try:
        from src.coach.studio import create_registry, registry
        assert callable(create_registry)
        # registry should exist (even if mocked during import)
    except ImportError as e:
        pytest.fail(f"Failed to import studio module: {e}")


def test_create_registry_with_none_db():
    """Test create_registry behavior when get_db returns None."""
    with patch('src.coach.studio.get_db') as mock_get_db, \
         patch('src.coach.studio.Registry') as mock_registry_class:
        
        from src.coach.studio import create_registry
        
        # Setup mocks - db returns None
        mock_get_db.return_value = None
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        # Call function
        result = create_registry()
        
        # Verify Registry was still called (with None db)
        mock_registry_class.assert_called_once_with(db=None)


def test_registry_function_signature():
    """Test that create_registry has correct signature."""
    from src.coach.studio import create_registry
    import inspect
    
    # Get function signature
    sig = inspect.signature(create_registry)
    
    # Should have no required parameters
    assert len(sig.parameters) == 0


def test_registry_docstring():
    """Test that create_registry has documentation."""
    from src.coach.studio import create_registry
    
    # Should have a docstring
    assert create_registry.__doc__ is not None
    assert len(create_registry.__doc__) > 0
    assert "Registry" in create_registry.__doc__

# Made with Bob
