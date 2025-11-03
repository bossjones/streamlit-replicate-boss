# streamlit-replicate-boss - Architecture Documentation

**Date:** 2025-11-02  
**Project Type:** Web Application  
**Architecture Pattern:** Component-based Single-Page Application

## Executive Summary

This application is a Streamlit-based web application that provides a text-to-image generation interface using Stability AI's SDXL model via the Replicate API. It follows a simple, monolithic architecture with clear separation between UI configuration, business logic, and API integration.

## Technology Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| Runtime | Python | 3.13+ | Core application runtime |
| Web Framework | Streamlit | ≥1.50.0 | UI framework and HTTP server |
| Package Manager | uv | Latest | Dependency management |
| API Client | replicate | ≥1.0.7 | Replicate API integration |
| HTTP Client | requests | ≥2.32.5 | Image downloading |
| UI Component | streamlit-image-select | ≥0.6.0 | Image gallery component |
| AI Model | Stability AI SDXL | 2b017d9... | Text-to-image generation |

## Architecture Pattern

### Single-Page Application (SPA) Architecture

The application uses Streamlit's declarative framework to create a reactive single-page interface:

1. **Page Configuration**: Set via `st.set_page_config()` at application startup
2. **Sidebar Configuration**: User input form and controls in left sidebar
3. **Main Content Area**: Dynamic content based on user interactions
4. **State Management**: Streamlit's session state for client-side data persistence

### Component Structure

```
Application Entry (streamlit_app.py)
├── Page Configuration
│   └── st.set_page_config()
├── Icon Display
│   └── utils.icon.show_icon()
├── Sidebar Configuration
│   └── configure_sidebar()
│       ├── Form inputs (width, height, prompts, etc.)
│       └── Resource links
└── Main Page
    └── main_page()
        ├── Image Generation Logic
        │   └── Replicate API call
        └── Gallery Display
            └── streamlit-image-select component
```

## Data Architecture

### State Management

The application uses Streamlit's session state to manage client-side data:

- **`st.session_state.generated_image`**: Stores generated image URL(s) from API
- **`st.session_state.all_images`**: List of all generated images for batch download

### Data Flow

1. **User Input** → Sidebar form collects parameters
2. **Form Submission** → Triggers API call with parameters
3. **API Response** → Image URL(s) returned
4. **State Update** → URLs stored in session state
5. **UI Update** → Images displayed and download options shown

### External Data Sources

- **Replicate API**: Image generation endpoint
  - Endpoint: Stability AI SDXL model (`stability-ai/sdxl:2b017d9b67edd2ee1401238df49d75da53c523f36e363881e057f5dc3ed3c5b2`)
  - Authentication: API token from `.streamlit/secrets.toml`
  - Input: Text prompts, generation parameters
  - Output: Image URL(s)

## API Design

### External API Integration

**Replicate API Integration:**

- **Library**: `replicate` Python client
- **Authentication**: Token-based via `st.secrets["REPLICATE_API_TOKEN"]`
- **Model Endpoint**: Configured via `st.secrets["REPLICATE_MODEL_ENDPOINTSTABILITY"]`

**API Call Pattern:**

```python
output = replicate.run(
    REPLICATE_MODEL_ENDPOINTSTABILITY,
    input={
        "prompt": str,
        "width": int,
        "height": int,
        "num_outputs": int,
        "scheduler": str,
        "num_inference_steps": int,
        "guidance_scale": float,
        "prompt_stregth": float,  # Note: typo in code ("stregth" not "strength")
        "refine": str,
        "high_noise_frac": float
    }
)
```

**Request Parameters:**
- `prompt`: Text description of desired image
- `negative_prompt`: Elements to avoid in image
- `width`, `height`: Output dimensions (default: 1024x1024)
- `num_outputs`: Number of images (1-4)
- `scheduler`: Denoising scheduler algorithm
- `num_inference_steps`: Number of denoising steps (1-500)
- `guidance_scale`: Classifier-free guidance scale (1.0-50.0)
- `prompt_strength`: Image-to-image strength (0.0-1.0)
- `refine`: Refiner style (e.g., "expert_ensemble_refiner")
- `high_noise_frac`: Noise fraction for refiner (0.0-1.0)

**Response:**
- Returns list of image URL strings
- URLs point to generated images on Replicate CDN

## Component Overview

### Core Functions

**`configure_sidebar()`**
- **Purpose**: Setup sidebar UI with form inputs
- **Returns**: Tuple of form values (submitted flag, parameters)
- **Features**: 
  - Expandable advanced settings
  - Number inputs, sliders, selectboxes, text areas
  - Resource links and credits section

**`main_page()`**
- **Purpose**: Main application logic and image display
- **Parameters**: All form values from sidebar
- **Features**:
  - Conditional image generation on form submission
  - Status display during API call
  - Image display with captions
  - Batch download as ZIP file
  - Image gallery with selectable examples

**`utils.icon.show_icon()`**
- **Purpose**: Display emoji icon as Notion-style page icon
- **Implementation**: Cached function using Streamlit's cache decorator
- **Style**: Large emoji (78px) with HTML rendering

## Source Tree

See [source-tree-analysis.md](./source-tree-analysis.md) for complete directory structure.

**Key Files:**
- `streamlit_app.py`: Main application (218 lines)
- `utils/icon.py`: Icon utility (15 lines)
- `.streamlit/config.toml`: Streamlit configuration
- `gallery/`: Static example images

## Development Workflow

See [development-guide.md](./development-guide.md) for detailed setup and development instructions.

**Quick Start:**
```bash
uv sync              # Install dependencies
make run             # Start development server
```

**Configuration:**
- Copy `.streamlit/example_secrets.toml` to `.streamlit/secrets.toml`
- Add Replicate API token and model endpoint

## Deployment Architecture

### Local Development

- **Server**: Streamlit development server (auto-started)
- **Port**: Default 8501 (configurable)
- **Hot Reload**: Enabled for code changes

### Potential Deployment Options

- **Streamlit Cloud**: Direct deployment from GitHub
- **Docker**: Containerize with Streamlit base image
- **Cloud Platforms**: Deploy to any platform supporting Python web apps

### Configuration Requirements

- **Environment Variables**: Replicate API token
- **Secrets Management**: `.streamlit/secrets.toml` (not committed to repo)

## Testing Strategy

**Current State:**
- No formal test suite detected
- Manual testing via Streamlit UI

**Recommendations:**
- Unit tests for utility functions (`utils/icon.py`)
- Integration tests for Replicate API calls (with mock)
- UI component tests for Streamlit widgets

## Security Considerations

- **API Tokens**: Stored in `.streamlit/secrets.toml` (excluded from version control)
- **Input Validation**: Streamlit provides built-in input validation for form fields
- **Error Handling**: Try-except blocks around API calls
- **User Data**: Session state is client-side only (no persistent storage)

## Performance Considerations

- **API Calls**: Synchronous blocking calls (consider async for multiple requests)
- **Image Download**: Downloads images on-demand for ZIP creation
- **Caching**: Icon display function uses `@st.cache_data` decorator
- **Gallery**: Static images loaded from local filesystem

## Known Issues & Technical Debt

- **Typo in Code**: Parameter name `prompt_stregth` should be `prompt_strength` (line 131)
- **No Error Recovery**: Failed API calls display error but don't retry
- **No Loading States**: Gallery loads synchronously
- **No Image Caching**: Generated images always downloaded fresh

## Future Architecture Considerations

- **Async API Calls**: Use async/await for non-blocking image generation
- **Image Caching**: Cache generated images locally to reduce API calls
- **User Preferences**: Store user parameter preferences in session state
- **Multi-model Support**: Allow switching between different Replicate models
- **History Tracking**: Store generation history in session state or database

---

_Generated using BMAD Method `document-project` workflow_

