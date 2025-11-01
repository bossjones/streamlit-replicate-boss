# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Run the application
```bash
make run
# or directly:
uv run streamlit run streamlit_app.py
```

### Install dependencies
```bash
uv sync
```

### Python environment
- Python version: 3.13 (specified in `.python-version`)
- Package manager: uv
- Virtual environment: `.venv` (managed by uv)

## Architecture

This is a Streamlit web application that generates images using the Replicate API and Stability AI's SDXL model. The application architecture consists of:

### Core Components

1. **streamlit_app.py**: Main application file containing:
   - `configure_sidebar()`: Sets up user controls for image generation parameters (width, height, prompts, scheduler settings)
   - `main_page()`: Handles image generation via Replicate API, displays results, and manages batch downloads
   - Gallery display with pre-generated example images

2. **API Integration**:
   - Uses Replicate API with Stability AI's SDXL model endpoint
   - Requires `REPLICATE_API_TOKEN` and `REPLICATE_MODEL_ENDPOINTSTABILITY` in `.streamlit/secrets.toml`
   - Template provided in `.streamlit/example_secrets.toml`

3. **Key Dependencies**:
   - `streamlit`: Web framework
   - `replicate`: API client for model inference
   - `streamlit-image-select`: Image gallery component
   - `requests`: HTTP requests for image downloads

### Configuration

- Streamlit config: `.streamlit/config.toml` (theme settings, usage stats disabled)
- Secrets: `.streamlit/secrets.toml` (copy from `example_secrets.toml` and add API token)

### Image Generation Flow

1. User inputs parameters and prompt through sidebar form
2. Application calls Replicate API with SDXL model
3. Generated images displayed in container
4. Batch download available as ZIP file
5. Gallery shows example prompts and outputs for inspiration