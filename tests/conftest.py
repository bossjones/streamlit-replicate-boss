"""Shared pytest fixtures and configuration for test suite."""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import streamlit as st


def pytest_configure(config):
    """Configure pytest hooks - runs before test collection."""
    # Set up st.secrets early to avoid import-time errors
    if not hasattr(st, 'secrets') or st.secrets is None:
        mock_secrets_dict = {
            "REPLICATE_API_TOKEN": "test-token-12345",
            "REPLICATE_MODEL_ENDPOINTSTABILITY": "stability-ai/sdxl:test-version"
        }
        
        # Create a mock secrets object that supports both dict access and .get()
        mock_secrets = MagicMock()
        mock_secrets.__getitem__ = lambda self, key: mock_secrets_dict[key]
        mock_secrets.get = lambda key, default=None: mock_secrets_dict.get(key, default)
        mock_secrets.__contains__ = lambda self, key: key in mock_secrets_dict
        mock_secrets.__bool__ = lambda self: True
        
        st.secrets = mock_secrets


@pytest.fixture(scope="function", autouse=True)
def mock_streamlit_secrets():
    """Mock Streamlit secrets for testing.
    
    This fixture is autouse=True to ensure st.secrets is always available
    before any module imports that might access it.
    """
    mock_secrets_dict = {
        "REPLICATE_API_TOKEN": "test-token-12345",
        "REPLICATE_MODEL_ENDPOINTSTABILITY": "stability-ai/sdxl:test-version"
    }
    
    # Create a mock secrets object that supports both dict access and .get()
    mock_secrets = MagicMock()
    mock_secrets.__getitem__ = lambda self, key: mock_secrets_dict[key]
    mock_secrets.get = lambda key, default=None: mock_secrets_dict.get(key, default)
    mock_secrets.__contains__ = lambda self, key: key in mock_secrets_dict
    mock_secrets.__bool__ = lambda self: True
    
    # Patch st.secrets to use our mock
    with patch.object(st, 'secrets', mock_secrets, create=True):
        yield mock_secrets


@pytest.fixture(scope="function")
def mock_replicate_run():
    """Mock Replicate API run function."""
    with patch('replicate.run') as mock_run:
        # Default mock response - single image URL
        mock_run.return_value = ["https://example.com/generated-image.png"]
        yield mock_run


@pytest.fixture(scope="function")
def mock_requests_get():
    """Mock requests.get for downloading images."""
    with patch('requests.get') as mock_get:
        # Default mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake-image-data'
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture(scope="function")
def temp_yaml_file():
    """Create a temporary YAML file for testing."""
    content = """models:
  - id: "test-model-1"
    name: "Test Model 1"
    endpoint: "owner/model:version"
    trigger_words: ["test"]
    default_settings:
      width: 1024
      height: 1024
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture(scope="function", autouse=True)
def reset_streamlit_state():
    """Reset Streamlit session state before each test."""
    if hasattr(st, 'session_state'):
        st.session_state.clear()
    yield
    if hasattr(st, 'session_state'):
        st.session_state.clear()


@pytest.fixture(scope="function")
def mock_streamlit_page_config():
    """Mock Streamlit page configuration."""
    with patch('streamlit_app.st.set_page_config') as mock_config:
        yield mock_config


@pytest.fixture(scope="function")
def mock_streamlit_empty():
    """Mock Streamlit empty placeholders."""
    with patch('streamlit_app.st.empty') as mock_empty:
        mock_placeholder = MagicMock()
        mock_container = MagicMock()
        mock_placeholder.container.return_value = mock_container
        mock_empty.return_value = mock_placeholder
        yield mock_empty, mock_placeholder, mock_container


@pytest.fixture(scope="function")
def mock_streamlit_status():
    """Mock Streamlit status context manager."""
    with patch('streamlit_app.st.status') as mock_status:
        mock_status_ctx = MagicMock()
        mock_status.return_value.__enter__.return_value = mock_status_ctx
        mock_status.return_value.__exit__.return_value = None
        yield mock_status, mock_status_ctx


@pytest.fixture(scope="function")
def sample_model_configs():
    """Sample model configurations for testing."""
    return [
        {
            'id': 'model-1',
            'name': 'Model 1',
            'endpoint': 'owner/model1:version1',
            'default': True
        },
        {
            'id': 'model-2',
            'name': 'Model 2',
            'endpoint': 'owner/model2:version2'
        }
    ]
