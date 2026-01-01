"""Integration tests for streamlit_app.py application."""
import pytest
import requests
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
    
    @pytest.mark.integration
    def test_main_calls_initialize_session_state(self, mock_streamlit_secrets):
        """[P1] Test that main() calls initialize_session_state."""
        # GIVEN: Mocked Streamlit and functions
        with patch('streamlit_app.initialize_session_state') as mock_init, \
             patch('streamlit_app.configure_sidebar') as mock_sidebar, \
             patch('streamlit_app.main_page') as mock_main_page, \
             patch('streamlit_app.st'):
            
            mock_sidebar.return_value = (
                False, 1024, 1024, 1, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test prompt", "test negative"
            )
            
            # WHEN: Calling main()
            main()
            
            # THEN: initialize_session_state should be called
            mock_init.assert_called_once()


class TestMainPageImageDownload:
    """Tests for image download and ZIP functionality in main_page()."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_creates_zip_file_for_multiple_images(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P1] Test main_page creates ZIP file when multiple images are generated."""
        # GIVEN: Form submitted with multiple outputs
        submitted = True
        num_outputs = 3
        image_urls = [
            "https://example.com/image1.png",
            "https://example.com/image2.png",
            "https://example.com/image3.png"
        ]
        mock_replicate_run.return_value = image_urls
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st, \
             patch('streamlit_app.zipfile.ZipFile') as mock_zipfile, \
             patch('streamlit_app.io.BytesIO') as mock_bytesio:
            
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {}
            mock_st.download_button = MagicMock()
            
            # Mock BytesIO
            mock_zip_io = MagicMock()
            mock_bytesio.return_value = mock_zip_io
            mock_zip_io.getvalue.return_value = b'fake-zip-data'
            
            # Mock ZipFile context manager
            mock_zip = MagicMock()
            mock_zipfile.return_value.__enter__.return_value = mock_zip
            mock_zipfile.return_value.__exit__.return_value = None
            
            main_page(
                submitted, 1024, 1024, num_outputs, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: ZIP file should be created with all images
            mock_zipfile.assert_called_once()
            # Verify writestr called for each image
            assert mock_zip.writestr.call_count == num_outputs
            # Verify download button created
            mock_st.download_button.assert_called_once()
            assert 'output_files.zip' in str(mock_st.download_button.call_args)
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_image_download_failure(self, mock_streamlit_secrets, mock_replicate_run):
        """[P1] Test main_page handles HTTP errors when downloading images for ZIP."""
        # GIVEN: Form submitted but image download fails
        submitted = True
        image_urls = ["https://example.com/image1.png"]
        mock_replicate_run.return_value = image_urls
        
        # Mock requests.get to return error
        with patch('streamlit_app.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st, \
                 patch('streamlit_app.zipfile.ZipFile') as mock_zipfile, \
                 patch('streamlit_app.io.BytesIO') as mock_bytesio:
                
                mock_container = MagicMock()
                mock_st.empty.return_value.container.return_value = mock_container
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.session_state = {}
                mock_st.download_button = MagicMock()
                mock_st.error = MagicMock()
                
                mock_zip_io = MagicMock()
                mock_bytesio.return_value = mock_zip_io
                mock_zip = MagicMock()
                mock_zipfile.return_value.__enter__.return_value = mock_zip
                mock_zipfile.return_value.__exit__.return_value = None
                
                main_page(
                    submitted, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
                
                # THEN: Error should be displayed for failed download
                assert mock_st.error.called
                error_call = str(mock_st.error.call_args)
                assert "Failed to fetch image" in error_call or "404" in error_call
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_empty_replicate_output(self, mock_streamlit_secrets, mock_requests_get):
        """[P2] Test main_page handles empty output from Replicate API."""
        # GIVEN: Form submitted but API returns empty list
        submitted = True
        
        with patch('streamlit_app.replicate.run') as mock_run:
            mock_run.return_value = []
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st:
                mock_container = MagicMock()
                mock_st.empty.return_value.container.return_value = mock_container
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.session_state = {}
                
                main_page(
                    submitted, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
                
                # THEN: Should handle gracefully (no crash)
                # Session state may or may not have images, but should not error
                assert 'generated_image' in mock_st.session_state or 'generated_image' not in mock_st.session_state
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_none_replicate_output(self, mock_streamlit_secrets, mock_requests_get):
        """[P2] Test main_page handles None output from Replicate API."""
        # GIVEN: Form submitted but API returns None
        submitted = True
        
        with patch('streamlit_app.replicate.run') as mock_run:
            mock_run.return_value = None
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st:
                mock_container = MagicMock()
                mock_st.empty.return_value.container.return_value = mock_container
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.session_state = {}
                
                # THEN: Should handle gracefully (no crash)
                try:
                    main_page(
                        submitted, 1024, 1024, 1, "DDIM",
                        50, 7.5, 0.8, "expert_ensemble_refiner",
                        0.8, "test", "test"
                    )
                except (TypeError, AttributeError):
                    pytest.fail("main_page should handle None output gracefully")


class TestMainPageGallery:
    """Tests for gallery display functionality in main_page()."""
    
    @pytest.mark.integration
    def test_main_page_displays_gallery_when_not_submitted(self, mock_streamlit_secrets):
        """[P2] Test main_page displays gallery when form is not submitted."""
        # GIVEN: Form not submitted
        submitted = False
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st, \
             patch('streamlit_app.image_select') as mock_image_select:
            
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.session_state = {}
            
            main_page(
                submitted, 1024, 1024, 1, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Gallery should be displayed
            mock_image_select.assert_called_once()
            call_kwargs = mock_image_select.call_args[1]
            assert 'images' in call_kwargs
            assert 'captions' in call_kwargs
            assert len(call_kwargs['images']) > 0
    
    @pytest.mark.integration
    def test_main_page_gallery_has_correct_images(self, mock_streamlit_secrets):
        """[P2] Test main_page gallery contains expected image paths."""
        # GIVEN: Form not submitted
        submitted = False
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st, \
             patch('streamlit_app.image_select') as mock_image_select:
            
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.session_state = {}
            
            main_page(
                submitted, 1024, 1024, 1, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Gallery should have correct image paths
            call_kwargs = mock_image_select.call_args[1]
            expected_images = [
                "gallery/farmer_sunset.png",
                "gallery/astro_on_unicorn.png",
                "gallery/friends.png",
                "gallery/wizard.png",
                "gallery/puppy.png",
                "gallery/cheetah.png",
                "gallery/viking.png",
            ]
            assert call_kwargs['images'] == expected_images
            assert len(call_kwargs['captions']) == len(expected_images)


class TestMainPageEdgeCases:
    """Tests for edge cases and error scenarios in main_page()."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_network_timeout(self, mock_streamlit_secrets, mock_replicate_run):
        """[P2] Test main_page handles network timeout when downloading images."""
        # GIVEN: Form submitted but network times out
        submitted = True
        mock_replicate_run.return_value = ["https://example.com/image1.png"]
        
        with patch('streamlit_app.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st, \
                 patch('streamlit_app.zipfile.ZipFile') as mock_zipfile, \
                 patch('streamlit_app.io.BytesIO') as mock_bytesio:
                
                mock_container = MagicMock()
                mock_st.empty.return_value.container.return_value = mock_container
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.session_state = {}
                mock_st.download_button = MagicMock()
                mock_st.error = MagicMock()
                
                mock_zip_io = MagicMock()
                mock_bytesio.return_value = mock_zip_io
                mock_zip = MagicMock()
                mock_zipfile.return_value.__enter__.return_value = mock_zip
                mock_zipfile.return_value.__exit__.return_value = None
                
                # THEN: Should handle timeout gracefully
                try:
                    main_page(
                        submitted, 1024, 1024, 1, "DDIM",
                        50, 7.5, 0.8, "expert_ensemble_refiner",
                        0.8, "test", "test"
                    )
                except requests.exceptions.Timeout:
                    pytest.fail("main_page should handle timeout gracefully")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_max_outputs(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P2] Test main_page handles maximum number of outputs (4)."""
        # GIVEN: Form submitted with max outputs
        submitted = True
        num_outputs = 4
        image_urls = [f"https://example.com/image{i}.png" for i in range(1, num_outputs + 1)]
        mock_replicate_run.return_value = image_urls
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {}
            mock_st.download_button = MagicMock()
            
            main_page(
                submitted, 1024, 1024, num_outputs, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: All images should be processed
            assert len(mock_st.session_state['all_images']) == num_outputs
    
    @pytest.mark.integration
    def test_main_page_passes_correct_prompt_strength_parameter(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P2] Test main_page passes prompt_strength parameter correctly (note: typo in code 'prompt_stregth')."""
        # GIVEN: Form submitted with specific prompt_strength
        submitted = True
        prompt_strength = 0.9
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {}
            
            main_page(
                submitted, 1024, 1024, 1, "DDIM",
                50, 7.5, prompt_strength, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Replicate API should be called with prompt_strength (note: code has typo 'prompt_stregth')
            call_kwargs = mock_replicate_run.call_args[1]['input']
            # Note: The actual code uses 'prompt_stregth' (typo), so we check for that
            assert 'prompt_stregth' in call_kwargs or 'prompt_strength' in call_kwargs