"""Integration tests for backward compatibility with existing configuration.

Tests verify that the app maintains backward compatibility with existing
single-model setup using secrets.toml when models.yaml is missing.
"""
import pytest
import streamlit as st
from unittest.mock import patch, MagicMock, Mock
import tempfile
import os
from pathlib import Path

from streamlit_app import initialize_session_state, get_replicate_model_endpoint
from config.model_loader import load_models_config


class TestBackwardCompatibilityFallback:
    """Tests for backward compatibility fallback to secrets.toml (AC: 1, 2, 3, 6)."""
    
    @pytest.fixture(autouse=True)
    def reset_session_state(self):
        """Reset session state before each test."""
        if hasattr(st, 'session_state'):
            # Clear only our keys
            for key in ['model_configs', 'selected_model', 'presets']:
                if key in st.session_state:
                    del st.session_state[key]
        yield
        if hasattr(st, 'session_state'):
            for key in ['model_configs', 'selected_model', 'presets']:
                if key in st.session_state:
                    del st.session_state[key]
    
    @pytest.mark.integration
    def test_fallback_detection_when_models_yaml_missing_with_secrets(self, mock_streamlit_secrets):
        """Test AC1: Fallback detection when models.yaml is missing and REPLICATE_MODEL_ENDPOINTSTABILITY exists."""
        # GIVEN: models.yaml doesn't exist and secrets.toml has REPLICATE_MODEL_ENDPOINTSTABILITY
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value="stability-ai/sdxl:real-version"):
                with patch('streamlit_app.st.warning') as mock_warning:
                    with patch('streamlit_app.st.info') as mock_info:
                        # WHEN: Calling initialize_session_state
                        initialize_session_state()
                        
                        # THEN: Should detect fallback and check for secrets
                        mock_warning.assert_called()  # Warning about missing models.yaml
                        # Should create fallback model
                        assert 'model_configs' in st.session_state
                        assert len(st.session_state.model_configs) == 1
                        assert st.session_state.model_configs[0]['id'] == 'default'
                        assert st.session_state.model_configs[0]['name'] == 'Default Model (from secrets.toml)'
                        assert st.session_state.model_configs[0]['endpoint'] == "stability-ai/sdxl:real-version"
                        assert st.session_state.selected_model == st.session_state.model_configs[0]
                        mock_info.assert_called()  # Info message about fallback mode
    
    @pytest.mark.integration
    def test_fallback_detection_when_models_yaml_missing_without_secrets(self, mock_streamlit_secrets):
        """Test AC1: Fallback detection when models.yaml is missing and REPLICATE_MODEL_ENDPOINTSTABILITY is not in secrets."""
        # GIVEN: models.yaml doesn't exist and secrets.toml doesn't have REPLICATE_MODEL_ENDPOINTSTABILITY
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value="stability-ai/sdxl:test-version"):
                with patch('streamlit_app.st.warning') as mock_warning:
                    with patch('streamlit_app.st.error') as mock_error:
                        # WHEN: Calling initialize_session_state
                        initialize_session_state()
                        
                        # THEN: Should detect fallback but no valid endpoint
                        mock_warning.assert_called()  # Warning about missing models.yaml
                        # Should not create fallback model (test version is rejected)
                        assert 'model_configs' in st.session_state
                        assert st.session_state.model_configs == []
                        assert st.session_state.selected_model is None
                        mock_error.assert_called()  # Error about no fallback available
    
    @pytest.mark.integration
    def test_automatic_single_model_configuration_from_secrets(self, mock_streamlit_secrets):
        """Test AC2: Automatic single-model configuration creation from secrets.toml."""
        # GIVEN: models.yaml missing, secrets.toml has valid endpoint
        fallback_endpoint = "stability-ai/sdxl:2b017d9b67edd2ee1401238df49d75da53c523f36e363881e057f5dc3ed3c5b2"
        
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value=fallback_endpoint):
                # WHEN: Calling initialize_session_state
                initialize_session_state()
                
                # THEN: Should create single-model configuration with correct structure
                assert 'model_configs' in st.session_state
                assert len(st.session_state.model_configs) == 1
                
                fallback_model = st.session_state.model_configs[0]
                assert fallback_model['id'] == 'default'
                assert fallback_model['name'] == 'Default Model (from secrets.toml)'
                assert fallback_model['endpoint'] == fallback_endpoint
                
                # Verify fallback model is set as selected_model
                assert st.session_state.selected_model == fallback_model
                assert st.session_state.selected_model['id'] == 'default'
    
    @pytest.mark.integration
    def test_fallback_model_structure_matches_expected_format(self, mock_streamlit_secrets):
        """Test AC2: Fallback model structure matches expected format."""
        # GIVEN: models.yaml missing, secrets.toml has valid endpoint
        fallback_endpoint = "owner/model:version"
        
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value=fallback_endpoint):
                # WHEN: Calling initialize_session_state
                initialize_session_state()
                
                # THEN: Fallback model should have all required fields
                fallback_model = st.session_state.model_configs[0]
                assert 'id' in fallback_model
                assert 'name' in fallback_model
                assert 'endpoint' in fallback_model
                assert isinstance(fallback_model['id'], str)
                assert isinstance(fallback_model['name'], str)
                assert isinstance(fallback_model['endpoint'], str)
    
    @pytest.mark.integration
    def test_app_functions_normally_with_secrets_only(self, mock_streamlit_secrets):
        """Test AC3: App functions normally with secrets.toml only (no models.yaml)."""
        # GIVEN: models.yaml missing, secrets.toml has valid endpoint
        fallback_endpoint = "stability-ai/sdxl:real-version"
        
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value=fallback_endpoint):
                # WHEN: Calling initialize_session_state
                initialize_session_state()
                
                # THEN: App should function normally
                assert 'model_configs' in st.session_state
                assert 'selected_model' in st.session_state
                assert st.session_state.selected_model is not None
                assert st.session_state.model_configs[0] == st.session_state.selected_model
                
                # Verify model selector would display fallback model correctly
                assert st.session_state.selected_model['id'] == 'default'
                assert st.session_state.selected_model['name'] == 'Default Model (from secrets.toml)'
                assert st.session_state.selected_model['endpoint'] == fallback_endpoint
    
    @pytest.mark.integration
    def test_preset_loading_works_in_fallback_mode(self, mock_streamlit_secrets):
        """Test AC3: Preset loading still works in fallback mode."""
        # GIVEN: models.yaml missing, secrets.toml has valid endpoint
        fallback_endpoint = "stability-ai/sdxl:real-version"
        
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value=fallback_endpoint):
                with patch('streamlit_app.load_presets_config', return_value={'default': [{'name': 'Test Preset'}]}):
                    # WHEN: Calling initialize_session_state
                    initialize_session_state()
                    
                    # THEN: Presets should be loaded even in fallback mode
                    assert 'presets' in st.session_state
                    assert st.session_state.presets == {'default': [{'name': 'Test Preset'}]}
    
    @pytest.mark.integration
    def test_no_errors_with_fallback_configuration(self, mock_streamlit_secrets):
        """Test AC3: No errors occur when using fallback configuration."""
        # GIVEN: models.yaml missing, secrets.toml has valid endpoint
        fallback_endpoint = "stability-ai/sdxl:real-version"
        
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value=fallback_endpoint):
                with patch('streamlit_app.st.warning') as mock_warning:
                    with patch('streamlit_app.st.info') as mock_info:
                        with patch('streamlit_app.st.error') as mock_error:
                            # WHEN: Calling initialize_session_state
                            initialize_session_state()
                            
                            # THEN: Should not raise exceptions
                            # Warning is expected, but no errors
                            mock_warning.assert_called()  # Expected: warning about missing models.yaml
                            mock_info.assert_called()  # Expected: info about fallback mode
                            mock_error.assert_not_called()  # No errors should occur
    
    @pytest.mark.integration
    def test_models_yaml_takes_precedence_when_both_exist(self, mock_streamlit_secrets):
        """Test AC6: models.yaml takes precedence when both exist."""
        # GIVEN: Both models.yaml and secrets.toml exist
        models_from_yaml = [
            {'id': 'model-1', 'name': 'Model 1', 'endpoint': 'owner/model1:version1'},
            {'id': 'model-2', 'name': 'Model 2', 'endpoint': 'owner/model2:version2'}
        ]
        
        with patch('streamlit_app.load_models_config', return_value=models_from_yaml):
            # WHEN: Calling initialize_session_state
            initialize_session_state()
            
            # THEN: Should use models.yaml, not fallback
            assert 'model_configs' in st.session_state
            assert len(st.session_state.model_configs) == 2
            assert st.session_state.model_configs[0]['id'] == 'model-1'
            assert st.session_state.model_configs[1]['id'] == 'model-2'
            # Should NOT be the fallback model
            assert st.session_state.selected_model['id'] != 'default'
            assert st.session_state.selected_model['id'] in ['model-1', 'model-2']
    
    @pytest.mark.integration
    def test_secrets_used_as_fallback_when_models_yaml_missing(self, mock_streamlit_secrets):
        """Test AC6: secrets.toml used as fallback when models.yaml missing."""
        # GIVEN: models.yaml missing, secrets.toml has valid endpoint
        fallback_endpoint = "stability-ai/sdxl:real-version"
        
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value=fallback_endpoint):
                # WHEN: Calling initialize_session_state
                initialize_session_state()
                
                # THEN: Should use secrets.toml as fallback
                assert st.session_state.model_configs[0]['id'] == 'default'
                assert st.session_state.model_configs[0]['endpoint'] == fallback_endpoint
    
    @pytest.mark.integration
    def test_no_conflicts_between_configurations(self, mock_streamlit_secrets):
        """Test AC6: No conflicts between configurations."""
        # GIVEN: models.yaml exists (should be used)
        models_from_yaml = [
            {'id': 'model-1', 'name': 'Model 1', 'endpoint': 'owner/model1:version1'}
        ]
        
        with patch('streamlit_app.load_models_config', return_value=models_from_yaml):
            # WHEN: Calling initialize_session_state
            initialize_session_state()
            
            # THEN: Should use models.yaml, secrets.toml should not interfere
            assert len(st.session_state.model_configs) == 1
            assert st.session_state.model_configs[0]['id'] == 'model-1'
            # Verify no fallback model is present
            assert st.session_state.model_configs[0]['id'] != 'default'


class TestBackwardCompatibilityMigration:
    """Tests for migration path from secrets.toml to models.yaml (AC: 4, 5)."""
    
    @pytest.fixture(autouse=True)
    def reset_session_state(self):
        """Reset session state before each test."""
        if hasattr(st, 'session_state'):
            for key in ['model_configs', 'selected_model', 'presets']:
                if key in st.session_state:
                    del st.session_state[key]
        yield
        if hasattr(st, 'session_state'):
            for key in ['model_configs', 'selected_model', 'presets']:
                if key in st.session_state:
                    del st.session_state[key]
    
    @pytest.mark.integration
    def test_app_switches_from_fallback_to_models_yaml_when_added(self, mock_streamlit_secrets):
        """Test AC4: App switches from fallback to models.yaml when file is added."""
        # GIVEN: Initially no models.yaml (fallback mode)
        fallback_endpoint = "stability-ai/sdxl:real-version"
        
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value=fallback_endpoint):
                # WHEN: First initialization (fallback mode)
                initialize_session_state()
                assert st.session_state.model_configs[0]['id'] == 'default'
        
        # GIVEN: Now models.yaml exists
        models_from_yaml = [
            {'id': 'model-1', 'name': 'Model 1', 'endpoint': 'owner/model1:version1'}
        ]
        
        # Clear session state to simulate app restart
        if 'model_configs' in st.session_state:
            del st.session_state.model_configs
        if 'selected_model' in st.session_state:
            del st.session_state.selected_model
        
        with patch('streamlit_app.load_models_config', return_value=models_from_yaml):
            # WHEN: Re-initialization with models.yaml present
            initialize_session_state()
            
            # THEN: Should use models.yaml instead of fallback
            assert len(st.session_state.model_configs) == 1
            assert st.session_state.model_configs[0]['id'] == 'model-1'
            assert st.session_state.model_configs[0]['id'] != 'default'
    
    @pytest.mark.integration
    def test_no_code_changes_needed_for_migration(self, mock_streamlit_secrets):
        """Test AC4: No code changes needed to switch from fallback to models.yaml."""
        # GIVEN: App works with fallback
        fallback_endpoint = "stability-ai/sdxl:real-version"
        
        with patch('streamlit_app.load_models_config', side_effect=FileNotFoundError("models.yaml not found")):
            with patch('streamlit_app.get_replicate_model_endpoint', return_value=fallback_endpoint):
                initialize_session_state()
                # Verify fallback works
                assert st.session_state.model_configs[0]['id'] == 'default'
        
        # GIVEN: User adds models.yaml
        models_from_yaml = [
            {'id': 'model-1', 'name': 'Model 1', 'endpoint': 'owner/model1:version1'}
        ]
        
        # Clear session state
        if 'model_configs' in st.session_state:
            del st.session_state.model_configs
        if 'selected_model' in st.session_state:
            del st.session_state.selected_model
        
        with patch('streamlit_app.load_models_config', return_value=models_from_yaml):
            # WHEN: Re-initialization (same code, just models.yaml now exists)
            initialize_session_state()
            
            # THEN: Should automatically use models.yaml without code changes
            assert st.session_state.model_configs[0]['id'] == 'model-1'
            # The same initialize_session_state() function handles both cases
            # No code changes needed - migration is automatic
