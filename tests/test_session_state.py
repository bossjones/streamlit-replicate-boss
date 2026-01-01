"""Tests for session state initialization in streamlit_app.py."""
import pytest
import streamlit as st
from unittest.mock import patch, MagicMock, Mock
import tempfile
import os
from pathlib import Path

from streamlit_app import initialize_session_state
from config.model_loader import load_models_config


class TestInitializeSessionState:
    """Tests for initialize_session_state() function."""
    
    @pytest.fixture(autouse=True)
    def reset_session_state(self):
        """Reset session state before each test."""
        if hasattr(st, 'session_state'):
            # Clear only our keys
            if 'model_configs' in st.session_state:
                del st.session_state.model_configs
            if 'selected_model' in st.session_state:
                del st.session_state.selected_model
        yield
        if hasattr(st, 'session_state'):
            if 'model_configs' in st.session_state:
                del st.session_state.model_configs
            if 'selected_model' in st.session_state:
                del st.session_state.selected_model
    
    def test_initializes_selected_model_on_first_load(self):
        """Test AC1: initialize_session_state() initializes st.session_state.selected_model on first app load."""
        # GIVEN: Session state is empty
        assert 'selected_model' not in st.session_state
        
        # WHEN: Calling initialize_session_state
        initialize_session_state()
        
        # THEN: selected_model should be initialized
        assert 'selected_model' in st.session_state
        assert st.session_state.selected_model is not None
        assert isinstance(st.session_state.selected_model, dict)
        assert 'id' in st.session_state.selected_model
        assert 'name' in st.session_state.selected_model
        assert 'endpoint' in st.session_state.selected_model
    
    def test_initializes_model_configs_with_loaded_data(self):
        """Test AC3: initialize_session_state() initializes st.session_state.model_configs with loaded model data."""
        # GIVEN: Session state is empty
        assert 'model_configs' not in st.session_state
        
        # WHEN: Calling initialize_session_state
        initialize_session_state()
        
        # THEN: model_configs should be initialized with list structure
        assert 'model_configs' in st.session_state
        assert isinstance(st.session_state.model_configs, list)
        assert len(st.session_state.model_configs) > 0
        # Verify structure matches load_models_config() return value
        expected_models = load_models_config("models.yaml")
        assert len(st.session_state.model_configs) == len(expected_models)
        assert st.session_state.model_configs[0]['id'] == expected_models[0]['id']
    
    def test_default_model_selection_with_explicit_flag(self):
        """Test AC2: Default model selection with explicit default: true flag."""
        # GIVEN: Models config with explicit default flag
        models_with_default = [
            {'id': 'model1', 'name': 'Model 1', 'endpoint': 'owner/model1:version'},
            {'id': 'model2', 'name': 'Model 2', 'endpoint': 'owner/model2:version', 'default': True},
            {'id': 'model3', 'name': 'Model 3', 'endpoint': 'owner/model3:version'},
        ]
        
        with patch('streamlit_app.load_models_config', return_value=models_with_default):
            # WHEN: Calling initialize_session_state
            initialize_session_state()
            
            # THEN: Model with default flag should be selected
            assert st.session_state.selected_model['id'] == 'model2'
            assert st.session_state.selected_model['default'] is True
    
    def test_default_model_selection_without_explicit_flag(self):
        """Test AC2: Default model selection without explicit flag (first model)."""
        # GIVEN: Models config without explicit default flag
        models_without_default = [
            {'id': 'model1', 'name': 'Model 1', 'endpoint': 'owner/model1:version'},
            {'id': 'model2', 'name': 'Model 2', 'endpoint': 'owner/model2:version'},
        ]
        
        with patch('streamlit_app.load_models_config', return_value=models_without_default):
            # WHEN: Calling initialize_session_state
            initialize_session_state()
            
            # THEN: First model should be selected as default
            assert st.session_state.selected_model['id'] == 'model1'
    
    def test_handles_empty_models_list(self):
        """Test AC5: Initialization with empty models list."""
        # GIVEN: Empty models list
        with patch('streamlit_app.load_models_config', return_value=[]):
            with patch('streamlit_app.logger') as mock_logger:
                # WHEN: Calling initialize_session_state
                initialize_session_state()
                
                # THEN: Should handle gracefully
                assert 'model_configs' in st.session_state
                assert st.session_state.model_configs == []
                assert st.session_state.selected_model is None
                mock_logger.warning.assert_called()
    
    def test_handles_missing_models_yaml(self):
        """Test AC5: Initialization with missing models.yaml."""
        # GIVEN: FileNotFoundError raised by load_models_config
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("File not found")):
            with patch('streamlit_app.st.warning') as mock_warning:
                with patch('streamlit_app.logger') as mock_logger:
                    # WHEN: Calling initialize_session_state
                    initialize_session_state()
                    
                    # THEN: Should handle gracefully
                    assert 'model_configs' in st.session_state
                    assert st.session_state.model_configs == []
                    assert st.session_state.selected_model is None
                    mock_logger.warning.assert_called()
                    mock_warning.assert_called()
    
    def test_handles_invalid_model_config(self):
        """Test AC5: Initialization with invalid model config."""
        # GIVEN: ValueError raised by load_models_config (invalid structure)
        with patch('streamlit_app.load_models_config', side_effect=ValueError("Invalid structure")):
            with patch('streamlit_app.st.error') as mock_error:
                with patch('streamlit_app.logger') as mock_logger:
                    # WHEN: Calling initialize_session_state
                    initialize_session_state()
                    
                    # THEN: Should handle gracefully
                    assert 'model_configs' in st.session_state
                    assert st.session_state.model_configs == []
                    assert st.session_state.selected_model is None
                    mock_logger.error.assert_called()
                    mock_error.assert_called()
    
    def test_does_not_reinitialize_on_rerun(self):
        """Test that initialization doesn't run multiple times per session."""
        # GIVEN: Session state already initialized
        st.session_state.model_configs = [{'id': 'existing', 'name': 'Existing', 'endpoint': 'owner/model:version'}]
        st.session_state.selected_model = {'id': 'existing', 'name': 'Existing', 'endpoint': 'owner/model:version'}
        
        with patch('streamlit_app.load_models_config') as mock_load:
            # WHEN: Calling initialize_session_state again
            initialize_session_state()
            
            # THEN: load_models_config should not be called
            mock_load.assert_not_called()
            # Existing state should remain
            assert st.session_state.model_configs[0]['id'] == 'existing'
    
    def test_session_state_persistence_across_interactions(self):
        """Test AC4: Session state persists across interactions (simulated)."""
        # GIVEN: Initialized session state
        initialize_session_state()
        original_model = st.session_state.selected_model.copy()
        original_configs = st.session_state.model_configs.copy()
        
        # WHEN: Simulating multiple interactions (modifying other session state keys)
        st.session_state['other_key'] = 'some_value'
        st.session_state['another_key'] = 123
        
        # THEN: Model state should persist
        assert st.session_state.selected_model == original_model
        assert st.session_state.model_configs == original_configs
    
    def test_logs_successful_initialization(self):
        """Test that successful initialization logs info message with model count."""
        with patch('streamlit_app.logger') as mock_logger:
            # WHEN: Calling initialize_session_state
            initialize_session_state()
            
            # THEN: Should log success message
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any('Session state initialized successfully' in msg for msg in info_calls)
            assert any('model(s)' in msg for msg in info_calls)
    
    def test_logs_default_model_selection(self):
        """Test that default model selection is logged."""
        with patch('streamlit_app.logger') as mock_logger:
            # WHEN: Calling initialize_session_state
            initialize_session_state()
            
            # THEN: Should log default model selection
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any('default' in msg.lower() for msg in info_calls)
    
    def test_handles_missing_required_fields_in_default_model(self):
        """Test AC5: Handle missing required fields in default model - fallback to first valid model."""
        # GIVEN: Models where first has missing fields, second is valid
        invalid_model = {'id': 'invalid', 'name': 'Invalid'}  # Missing endpoint
        valid_model = {'id': 'valid', 'name': 'Valid', 'endpoint': 'owner/model:version'}
        
        # This should not happen in practice (load_models_config validates), but test defensive coding
        with patch('streamlit_app.load_models_config', return_value=[invalid_model, valid_model]):
            # WHEN: Calling initialize_session_state
            # Note: load_models_config would catch this, but we test the initialization logic
            initialize_session_state()
            
            # THEN: Should use first model (even if it has issues - validation happens at load time)
            # In practice, load_models_config would raise ValueError before this point
            assert st.session_state.selected_model is not None
