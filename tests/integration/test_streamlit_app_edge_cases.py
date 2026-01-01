"""Additional edge case and error scenario tests for streamlit_app.py."""
import pytest
from unittest.mock import patch, MagicMock, Mock
import streamlit as st
from streamlit_app import initialize_session_state, configure_sidebar, main_page


class MockSessionState:
    """Mock Streamlit session_state that supports both dict and attribute access."""
    def __init__(self):
        self._data = {}
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __contains__(self, key):
        return key in self._data
    
    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return self._data.get(name)
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            if not hasattr(self, '_data'):
                super().__setattr__('_data', {})
            self._data[name] = value
    
    def get(self, key, default=None):
        return self._data.get(key, default)


class TestInitializeSessionStateEdgeCases:
    """Edge case tests for initialize_session_state() function."""
    
    @pytest.mark.integration
    def test_initialize_session_state_handles_yaml_parse_error(self):
        """[P2] Test initialize_session_state handles YAML parsing errors gracefully."""
        # GIVEN: YAML file exists but has parse errors
        import yaml
        
        with patch('streamlit_app.load_models_config') as mock_load:
            mock_load.side_effect = yaml.YAMLError("Invalid YAML syntax")
            
            with patch('streamlit_app.st') as mock_st, \
                 patch('streamlit_app.logger') as mock_logger:
                
                mock_st.warning = MagicMock()
                mock_st.error = MagicMock()
                mock_st.session_state = MockSessionState()
                
                # WHEN: Calling initialize_session_state
                initialize_session_state()
                
                # THEN: Should handle gracefully
                assert mock_st.session_state['model_configs'] == []
                assert mock_st.session_state['selected_model'] is None
                mock_logger.error.assert_called()
                mock_st.error.assert_called()
    
    @pytest.mark.integration
    def test_initialize_session_state_handles_invalid_model_structure(self):
        """[P2] Test initialize_session_state handles invalid model structure."""
        # GIVEN: Models loaded but structure is invalid
        with patch('streamlit_app.load_models_config') as mock_load:
            mock_load.side_effect = ValueError("Invalid model structure")
            
            with patch('streamlit_app.st') as mock_st, \
                 patch('streamlit_app.logger') as mock_logger:
                
                mock_st.error = MagicMock()
                mock_st.session_state = MockSessionState()
                
                # WHEN: Calling initialize_session_state
                initialize_session_state()
                
                # THEN: Should handle gracefully
                assert mock_st.session_state['model_configs'] == []
                assert mock_st.session_state['selected_model'] is None
                mock_logger.error.assert_called()
                mock_st.error.assert_called()
    
    @pytest.mark.integration
    def test_initialize_session_state_logs_warning_for_empty_models(self):
        """[P2] Test initialize_session_state logs warning when models list is empty."""
        # GIVEN: Empty models list
        with patch('streamlit_app.load_models_config', return_value=[]):
            with patch('streamlit_app.st') as mock_st, \
                 patch('streamlit_app.logger') as mock_logger:
                
                mock_st.warning = MagicMock()
                mock_st.session_state = MockSessionState()
                
                # WHEN: Calling initialize_session_state
                initialize_session_state()
                
                # THEN: Should log warning
                mock_logger.warning.assert_called()
                assert 'model' in str(mock_logger.warning.call_args).lower()


class TestConfigureSidebarEdgeCases:
    """Edge case tests for configure_sidebar() function."""
    
    @pytest.mark.integration
    def test_configure_sidebar_handles_missing_secrets(self):
        """[P2] Test configure_sidebar handles missing Streamlit secrets."""
        # GIVEN: Secrets not configured
        with patch('streamlit_app.st') as mock_st:
            # Simulate missing secrets using MagicMock
            mock_secrets = MagicMock()
            mock_secrets.__getitem__ = Mock(side_effect=KeyError("REPLICATE_API_TOKEN"))
            mock_st.secrets = mock_secrets
            
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            # Mock form inputs
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.selectbox.return_value = "DDIM"
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_st.divider = MagicMock()
            mock_st.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            # THEN: Should raise KeyError or handle gracefully
            try:
                configure_sidebar()
            except KeyError:
                # Expected behavior - secrets are required
                pass


class TestMainPageEdgeCasesAdvanced:
    """Advanced edge case tests for main_page() function."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_partial_image_download_failure(self, mock_streamlit_secrets, mock_replicate_run):
        """[P2] Test main_page handles partial failures when downloading images."""
        # GIVEN: Multiple images, one download fails
        submitted = True
        image_urls = [
            "https://example.com/image1.png",
            "https://example.com/image2.png",
            "https://example.com/image3.png"
        ]
        mock_replicate_run.return_value = image_urls
        
        import requests
        with patch('streamlit_app.requests.get') as mock_get:
            # First two succeed, third fails
            mock_response_success = Mock()
            mock_response_success.status_code = 200
            mock_response_success.content = b'fake-image-data'
            
            mock_response_fail = Mock()
            mock_response_fail.status_code = 500
            
            mock_get.side_effect = [
                mock_response_success,
                mock_response_success,
                mock_response_fail
            ]
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st, \
                 patch('streamlit_app.zipfile.ZipFile') as mock_zipfile, \
                 patch('streamlit_app.io.BytesIO') as mock_bytesio:
                
                mock_container = MagicMock()
                mock_st.empty.return_value.container.return_value = mock_container
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.session_state = MockSessionState()
                mock_st.session_state.generated_image = None
                mock_st.session_state.all_images = []
                mock_st.download_button = MagicMock()
                mock_st.error = MagicMock()
                
                mock_zip_io = MagicMock()
                mock_bytesio.return_value = mock_zip_io
                mock_zip = MagicMock()
                mock_zipfile.return_value.__enter__.return_value = mock_zip
                mock_zipfile.return_value.__exit__.return_value = None
                
                main_page(
                    submitted, 1024, 1024, 3, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
                
                # THEN: Should handle partial failure gracefully
                # Error should be displayed for failed image
                assert mock_st.error.called
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_very_large_image_list(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P3] Test main_page handles maximum number of images (4)."""
        # GIVEN: Maximum number of outputs
        submitted = True
        num_outputs = 4
        image_urls = [f"https://example.com/image{i}.png" for i in range(1, num_outputs + 1)]
        mock_replicate_run.return_value = image_urls
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = MockSessionState()
            mock_st.session_state.generated_image = None
            mock_st.session_state.all_images = []
            mock_st.download_button = MagicMock()
            
            main_page(
                submitted, 1024, 1024, num_outputs, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: All images should be processed
            assert len(mock_st.session_state['all_images']) == num_outputs
    
    @pytest.mark.integration
    def test_main_page_gallery_uses_correct_container(self, mock_streamlit_secrets):
        """[P2] Test main_page gallery uses correct placeholder container."""
        # GIVEN: Form not submitted
        submitted = False
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st, \
             patch('streamlit_app.image_select') as mock_image_select:
            
            mock_gallery_placeholder = MagicMock()
            mock_gallery_container = MagicMock()
            mock_gallery_placeholder.container.return_value = mock_gallery_container
            
            mock_images_placeholder = MagicMock()
            mock_images_container = MagicMock()
            mock_images_placeholder.container.return_value = mock_images_container
            
            mock_st.session_state = MockSessionState()
            mock_st.session_state.generated_image = None
            mock_st.session_state.all_images = []
            
            # Patch the module-level placeholders directly
            with patch('streamlit_app.gallery_placeholder', mock_gallery_placeholder), \
                 patch('streamlit_app.generated_images_placeholder', mock_images_placeholder):
                
                main_page(
                    submitted, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
            
            # THEN: Gallery should be called within container context
            mock_gallery_placeholder.container.assert_called_once()
            mock_image_select.assert_called_once()
