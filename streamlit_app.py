import replicate
import streamlit as st
import requests
import zipfile
import io
import logging
import os
import yaml
from utils import icon
from streamlit_image_select import image_select
from config.model_loader import load_models_config
from utils.preset_manager import load_presets_config

logger = logging.getLogger(__name__)

# UI configurations
st.set_page_config(page_title="Replicate Image Generator",
                   page_icon=":bridge_at_night:",
                   layout="wide")
icon.show_icon(":foggy:")
st.markdown("# :rainbow[Text-to-Image Artistry Studio]")


def _set_session_state(key: str, value: any) -> None:
    """
    Helper function to set session state values that works with both
    dict-style and attribute-style access (for testing compatibility).
    
    Args:
        key: The session state key to set
        value: The value to set
    """
    try:
        # Try attribute-style access first (works in real Streamlit)
        setattr(st.session_state, key, value)
    except (AttributeError, TypeError):
        # Fall back to dict-style access (works in tests with mocked dict)
        st.session_state[key] = value


def _apply_preset_for_model(selected_model: dict) -> tuple[dict | None, bool]:
    """
    Apply preset for selected model if preset exists.
    
    This function:
    - Finds matching preset by model_id
    - Applies trigger words to prompt (prepend or append)
    - Applies preset settings to form field session state keys
    - Respects user modifications and doesn't re-apply if user has modified values
    - Returns preset dict and success flag
    
    Args:
        selected_model: The currently selected model dict
        
    Returns:
        Tuple of (preset_dict, was_applied) where:
        - preset_dict: The preset that was applied, or None if no preset found
        - was_applied: True if preset was applied, False otherwise
    """
    if not selected_model:
        return None, False
    
    model_id = selected_model.get('id')
    if not model_id:
        return None, False
    
    # Get presets from session state
    presets = st.session_state.get('presets', {})
    model_presets = presets.get(model_id, [])
    
    # If no presets for this model, return None
    if not model_presets or len(model_presets) == 0:
        return None, False
    
    # Find preset to use: first preset with default: true, or first preset
    preset_to_apply = None
    for preset in model_presets:
        if preset.get('default', False):
            preset_to_apply = preset
            break
    
    if not preset_to_apply:
        preset_to_apply = model_presets[0]
    
    # Check if user has modified values for this model - if so, don't re-apply preset
    user_modified_fields_by_model = st.session_state.get('user_modified_fields_by_model', {})
    user_modified_fields = user_modified_fields_by_model.get(model_id, {
        'prompt': False,
        'settings': False,
        'setting_keys': []
    })
    applied_model_id = st.session_state.get('preset_applied_for_model_id', None)
    
    # Check if user has modified values for this model - if so, don't re-apply preset
    # This check applies whether we're on the same model or switching back to a previously modified model
    if user_modified_fields.get('prompt', False) or user_modified_fields.get('settings', False):
        # User has modified values for this model, don't re-apply preset
        return preset_to_apply, False
    
    # If preset was already applied for this model and no user modifications, don't re-apply
    if applied_model_id == model_id:
        # No user modifications, but preset already applied - don't re-apply
        return preset_to_apply, False
    
    # Apply trigger words to prompt if available
    # Only apply if user hasn't modified the prompt
    trigger_words = preset_to_apply.get('trigger_words')
    if trigger_words and not user_modified_fields.get('prompt', False):
        # Determine injection position (default to "prepend")
        position = preset_to_apply.get('trigger_words_position', 'prepend')
        
        # Format trigger words
        if isinstance(trigger_words, list):
            # Filter out empty strings and join
            filtered = [tw for tw in trigger_words if tw and str(tw).strip()]
            if filtered:
                trigger_words_str = ", ".join(str(tw) for tw in filtered)
            else:
                trigger_words_str = None
        elif isinstance(trigger_words, str) and trigger_words.strip():
            trigger_words_str = trigger_words
        else:
            trigger_words_str = None
        
        # Apply trigger words to prompt
        if trigger_words_str:
            # Get current prompt from session state (may not exist yet)
            current_prompt = st.session_state.get('form_prompt', '')
            if position == 'append':
                # Append trigger words to end of prompt
                if current_prompt:
                    new_prompt = f"{current_prompt} {trigger_words_str}".strip()
                else:
                    new_prompt = trigger_words_str
            else:  # prepend (default)
                # Prepend trigger words to beginning of prompt
                if current_prompt:
                    new_prompt = f"{trigger_words_str} {current_prompt}".strip()
                else:
                    new_prompt = trigger_words_str
            
            _set_session_state('form_prompt', new_prompt)
    
    # Apply preset settings to form field session state keys
    # Only apply settings that user hasn't modified
    settings = preset_to_apply.get('settings', {})
    if settings:
        # Map preset settings to form field keys
        setting_mappings = {
            'width': 'form_width',
            'height': 'form_height',
            'num_outputs': 'form_num_outputs',
            'scheduler': 'form_scheduler',
            'num_inference_steps': 'form_num_inference_steps',
            'guidance_scale': 'form_guidance_scale',
            'prompt_strength': 'form_prompt_strength',
            'refine': 'form_refine',
            'high_noise_frac': 'form_high_noise_frac',
            'negative_prompt': 'form_negative_prompt',
        }
        
        # Get list of user-modified setting keys for this model (convert to set for efficient lookup)
        user_modified_setting_keys = set(user_modified_fields.get('setting_keys', []))
        
        for setting_key, form_key in setting_mappings.items():
            # Only apply if user hasn't modified this specific setting
            if setting_key in settings and setting_key not in user_modified_setting_keys:
                _set_session_state(form_key, settings[setting_key])
    
    # Track that preset was applied for this model
    _set_session_state('preset_applied_for_model_id', model_id)
    
    return preset_to_apply, True

# Helper function to get secrets with fallback for testing
def get_secret(key: str, default: str = None) -> str:
    """Get secret from Streamlit secrets or environment variable, with fallback for testing.
    
    Args:
        key: The secret key to retrieve
        default: Default value if secret is not found (for testing)
        
    Returns:
        The secret value or default
    """
    # Try to get from Streamlit secrets (with multiple fallbacks for testing)
    try:
        if hasattr(st, 'secrets') and st.secrets is not None:
            try:
                return st.secrets[key]
            except (KeyError, AttributeError, TypeError):
                # Key not found in secrets, try environment variable
                pass
    except (AttributeError, RuntimeError, Exception):
        # Secrets not available (e.g., in testing), try environment variable
        pass
    
    # Fallback to environment variable or default
    return os.getenv(key, default)

# API Tokens and endpoints from `.streamlit/secrets.toml` file or environment variables
# Access lazily to avoid import-time errors in testing
def get_replicate_api_token() -> str:
    """Get Replicate API token."""
    return get_secret("REPLICATE_API_TOKEN", "test-token-12345")

def get_replicate_model_endpoint() -> str:
    """Get Replicate model endpoint."""
    return get_secret("REPLICATE_MODEL_ENDPOINTSTABILITY", "stability-ai/sdxl:test-version")

# Resources text, link, and logo
replicate_text = "Stability AI SDXL Model on Replicate"
replicate_link = "https://replicate.com/stability-ai/sdxl"
replicate_logo = "https://storage.googleapis.com/llama2_release/Screen%20Shot%202023-07-21%20at%2012.34.05%20PM.png"

# Placeholders for images and gallery
generated_images_placeholder = st.empty()
gallery_placeholder = st.empty()


def initialize_session_state() -> None:
    """
    Initialize session state for model management.
    
    This function:
    - Loads model configurations from models.yaml
    - Initializes st.session_state.model_configs with loaded models
    - Sets default model (first model or model with default: true flag)
    - Initializes st.session_state.selected_model with default model
    - Handles edge cases (missing config, empty models list)
    - Provides fallback to secrets.toml when models.yaml is missing or invalid
    
    Only runs once per session to avoid re-initialization on reruns.
    """
    # Check if already initialized to avoid re-initialization on reruns
    if 'model_configs' in st.session_state and 'selected_model' in st.session_state:
        # Still load presets if not already loaded (presets are independent of model initialization)
        if 'presets' not in st.session_state:
            try:
                presets = load_presets_config("presets.yaml")
                _set_session_state('presets', presets)
                logger.info(f"Presets loaded: {len(presets)} model(s) with presets")
            except (yaml.YAMLError, ValueError) as e:
                logger.error(f"Error loading presets: {e}")
                _set_session_state('presets', {})
                try:
                    st.error(f"Error loading presets configuration: {e}")
                except (AttributeError, RuntimeError):
                    pass
        return
    
    try:
        # Load models from configuration
        models = load_models_config("models.yaml")
        
        # Initialize model_configs with loaded models
        _set_session_state('model_configs', models)
        
        # Load presets from configuration (AC: 3)
        try:
            presets = load_presets_config("presets.yaml")
            _set_session_state('presets', presets)
            logger.info(f"Presets loaded: {len(presets)} model(s) with presets")
        except (yaml.YAMLError, ValueError) as e:
            logger.error(f"Error loading presets: {e}")
            _set_session_state('presets', {})
            try:
                st.error(f"Error loading presets configuration: {e}")
            except (AttributeError, RuntimeError):
                pass
        
        # Handle empty models list
        if not models:
            logger.warning("No models found in configuration. Model selector will be disabled.")
            _set_session_state('selected_model', None)
            return
        
        # Determine default model: check for explicit default flag first
        default_model = None
        for model in models:
            if model.get('default', False) is True:
                default_model = model
                logger.info(f"Using explicit default model: {model.get('name', model.get('id'))}")
                break
        
        # If no explicit default, use first model
        if default_model is None:
            default_model = models[0]
            logger.info(f"Using first model as default: {default_model.get('name', default_model.get('id'))}")
        
        # Initialize selected_model with default
        _set_session_state('selected_model', default_model)
        
        logger.info(f"Session state initialized successfully with {len(models)} model(s)")
        
    except FileNotFoundError as e:
        # Handle missing models.yaml - attempt fallback to secrets.toml
        logger.warning(f"models.yaml not found: {e}")
        # Show warning to user
        try:
            st.warning(f"models.yaml not found: {e}")
        except (AttributeError, RuntimeError):
            # st.warning may not be available in all contexts (e.g., testing)
            pass
        
        # Attempt fallback to secrets.toml
        try:
            fallback_endpoint = get_replicate_model_endpoint()
            # Only use fallback if endpoint is a valid string and not the test version
            if (fallback_endpoint and 
                isinstance(fallback_endpoint, str) and 
                fallback_endpoint != "stability-ai/sdxl:test-version"):
                # Create single-model configuration from fallback
                fallback_model = {
                    'id': 'default',
                    'name': 'Default Model (from secrets.toml)',
                    'endpoint': fallback_endpoint
                }
                _set_session_state('model_configs', [fallback_model])
                _set_session_state('selected_model', fallback_model)
                
                # Load presets even in fallback mode (presets are independent)
                try:
                    presets = load_presets_config("presets.yaml")
                    _set_session_state('presets', presets)
                    logger.info(f"Presets loaded: {len(presets)} model(s) with presets")
                except (yaml.YAMLError, ValueError) as e:
                    logger.error(f"Error loading presets: {e}")
                    _set_session_state('presets', {})
                
                logger.info(f"Using fallback configuration from secrets.toml: {fallback_endpoint}")
                st.info(
                    "ℹ️ **Fallback Mode Activated**\n\n"
                    "The models.yaml configuration file was not found. "
                    "The application is using the default model endpoint from secrets.toml. "
                    "To use multiple models, please create a models.yaml file at the project root."
                )
            else:
                # No valid fallback available
                _set_session_state('model_configs', [])
                _set_session_state('selected_model', None)
                
                # Still try to load presets (presets are independent)
                try:
                    presets = load_presets_config("presets.yaml")
                    _set_session_state('presets', presets)
                    logger.info(f"Presets loaded: {len(presets)} model(s) with presets")
                except (yaml.YAMLError, ValueError) as e:
                    logger.error(f"Error loading presets: {e}")
                    _set_session_state('presets', {})
                
                logger.error("No fallback configuration available. models.yaml missing and REPLICATE_MODEL_ENDPOINTSTABILITY not found in secrets.toml.")
                st.error(
                    "❌ **Configuration Error**\n\n"
                    "The models.yaml configuration file was not found, and no fallback configuration is available. "
                    "Please either:\n"
                    "1. Create a models.yaml file at the project root, or\n"
                    "2. Ensure REPLICATE_MODEL_ENDPOINTSTABILITY is set in .streamlit/secrets.toml"
                )
        except Exception as fallback_error:
            # Fallback also failed
            logger.error(f"Fallback to secrets.toml failed: {fallback_error}")
            _set_session_state('model_configs', [])
            _set_session_state('selected_model', None)
            
            # Still try to load presets (presets are independent)
            try:
                presets = load_presets_config("presets.yaml")
                _set_session_state('presets', presets)
                logger.info(f"Presets loaded: {len(presets)} model(s) with presets")
            except (yaml.YAMLError, ValueError) as preset_error:
                logger.error(f"Error loading presets: {preset_error}")
                _set_session_state('presets', {})
            st.error(
                "❌ **Configuration Error**\n\n"
                f"Failed to load model configuration: {str(e)}\n\n"
                "The application will continue, but model selection will be disabled. "
                "Please check your configuration files."
            )
        
    except yaml.YAMLError as e:
        # Handle invalid YAML syntax
        error_msg = str(e)
        logger.error(f"Invalid YAML syntax in models.yaml: {error_msg}", exc_info=True)
        _set_session_state('model_configs', [])
        _set_session_state('selected_model', None)
        
        # Attempt fallback to secrets.toml
        try:
            fallback_endpoint = get_replicate_model_endpoint()
            # Only use fallback if endpoint is a valid string and not the test version
            if (fallback_endpoint and 
                isinstance(fallback_endpoint, str) and 
                fallback_endpoint != "stability-ai/sdxl:test-version"):
                fallback_model = {
                    'id': 'default',
                    'name': 'Default Model (from secrets.toml)',
                    'endpoint': fallback_endpoint
                }
                _set_session_state('model_configs', [fallback_model])
                _set_session_state('selected_model', fallback_model)
                logger.info(f"Using fallback configuration from secrets.toml due to YAML error: {fallback_endpoint}")
                st.warning(
                    "⚠️ **YAML Syntax Error - Fallback Mode Activated**\n\n"
                    f"The models.yaml file contains invalid YAML syntax: {error_msg}\n\n"
                    "The application is using the default model endpoint from secrets.toml. "
                    "Please fix the YAML syntax in models.yaml to use multiple models."
                )
            else:
                st.error(
                    "❌ **YAML Syntax Error**\n\n"
                    f"The models.yaml file contains invalid YAML syntax: {error_msg}\n\n"
                    "Please fix the YAML syntax in models.yaml. "
                    "Check for missing quotes, incorrect indentation, or invalid characters."
                )
        except Exception:
            st.error(
                "❌ **YAML Syntax Error**\n\n"
                f"The models.yaml file contains invalid YAML syntax: {error_msg}\n\n"
                "Please fix the YAML syntax in models.yaml. "
                "Check for missing quotes, incorrect indentation, or invalid characters."
            )
        
    except ValueError as e:
        # Handle validation errors (missing fields, invalid endpoint format, etc.)
        error_msg = str(e)
        logger.error(f"Model configuration validation error: {error_msg}", exc_info=True)
        _set_session_state('model_configs', [])
        _set_session_state('selected_model', None)
        
        # Attempt fallback to secrets.toml
        try:
            fallback_endpoint = get_replicate_model_endpoint()
            # Only use fallback if endpoint is a valid string and not the test version
            if (fallback_endpoint and 
                isinstance(fallback_endpoint, str) and 
                fallback_endpoint != "stability-ai/sdxl:test-version"):
                fallback_model = {
                    'id': 'default',
                    'name': 'Default Model (from secrets.toml)',
                    'endpoint': fallback_endpoint
                }
                _set_session_state('model_configs', [fallback_model])
                _set_session_state('selected_model', fallback_model)
                logger.info(f"Using fallback configuration from secrets.toml due to validation error: {fallback_endpoint}")
                st.warning(
                    "⚠️ **Configuration Validation Error - Fallback Mode Activated**\n\n"
                    f"{error_msg}\n\n"
                    "The application is using the default model endpoint from secrets.toml. "
                    "Please fix the configuration errors in models.yaml to use multiple models."
                )
            else:
                st.error(
                    "❌ **Configuration Validation Error**\n\n"
                    f"{error_msg}\n\n"
                    "Please fix the configuration errors in models.yaml."
                )
        except Exception:
            st.error(
                "❌ **Configuration Validation Error**\n\n"
                f"{error_msg}\n\n"
                "Please fix the configuration errors in models.yaml."
            )
        
    except Exception as e:
        # Handle any other unexpected errors
        error_msg = str(e)
        logger.error(f"Unexpected error initializing session state: {error_msg}", exc_info=True)
        _set_session_state('model_configs', [])
        _set_session_state('selected_model', None)
        
        # Attempt fallback to secrets.toml
        try:
            fallback_endpoint = get_replicate_model_endpoint()
            # Only use fallback if endpoint is a valid string and not the test version
            if (fallback_endpoint and 
                isinstance(fallback_endpoint, str) and 
                fallback_endpoint != "stability-ai/sdxl:test-version"):
                fallback_model = {
                    'id': 'default',
                    'name': 'Default Model (from secrets.toml)',
                    'endpoint': fallback_endpoint
                }
                _set_session_state('model_configs', [fallback_model])
                _set_session_state('selected_model', fallback_model)
                logger.info(f"Using fallback configuration from secrets.toml due to unexpected error: {fallback_endpoint}")
                st.warning(
                    "⚠️ **Configuration Error - Fallback Mode Activated**\n\n"
                    f"An unexpected error occurred while loading models.yaml: {error_msg}\n\n"
                    "The application is using the default model endpoint from secrets.toml. "
                    "Please check the models.yaml file for issues."
                )
            else:
                st.error(
                    "❌ **Configuration Error**\n\n"
                    f"An unexpected error occurred while loading model configuration: {error_msg}\n\n"
                    "The application will continue, but model selection will be disabled. "
                    "Please check your configuration files."
                )
        except Exception:
            st.error(
                "❌ **Configuration Error**\n\n"
                f"An unexpected error occurred while loading model configuration: {error_msg}\n\n"
                "The application will continue, but model selection will be disabled. "
                "Please check your configuration files."
            )


def configure_sidebar() -> None:
    """
    Setup and display the sidebar elements.

    This function configures the sidebar of the Streamlit application, 
    including the form for user inputs and the resources section.
    """
    with st.sidebar:
        # Model selector - placed at top of sidebar before form
        model_configs = st.session_state.get('model_configs', [])
        selected_model = st.session_state.get('selected_model', None)
        
        # Initialize preserved state if not exists
        if 'preserved_prompt' not in st.session_state:
            _set_session_state('preserved_prompt', None)
        if 'preserved_settings' not in st.session_state:
            _set_session_state('preserved_settings', None)
        
        # Initialize user modification tracking if not exists
        # Track modifications per model_id to preserve across model switches
        if 'user_modified_fields_by_model' not in st.session_state:
            _set_session_state('user_modified_fields_by_model', {})
        
        # Initialize preset-applied values tracking if not exists
        # This tracks what values were set by preset, so we can detect user modifications
        # Track per model_id to preserve across model switches
        if 'preset_applied_values_by_model' not in st.session_state:
            _set_session_state('preset_applied_values_by_model', {})
        
        # Check if model_configs exists and is not empty before allowing switch
        if not model_configs:
            st.warning("⚠️ No models configured. Please check models.yaml file.")
        else:
                # Get list of model names for selectbox options
                model_names = [model.get('name', model.get('id', 'Unknown')) for model in model_configs]
                
                # Get current selection index
                current_index = 0
                if selected_model and selected_model.get('name'):
                    try:
                        current_index = model_names.index(selected_model['name'])
                    except ValueError:
                        # If selected model name not found, default to first
                        current_index = 0
                
                # Store previous model selection to detect changes
                previous_model = selected_model
                
                # Model selector selectbox
                selected_model_name = st.selectbox(
                    "Select Model",
                    options=model_names,
                    index=current_index,
                    key="model_selector"
                )
                
                # Update session state when selection changes
                if selected_model_name:
                    # Find the model object matching the selected name
                    new_selected_model = None
                    for model in model_configs:
                        if model.get('name') == selected_model_name:
                            new_selected_model = model
                            break
                    
                    # Validate selected model exists in configs
                    if new_selected_model is None:
                        logger.warning(f"Invalid model selection: {selected_model_name}. Model not found in configuration.")
                        st.error(f"⚠️ Invalid model selection: {selected_model_name}. Please select a valid model.")
                    else:
                        # Detect if model changed
                        model_changed = (
                            previous_model is None or 
                            new_selected_model.get('name') != previous_model.get('name')
                        )
                        
                        # If model changed, preserve current form values before switching
                        if model_changed:
                            # Capture current form values from session state keys (form inputs use keys)
                            # These values persist across reruns even when form isn't submitted
                            if 'form_width' in st.session_state:
                                _set_session_state('preserved_prompt', st.session_state.get('form_prompt'))
                                _set_session_state('preserved_settings', {
                                    'width': st.session_state.get('form_width'),
                                    'height': st.session_state.get('form_height'),
                                    'num_outputs': st.session_state.get('form_num_outputs'),
                                    'scheduler': st.session_state.get('form_scheduler'),
                                    'num_inference_steps': st.session_state.get('form_num_inference_steps'),
                                    'guidance_scale': st.session_state.get('form_guidance_scale'),
                                    'prompt_strength': st.session_state.get('form_prompt_strength'),
                                    'refine': st.session_state.get('form_refine'),
                                    'high_noise_frac': st.session_state.get('form_high_noise_frac'),
                                    'negative_prompt': st.session_state.get('form_negative_prompt'),
                                })
                        
                        # Update selected model atomically
                        _set_session_state('selected_model', new_selected_model)
                        
                        # Show visual feedback when model switches (Task 6: AC 3)
                        if model_changed:
                            model_name = new_selected_model.get('name', new_selected_model.get('id', 'Model'))
                            # Use info message for brief, non-intrusive feedback
                            st.info(f"🔄 Switched to model: **{model_name}**")
                        
                        # Apply preset for newly selected model (if model changed or on initial load)
                        # Check if preset hasn't been applied for this model yet
                        applied_model_id = st.session_state.get('preset_applied_for_model_id', None)
                        current_model_id = new_selected_model.get('id')
                        should_apply_preset = model_changed or (applied_model_id != current_model_id)
                        
                        if should_apply_preset:
                            # Reset preset applied tracking when switching to different model
                            if model_changed:
                                _set_session_state('preset_applied_for_model_id', None)
                            
                            # Apply preset for new model
                            preset_applied, was_applied = _apply_preset_for_model(new_selected_model)
                            
                            # Track preset-applied values after applying preset (per model)
                            if was_applied and preset_applied:
                                current_model_id = new_selected_model.get('id')
                                preset_applied_values_by_model = st.session_state.get('preset_applied_values_by_model', {})
                                
                                # Store what values were set by preset for comparison later
                                preset_applied_values = {
                                    'prompt': st.session_state.get('form_prompt'),
                                    'settings': {}
                                }
                                
                                # Store preset-applied setting values
                                setting_mappings = {
                                    'width': 'form_width',
                                    'height': 'form_height',
                                    'num_outputs': 'form_num_outputs',
                                    'scheduler': 'form_scheduler',
                                    'num_inference_steps': 'form_num_inference_steps',
                                    'guidance_scale': 'form_guidance_scale',
                                    'prompt_strength': 'form_prompt_strength',
                                    'refine': 'form_refine',
                                    'high_noise_frac': 'form_high_noise_frac',
                                    'negative_prompt': 'form_negative_prompt',
                                }
                                
                                preset_settings = preset_applied.get('settings', {})
                                for setting_key, form_key in setting_mappings.items():
                                    if setting_key in preset_settings:
                                        preset_applied_values['settings'][setting_key] = preset_settings[setting_key]
                                
                                # Store preset-applied values for this model
                                preset_applied_values_by_model[current_model_id] = preset_applied_values
                                _set_session_state('preset_applied_values_by_model', preset_applied_values_by_model)
                                
                                preset_name = preset_applied.get('name', 'Default')
                                model_name = new_selected_model.get('name', new_selected_model.get('id', 'Model'))
                                st.success(f"✅ Preset '{preset_name}' applied for {model_name}")
        
        # Model Information Section - Display selected model details
        # Get updated selected_model after potential change
        selected_model = st.session_state.get('selected_model', None)
        
        if selected_model:
            # Visual separator between model selector and info
            st.divider()
            
            # Display model name prominently
            model_name = selected_model.get('name', selected_model.get('id', 'Unknown Model'))
            st.subheader(f"📦 {model_name}")
            
            # Show trigger words if available (from model config or preset)
            trigger_words = None
            
            # First, check for trigger words in model config
            model_trigger_words = selected_model.get('trigger_words')
            if model_trigger_words:
                # Check if it's a non-empty list or non-empty string
                if isinstance(model_trigger_words, list) and len(model_trigger_words) > 0:
                    # Filter out empty strings from list
                    filtered = [tw for tw in model_trigger_words if tw and str(tw).strip()]
                    if filtered:
                        trigger_words = filtered
                elif isinstance(model_trigger_words, str) and model_trigger_words.strip():
                    trigger_words = model_trigger_words
            
            # If not in model config, check for trigger words in matching preset
            if not trigger_words:
                model_id = selected_model.get('id')
                if model_id:
                    presets = st.session_state.get('presets', {})
                    model_presets = presets.get(model_id, [])
                    # Use first preset's trigger words if available
                    if model_presets and len(model_presets) > 0:
                        first_preset = model_presets[0]
                        preset_trigger_words = first_preset.get('trigger_words')
                        if preset_trigger_words:
                            if isinstance(preset_trigger_words, list) and len(preset_trigger_words) > 0:
                                # Filter out empty strings from list
                                filtered = [tw for tw in preset_trigger_words if tw and str(tw).strip()]
                                if filtered:
                                    trigger_words = filtered
                            elif isinstance(preset_trigger_words, str) and preset_trigger_words.strip():
                                trigger_words = preset_trigger_words
            
            # Display trigger words if available
            if trigger_words:
                # Format trigger words for display
                if isinstance(trigger_words, list):
                    trigger_words_display = ", ".join(str(tw) for tw in trigger_words)
                    st.info(f"**Trigger Words:** {trigger_words_display}")
                elif isinstance(trigger_words, str):
                    st.info(f"**Trigger Words:** {trigger_words}")
            
            # Display model description if provided
            description = selected_model.get('description')
            if description and description.strip():
                st.caption(description)
        
        with st.form("my_form"):
            st.info("**Yo fam! Start here ↓**", icon="👋🏾")
            
            # Get preserved values if they exist, otherwise use defaults
            preserved_settings = st.session_state.get('preserved_settings', {})
            preserved_prompt = st.session_state.get('preserved_prompt')
            
            with st.expander(":rainbow[**Refine your output here**]"):
                # Advanced Settings (for the curious minds!)
                # Use preserved values if available, otherwise defaults
                # Use session state keys so values persist across reruns
                width_default = preserved_settings.get('width', 1024) if preserved_settings else 1024
                width = st.number_input(
                    "Width of output image", 
                    value=width_default,
                    key='form_width'
                )
                height_default = preserved_settings.get('height', 1024) if preserved_settings else 1024
                height = st.number_input(
                    "Height of output image", 
                    value=height_default,
                    key='form_height'
                )
                num_outputs_default = preserved_settings.get('num_outputs', 1) if preserved_settings else 1
                num_outputs = st.slider(
                    "Number of images to output", 
                    value=num_outputs_default, 
                    min_value=1, 
                    max_value=4,
                    key='form_num_outputs'
                )
                scheduler_options = ('DDIM', 'DPMSolverMultistep', 'HeunDiscrete',
                                   'KarrasDPM', 'K_EULER_ANCESTRAL', 'K_EULER', 'PNDM')
                scheduler_default = preserved_settings.get('scheduler', 'DDIM') if preserved_settings else 'DDIM'
                scheduler_index = scheduler_options.index(scheduler_default) if scheduler_default in scheduler_options else 0
                scheduler = st.selectbox(
                    'Scheduler', 
                    scheduler_options, 
                    index=scheduler_index,
                    key='form_scheduler'
                )
                num_inference_steps_default = preserved_settings.get('num_inference_steps', 50) if preserved_settings else 50
                num_inference_steps = st.slider(
                    "Number of denoising steps", 
                    value=num_inference_steps_default, 
                    min_value=1, 
                    max_value=500,
                    key='form_num_inference_steps'
                )
                guidance_scale_default = preserved_settings.get('guidance_scale', 7.5) if preserved_settings else 7.5
                guidance_scale = st.slider(
                    "Scale for classifier-free guidance", 
                    value=guidance_scale_default, 
                    min_value=1.0, 
                    max_value=50.0, 
                    step=0.1,
                    key='form_guidance_scale'
                )
                prompt_strength_default = preserved_settings.get('prompt_strength', 0.8) if preserved_settings else 0.8
                prompt_strength = st.slider(
                    "Prompt strength when using img2img/inpaint(1.0 corresponds to full destruction of information in image)", 
                    value=prompt_strength_default, 
                    max_value=1.0, 
                    step=0.1,
                    key='form_prompt_strength'
                )
                refine_options = ("expert_ensemble_refiner", "None")
                refine_default = preserved_settings.get('refine', 'expert_ensemble_refiner') if preserved_settings else 'expert_ensemble_refiner'
                refine_index = refine_options.index(refine_default) if refine_default in refine_options else 0
                refine = st.selectbox(
                    "Select refine style to use (left out the other 2)", 
                    refine_options,
                    index=refine_index,
                    key='form_refine'
                )
                high_noise_frac_default = preserved_settings.get('high_noise_frac', 0.8) if preserved_settings else 0.8
                high_noise_frac = st.slider(
                    "Fraction of noise to use for `expert_ensemble_refiner`", 
                    value=high_noise_frac_default, 
                    max_value=1.0, 
                    step=0.1,
                    key='form_high_noise_frac'
                )
            
            # Use preserved prompt if available, otherwise default
            prompt_default = preserved_prompt if preserved_prompt else "An astronaut riding a rainbow unicorn, cinematic, dramatic"
            prompt = st.text_area(
                ":orange[**Enter prompt: start typing, Shakespeare ✍🏾**]",
                value=prompt_default,
                key='form_prompt'
            )
            negative_prompt_default = preserved_settings.get('negative_prompt', "the absolute worst quality, distorted features") if preserved_settings else "the absolute worst quality, distorted features"
            negative_prompt = st.text_area(
                ":orange[**Party poopers you don't want in image? 🙅🏽‍♂️**]",
                value=negative_prompt_default,
                help="This is a negative prompt, basically type what you don't want to see in the generated image",
                key='form_negative_prompt'
            )

            # The Big Red "Submit" Button!
            submitted = st.form_submit_button(
                "Submit", type="primary", use_container_width=True)
        
        # Detect user modifications by comparing current form values with preset-applied values
        # This runs after form fields are rendered, so we can detect if user changed values
        # Get current model to track modifications per model
        current_model = st.session_state.get('selected_model', None)
        current_model_id = current_model.get('id') if current_model else None
        
        if current_model_id:
            preset_applied_values_by_model = st.session_state.get('preset_applied_values_by_model', {})
            preset_applied_values = preset_applied_values_by_model.get(current_model_id, {'prompt': None, 'settings': {}})
            
            user_modified_fields_by_model = st.session_state.get('user_modified_fields_by_model', {})
            user_modified_fields = user_modified_fields_by_model.get(current_model_id, {
                'prompt': False,
                'settings': False,
                'setting_keys': []  # Use list instead of set
            })
        else:
            # No model selected, skip tracking
            preset_applied_values = {'prompt': None, 'settings': {}}
            user_modified_fields = {'prompt': False, 'settings': False, 'setting_keys': []}
        
        # Check if prompt was modified
        current_prompt = st.session_state.get('form_prompt', '')
        preset_prompt = preset_applied_values.get('prompt')
        if preset_prompt is not None and current_prompt != preset_prompt:
            # User has modified prompt
            user_modified_fields['prompt'] = True
        
        # Check if settings were modified
        setting_mappings = {
            'width': 'form_width',
            'height': 'form_height',
            'num_outputs': 'form_num_outputs',
            'scheduler': 'form_scheduler',
            'num_inference_steps': 'form_num_inference_steps',
            'guidance_scale': 'form_guidance_scale',
            'prompt_strength': 'form_prompt_strength',
            'refine': 'form_refine',
            'high_noise_frac': 'form_high_noise_frac',
            'negative_prompt': 'form_negative_prompt',
        }
        
        preset_settings = preset_applied_values.get('settings', {})
        modified_setting_keys = set()
        
        for setting_key, form_key in setting_mappings.items():
            if setting_key in preset_settings:
                # This setting was set by preset, check if user modified it
                current_value = st.session_state.get(form_key)
                preset_value = preset_settings[setting_key]
                
                # Compare values (handle different types)
                if current_value != preset_value:
                    modified_setting_keys.add(setting_key)
        
        # Update user modification tracking (per model)
        if current_model_id:
            if modified_setting_keys:
                user_modified_fields['settings'] = True
                # Convert existing list to set, merge with new modifications, convert back to list
                existing_keys = set(user_modified_fields.get('setting_keys', []))
                all_modified_keys = existing_keys | modified_setting_keys
                user_modified_fields['setting_keys'] = list(all_modified_keys)
            
            # Update session state with modified tracking for this model
            user_modified_fields_by_model = st.session_state.get('user_modified_fields_by_model', {})
            user_modified_fields_by_model[current_model_id] = user_modified_fields
            _set_session_state('user_modified_fields_by_model', user_modified_fields_by_model)

        # Credits and resources
        st.divider()
        st.markdown(
            ":orange[**Resources:**]  \n"
            f"<img src='{replicate_logo}' style='height: 1em'> [{replicate_text}]({replicate_link})",
            unsafe_allow_html=True
        )
        st.markdown(
            """
            ---
            Follow me on:

            𝕏 → [@tonykipkemboi](https://twitter.com/tonykipkemboi)

            LinkedIn → [Tony Kipkemboi](https://www.linkedin.com/in/tonykipkemboi)

            """
        )

        return submitted, width, height, num_outputs, scheduler, num_inference_steps, guidance_scale, prompt_strength, refine, high_noise_frac, prompt, negative_prompt


def main_page(submitted: bool, width: int, height: int, num_outputs: int,
              scheduler: str, num_inference_steps: int, guidance_scale: float,
              prompt_strength: float, refine: str, high_noise_frac: float,
              prompt: str, negative_prompt: str) -> None:
    """Main page layout and logic for generating images.

    Args:
        submitted (bool): Flag indicating whether the form has been submitted.
        width (int): Width of the output image.
        height (int): Height of the output image.
        num_outputs (int): Number of images to output.
        scheduler (str): Scheduler type for the model.
        num_inference_steps (int): Number of denoising steps.
        guidance_scale (float): Scale for classifier-free guidance.
        prompt_strength (float): Prompt strength when using img2img/inpaint.
        refine (str): Refine style to use.
        high_noise_frac (float): Fraction of noise to use for `expert_ensemble_refiner`.
        prompt (str): Text prompt for the image generation.
        negative_prompt (str): Text prompt for elements to avoid in the image.
    """
    if submitted:
        with st.status('👩🏾‍🍳 Whipping up your words into art...', expanded=True) as status:
            st.write("⚙️ Model initiated")
            st.write("🙆‍♀️ Stand up and strecth in the meantime")
            try:
                # Only call the API if the "Submit" button was pressed
                if submitted:
                    # Get the selected model endpoint with backward compatibility fallback
                    selected_model = st.session_state.get('selected_model', None)
                    
                    # Determine endpoint: use selected model endpoint if available, otherwise fallback
                    if selected_model and isinstance(selected_model, dict) and 'endpoint' in selected_model:
                        model_endpoint = selected_model['endpoint']
                        model_name = selected_model.get('name', selected_model.get('id', 'Unknown'))
                        logger.info(f"Using selected model endpoint: {model_endpoint} (Model: {model_name})")
                    else:
                        # Backward compatibility: fallback to secrets.toml endpoint
                        model_endpoint = get_replicate_model_endpoint()
                        model_name = "Default (from secrets.toml)"
                        logger.info(f"Using fallback endpoint: {model_endpoint} (selected_model not available)")
                        if selected_model is None:
                            st.warning("⚠️ No model selected. Using default endpoint from secrets.toml.")
                    
                    # Validate endpoint is not empty
                    if not model_endpoint or not isinstance(model_endpoint, str) or not model_endpoint.strip():
                        raise ValueError(f"Invalid model endpoint: {model_endpoint}. Cannot proceed with image generation.")
                    
                    # Calling the replicate API to get the image
                    with generated_images_placeholder.container():
                        logger.info(f"Calling Replicate API with model endpoint: {model_endpoint}")
                        all_images = []  # List to store all generated images
                        output = replicate.run(
                            model_endpoint,
                            input={
                                "prompt": prompt,
                                "width": width,
                                "height": height,
                                "num_outputs": num_outputs,
                                "scheduler": scheduler,
                                "num_inference_steps": num_inference_steps,
                                "guidance_scale": guidance_scale,
                                "prompt_strength": prompt_strength,
                                "refine": refine,
                                "high_noise_frac": high_noise_frac
                            }
                        )
                        if output:
                            st.toast(
                                'Your image has been generated!', icon='😍')
                            # Save generated image to session state
                            _set_session_state('generated_image', output)

                            # Displaying the image
                            for image in st.session_state.generated_image:
                                with st.container():
                                    # Convert FileOutput objects to URL strings
                                    # FileOutput objects have a .url attribute or can be converted with str()
                                    if hasattr(image, 'url'):
                                        image_url = image.url
                                    elif hasattr(image, '__str__'):
                                        image_url = str(image)
                                    else:
                                        image_url = image
                                    
                                    st.image(image_url, caption="Generated Image 🎈",
                                             use_container_width=True)
                                    # Add image URL to the list
                                    all_images.append(image_url)

                                    response = requests.get(image_url)
                        # Save all generated images to session state
                        _set_session_state('all_images', all_images)

                        # Create a BytesIO object
                        zip_io = io.BytesIO()

                        # Download option for each image
                        with zipfile.ZipFile(zip_io, 'w') as zipf:
                            for i, image in enumerate(st.session_state.all_images):
                                response = requests.get(image)
                                if response.status_code == 200:
                                    image_data = response.content
                                    # Write each image to the zip file with a name
                                    zipf.writestr(
                                        f"output_file_{i+1}.png", image_data)
                                else:
                                    st.error(
                                        f"Failed to fetch image {i+1} from {image}. Error code: {response.status_code}", icon="🚨")
                        # Create a download button for the zip file
                        st.download_button(
                            ":red[**Download All Images**]", data=zip_io.getvalue(), file_name="output_files.zip", mime="application/zip", use_container_width=True)
                status.update(label="✅ Images generated!",
                              state="complete", expanded=False)
            except ValueError as e:
                # Handle validation errors (missing endpoint, invalid endpoint)
                error_msg = str(e)
                selected_model = st.session_state.get('selected_model', None)
                model_name = selected_model.get('name', 'Unknown') if selected_model else 'Default'
                model_id = selected_model.get('id', 'unknown') if selected_model else 'unknown'
                logger.error(f"Validation error for model '{model_name}' (id: {model_id}): {error_msg}")
                st.error(
                    f'❌ **Configuration Error for Model "{model_name}"**\n\n'
                    f'{error_msg}\n\n'
                    'Please check your model configuration in models.yaml or secrets.toml.',
                    icon="🚨"
                )
                status.update(label="❌ Configuration Error", state="error", expanded=False)
            except KeyError as e:
                # Handle missing keys in selected_model
                error_msg = f"Missing required field in model configuration: {e}"
                selected_model = st.session_state.get('selected_model', None)
                model_name = selected_model.get('name', 'Unknown') if selected_model else 'Unknown'
                model_id = selected_model.get('id', 'unknown') if selected_model else 'unknown'
                logger.error(f"Configuration error for model '{model_name}' (id: {model_id}): {error_msg}")
                st.error(
                    f'❌ **Model Configuration Error for "{model_name}"**\n\n'
                    f'{error_msg}\n\n'
                    'Please check models.yaml to ensure all required fields (id, name, endpoint) are present.',
                    icon="🚨"
                )
                status.update(label="❌ Configuration Error", state="error", expanded=False)
            except requests.exceptions.RequestException as e:
                # Handle network errors
                error_msg = str(e)
                selected_model = st.session_state.get('selected_model', None)
                model_name = selected_model.get('name', 'Unknown') if selected_model else 'Default'
                model_id = selected_model.get('id', 'unknown') if selected_model else 'unknown'
                logger.error(f"Network error for model '{model_name}' (id: {model_id}): {error_msg}", exc_info=True)
                st.error(
                    f'❌ **Network Error with Model "{model_name}"**\n\n'
                    f'Unable to connect to the Replicate API: {error_msg}\n\n'
                    'Please check your internet connection and try again.',
                    icon="🚨"
                )
                status.update(label="❌ Network Error", state="error", expanded=False)
            except replicate.exceptions.ReplicateError as e:
                # Handle Replicate API-specific errors
                error_msg = str(e)
                selected_model = st.session_state.get('selected_model', None)
                model_name = selected_model.get('name', 'Unknown') if selected_model else 'Default'
                model_id = selected_model.get('id', 'unknown') if selected_model else 'unknown'
                logger.error(f"Replicate API error for model '{model_name}' (id: {model_id}): {error_msg}", exc_info=True)
                st.error(
                    f'❌ **Replicate API Error with Model "{model_name}"**\n\n'
                    f'{error_msg}\n\n'
                    'This may be due to authentication issues, invalid model endpoint, or API rate limits. '
                    'Please check your REPLICATE_API_TOKEN and model endpoint configuration.',
                    icon="🚨"
                )
                status.update(label="❌ API Error", state="error", expanded=False)
            except Exception as e:
                # Handle other API errors and unexpected exceptions
                error_msg = str(e)
                selected_model = st.session_state.get('selected_model', None)
                model_name = selected_model.get('name', 'Unknown') if selected_model else 'Default'
                model_id = selected_model.get('id', 'unknown') if selected_model else 'unknown'
                error_type = type(e).__name__
                logger.error(f"Unexpected error for model '{model_name}' (id: {model_id}): {error_type}: {error_msg}", exc_info=True)
                st.error(
                    f'❌ **Error Generating Image with Model "{model_name}"**\n\n'
                    f'Error type: {error_type}\n'
                    f'Error message: {error_msg}\n\n'
                    'Please try again or check your configuration. If the problem persists, check the logs for more details.',
                    icon="🚨"
                )
                status.update(label="❌ Generation Failed", state="error", expanded=False)

    # If not submitted, chill here 🍹
    else:
        pass

    # Gallery display for inspo
    with gallery_placeholder.container():
        img = image_select(
            label="Like what you see? Right-click and save! It's not stealing if we're sharing! 😉",
            images=[
                "gallery/helldiver-b01-tactical-armor1.png",
                "gallery/firebeardjones2.png",
                "gallery/starship-trooper-uniform-with-helmet1.webp",
            ],
            captions=[
                "FIREBEARDJONES wearing HELLDIVERB01TACTICALARMOR, standing on a moon like planet, helmet in hand, beard of fire.",
                "FIREBEARDJONES wearing a suit, full body",
                "a man wearing STARSHIPTROOPERUNIFORMWITHHELMET engaged in a fierce ball",
            ],
            use_container_width=True
        )


def main():
    """
    Main function to run the Streamlit application.

    This function:
    - Initializes session state for model management
    - Initializes the sidebar configuration
    - Sets up the main page layout
    - Retrieves user inputs from the sidebar and passes them to the main page function
    """
    # Initialize session state before UI rendering
    initialize_session_state()
    
    submitted, width, height, num_outputs, scheduler, num_inference_steps, guidance_scale, prompt_strength, refine, high_noise_frac, prompt, negative_prompt = configure_sidebar()
    main_page(submitted, width, height, num_outputs, scheduler, num_inference_steps,
              guidance_scale, prompt_strength, refine, high_noise_frac, prompt, negative_prompt)


if __name__ == "__main__":
    main()
