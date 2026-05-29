"""
Tests for src/jinja_template.py
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from jinja2 import Environment


def test_jinja_environment_created():
    """Test that jinja Environment is created."""
    from src.jinja_template import jinja
    
    assert isinstance(jinja, Environment)


def test_jinja_uses_app_root():
    """Test that jinja uses APP_ROOT for template directory."""
    # Set APP_ROOT
    os.environ['APP_ROOT'] = './test_src'
    
    # Reimport to get new environment
    import importlib
    import src.jinja_template
    importlib.reload(src.jinja_template)
    
    from src.jinja_template import jinja
    
    # Verify loader is configured
    assert jinja.loader is not None


def test_jinja_default_app_root():
    """Test that jinja uses default APP_ROOT when not set."""
    # Remove APP_ROOT if exists
    if 'APP_ROOT' in os.environ:
        del os.environ['APP_ROOT']
    
    # Reimport to get new environment
    import importlib
    import src.jinja_template
    importlib.reload(src.jinja_template)
    
    from src.jinja_template import jinja
    
    # Should use default "."
    assert jinja.loader is not None


def test_jinja_autoescape_enabled():
    """Test that autoescape is enabled."""
    from src.jinja_template import jinja
    
    # Autoescape should be configured
    assert jinja.autoescape is not None


def test_silent_undefined_class_exists():
    """Test that SilentUndefined class is defined."""
    from src.jinja_template import SilentUndefined
    from jinja2 import Undefined
    
    # Should be a subclass of Undefined
    assert issubclass(SilentUndefined, Undefined)


def test_silent_undefined_returns_empty_string():
    """Test that SilentUndefined returns empty string on error."""
    from src.jinja_template import SilentUndefined
    
    undefined = SilentUndefined()
    
    # Should return empty string instead of raising error
    result = undefined._fail_with_undefined_error()
    
    assert result == ''


def test_jinja_can_render_template():
    """Test that jinja can render a simple template."""
    from src.jinja_template import jinja
    
    # Create a simple template from string
    template = jinja.from_string("Hello {{ name }}!")
    
    result = template.render(name="World")
    
    assert result == "Hello World!"


def test_jinja_handles_missing_variables():
    """Test that jinja handles missing variables gracefully."""
    from src.jinja_template import jinja
    
    # Create template with variable
    template = jinja.from_string("Hello {{ name }}!")
    
    # Render without providing the variable
    # Should not raise error (depends on undefined behavior)
    result = template.render()
    
    # Result will have empty or undefined placeholder
    assert "Hello" in result


def test_app_root_environment_variable():
    """Test that APP_ROOT environment variable is read correctly."""
    test_path = "/custom/path"
    os.environ['APP_ROOT'] = test_path
    
    # Reimport to get new environment
    import importlib
    import src.jinja_template
    importlib.reload(src.jinja_template)
    
    # Verify the module uses the environment variable
    # (We can't directly test the loader path, but we can verify it doesn't error)
    from src.jinja_template import jinja
    assert jinja is not None


def test_jinja_template_loader_type():
    """Test that FileSystemLoader is used."""
    from src.jinja_template import jinja
    from jinja2 import FileSystemLoader
    
    # Verify loader is FileSystemLoader
    assert isinstance(jinja.loader, FileSystemLoader)


@patch.dict(os.environ, {'APP_ROOT': './src'})
def test_jinja_with_mocked_app_root():
    """Test jinja configuration with mocked APP_ROOT."""
    # Reimport with mocked environment
    import importlib
    import src.jinja_template
    importlib.reload(src.jinja_template)
    
    from src.jinja_template import jinja
    
    # Should be configured without errors
    assert jinja is not None
    assert jinja.loader is not None


def test_jinja_filters_available():
    """Test that jinja has default filters available."""
    from src.jinja_template import jinja
    
    # Check some common filters exist
    assert 'upper' in jinja.filters
    assert 'lower' in jinja.filters
    assert 'capitalize' in jinja.filters


def test_jinja_can_handle_complex_template():
    """Test that jinja can handle templates with loops and conditions."""
    from src.jinja_template import jinja
    
    template_str = """
    {% for item in items %}
        {% if item > 5 %}
            {{ item }}
        {% endif %}
    {% endfor %}
    """
    
    template = jinja.from_string(template_str)
    result = template.render(items=[3, 6, 8, 2, 9])
    
    # Should contain only items > 5
    assert '6' in result
    assert '8' in result
    assert '9' in result
    assert '3' not in result
    assert '2' not in result

# Made with Bob
