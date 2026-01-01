# streamlit-replicate-boss
Using Replicate to build Streamlit app for image generations!





# ✨ Image Generation App ✨

[![Streamlit Replicate Image App](https://github.com/tonykipkemboi/streamlit-replicate-img-app/actions/workflows/python-app.yml/badge.svg)](https://github.com/tonykipkemboi/streamlit-replicate-img-app/actions/workflows/python-app.yml)

_Image Generator App: where art meets algorithms and dreams meet pixels!_ 🚀

![Astronaut on a unicorn](./gallery/astro_on_unicorn.png)

## Overview

Powered by cutting-edge AI models running on [Replicate](https://replicate.com/about) and wrapped in a Streamlit interface, this app lets you transform plain text prompts into mesmerizing visual masterpieces.

## Technical Features

- **Neural Model**: Leverages the power of the replicate.run model for image generation, providing detailed and accurate depictions.
- **Streamlit Framework**: Built atop the versatile Streamlit library, ensuring a smooth and responsive UI/UX.
- **Dynamic Customization**: You can peek "under the hood", tune hyperparameters like guidance_scale, prompt_strength, and more for fine-grained control.
- **Gallery**: A curated gallery for inspiration, showcasing the prowess of the underlying model.

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/tonykipkemboi/streamlit-replicate-img-app.git
   ```

2. Navigate to the project directory:

   ```bash
   cd streamlit-replicate-img-app
   ```

3. Install the dependencies:

   ```python
   pip install -r requirements.txt
   ```

4. Rename the `.streamlit/example_secrets.toml` file to `.streamlit/secrets.toml`.

5. Paste your Replicate API token in the secrets.toml file:

   ```bash
   REPLICATE_API_TOKEN = "paste-your-replicate-api-token-here"
   ```

## Model Configuration

The application supports multiple AI image generation models configured via `models.yaml` in the project root.

### Adding Models

To add a new model, edit `models.yaml` and add a new entry to the `models` array:

```yaml
models:
  - id: "your-model-id"           # Required: Unique identifier
    name: "Your Model Name"        # Required: Display name
    endpoint: "owner/model:version"  # Required: Replicate API endpoint
    trigger_words: []              # Optional: Model-specific trigger words
    default_settings: {}           # Optional: Default parameter values
```

**Required Fields:**
- `id`: Unique string identifier (e.g., "sdxl", "helldiver")
- `name`: Display name shown in the UI
- `endpoint`: Replicate API endpoint in format `owner/model:version`

**Optional Fields:**
- `trigger_words`: String or array of trigger words to prepend/append to prompts
- `default_settings`: Object with default parameter values (width, height, etc.)

**Example:**
```yaml
- id: "custom-model"
  name: "My Custom Model"
  endpoint: "username/model-name:version-hash"
  trigger_words: ["custom", "style"]
  default_settings:
    width: 1024
    height: 1024
```

See `models.yaml` for the current model configuration and schema documentation.

## Backward Compatibility & Migration

The application maintains **full backward compatibility** with existing single-model setups using `secrets.toml`. This allows you to migrate gradually from the old configuration to the new multi-model system.

### How It Works

1. **Fallback Detection**: If `models.yaml` doesn't exist, the app automatically checks for `REPLICATE_MODEL_ENDPOINTSTABILITY` in `.streamlit/secrets.toml`.

2. **Automatic Configuration**: If found, the app creates a single-model configuration automatically from your secrets file.

3. **Seamless Operation**: The app functions normally with the fallback configuration - no errors, no crashes, full functionality.

4. **Easy Migration**: You can add `models.yaml` at any time to enable multi-model support. The app automatically switches from fallback to `models.yaml` when the file is present.

### Migration Path

#### Step 1: Current Setup (Using secrets.toml)

Your current `.streamlit/secrets.toml` configuration:

```toml
REPLICATE_API_TOKEN = "your-api-token"
REPLICATE_MODEL_ENDPOINTSTABILITY = "stability-ai/sdxl:version-hash"
```

The app works perfectly with this setup. No changes needed!

#### Step 2: Create models.yaml (Optional - When Ready)

When you're ready to use multiple models, create `models.yaml` in the project root:

```yaml
models:
  - id: "sdxl"
    name: "Stability AI SDXL"
    endpoint: "stability-ai/sdxl:version-hash"
    default: true
  - id: "another-model"
    name: "Another Model"
    endpoint: "owner/model:version"
```

**That's it!** The app automatically detects `models.yaml` and uses it instead of the fallback. No code changes needed.

#### Step 3: Both Configurations Can Coexist

- **Priority**: `models.yaml` takes precedence when both exist
- **Fallback**: `secrets.toml` is only used when `models.yaml` is missing
- **No Conflicts**: Both configurations can coexist without issues

### Benefits

- ✅ **Zero Downtime**: Migrate at your own pace
- ✅ **No Breaking Changes**: Existing setups continue to work
- ✅ **Automatic Detection**: App handles configuration switching automatically
- ✅ **Flexible**: Use either configuration or both

### Example Scenarios

**Scenario 1: New Installation**
- Create `models.yaml` → App uses multi-model configuration
- Don't create `models.yaml` → App uses fallback from `secrets.toml`

**Scenario 2: Existing Installation**
- Keep using `secrets.toml` → App continues working as before
- Add `models.yaml` later → App automatically switches to multi-model

**Scenario 3: Both Exist**
- `models.yaml` present → App uses `models.yaml` (takes precedence)
- `models.yaml` missing → App falls back to `secrets.toml`

## Usage

1. Run the Streamlit app:

   ```python
   streamlit run streamlit_app.py
   ```

2. Navigate to the provided local URL, and voila! Start crafting your visual narratives.

## Contributions

Your insights can make this tool even better! Feel free to fork, make enhancements, and raise a PR.

## Attribution

- **Developed by**: The wizards over at [Stability AI](https://stability.ai/) 🧙‍♂️

- **Model type**: Diffusion-based text-to-image generative model

- **License**: [CreativeML Open RAIL++-M License](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/LICENSE.md)

- **Model Description**: This is a model that can be used to generate and modify images based on text prompts. It is a [Latent Diffusion Model](https://arxiv.org/abs/2112.10752) that uses two fixed, pretrained text encoders ([OpenCLIP-ViT/G](https://github.com/mlfoundations/open_clip) and [CLIP-ViT/L](https://github.com/openai/CLIP/tree/main)).

- **Resources for more information**: Check out our [GitHub Repository](https://github.com/Stability-AI/generative-models) and the [SDXL report on arXiv](https://arxiv.org/abs/2307.01952).
