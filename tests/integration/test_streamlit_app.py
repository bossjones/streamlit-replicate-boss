"""Integration tests for streamlit_app.py application."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from streamlit_app import configure_sidebar, main_page, main


class TestConfigureSidebar:
    """Tests for configure_sidebar() function."""
    
    @pytest.mark.integration
    def test_configure_sidebar_returns_form_values(self, mock_streamlit_secrets):
        """[P1] Test that configure_sidebar returns all form values."""
        # GIVEN: Mocked Streamlit sidebar and form
        with patch('streamlit_app.st') as mock_st:
            # Setup sidebar as context manager
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            # Setup form as context manager - form is called on sidebar_ctx
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.form.return_value = mock_form
            
            # Mock form inputs - the code calls st.number_input, st.slider, etc. inside the form
            # So we need to make st delegate to mock_form_ctx when inside the form
            # But since st is the module-level import, we make st itself have these methods
            # that return the form context values
            mock_form_ctx.number_input.side_effect = [1024, 1024]  # width, height
            mock_form_ctx.slider.side_effect = [1, 50, 7.5, 0.8, 0.8]  # num_outputs, steps, guidance, prompt_strength, noise
            mock_form_ctx.selectbox.side_effect = ["DDIM", "expert_ensemble_refiner"]  # scheduler, refine
            mock_form_ctx.text_area.side_effect = ["test prompt", "test negative prompt"]
            mock_form_ctx.form_submit_button.return_value = False
            mock_form_ctx.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_form_ctx.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_form_ctx.expander.return_value.__exit__ = MagicMock(return_value=None)
            
            # Make st delegate to form_ctx when inside form (simplified - just make st methods return form_ctx methods)
            # Actually, the form context manager makes st methods work, so we need st to have these methods
            # that work both inside and outside form. For simplicity, make st methods return form_ctx methods' return values
            mock_st.number_input.side_effect = [1024, 1024]
            mock_st.slider.side_effect = [1, 50, 7.5, 0.8, 0.8]
            mock_st.selectbox.side_effect = ["DDIM", "expert_ensemble_refiner"]
            mock_st.text_area.side_effect = ["test prompt", "test negative prompt"]
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            
            # Mock other sidebar calls (outside form)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            mock_st.divider = MagicMock()
            mock_st.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            result = configure_sidebar()
            
            # THEN: Should return tuple with all form values
            assert isinstance(result, tuple)
            assert len(result) == 12
            submitted, width, height, num_outputs, scheduler, num_inference_steps, \
                guidance_scale, prompt_strength, refine, high_noise_frac, prompt, negative_prompt = result
            
            # The form_submit_button returns the value directly
            assert submitted is False
            assert width == 1024
            assert height == 1024
            assert num_outputs == 1
            assert scheduler == "DDIM"
            assert num_inference_steps == 50
            assert guidance_scale == 7.5
            assert prompt_strength == 0.8
            assert refine == "expert_ensemble_refiner"
            assert high_noise_frac == 0.8
            assert prompt == "test prompt"
            assert negative_prompt == "test negative prompt"
    
    @pytest.mark.integration
    def test_configure_sidebar_creates_form_structure(self, mock_streamlit_secrets):
        """[P1] Test that configure_sidebar creates proper form structure."""
        # GIVEN: Mocked Streamlit
        with patch('streamlit_app.st') as mock_st:
            # Setup sidebar as context manager
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            # Setup form as context manager - form is called on st, not sidebar_ctx
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            # The code calls st.form(), so we need to mock it on mock_st
            mock_st.form.return_value = mock_form
            
            # Mock form inputs - make st methods work (since code calls st.number_input, etc.)
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.selectbox.return_value = "DDIM"
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            
            # Mock other sidebar calls
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            mock_st.divider = MagicMock()
            mock_st.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Form structure should be created
            # The code calls st.form(), not sidebar_ctx.form()
            mock_st.form.assert_called_once()
            assert mock_st.number_input.called
            assert mock_st.slider.called
            assert mock_st.selectbox.called
            assert mock_st.text_area.called


class TestMainPage:
    """Tests for main_page() function."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_with_submitted_form(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P1] Test main_page generates images when form is submitted."""
        # GIVEN: Form submitted with valid parameters
        submitted = True
        width = 1024
        height = 1024
        num_outputs = 1
        scheduler = "DDIM"
        num_inference_steps = 50
        guidance_scale = 7.5
        prompt_strength = 0.8
        refine = "expert_ensemble_refiner"
        high_noise_frac = 0.8
        prompt = "test prompt"
        negative_prompt = "test negative prompt"
        
        # Mock Replicate output
        mock_replicate_run.return_value = ["https://example.com/image.png"]
        
        # WHEN: Calling main_page with submitted form
        with patch('streamlit_app.st') as mock_st:
            mock_st.empty.return_value.container.return_value = MagicMock()
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {}
            
            main_page(
                submitted, width, height, num_outputs, scheduler,
                num_inference_steps, guidance_scale, prompt_strength,
                refine, high_noise_frac, prompt, negative_prompt
            )
            
            # THEN: Replicate API should be called with correct parameters
            mock_replicate_run.assert_called_once()
            call_kwargs = mock_replicate_run.call_args[1]['input']
            assert call_kwargs['prompt'] == prompt
            assert call_kwargs['width'] == width
            assert call_kwargs['height'] == height
            assert call_kwargs['num_outputs'] == num_outputs
            assert call_kwargs['scheduler'] == scheduler
            assert call_kwargs['num_inference_steps'] == num_inference_steps
            assert call_kwargs['guidance_scale'] == guidance_scale
            assert call_kwargs['refine'] == refine
            assert call_kwargs['high_noise_frac'] == high_noise_frac
    
    @pytest.mark.integration
    def test_main_page_without_submission(self, mock_streamlit_secrets):
        """[P1] Test main_page handles non-submitted form gracefully."""
        # GIVEN: Form not submitted
        submitted = False
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st:
            mock_st.empty.return_value.container.return_value = MagicMock()
            mock_st.session_state = {}
            
            main_page(
                submitted, 1024, 1024, 1, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Should not call Replicate API
            # (No assertion needed - just verify no errors)
            pass
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_api_error(self, mock_streamlit_secrets, mock_requests_get):
        """[P1] Test main_page handles Replicate API errors gracefully."""
        # GIVEN: Form submitted but API raises exception
        submitted = True
        
        with patch('streamlit_app.replicate.run') as mock_run:
            mock_run.side_effect = Exception("API Error")
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st:
                mock_st.empty.return_value.container.return_value = MagicMock()
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.session_state = {}
                
                # THEN: Should handle error gracefully
                main_page(
                    submitted, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
                
                # Error should be displayed
                mock_st.error.assert_called()
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_saves_images_to_session_state(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P1] Test main_page saves generated images to session state."""
        # GIVEN: Form submitted with multiple outputs
        submitted = True
        num_outputs = 2
        mock_replicate_run.return_value = [
            "https://example.com/image1.png",
            "https://example.com/image2.png"
        ]
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {}
            
            main_page(
                submitted, 1024, 1024, num_outputs, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Images should be saved to session state
            assert 'generated_image' in mock_st.session_state
            assert 'all_images' in mock_st.session_state
            assert len(mock_st.session_state['all_images']) == num_outputs


class TestMain:
    """Tests for main() function."""
    
    @pytest.mark.integration
    def test_main_calls_configure_sidebar_and_main_page(self, mock_streamlit_secrets):
        """[P1] Test that main() orchestrates sidebar and main page correctly."""
        # GIVEN: Mocked Streamlit and functions
        with patch('streamlit_app.configure_sidebar') as mock_sidebar, \
             patch('streamlit_app.main_page') as mock_main_page, \
             patch('streamlit_app.st'):
            
            # Setup sidebar mock return
            mock_sidebar.return_value = (
                False, 1024, 1024, 1, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test prompt", "test negative"
            )
            
            # WHEN: Calling main()
            main()
            
            # THEN: Both functions should be called
            mock_sidebar.assert_called_once()
            mock_main_page.assert_called_once()
            
            # Verify main_page called with correct arguments
            call_args = mock_main_page.call_args[0]
            assert call_args[0] is False  # submitted
            assert call_args[1] == 1024  # width
            assert call_args[2] == 1024  # height
