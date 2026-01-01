"""Shared pytest fixtures and configuration for test suite."""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import streamlit as st


@pytest.fixture(scope="function")
def mock_streamlit_secrets():
    """Mock Streamlit secrets for testing."""
    mock_secrets = {
        "REPLICATE_API_TOKEN": "test-token-12345",
        "REPLICATE_MODEL_ENDPOINTSTABILITY": "stability-ai/sdxl:test-version"
    }
    return mock_secrets


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
