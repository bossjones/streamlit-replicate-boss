import replicate
import streamlit as st
import requests
import zipfile
import io
import logging
import os
from utils import icon
from streamlit_image_select import image_select
from config.model_loader import load_models_config

logger = logging.getLogger(__name__)

# UI configurations
st.set_page_config(page_title="Replicate Image Generator",
                   page_icon=":bridge_at_night:",
                   layout="wide")
icon.show_icon(":foggy:")
st.markdown("# :rainbow[Text-to-Image Artistry Studio]")

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
    
    Only runs once per session to avoid re-initialization on reruns.
    """
    # Check if already initialized to avoid re-initialization on reruns
    if 'model_configs' in st.session_state and 'selected_model' in st.session_state:
        return
    
    try:
        # Load models from configuration
        models = load_models_config("models.yaml")
        
        # Initialize model_configs with loaded models
        st.session_state.model_configs = models
        
        # Handle empty models list
        if not models:
            logger.warning("No models found in configuration. Model selector will be disabled.")
            st.session_state.selected_model = None
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
        st.session_state.selected_model = default_model
        
        logger.info(f"Session state initialized successfully with {len(models)} model(s)")
        
    except FileNotFoundError:
        # Handle missing models.yaml
        logger.warning("models.yaml not found. Initializing with empty session state.")
        st.session_state.model_configs = []
        st.session_state.selected_model = None
        st.warning("⚠️ Model configuration file not found. Please ensure models.yaml exists at the project root.")
        
    except Exception as e:
        # Handle other errors (invalid YAML, invalid structure, etc.)
        logger.error(f"Error initializing session state: {e}")
        st.session_state.model_configs = []
        st.session_state.selected_model = None
        st.error(f"❌ Error loading model configuration: {e}")


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
            st.session_state.preserved_prompt = None
        if 'preserved_settings' not in st.session_state:
            st.session_state.preserved_settings = None
        
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
                                st.session_state.preserved_prompt = st.session_state.get('form_prompt')
                                st.session_state.preserved_settings = {
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
                                }
                        
                        # Update selected model
                        st.session_state.selected_model = new_selected_model
        
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
                    "Prompt strength when using img2img/inpaint(1.0 corresponds to full destruction of infomation in image)", 
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
                                "prompt_stregth": prompt_strength,
                                "refine": refine,
                                "high_noise_frac": high_noise_frac
                            }
                        )
                        if output:
                            st.toast(
                                'Your image has been generated!', icon='😍')
                            # Save generated image to session state
                            st.session_state.generated_image = output

                            # Displaying the image
                            for image in st.session_state.generated_image:
                                with st.container():
                                    st.image(image, caption="Generated Image 🎈",
                                             use_column_width=True)
                                    # Add image to the list
                                    all_images.append(image)

                                    response = requests.get(image)
                        # Save all generated images to session state
                        st.session_state.all_images = all_images

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
                logger.error(f"Validation error: {error_msg}")
                st.error(f'❌ Configuration Error: {error_msg}', icon="🚨")
                status.update(label="❌ Configuration Error", state="error", expanded=False)
            except KeyError as e:
                # Handle missing keys in selected_model
                error_msg = f"Missing required field in model configuration: {e}"
                logger.error(f"Configuration error: {error_msg}")
                selected_model = st.session_state.get('selected_model', None)
                model_name = selected_model.get('name', 'Unknown') if selected_model else 'Unknown'
                st.error(f'❌ Model Configuration Error for "{model_name}": {error_msg}. Please check models.yaml.', icon="🚨")
                status.update(label="❌ Configuration Error", state="error", expanded=False)
            except Exception as e:
                # Handle API errors and other exceptions
                error_msg = str(e)
                logger.error(f"API error: {error_msg}", exc_info=True)
                selected_model = st.session_state.get('selected_model', None)
                model_name = selected_model.get('name', 'Unknown') if selected_model else 'Default'
                st.error(f'❌ Error generating image with model "{model_name}": {error_msg}', icon="🚨")
                status.update(label="❌ Generation Failed", state="error", expanded=False)

    # If not submitted, chill here 🍹
    else:
        pass

    # Gallery display for inspo
    with gallery_placeholder.container():
        img = image_select(
            label="Like what you see? Right-click and save! It's not stealing if we're sharing! 😉",
            images=[
                "gallery/farmer_sunset.png", "gallery/astro_on_unicorn.png",
                "gallery/friends.png", "gallery/wizard.png", "gallery/puppy.png",
                "gallery/cheetah.png", "gallery/viking.png",
            ],
            captions=["A farmer tilling a farm with a tractor during sunset, cinematic, dramatic",
                      "An astronaut riding a rainbow unicorn, cinematic, dramatic",
                      "A group of friends laughing and dancing at a music festival, joyful atmosphere, 35mm film photography",
                      "A wizard casting a spell, intense magical energy glowing from his hands, extremely detailed fantasy illustration",
                      "A cute puppy playing in a field of flowers, shallow depth of field, Canon photography",
                      "A cheetah mother nurses her cubs in the tall grass of the Serengeti. The early morning sun beams down through the grass. National Geographic photography by Frans Lanting",
                      "A close-up portrait of a bearded viking warrior in a horned helmet. He stares intensely into the distance while holding a battle axe. Dramatic mood lighting, digital oil painting",
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
