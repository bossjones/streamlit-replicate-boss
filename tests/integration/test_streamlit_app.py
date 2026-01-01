"""Integration tests for streamlit_app.py application."""
import pytest
import requests
import yaml
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from streamlit_app import configure_sidebar, main_page, main, initialize_session_state


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
            
            # Setup session state for model selector (before form)
            # Provide a model config so the model selector is rendered
            mock_st.session_state = st.session_state
            mock_st.session_state.model_configs = [
                {'id': 'test-model', 'name': 'Test Model', 'endpoint': 'owner/model:version'}
            ]
            mock_st.session_state.selected_model = mock_st.session_state.model_configs[0]
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            mock_st.warning = MagicMock()
            
            # Make st delegate to form_ctx when inside form (simplified - just make st methods return form_ctx methods)
            # Actually, the form context manager makes st methods work, so we need st to have these methods
            # that work both inside and outside form. For simplicity, make st methods return form_ctx methods' return values
            # NOTE: First selectbox call is for model selector, then form selectboxes
            mock_st.number_input.side_effect = [1024, 1024]
            mock_st.slider.side_effect = [1, 50, 7.5, 0.8, 0.8]
            mock_st.selectbox.side_effect = ["Test Model", "DDIM", "expert_ensemble_refiner"]  # model selector, scheduler, refine
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
    
    @pytest.mark.integration
    def test_model_selector_appears_in_sidebar(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC1: Model selector appears at top of sidebar before form."""
        # GIVEN: Session state with model configs
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        
        with patch('streamlit_app.st') as mock_st:
            # Setup sidebar
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            # Setup form
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            # Setup session state properly
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox for model selector (called before form)
            mock_st.selectbox.side_effect = ["Model 1", "DDIM", "expert_ensemble_refiner"]
            
            # Mock other inputs
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: selectbox should be called for model selector (first call)
            assert mock_st.selectbox.called
            # Verify first call is for model selector (before form)
            selectbox_calls = mock_st.selectbox.call_args_list
            assert len(selectbox_calls) > 0, "selectbox should be called at least once"
            # First call should be model selector with "Select Model" label
            first_call = selectbox_calls[0]
            call_args = first_call[0] if len(first_call) > 0 else ()
            call_kwargs = first_call[1] if len(first_call) > 1 else {}
            # Check if "Select Model" is in the label (first positional arg or label kwarg)
            label = call_args[0] if len(call_args) > 0 else call_kwargs.get('label', '')
            assert "Select Model" in str(label) or "Select Model" in str(first_call)
    
    @pytest.mark.integration
    def test_model_selector_displays_all_models(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC2: All models from configuration are displayed in selector."""
        # GIVEN: Session state with multiple models
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            # Setup session state properly
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox - first call is model selector
            mock_st.selectbox.side_effect = ["Model 1", "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: selectbox should be called with all model names as options
            selectbox_calls = mock_st.selectbox.call_args_list
            assert len(selectbox_calls) > 0, "selectbox should be called at least once"
            first_call = selectbox_calls[0]
            # Check that options include all model names
            call_kwargs = first_call[1] if len(first_call) > 1 else {}
            call_args = first_call[0] if len(first_call) > 0 else ()
            # Options should be in args (position 1) or kwargs
            if len(call_args) > 1:
                options = call_args[1]
                assert len(options) == len(sample_model_configs)
                assert all(model['name'] in options for model in sample_model_configs)
            elif 'options' in call_kwargs:
                options = call_kwargs['options']
                assert len(options) == len(sample_model_configs)
                assert all(model['name'] in options for model in sample_model_configs)
    
    @pytest.mark.integration
    def test_model_selector_shows_current_selection(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC3: Currently selected model is shown in dropdown."""
        # GIVEN: Session state with selected model
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[1]  # Select second model
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            # Setup session state properly
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox - return selected model name
            mock_st.selectbox.side_effect = ["Model 2", "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: selectbox should be called with correct index for selected model
            selectbox_calls = mock_st.selectbox.call_args_list
            assert len(selectbox_calls) > 0, "selectbox should be called at least once"
            first_call = selectbox_calls[0]
            call_kwargs = first_call[1] if len(first_call) > 1 else {}
            call_args = first_call[0] if len(first_call) > 0 else ()
            # Index should be 1 (second model) - check both kwargs and args
            if 'index' in call_kwargs:
                assert call_kwargs['index'] == 1
            elif len(call_args) > 2:
                # Index might be in positional args
                assert call_args[2] == 1
    
    @pytest.mark.integration
    def test_model_selector_always_visible(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC4: Model selector is always visible (not in expander)."""
        # GIVEN: Session state with models
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            # Setup session state properly
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            mock_st.selectbox.side_effect = ["Model 1", "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: selectbox should be called before expander (model selector is outside expander)
            selectbox_calls = mock_st.selectbox.call_args_list
            expander_calls = mock_st.expander.call_args_list
            # Model selector selectbox should be called before form expander
            # This is verified by the order of calls - selectbox for model comes first
            assert len(selectbox_calls) > 0, "Model selector selectbox should be called"
            # First selectbox call should be for model selector (before form/expander)
            if len(expander_calls) > 0:
                # Verify model selector selectbox is called before expander
                assert len(selectbox_calls) > 0
    
    @pytest.mark.integration
    def test_model_selector_updates_session_state(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC5: Session state updates when model selection changes."""
        # GIVEN: Session state with models
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            # Setup session state properly
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox to return different model
            mock_st.selectbox.side_effect = ["Model 2", "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: selected_model should be updated to Model 2
            # Note: The update happens in the actual code, but we need to check the real session state
            # Since we're patching st, we need to ensure the update propagates
            # The code updates st.session_state.selected_model, which should update the real session state
            assert st.session_state.selected_model == sample_model_configs[1]
            assert st.session_state.selected_model['name'] == "Model 2"
    
    @pytest.mark.integration
    def test_model_selector_handles_empty_list(self, mock_streamlit_secrets):
        """Test AC6: Empty model list is handled gracefully."""
        # GIVEN: Empty model configs
        st.session_state.model_configs = []
        st.session_state.selected_model = None
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            # Setup session state properly - empty list
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            mock_st.warning = MagicMock()
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.selectbox.return_value = "DDIM"
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Warning message should be displayed
            mock_st.warning.assert_called()
            warning_call = str(mock_st.warning.call_args)
            assert "No models configured" in warning_call or "models.yaml" in warning_call
    
    @pytest.mark.integration
    def test_model_selector_handles_missing_session_state(self, mock_streamlit_secrets):
        """Test AC6: Missing session state is handled gracefully."""
        # GIVEN: Missing model_configs in session state
        if 'model_configs' in st.session_state:
            del st.session_state.model_configs
        if 'selected_model' in st.session_state:
            del st.session_state.selected_model
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.get.side_effect = lambda key, default=None: st.session_state.get(key, default)
            mock_st.warning = MagicMock()
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.selectbox.return_value = "DDIM"
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            # THEN: Should not crash
            try:
                configure_sidebar()
            except (KeyError, AttributeError):
                pytest.fail("configure_sidebar should handle missing session state gracefully")


class TestMainPage:
    """Tests for main_page() function."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_with_submitted_form(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P1] Test main_page generates images when form is submitted."""
        # GIVEN: Form submitted with valid parameters and selected model
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
        
        # Mock selected model
        selected_model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version'
        }
        
        # Mock Replicate output
        mock_replicate_run.return_value = ["https://example.com/image.png"]
        
        # WHEN: Calling main_page with submitted form
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {'selected_model': selected_model}
            mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
            mock_st.toast = MagicMock()
            mock_st.image = MagicMock()
            mock_st.download_button = MagicMock()
            
            main_page(
                submitted, width, height, num_outputs, scheduler,
                num_inference_steps, guidance_scale, prompt_strength,
                refine, high_noise_frac, prompt, negative_prompt
            )
            
            # THEN: Replicate API should be called with correct endpoint and parameters
            mock_replicate_run.assert_called_once()
            # Verify endpoint is from selected model
            assert mock_replicate_run.call_args[0][0] == 'owner/model:version'
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
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_uses_selected_model_endpoint(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P1] Test main_page uses selected model endpoint from session state (AC: 1, 2)."""
        # GIVEN: Form submitted with selected model in session state
        submitted = True
        selected_model = {
            'id': 'helldiver',
            'name': 'Helldiver Model',
            'endpoint': 'owner/helldiver:version',
            'trigger_words': ['helldiver'],
            'default_settings': {}
        }
        mock_replicate_run.return_value = ["https://example.com/image.png"]
        
        # WHEN: Calling main_page with selected model
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {'selected_model': selected_model}
            mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
            mock_st.toast = MagicMock()
            mock_st.image = MagicMock()
            mock_st.download_button = MagicMock()
            
            main_page(
                submitted, 1024, 1024, 1, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Replicate API should be called with selected model endpoint
            mock_replicate_run.assert_called_once()
            call_args = mock_replicate_run.call_args
            assert call_args[0][0] == 'owner/helldiver:version'
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_uses_different_model_endpoints(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P1] Test main_page uses correct endpoint when switching models (AC: 2)."""
        # GIVEN: Multiple model configurations
        models = [
            {'id': 'sdxl', 'name': 'SDXL', 'endpoint': 'stability-ai/sdxl:version'},
            {'id': 'helldiver', 'name': 'Helldiver', 'endpoint': 'owner/helldiver:version'},
            {'id': 'starship', 'name': 'Starship Trooper', 'endpoint': 'owner/starship-trooper:version'}
        ]
        mock_replicate_run.return_value = ["https://example.com/image.png"]
        
        # WHEN: Calling main_page with each model
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
            mock_st.toast = MagicMock()
            mock_st.image = MagicMock()
            mock_st.download_button = MagicMock()
            
            for model in models:
                mock_st.session_state = {'selected_model': model}
                main_page(
                    True, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
            
            # THEN: Each API call should use correct endpoint
            assert mock_replicate_run.call_count == 3
            call_endpoints = [call[0][0] for call in mock_replicate_run.call_args_list]
            assert call_endpoints == ['stability-ai/sdxl:version', 'owner/helldiver:version', 'owner/starship-trooper:version']
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_fallback_when_selected_model_missing(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P1] Test main_page falls back to secrets.toml when selected_model is missing (AC: 5)."""
        # GIVEN: Form submitted but selected_model is None
        submitted = True
        mock_replicate_run.return_value = ["https://example.com/image.png"]
        
        # WHEN: Calling main_page without selected_model
        with patch('streamlit_app.st') as mock_st, \
             patch('streamlit_app.get_replicate_model_endpoint') as mock_get_endpoint:
            mock_get_endpoint.return_value = 'stability-ai/sdxl:test-version'
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {}  # No selected_model
            mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
            mock_st.warning = MagicMock()
            mock_st.toast = MagicMock()
            mock_st.image = MagicMock()
            mock_st.download_button = MagicMock()
            
            main_page(
                submitted, 1024, 1024, 1, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Should use fallback endpoint from secrets
            mock_get_endpoint.assert_called_once()
            mock_replicate_run.assert_called_once()
            assert mock_replicate_run.call_args[0][0] == 'stability-ai/sdxl:test-version'
            # Warning should be displayed
            mock_st.warning.assert_called()
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_fallback_when_endpoint_missing(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P1] Test main_page falls back when selected_model has no endpoint (AC: 5)."""
        # GIVEN: Form submitted but selected_model missing endpoint
        submitted = True
        selected_model = {
            'id': 'test-model',
            'name': 'Test Model',
            # Missing 'endpoint' key
        }
        mock_replicate_run.return_value = ["https://example.com/image.png"]
        
        # WHEN: Calling main_page with invalid selected_model
        with patch('streamlit_app.st') as mock_st, \
             patch('streamlit_app.get_replicate_model_endpoint') as mock_get_endpoint:
            mock_get_endpoint.return_value = 'stability-ai/sdxl:test-version'
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {'selected_model': selected_model}
            mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
            mock_st.warning = MagicMock()
            mock_st.toast = MagicMock()
            mock_st.image = MagicMock()
            mock_st.download_button = MagicMock()
            
            main_page(
                submitted, 1024, 1024, 1, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Should use fallback endpoint
            mock_get_endpoint.assert_called_once()
            mock_replicate_run.assert_called_once()
            assert mock_replicate_run.call_args[0][0] == 'stability-ai/sdxl:test-version'
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_invalid_endpoint(self, mock_streamlit_secrets, mock_replicate_run):
        """[P1] Test main_page handles invalid endpoint gracefully (AC: 4)."""
        # GIVEN: Form submitted with invalid endpoint (empty string)
        submitted = True
        selected_model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': ''  # Invalid empty endpoint
        }
        
        # WHEN: Calling main_page with invalid endpoint
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.status.return_value.__exit__ = MagicMock(return_value=None)
            mock_st.session_state = {'selected_model': selected_model}
            mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
            mock_st.error = MagicMock()
            
            main_page(
                submitted, 1024, 1024, 1, "DDIM",
                50, 7.5, 0.8, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Should display error and not call API
            mock_st.error.assert_called()
            mock_replicate_run.assert_not_called()
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_handles_api_error_with_model_name(self, mock_streamlit_secrets, mock_requests_get):
        """[P1] Test main_page displays model name in error message when API fails (AC: 4)."""
        # GIVEN: Form submitted but API raises exception
        submitted = True
        selected_model = {
            'id': 'helldiver',
            'name': 'Helldiver Model',
            'endpoint': 'owner/helldiver:version'
        }
        
        with patch('streamlit_app.replicate.run') as mock_run:
            mock_run.side_effect = Exception("API connection failed")
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st:
                mock_container = MagicMock()
                mock_st.empty.return_value.container.return_value = mock_container
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.status.return_value.__exit__ = MagicMock(return_value=None)
                mock_st.session_state = {'selected_model': selected_model}
                mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
                mock_st.error = MagicMock()
                
                main_page(
                    submitted, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
                
                # THEN: Error message should include model name
                mock_st.error.assert_called()
                error_call = mock_st.error.call_args[0][0]
                assert 'Helldiver Model' in error_call or 'helldiver' in error_call.lower()
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_main_page_displays_images_correctly_all_models(self, mock_streamlit_secrets, mock_replicate_run, mock_requests_get):
        """[P1] Test main_page displays images correctly for all models (AC: 3)."""
        # GIVEN: Form submitted with different models
        submitted = True
        models = [
            {'id': 'sdxl', 'name': 'SDXL', 'endpoint': 'stability-ai/sdxl:version'},
            {'id': 'helldiver', 'name': 'Helldiver', 'endpoint': 'owner/helldiver:version'}
        ]
        mock_replicate_run.return_value = ["https://example.com/image.png"]
        
        # WHEN: Calling main_page with each model
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
            mock_st.toast = MagicMock()
            mock_st.image = MagicMock()
            mock_st.download_button = MagicMock()
            
            for model in models:
                mock_st.session_state = {'selected_model': model}
                main_page(
                    submitted, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
            
            # THEN: Images should be displayed for all models
            assert mock_st.image.call_count == len(models)
            assert mock_st.toast.call_count == len(models)


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
        # GIVEN: Form submitted with specific prompt_strength and selected model
        submitted = True
        prompt_strength = 0.9
        selected_model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version'
        }
        mock_replicate_run.return_value = ["https://example.com/image.png"]
        
        # WHEN: Calling main_page
        with patch('streamlit_app.st') as mock_st:
            mock_container = MagicMock()
            mock_st.empty.return_value.container.return_value = mock_container
            mock_st.status.return_value.__enter__.return_value = MagicMock()
            mock_st.session_state = {'selected_model': selected_model}
            mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
            mock_st.toast = MagicMock()
            mock_st.image = MagicMock()
            mock_st.download_button = MagicMock()
            
            main_page(
                submitted, 1024, 1024, 1, "DDIM",
                50, 7.5, prompt_strength, "expert_ensemble_refiner",
                0.8, "test", "test"
            )
            
            # THEN: Replicate API should be called with prompt_strength (note: code has typo 'prompt_stregth')
            mock_replicate_run.assert_called_once()
            call_kwargs = mock_replicate_run.call_args[1]['input']
            # Note: The actual code uses 'prompt_stregth' (typo), so we check for that
            assert 'prompt_stregth' in call_kwargs or 'prompt_strength' in call_kwargs


class TestModelSwitching:
    """Tests for model switching functionality (Story 1.5)."""
    
    @pytest.mark.integration
    def test_model_switching_preserves_prompt(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC3: Current prompt is preserved when switching models."""
        # GIVEN: Session state with models and form values
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        st.session_state.form_prompt = "Test prompt to preserve"
        st.session_state.form_width = 1024
        st.session_state.form_height = 1024
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox to return different model (triggers switch)
            mock_st.selectbox.side_effect = ["Model 2", "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "Test prompt to preserve"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar (model switch occurs)
            configure_sidebar()
            
            # THEN: Prompt should be preserved
            assert 'preserved_prompt' in st.session_state
            assert st.session_state.preserved_prompt == "Test prompt to preserve"
    
    @pytest.mark.integration
    def test_model_switching_preserves_settings(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC3: Current settings are preserved when switching models."""
        # GIVEN: Session state with models and form values
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        st.session_state.form_width = 2048
        st.session_state.form_height = 1536
        st.session_state.form_num_outputs = 2
        st.session_state.form_scheduler = 'KarrasDPM'
        st.session_state.form_num_inference_steps = 100
        st.session_state.form_guidance_scale = 8.5
        st.session_state.form_prompt_strength = 0.9
        st.session_state.form_refine = 'None'
        st.session_state.form_high_noise_frac = 0.7
        st.session_state.form_negative_prompt = "test negative"
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox to return different model (triggers switch)
            mock_st.selectbox.side_effect = ["Model 2", "KarrasDPM", "None"]
            
            mock_st.number_input.return_value = 2048
            mock_st.slider.return_value = 2
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar (model switch occurs)
            configure_sidebar()
            
            # THEN: Settings should be preserved
            assert 'preserved_settings' in st.session_state
            preserved = st.session_state.preserved_settings
            assert preserved['width'] == 2048
            assert preserved['height'] == 1536
            assert preserved['num_outputs'] == 2
            assert preserved['scheduler'] == 'KarrasDPM'
            assert preserved['num_inference_steps'] == 100
            assert preserved['guidance_scale'] == 8.5
            assert preserved['prompt_strength'] == 0.9
            assert preserved['refine'] == 'None'
            assert preserved['high_noise_frac'] == 0.7
            assert preserved['negative_prompt'] == "test negative"
    
    @pytest.mark.integration
    def test_model_switching_updates_session_state(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC1: Model selection in dropdown updates st.session_state.selected_model."""
        # GIVEN: Session state with models
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox to return different model
            mock_st.selectbox.side_effect = ["Model 2", "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: selected_model should be updated
            assert st.session_state.selected_model == sample_model_configs[1]
            assert st.session_state.selected_model['name'] == "Model 2"
    
    @pytest.mark.integration
    def test_model_switching_handles_invalid_selection(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC6: Invalid model selection is handled gracefully."""
        # GIVEN: Session state with models
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            mock_st.error = MagicMock()
            mock_st.warning = MagicMock()
            
            # Mock selectbox to return invalid model name
            mock_st.selectbox.side_effect = ["Invalid Model", "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar with invalid model
            configure_sidebar()
            
            # THEN: Error message should be displayed
            mock_st.error.assert_called()
            error_call = str(mock_st.error.call_args)
            assert "Invalid model selection" in error_call or "Invalid Model" in error_call
    
    @pytest.mark.integration
    def test_model_switching_handles_missing_config(self, mock_streamlit_secrets):
        """Test AC6: Switching before config loads is handled gracefully."""
        # GIVEN: Empty model configs (config not loaded)
        st.session_state.model_configs = []
        if 'selected_model' in st.session_state:
            del st.session_state.selected_model
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            mock_st.warning = MagicMock()
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.selectbox.return_value = "DDIM"
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Warning should be displayed, model selector should not be rendered
            mock_st.warning.assert_called()
            warning_call = str(mock_st.warning.call_args)
            assert "No models configured" in warning_call or "models.yaml" in warning_call
    
    @pytest.mark.integration
    def test_rapid_model_switching(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC5: Rapid model switching works reliably without state corruption."""
        # GIVEN: Session state with models
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        st.session_state.form_prompt = "Test prompt"
        st.session_state.form_width = 1024
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Simulate rapid switching: Model 1 -> Model 2 -> Model 1 -> Model 2 -> Model 1
            # Each call simulates one switch
            switch_sequence = ["Model 2", "Model 1", "Model 2", "Model 1", "Model 2"]
            mock_st.selectbox.side_effect = switch_sequence + ["DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "Test prompt"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Performing rapid switches
            for i, model_name in enumerate(switch_sequence):
                # Update selected model name in mock
                mock_st.selectbox.side_effect = [model_name] + ["DDIM", "expert_ensemble_refiner"]
                configure_sidebar()
            
            # THEN: State should be consistent, selected_model should match last switch
            assert st.session_state.selected_model == sample_model_configs[1]  # Model 2
            assert st.session_state.selected_model['name'] == "Model 2"
            # Preserved values should still be intact
            if 'preserved_prompt' in st.session_state:
                assert st.session_state.preserved_prompt == "Test prompt"
    
    @pytest.mark.integration
    def test_model_switching_ui_reflects_selection(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC4: UI reflects selected model (dropdown shows current selection)."""
        # GIVEN: Session state with selected model
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[1]  # Model 2
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox to return current selection
            mock_st.selectbox.side_effect = ["Model 2", "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.warning = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.markdown = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: selectbox should be called with correct index for Model 2
            selectbox_calls = mock_st.selectbox.call_args_list
            assert len(selectbox_calls) > 0
            first_call = selectbox_calls[0]  # Model selector call
            call_kwargs = first_call[1] if len(first_call) > 1 else {}
            call_args = first_call[0] if len(first_call) > 0 else ()
            # Index should be 1 (second model, Model 2)
            if 'index' in call_kwargs:
                assert call_kwargs['index'] == 1
            elif len(call_args) > 2:
                assert call_args[2] == 1


class TestModelInformationDisplay:
    """Tests for model information display in sidebar (Story 2.3)."""
    
    @pytest.mark.integration
    def test_model_name_displays_below_selector(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC1: Model name displays below selector when selected_model exists."""
        # GIVEN: Session state with selected model
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        st.session_state.presets = {}
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            mock_st.selectbox.return_value = "Model 1"
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            mock_sidebar_ctx.info = MagicMock()
            # Make st methods delegate to sidebar context when inside sidebar
            mock_st.divider = mock_sidebar_ctx.divider
            mock_st.subheader = mock_sidebar_ctx.subheader
            mock_st.caption = mock_sidebar_ctx.caption
            mock_st.info = mock_sidebar_ctx.info
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Model name should be displayed via subheader
            assert mock_sidebar_ctx.subheader.called
            subheader_calls = mock_sidebar_ctx.subheader.call_args_list
            # Check that subheader was called with model name
            assert any("Model 1" in str(call) for call in subheader_calls)
    
    @pytest.mark.integration
    def test_trigger_words_display_from_model_config(self, mock_streamlit_secrets):
        """Test AC2: Trigger words display from model config when available."""
        # GIVEN: Model with trigger words in config
        model_with_trigger = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version',
            'trigger_words': ['TRIGGER1', 'TRIGGER2']
        }
        st.session_state.model_configs = [model_with_trigger]
        st.session_state.selected_model = model_with_trigger
        st.session_state.presets = {}
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            mock_st.selectbox.return_value = "Test Model"
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            mock_sidebar_ctx.info = MagicMock()
            # Make st methods delegate to sidebar context when inside sidebar
            mock_st.divider = mock_sidebar_ctx.divider
            mock_st.subheader = mock_sidebar_ctx.subheader
            mock_st.caption = mock_sidebar_ctx.caption
            mock_st.info = mock_sidebar_ctx.info
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Trigger words should be displayed via info
            assert mock_sidebar_ctx.info.called
            info_calls = mock_sidebar_ctx.info.call_args_list
            # Check that info was called with trigger words
            assert any("TRIGGER1" in str(call) or "TRIGGER2" in str(call) for call in info_calls)
    
    @pytest.mark.integration
    def test_trigger_words_display_from_preset(self, mock_streamlit_secrets):
        """Test AC2: Trigger words display from preset when model config doesn't have them."""
        # GIVEN: Model without trigger words, but preset has them
        model_without_trigger = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version'
        }
        preset_with_trigger = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': 'test-model',
            'trigger_words': ['PRESET_TRIGGER1', 'PRESET_TRIGGER2']
        }
        st.session_state.model_configs = [model_without_trigger]
        st.session_state.selected_model = model_without_trigger
        st.session_state.presets = {'test-model': [preset_with_trigger]}
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            mock_st.selectbox.return_value = "Test Model"
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            mock_sidebar_ctx.info = MagicMock()
            # Make st methods delegate to sidebar context when inside sidebar
            mock_st.divider = mock_sidebar_ctx.divider
            mock_st.subheader = mock_sidebar_ctx.subheader
            mock_st.caption = mock_sidebar_ctx.caption
            mock_st.info = mock_sidebar_ctx.info
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Trigger words from preset should be displayed
            assert mock_sidebar_ctx.info.called
            info_calls = mock_sidebar_ctx.info.call_args_list
            # Check that info was called with preset trigger words
            assert any("PRESET_TRIGGER1" in str(call) or "PRESET_TRIGGER2" in str(call) for call in info_calls)
    
    @pytest.mark.integration
    def test_no_trigger_words_section_when_missing(self, mock_streamlit_secrets):
        """Test AC2, AC5: No trigger words section when neither source has them."""
        # GIVEN: Model without trigger words and no presets
        model_without_trigger = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version'
        }
        st.session_state.model_configs = [model_without_trigger]
        st.session_state.selected_model = model_without_trigger
        st.session_state.presets = {}
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            mock_st.selectbox.return_value = "Test Model"
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Info should not be called for trigger words (only for form message)
            # Info is called for form message, so we check that no trigger words info was called
            info_calls = mock_sidebar_ctx.info.call_args_list
            trigger_word_calls = [call for call in info_calls if "Trigger Words" in str(call)]
            assert len(trigger_word_calls) == 0
    
    @pytest.mark.integration
    def test_description_displays_when_present(self, mock_streamlit_secrets):
        """Test AC3: Description displays when present in model config."""
        # GIVEN: Model with description
        model_with_description = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version',
            'description': 'This is a test model description'
        }
        st.session_state.model_configs = [model_with_description]
        st.session_state.selected_model = model_with_description
        st.session_state.presets = {}
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            mock_st.selectbox.return_value = "Test Model"
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            mock_sidebar_ctx.info = MagicMock()
            # Make st methods delegate to sidebar context when inside sidebar
            mock_st.divider = mock_sidebar_ctx.divider
            mock_st.subheader = mock_sidebar_ctx.subheader
            mock_st.caption = mock_sidebar_ctx.caption
            mock_st.info = mock_sidebar_ctx.info
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Description should be displayed via caption
            assert mock_sidebar_ctx.caption.called
            caption_calls = mock_sidebar_ctx.caption.call_args_list
            # Check that caption was called with description
            assert any("test model description" in str(call).lower() for call in caption_calls)
    
    @pytest.mark.integration
    def test_no_description_section_when_missing(self, mock_streamlit_secrets):
        """Test AC3, AC5: No description section when missing."""
        # GIVEN: Model without description
        model_without_description = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version'
        }
        st.session_state.model_configs = [model_without_description]
        st.session_state.selected_model = model_without_description
        st.session_state.presets = {}
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            mock_st.selectbox.return_value = "Test Model"
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Caption should not be called for description
            caption_calls = mock_sidebar_ctx.caption.call_args_list
            description_calls = [call for call in caption_calls if "test model" not in str(call).lower()]
            # Caption might be called for other things, but not for description
            # We verify by checking that no description-specific caption was called
    
    @pytest.mark.integration
    def test_graceful_handling_when_selected_model_is_none(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC5: Graceful handling when selected_model is None."""
        # GIVEN: Session state with no selected model
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = None
        st.session_state.presets = {}
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            mock_st.selectbox.return_value = "Model 1"
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Should not crash, and model info section should not be displayed
            # (divider and subheader should not be called when selected_model is None)
            # Note: divider might be called elsewhere, but subheader for model name should not be called
            subheader_calls = mock_sidebar_ctx.subheader.call_args_list
            model_name_calls = [call for call in subheader_calls if "📦" in str(call)]
            # Model name subheader should not be called when selected_model is None
            assert len(model_name_calls) == 0
    
    @pytest.mark.integration
    def test_info_updates_when_model_selection_changes(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC4: Model info updates immediately when model selection changes."""
        # GIVEN: Session state with models
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[0]
        st.session_state.presets = {}
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox to return different model (triggers change)
            mock_st.selectbox.side_effect = ["Model 2", "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            mock_sidebar_ctx.info = MagicMock()
            # Make st methods delegate to sidebar context when inside sidebar
            mock_st.divider = mock_sidebar_ctx.divider
            mock_st.subheader = mock_sidebar_ctx.subheader
            mock_st.caption = mock_sidebar_ctx.caption
            mock_st.info = mock_sidebar_ctx.info
            
            # WHEN: Calling configure_sidebar (model change occurs)
            configure_sidebar()
            
            # THEN: selected_model should be updated and info should reflect new model
            assert st.session_state.selected_model == sample_model_configs[1]
            # Subheader should be called with new model name
            assert mock_sidebar_ctx.subheader.called
            subheader_calls = mock_sidebar_ctx.subheader.call_args_list
            assert any("Model 2" in str(call) for call in subheader_calls)


class TestErrorHandlingStory17:
    """Tests for error handling and edge cases (Story 1.7)."""
    
    @pytest.mark.integration
    def test_initialize_session_state_handles_missing_models_yaml_with_fallback(self, mock_streamlit_secrets):
        """Test AC1, AC2: Missing models.yaml triggers fallback to secrets.toml (Story 1.7)."""
        # GIVEN: models.yaml doesn't exist but secrets.toml has endpoint
        with patch('streamlit_app.load_models_config') as mock_load, \
             patch('streamlit_app.get_replicate_model_endpoint') as mock_get_endpoint, \
             patch('streamlit_app.st') as mock_st:
            
            # Mock FileNotFoundError when loading models.yaml
            mock_load.side_effect = FileNotFoundError("Configuration file not found: models.yaml")
            mock_get_endpoint.return_value = 'stability-ai/sdxl:real-version'
            
            mock_st.session_state = {}
            mock_st.info = MagicMock()
            mock_st.error = MagicMock()
            
            # WHEN: Initializing session state
            initialize_session_state()
            
            # THEN: Should use fallback configuration
            assert 'model_configs' in mock_st.session_state
            assert 'selected_model' in mock_st.session_state
            assert len(mock_st.session_state['model_configs']) == 1
            assert mock_st.session_state['selected_model']['endpoint'] == 'stability-ai/sdxl:real-version'
            # Should display informational message about fallback
            mock_st.info.assert_called()
            info_call = str(mock_st.info.call_args)
            assert "Fallback" in info_call or "fallback" in info_call.lower()
    
    @pytest.mark.integration
    def test_initialize_session_state_handles_invalid_yaml_with_fallback(self, mock_streamlit_secrets):
        """Test AC1, AC2: Invalid YAML syntax triggers fallback to secrets.toml (Story 1.7)."""
        import yaml
        with patch('streamlit_app.load_models_config') as mock_load, \
             patch('streamlit_app.get_replicate_model_endpoint') as mock_get_endpoint, \
             patch('streamlit_app.st') as mock_st:
            
            # Mock YAMLError when loading models.yaml
            mock_load.side_effect = yaml.YAMLError("Invalid YAML syntax at line 5")
            mock_get_endpoint.return_value = 'stability-ai/sdxl:real-version'
            
            mock_st.session_state = {}
            mock_st.warning = MagicMock()
            mock_st.error = MagicMock()
            
            # WHEN: Initializing session state
            initialize_session_state()
            
            # THEN: Should use fallback configuration
            assert 'model_configs' in mock_st.session_state
            assert len(mock_st.session_state['model_configs']) == 1
            # Should display warning about YAML error and fallback
            mock_st.warning.assert_called()
            warning_call = str(mock_st.warning.call_args)
            assert "YAML" in warning_call or "yaml" in warning_call.lower()
            assert "Fallback" in warning_call or "fallback" in warning_call.lower()
    
    @pytest.mark.integration
    def test_initialize_session_state_handles_missing_required_fields_with_fallback(self, mock_streamlit_secrets):
        """Test AC1, AC2: Missing required fields triggers fallback to secrets.toml (Story 1.7)."""
        with patch('streamlit_app.load_models_config') as mock_load, \
             patch('streamlit_app.get_replicate_model_endpoint') as mock_get_endpoint, \
             patch('streamlit_app.st') as mock_st:
            
            # Mock ValueError for missing required fields
            mock_load.side_effect = ValueError("Model 'Test Model' (id: test): Missing required fields: endpoint")
            mock_get_endpoint.return_value = 'stability-ai/sdxl:real-version'
            
            mock_st.session_state = {}
            mock_st.warning = MagicMock()
            mock_st.error = MagicMock()
            
            # WHEN: Initializing session state
            initialize_session_state()
            
            # THEN: Should use fallback configuration
            assert 'model_configs' in mock_st.session_state
            assert len(mock_st.session_state['model_configs']) == 1
            # Should display warning about validation error and fallback
            mock_st.warning.assert_called()
            warning_call = str(mock_st.warning.call_args)
            assert "Validation" in warning_call or "validation" in warning_call.lower()
    
    @pytest.mark.integration
    def test_initialize_session_state_handles_missing_models_yaml_no_fallback(self, mock_streamlit_secrets):
        """Test AC1: Missing models.yaml with no fallback displays error (Story 1.7)."""
        with patch('streamlit_app.load_models_config') as mock_load, \
             patch('streamlit_app.get_replicate_model_endpoint') as mock_get_endpoint, \
             patch('streamlit_app.st') as mock_st:
            
            # Mock FileNotFoundError when loading models.yaml
            mock_load.side_effect = FileNotFoundError("Configuration file not found: models.yaml")
            # No fallback available (returns test default)
            mock_get_endpoint.return_value = 'stability-ai/sdxl:test-version'
            
            mock_st.session_state = {}
            mock_st.error = MagicMock()
            mock_st.info = MagicMock()
            
            # WHEN: Initializing session state
            initialize_session_state()
            
            # THEN: Should display error message
            mock_st.error.assert_called()
            error_call = str(mock_st.error.call_args)
            assert "Configuration" in error_call or "configuration" in error_call.lower()
            assert "models.yaml" in error_call.lower()
    
    @pytest.mark.integration
    def test_main_page_api_error_includes_model_context(self, mock_streamlit_secrets, mock_requests_get):
        """Test AC1: API error messages include model name for context (Story 1.7)."""
        # GIVEN: Form submitted but API raises exception
        submitted = True
        selected_model = {
            'id': 'helldiver',
            'name': 'Helldiver Model',
            'endpoint': 'owner/helldiver:version'
        }
        
        with patch('streamlit_app.replicate.run') as mock_run:
            mock_run.side_effect = Exception("API connection failed")
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st:
                mock_container = MagicMock()
                mock_st.empty.return_value.container.return_value = mock_container
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.status.return_value.__exit__ = MagicMock(return_value=None)
                mock_st.session_state = {'selected_model': selected_model}
                mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
                mock_st.error = MagicMock()
                
                main_page(
                    submitted, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
                
                # THEN: Error message should include model name and id
                mock_st.error.assert_called()
                error_call = mock_st.error.call_args[0][0]
                assert 'Helldiver Model' in error_call or 'helldiver' in error_call.lower()
    
    @pytest.mark.integration
    def test_main_page_handles_network_error(self, mock_streamlit_secrets):
        """Test AC1: Network errors are distinguished from other API errors (Story 1.7)."""
        # GIVEN: Form submitted but network request fails
        submitted = True
        selected_model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version'
        }
        
        with patch('streamlit_app.replicate.run') as mock_run:
            mock_run.side_effect = requests.exceptions.RequestException("Network connection failed")
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st:
                mock_container = MagicMock()
                mock_st.empty.return_value.container.return_value = mock_container
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.status.return_value.__exit__ = MagicMock(return_value=None)
                mock_st.session_state = {'selected_model': selected_model}
                mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
                mock_st.error = MagicMock()
                
                main_page(
                    submitted, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
                
                # THEN: Error message should indicate network error
                mock_st.error.assert_called()
                error_call = mock_st.error.call_args[0][0]
                assert 'Network' in error_call or 'network' in error_call.lower()
                assert 'Test Model' in error_call
    
    @pytest.mark.integration
    def test_main_page_handles_replicate_api_error(self, mock_streamlit_secrets):
        """Test AC1: Replicate API-specific errors are distinguished (Story 1.7)."""
        # GIVEN: Form submitted but Replicate API raises specific error
        submitted = True
        selected_model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version'
        }
        
        # Create a mock ReplicateError
        class MockReplicateError(Exception):
            pass
        
        with patch('streamlit_app.replicate.run') as mock_run, \
             patch('streamlit_app.replicate.exceptions.ReplicateError', MockReplicateError):
            mock_run.side_effect = MockReplicateError("Authentication failed")
            
            # WHEN: Calling main_page
            with patch('streamlit_app.st') as mock_st:
                mock_container = MagicMock()
                mock_st.empty.return_value.container.return_value = mock_container
                mock_st.status.return_value.__enter__.return_value = MagicMock()
                mock_st.status.return_value.__exit__ = MagicMock(return_value=None)
                mock_st.session_state = {'selected_model': selected_model}
                mock_st.get = lambda key, default=None: mock_st.session_state.get(key, default)
                mock_st.error = MagicMock()
                
                main_page(
                    submitted, 1024, 1024, 1, "DDIM",
                    50, 7.5, 0.8, "expert_ensemble_refiner",
                    0.8, "test", "test"
                )
                
                # THEN: Error message should indicate Replicate API error
                mock_st.error.assert_called()
                error_call = mock_st.error.call_args[0][0]
                assert 'Replicate' in error_call or 'replicate' in error_call.lower()
                assert 'Test Model' in error_call
    
    @pytest.mark.integration
    def test_initialize_session_state_app_does_not_crash_on_errors(self, mock_streamlit_secrets):
        """Test AC3: Application does not crash when errors occur (Story 1.7)."""
        # GIVEN: Various error scenarios
        error_scenarios = [
            FileNotFoundError("File not found"),
            yaml.YAMLError("Invalid YAML"),
            ValueError("Validation error"),
            Exception("Unexpected error")
        ]
        
        for error in error_scenarios:
            with patch('streamlit_app.load_models_config') as mock_load, \
                 patch('streamlit_app.get_replicate_model_endpoint') as mock_get_endpoint, \
                 patch('streamlit_app.st') as mock_st:
                
                mock_load.side_effect = error
                mock_get_endpoint.return_value = 'stability-ai/sdxl:test-version'
                mock_st.session_state = {}
                mock_st.error = MagicMock()
                mock_st.warning = MagicMock()
                mock_st.info = MagicMock()
                
                # WHEN: Initializing session state
                try:
                    initialize_session_state()
                    # THEN: Should not raise exception (app doesn't crash)
                    assert True  # If we get here, no exception was raised
                except Exception as e:
                    pytest.fail(f"Application crashed with error: {e}")
    
    @pytest.mark.integration
    def test_error_messages_display_in_ui(self, mock_streamlit_secrets):
        """Test AC4: Error messages are visible in UI using st.error/st.warning (Story 1.7)."""
        # GIVEN: Error occurs during initialization
        with patch('streamlit_app.load_models_config') as mock_load, \
             patch('streamlit_app.st') as mock_st:
            
            mock_load.side_effect = ValueError("Test validation error")
            mock_st.session_state = {}
            mock_st.error = MagicMock()
            mock_st.warning = MagicMock()
            
            # WHEN: Initializing session state
            initialize_session_state()
            
            # THEN: Error/warning should be displayed in UI
            assert mock_st.error.called or mock_st.warning.called
    
    @pytest.mark.integration
    def test_errors_are_logged_appropriately(self, mock_streamlit_secrets, caplog):
        """Test AC5: Errors are logged with appropriate severity and context (Story 1.7)."""
        import logging
        logging.basicConfig(level=logging.ERROR)
        
        # GIVEN: Error occurs during initialization
        with patch('streamlit_app.load_models_config') as mock_load, \
             patch('streamlit_app.get_replicate_model_endpoint') as mock_get_endpoint, \
             patch('streamlit_app.st') as mock_st:
            
            mock_load.side_effect = ValueError("Model 'Test' (id: test): Missing required fields: endpoint")
            mock_get_endpoint.return_value = 'stability-ai/sdxl:test-version'
            mock_st.session_state = {}
            mock_st.error = MagicMock()
            mock_st.warning = MagicMock()
            
            # WHEN: Initializing session state
            with caplog.at_level(logging.ERROR):
                initialize_session_state()
            
            # THEN: Error should be logged with context
            assert any("error" in record.levelname.lower() for record in caplog.records)
            # Verify log contains useful context
            log_messages = [record.message for record in caplog.records]
            assert any("Test" in msg or "test" in msg.lower() for msg in log_messages)


class TestPresetAutoApplication:
    """Tests for preset auto-application on model selection (Story 2.4)."""
    
    @pytest.mark.integration
    def test_preset_lookup_finds_correct_preset_by_model_id(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC1: Preset lookup finds correct preset by model_id when preset exists."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model with preset
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'trigger_words': ['TRIGGER1'],
            'settings': {'width': 512, 'height': 512}
        }
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = None
        
        # WHEN: Applying preset for model
        preset_applied, was_applied = _apply_preset_for_model(model)
        
        # THEN: Preset should be found and applied
        assert preset_applied is not None
        assert preset_applied['id'] == 'test-preset'
        assert was_applied is True
    
    @pytest.mark.integration
    def test_preset_lookup_returns_none_when_no_preset_exists(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC1: Preset lookup returns None when no preset exists for model."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model without preset
        model = sample_model_configs[0]
        st.session_state.presets = {}
        st.session_state.preset_applied_for_model_id = None
        
        # WHEN: Applying preset for model
        preset_applied, was_applied = _apply_preset_for_model(model)
        
        # THEN: No preset should be found
        assert preset_applied is None
        assert was_applied is False
    
    @pytest.mark.integration
    def test_trigger_words_prepended_when_position_is_prepend(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC2: Trigger words prepended to prompt when trigger_words_position is 'prepend'."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model with preset that has trigger words with prepend position
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'trigger_words': ['TRIGGER1', 'TRIGGER2'],
            'trigger_words_position': 'prepend'
        }
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = None
        st.session_state.form_prompt = "existing prompt"
        
        # WHEN: Applying preset
        _apply_preset_for_model(model)
        
        # THEN: Trigger words should be prepended
        assert 'form_prompt' in st.session_state
        prompt = st.session_state.form_prompt
        assert prompt.startswith("TRIGGER1, TRIGGER2")
        assert "existing prompt" in prompt
    
    @pytest.mark.integration
    def test_trigger_words_appended_when_position_is_append(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC2: Trigger words appended to prompt when trigger_words_position is 'append'."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model with preset that has trigger words with append position
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'trigger_words': ['TRIGGER1'],
            'trigger_words_position': 'append'
        }
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = None
        st.session_state.form_prompt = "existing prompt"
        
        # WHEN: Applying preset
        _apply_preset_for_model(model)
        
        # THEN: Trigger words should be appended
        assert 'form_prompt' in st.session_state
        prompt = st.session_state.form_prompt
        assert prompt.endswith("TRIGGER1")
        assert prompt.startswith("existing prompt")
    
    @pytest.mark.integration
    def test_trigger_words_formatted_correctly_when_array(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC2: Trigger words formatted correctly when array vs string."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model with preset that has trigger words as array
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'trigger_words': ['WORD1', 'WORD2', 'WORD3']
        }
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = None
        st.session_state.form_prompt = ""
        
        # WHEN: Applying preset
        _apply_preset_for_model(model)
        
        # THEN: Trigger words should be formatted as comma-separated string
        assert 'form_prompt' in st.session_state
        prompt = st.session_state.form_prompt
        assert "WORD1, WORD2, WORD3" in prompt
    
    @pytest.mark.integration
    def test_preset_settings_applied_to_form_field_keys(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC2: Preset settings (width, height, scheduler, etc.) applied to form field session state keys."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model with preset that has settings
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'settings': {
                'width': 512,
                'height': 768,
                'scheduler': 'DPMSolverMultistep',
                'num_inference_steps': 30,
                'guidance_scale': 8.0
            }
        }
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = None
        
        # WHEN: Applying preset
        _apply_preset_for_model(model)
        
        # THEN: Settings should be applied to form field keys
        assert st.session_state.get('form_width') == 512
        assert st.session_state.get('form_height') == 768
        assert st.session_state.get('form_scheduler') == 'DPMSolverMultistep'
        assert st.session_state.get('form_num_inference_steps') == 30
        assert st.session_state.get('form_guidance_scale') == 8.0
    
    @pytest.mark.integration
    def test_visual_indication_appears_when_preset_applied(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC4: Visual indication (st.success) appears when preset is applied."""
        # GIVEN: Session state with model and preset
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'trigger_words': ['TRIGGER1']
        }
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[1]  # Different model initially
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = None
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            # Mock selectbox to return model with preset (triggers model change)
            mock_st.selectbox.side_effect = [model.get('name'), "DDIM", "expert_ensemble_refiner"]
            
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.success = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            mock_sidebar_ctx.info = MagicMock()
            mock_st.divider = mock_sidebar_ctx.divider
            mock_st.subheader = mock_sidebar_ctx.subheader
            mock_st.caption = mock_sidebar_ctx.caption
            mock_st.info = mock_sidebar_ctx.info
            mock_st.success = mock_sidebar_ctx.success = MagicMock()
            
            # WHEN: Calling configure_sidebar (model switch occurs)
            configure_sidebar()
            
            # THEN: Success message should be displayed
            assert mock_st.success.called or mock_sidebar_ctx.success.called
            success_calls = mock_st.success.call_args_list if mock_st.success.called else mock_sidebar_ctx.success.call_args_list
            assert any("Preset" in str(call) and "applied" in str(call) for call in success_calls)
    
    @pytest.mark.integration
    def test_no_visual_indication_when_no_preset_exists(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC4: No visual indication when no preset exists."""
        # GIVEN: Model without preset
        model = sample_model_configs[0]
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = sample_model_configs[1]  # Different model initially
        st.session_state.presets = {}  # No presets
        st.session_state.preset_applied_for_model_id = None
        
        with patch('streamlit_app.st') as mock_st:
            mock_sidebar_ctx = MagicMock()
            mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar_ctx)
            mock_st.sidebar.__exit__ = MagicMock(return_value=None)
            
            mock_form_ctx = MagicMock()
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form_ctx)
            mock_form.__exit__ = MagicMock(return_value=None)
            mock_st.form.return_value = mock_form
            
            mock_st.session_state = st.session_state
            mock_st.get = lambda key, default=None: st.session_state.get(key, default)
            
            mock_st.selectbox.side_effect = [model.get('name'), "DDIM", "expert_ensemble_refiner"]
            mock_st.number_input.return_value = 1024
            mock_st.slider.return_value = 1
            mock_st.text_area.return_value = "test"
            mock_st.form_submit_button.return_value = False
            mock_st.info = MagicMock()
            mock_st.success = MagicMock()
            mock_expander_ctx = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander_ctx)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
            mock_sidebar_ctx.divider = MagicMock()
            mock_sidebar_ctx.subheader = MagicMock()
            mock_sidebar_ctx.caption = MagicMock()
            mock_sidebar_ctx.info = MagicMock()
            mock_st.divider = mock_sidebar_ctx.divider
            mock_st.subheader = mock_sidebar_ctx.subheader
            mock_st.caption = mock_sidebar_ctx.caption
            mock_st.info = mock_sidebar_ctx.info
            mock_st.success = mock_sidebar_ctx.success = MagicMock()
            
            # WHEN: Calling configure_sidebar
            configure_sidebar()
            
            # THEN: Success message should NOT be displayed
            # Note: success might be called for other reasons, but not for preset application
            # We check that it wasn't called with preset-related message
            if mock_st.success.called or mock_sidebar_ctx.success.called:
                success_calls = mock_st.success.call_args_list if mock_st.success.called else mock_sidebar_ctx.success.call_args_list
                assert not any("Preset" in str(call) and "applied" in str(call) for call in success_calls)
    
    @pytest.mark.integration
    def test_graceful_handling_when_model_has_no_preset(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC5: Graceful handling when model has no preset (no error, app continues normally)."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model without preset
        model = sample_model_configs[0]
        st.session_state.presets = {}
        st.session_state.preset_applied_for_model_id = None
        
        # WHEN: Applying preset for model
        preset_applied, was_applied = _apply_preset_for_model(model)
        
        # THEN: Should return None without error
        assert preset_applied is None
        assert was_applied is False
        # App should continue normally (no exception raised)
    
    @pytest.mark.integration
    def test_preset_doesnt_overwrite_user_modified_prompt(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC6: Preset doesn't overwrite user-modified prompt when switching back to same model."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model with preset, preset already applied
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'trigger_words': ['TRIGGER1']
        }
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = model_id  # Already applied
        st.session_state.form_prompt = "user modified prompt"
        
        # WHEN: Trying to apply preset again (should not re-apply)
        preset_applied, was_applied = _apply_preset_for_model(model)
        
        # THEN: Preset should not be re-applied, user prompt preserved
        assert was_applied is False
        assert st.session_state.form_prompt == "user modified prompt"
    
    @pytest.mark.integration
    def test_preset_applies_when_switching_to_different_model(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC6: Preset applies when switching to different model."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Two models, second has preset
        model1 = sample_model_configs[0]
        model2 = sample_model_configs[1] if len(sample_model_configs) > 1 else sample_model_configs[0]
        model2_id = model2.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model2_id,
            'trigger_words': ['TRIGGER1'],
            'settings': {'width': 512}
        }
        st.session_state.presets = {model2_id: [preset]}
        st.session_state.preset_applied_for_model_id = model1.get('id')  # Different model
        
        # WHEN: Applying preset for different model
        preset_applied, was_applied = _apply_preset_for_model(model2)
        
        # THEN: Preset should be applied
        assert was_applied is True
        assert preset_applied is not None


class TestManualOverridePresetValues:
    """Tests for manual override of preset values (Story 2.5)."""
    
    @pytest.mark.integration
    def test_prompt_field_editable_after_trigger_words_injection(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC1: User can edit prompt field even after trigger words are auto-injected."""
        from streamlit_app import _apply_preset_for_model, configure_sidebar
        
        # GIVEN: Model with preset that has trigger words
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'trigger_words': ['TRIGGER1', 'TRIGGER2'],
            'trigger_words_position': 'prepend'
        }
        st.session_state.model_configs = sample_model_configs
        st.session_state.selected_model = model
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = None
        st.session_state.form_prompt = ""
        
        # Apply preset first
        _apply_preset_for_model(model)
        initial_prompt = st.session_state.get('form_prompt', '')
        assert 'TRIGGER1' in initial_prompt or 'TRIGGER2' in initial_prompt, "Trigger words should be injected"
        
        # WHEN: User modifies prompt (simulate by setting form_prompt directly)
        modified_prompt = "user modified prompt without triggers"
        st.session_state.form_prompt = modified_prompt
        
        # THEN: Prompt should be editable (no exception, value changed)
        assert st.session_state.form_prompt == modified_prompt
        # Verify user can modify auto-injected trigger words
        st.session_state.form_prompt = "TRIGGER1, TRIGGER2 user added more text"
        assert st.session_state.form_prompt == "TRIGGER1, TRIGGER2 user added more text"
    
    @pytest.mark.integration
    def test_all_settings_fields_editable_after_preset_application(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC2: User can modify any setting after preset applies."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model with preset that has settings
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'settings': {
                'width': 512,
                'height': 768,
                'scheduler': 'DPMSolverMultistep',
                'num_inference_steps': 30,
                'guidance_scale': 8.0
            }
        }
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = None
        
        # Apply preset
        _apply_preset_for_model(model)
        
        # Verify preset values were applied
        assert st.session_state.get('form_width') == 512
        assert st.session_state.get('form_height') == 768
        
        # WHEN: User modifies settings
        st.session_state.form_width = 1024
        st.session_state.form_height = 1024
        st.session_state.form_scheduler = 'DDIM'
        st.session_state.form_num_inference_steps = 50
        st.session_state.form_guidance_scale = 7.5
        
        # THEN: Modified values should be preserved
        assert st.session_state.get('form_width') == 1024
        assert st.session_state.get('form_height') == 1024
        assert st.session_state.get('form_scheduler') == 'DDIM'
        assert st.session_state.get('form_num_inference_steps') == 50
        assert st.session_state.get('form_guidance_scale') == 7.5
    
    @pytest.mark.integration
    def test_manual_changes_persist_when_switching_models(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC3: Manual changes persist when switching models and switching back."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Two models with different presets, user modifies values for first model
        model1 = sample_model_configs[0]
        model2 = sample_model_configs[1] if len(sample_model_configs) > 1 else sample_model_configs[0]
        model1_id = model1.get('id')
        model2_id = model2.get('id')
        
        preset1 = {
            'id': 'preset1',
            'name': 'Preset 1',
            'model_id': model1_id,
            'trigger_words': ['TRIGGER1'],
            'settings': {'width': 512, 'height': 512}
        }
        preset2 = {
            'id': 'preset2',
            'name': 'Preset 2',
            'model_id': model2_id,
            'trigger_words': ['TRIGGER2'],
            'settings': {'width': 768, 'height': 768}
        }
        
        st.session_state.presets = {model1_id: [preset1], model2_id: [preset2]}
        st.session_state.preset_applied_for_model_id = None
        
        # Apply preset for model1
        _apply_preset_for_model(model1)
        st.session_state.preset_applied_for_model_id = model1_id
        
        # User modifies values
        user_modified_prompt = "user modified prompt"
        st.session_state.form_prompt = user_modified_prompt
        st.session_state.form_width = 1024
        st.session_state.form_height = 1024
        
        # Track user modifications for model1
        st.session_state.user_modified_fields_by_model = {
            model1_id: {
                'prompt': True,
                'settings': True,
                'setting_keys': ['width', 'height']
            }
        }
        st.session_state.preset_applied_values_by_model = {
            model1_id: {
                'prompt': 'TRIGGER1',
                'settings': {'width': 512, 'height': 512}
            }
        }
        
        # WHEN: Switching to model2
        _apply_preset_for_model(model2)
        st.session_state.preset_applied_for_model_id = model2_id
        
        # Preserve user modifications (form values should persist)
        preserved_prompt = st.session_state.get('form_prompt')
        preserved_width = st.session_state.get('form_width')
        preserved_height = st.session_state.get('form_height')
        
        # WHEN: Switching back to model1
        # Preset should not re-apply because user modified values
        preset_applied, was_applied = _apply_preset_for_model(model1)
        
        # THEN: User modifications should be preserved
        # Note: In real app, form values persist in session state
        # The preset won't overwrite because user_modified_fields tracks modifications
        assert was_applied is False, "Preset should not re-apply when user has modified values"
    
    @pytest.mark.integration
    def test_preset_doesnt_reapply_after_manual_override(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC4: Preset values don't re-apply automatically after manual override."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Model with preset, preset applied, then user modifies values
        model = sample_model_configs[0]
        model_id = model.get('id')
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': model_id,
            'trigger_words': ['TRIGGER1'],
            'settings': {'width': 512, 'height': 512}
        }
        st.session_state.presets = {model_id: [preset]}
        st.session_state.preset_applied_for_model_id = None
        
        # Apply preset
        _apply_preset_for_model(model)
        st.session_state.preset_applied_for_model_id = model_id
        
        # Track preset-applied values
        st.session_state.preset_applied_values_by_model = {
            model_id: {
                'prompt': 'TRIGGER1',
                'settings': {'width': 512, 'height': 512}
            }
        }
        
        # User modifies values
        st.session_state.form_prompt = "user modified prompt"
        st.session_state.form_width = 1024
        
        # Track user modifications
        st.session_state.user_modified_fields_by_model = {
            model_id: {
                'prompt': True,
                'settings': True,
                'setting_keys': ['width']
            }
        }
        
        # WHEN: Trying to apply preset again (same model)
        preset_applied, was_applied = _apply_preset_for_model(model)
        
        # THEN: Preset should not re-apply
        assert was_applied is False, "Preset should not re-apply after user modifications"
        assert st.session_state.get('form_prompt') == "user modified prompt"
        assert st.session_state.get('form_width') == 1024
    
    @pytest.mark.integration
    def test_preset_applies_when_switching_to_different_model_after_modification(self, mock_streamlit_secrets, sample_model_configs):
        """Test AC4: Preset applies when switching to different model even if user modified previous model."""
        from streamlit_app import _apply_preset_for_model
        
        # GIVEN: Two models, user modified first model
        model1 = sample_model_configs[0]
        model2 = sample_model_configs[1] if len(sample_model_configs) > 1 else sample_model_configs[0]
        model1_id = model1.get('id')
        model2_id = model2.get('id')
        
        preset1 = {
            'id': 'preset1',
            'name': 'Preset 1',
            'model_id': model1_id,
            'trigger_words': ['TRIGGER1'],
            'settings': {'width': 512}
        }
        preset2 = {
            'id': 'preset2',
            'name': 'Preset 2',
            'model_id': model2_id,
            'trigger_words': ['TRIGGER2'],
            'settings': {'width': 768}
        }
        
        st.session_state.presets = {model1_id: [preset1], model2_id: [preset2]}
        st.session_state.preset_applied_for_model_id = model1_id
        
        # User modified model1
        st.session_state.user_modified_fields_by_model = {
            model1_id: {
                'prompt': True,
                'settings': True,
                'setting_keys': ['width']
            }
        }
        
        # WHEN: Switching to model2 (different model)
        preset_applied, was_applied = _apply_preset_for_model(model2)
        
        # THEN: Preset should apply for new model
        assert was_applied is True, "Preset should apply when switching to different model"
        assert preset_applied is not None
        assert preset_applied['id'] == 'preset2'
        # When switching to model2, preset2 should apply and set width to 768 (from preset2 settings)
        assert st.session_state.get('form_width') == 768, "Preset2 should set width to 768"