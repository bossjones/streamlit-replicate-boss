"""Unit tests for helper functions in streamlit_app.py."""
import pytest
import os
from unittest.mock import patch, MagicMock
import streamlit as st
from streamlit_app import get_secret, get_replicate_api_token, get_replicate_model_endpoint


class TestGetSecret:
    """Tests for get_secret() helper function."""
    
    @pytest.mark.unit
    def test_get_secret_from_streamlit_secrets(self):
        """[P2] Test that get_secret retrieves value from Streamlit secrets."""
        # GIVEN: Streamlit secrets with a key
        mock_secrets = MagicMock()
        mock_secrets.__getitem__ = lambda self, key: {"TEST_KEY": "secret-value"}[key]
        mock_secrets.get = lambda key, default=None: {"TEST_KEY": "secret-value"}.get(key, default)
        mock_secrets.__contains__ = lambda self, key: key in {"TEST_KEY": "secret-value"}
        mock_secrets.__bool__ = lambda self: True
        
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = mock_secrets
            
            # WHEN: Getting secret from Streamlit secrets
            result = get_secret("TEST_KEY")
            
            # THEN: Should return the secret value
            assert result == "secret-value"
    
    @pytest.mark.unit
    def test_get_secret_falls_back_to_environment_variable(self):
        """[P2] Test that get_secret falls back to environment variable when secret not in Streamlit."""
        # GIVEN: Streamlit secrets not available, but environment variable is set
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = None
            
            with patch.dict(os.environ, {"TEST_KEY": "env-value"}, clear=False):
                # WHEN: Getting secret
                result = get_secret("TEST_KEY")
                
                # THEN: Should return environment variable value
                assert result == "env-value"
    
    @pytest.mark.unit
    def test_get_secret_uses_default_when_not_found(self):
        """[P2] Test that get_secret uses default value when key not found."""
        # GIVEN: Secret not in Streamlit and not in environment
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = None
            
            with patch.dict(os.environ, {}, clear=True):
                # WHEN: Getting secret with default
                result = get_secret("MISSING_KEY", default="default-value")
                
                # THEN: Should return default value
                assert result == "default-value"
    
    @pytest.mark.unit
    def test_get_secret_handles_keyerror_gracefully(self):
        """[P2] Test that get_secret handles KeyError from Streamlit secrets gracefully."""
        # GIVEN: Streamlit secrets raises KeyError
        mock_secrets = MagicMock()
        mock_secrets.__getitem__ = lambda self, key: _raise(KeyError("Key not found"))
        mock_secrets.get = lambda key, default=None: default
        mock_secrets.__contains__ = lambda self, key: False
        mock_secrets.__bool__ = lambda self: True
        
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = mock_secrets
            
            with patch.dict(os.environ, {"TEST_KEY": "env-value"}, clear=False):
                # WHEN: Getting secret that doesn't exist in secrets
                result = get_secret("TEST_KEY", default="default-value")
                
                # THEN: Should fall back to environment variable
                assert result == "env-value"
    
    @pytest.mark.unit
    def test_get_secret_handles_attribute_error_gracefully(self):
        """[P2] Test that get_secret handles AttributeError when secrets is None."""
        # GIVEN: Streamlit secrets is None
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = None
            
            with patch.dict(os.environ, {"TEST_KEY": "env-value"}, clear=False):
                # WHEN: Getting secret
                result = get_secret("TEST_KEY", default="default-value")
                
                # THEN: Should fall back to environment variable
                assert result == "env-value"
    
    @pytest.mark.unit
    def test_get_secret_handles_runtime_error_gracefully(self):
        """[P2] Test that get_secret handles RuntimeError gracefully."""
        # GIVEN: Streamlit raises RuntimeError when accessing secrets
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = None
            mock_st.__getattribute__ = lambda self, name: _raise(RuntimeError("Not in Streamlit context"))
            
            with patch.dict(os.environ, {"TEST_KEY": "env-value"}, clear=False):
                # WHEN: Getting secret
                result = get_secret("TEST_KEY", default="default-value")
                
                # THEN: Should fall back to environment variable
                assert result == "env-value"


class TestGetReplicateApiToken:
    """Tests for get_replicate_api_token() helper function."""
    
    @pytest.mark.unit
    def test_get_replicate_api_token_from_secrets(self):
        """[P2] Test that get_replicate_api_token retrieves token from secrets."""
        # GIVEN: Streamlit secrets with API token
        mock_secrets = MagicMock()
        mock_secrets.__getitem__ = lambda self, key: {"REPLICATE_API_TOKEN": "real-token-123"}[key]
        mock_secrets.get = lambda key, default=None: {"REPLICATE_API_TOKEN": "real-token-123"}.get(key, default)
        mock_secrets.__contains__ = lambda self, key: key in {"REPLICATE_API_TOKEN": "real-token-123"}
        mock_secrets.__bool__ = lambda self: True
        
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = mock_secrets
            
            # WHEN: Getting API token
            result = get_replicate_api_token()
            
            # THEN: Should return the token from secrets
            assert result == "real-token-123"
    
    @pytest.mark.unit
    def test_get_replicate_api_token_uses_default_when_not_found(self):
        """[P2] Test that get_replicate_api_token uses default test token when not found."""
        # GIVEN: Secret not available
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = None
            
            with patch.dict(os.environ, {}, clear=True):
                # WHEN: Getting API token
                result = get_replicate_api_token()
                
                # THEN: Should return default test token
                assert result == "test-token-12345"


class TestGetReplicateModelEndpoint:
    """Tests for get_replicate_model_endpoint() helper function."""
    
    @pytest.mark.unit
    def test_get_replicate_model_endpoint_from_secrets(self):
        """[P2] Test that get_replicate_model_endpoint retrieves endpoint from secrets."""
        # GIVEN: Streamlit secrets with model endpoint
        mock_secrets = MagicMock()
        mock_secrets.__getitem__ = lambda self, key: {"REPLICATE_MODEL_ENDPOINTSTABILITY": "stability-ai/sdxl:real-version"}[key]
        mock_secrets.get = lambda key, default=None: {"REPLICATE_MODEL_ENDPOINTSTABILITY": "stability-ai/sdxl:real-version"}.get(key, default)
        mock_secrets.__contains__ = lambda self, key: key in {"REPLICATE_MODEL_ENDPOINTSTABILITY": "stability-ai/sdxl:real-version"}
        mock_secrets.__bool__ = lambda self: True
        
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = mock_secrets
            
            # WHEN: Getting model endpoint
            result = get_replicate_model_endpoint()
            
            # THEN: Should return the endpoint from secrets
            assert result == "stability-ai/sdxl:real-version"
    
    @pytest.mark.unit
    def test_get_replicate_model_endpoint_uses_default_when_not_found(self):
        """[P2] Test that get_replicate_model_endpoint uses default test endpoint when not found."""
        # GIVEN: Secret not available
        with patch('streamlit_app.st') as mock_st:
            mock_st.secrets = None
            
            with patch.dict(os.environ, {}, clear=True):
                # WHEN: Getting model endpoint
                result = get_replicate_model_endpoint()
                
                # THEN: Should return default test endpoint
                assert result == "stability-ai/sdxl:test-version"


def _raise(exc):
    """Helper function to raise an exception in lambda."""
    raise exc
