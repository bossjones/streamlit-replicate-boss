# streamlit-replicate-boss - Development Guide

**Date:** 2025-11-02

## Prerequisites

### Required Software

- **Python**: Version 3.13 or higher
- **uv**: Modern Python package manager (install from https://github.com/astral-sh/uv)
- **Replicate API Account**: Sign up at https://replicate.com and obtain API token

### System Requirements

- Operating System: macOS, Linux, or Windows
- Terminal/Command Line access
- Internet connection (for API calls and package installation)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd streamlit-replicate-boss
```

### 2. Install Dependencies

Using uv (recommended):

```bash
uv sync
```

This will:
- Create a virtual environment in `.venv/`
- Install all dependencies from `pyproject.toml`
- Lock dependencies in `uv.lock`

Using pip (alternative):

```bash
pip install -r requirements.txt
```

### 3. Configure Secrets

Copy the example secrets file:

```bash
cp .streamlit/example_secrets.toml .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and add your Replicate API token:

```toml
REPLICATE_API_TOKEN = "your-replicate-api-token-here"
REPLICATE_MODEL_ENDPOINTSTABILITY = "stability-ai/sdxl:2b017d9b67edd2ee1401238df49d75da53c523f36e363881e057f5dc3ed3c5b2"
```

**Note**: `.streamlit/secrets.toml` is excluded from version control for security.

## Environment Setup

### Virtual Environment

uv automatically manages the virtual environment in `.venv/`. To activate manually:

```bash
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

### Environment Variables

The application uses Streamlit's secrets management. No additional environment variables are required if using `.streamlit/secrets.toml`.

For alternative configuration, you can set environment variables:
- `REPLICATE_API_TOKEN`
- `REPLICATE_MODEL_ENDPOINTSTABILITY`

## Local Development

### Running the Application

**Using Make (recommended):**

```bash
make run
```

**Direct command:**

```bash
uv run streamlit run streamlit_app.py
```

**With pip/virtualenv:**

```bash
streamlit run streamlit_app.py
```

### Development Server

The Streamlit development server will:
- Start on `http://localhost:8501` by default
- Auto-reload on code changes
- Display logs in the terminal

### Accessing the Application

Open your browser and navigate to:
```
http://localhost:8501
```

## Build Process

This application does not require a build step. Streamlit runs Python code directly.

### Production Considerations

For production deployment, you may want to:
- Set Streamlit configuration for production
- Configure proper secrets management
- Set up proper error logging
- Consider containerization (Docker)

## Testing

### Current Test Status

No formal test suite is currently configured.

### Manual Testing

1. **UI Testing**: Verify all form controls work correctly
2. **API Testing**: Test image generation with various prompts
3. **Error Handling**: Test with invalid API tokens or network errors
4. **Gallery Testing**: Verify gallery images load and display

### Recommended Test Setup

Consider adding:
- Unit tests for utility functions (`utils/icon.py`)
- Integration tests for Replicate API calls (with mocking)
- UI tests using Streamlit testing utilities

**Example test structure:**
```
tests/
├── test_utils.py
├── test_api_integration.py
└── test_ui_components.py
```

## Common Development Tasks

### Adding New Parameters

1. Add input control in `configure_sidebar()` function
2. Include parameter in return tuple
3. Pass parameter to `main_page()` function
4. Add parameter to Replicate API call

### Modifying Gallery Images

1. Add image files to `/gallery/` directory
2. Update `image_select()` images array in `main_page()`
3. Add corresponding caption to captions array

### Changing UI Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
base = "light"  # or "dark"
font = "monospace"  # or "sans serif"
```

### Debugging

**Streamlit Debug Mode:**

Add to top of `streamlit_app.py`:

```python
import streamlit as st
st.debug = True  # Shows detailed errors
```

**Print Statements:**

Use `print()` for terminal debugging (visible in Streamlit logs).

**Streamlit Debugging:**

Use `st.write()` to display variable values in the UI.

## Development Workflow

### Code Changes

1. Make changes to Python files
2. Streamlit auto-reloads on save
3. Refresh browser to see changes

### Dependency Updates

```bash
uv sync  # Updates dependencies
uv lock  # Updates lock file
```

### Code Formatting

Consider adding a formatter (Black, Ruff) for consistent code style:

```bash
black streamlit_app.py
# or
ruff format streamlit_app.py
```

## Troubleshooting

### Application Won't Start

**Issue**: `ModuleNotFoundError`  
**Solution**: Run `uv sync` to install dependencies

**Issue**: `StreamlitCommandException`  
**Solution**: Verify `streamlit_app.py` exists and is valid Python

### API Errors

**Issue**: `KeyError: 'REPLICATE_API_TOKEN'`  
**Solution**: Verify `.streamlit/secrets.toml` exists with correct token

**Issue**: API call fails  
**Solution**: 
- Check internet connection
- Verify API token is valid
- Check Replicate API status

### Image Generation Issues

**Issue**: Images not generating  
**Solution**: 
- Check API token validity
- Verify model endpoint is correct
- Check network connectivity
- Review error messages in Streamlit UI

### Port Already in Use

**Issue**: `Port 8501 is already in use`  
**Solution**: 
- Stop other Streamlit instances
- Use custom port: `streamlit run streamlit_app.py --server.port 8502`

## Project Structure

See [source-tree-analysis.md](./source-tree-analysis.md) for detailed directory structure.

**Key Directories:**
- `streamlit_app.py`: Main application code
- `utils/`: Utility functions
- `.streamlit/`: Configuration files
- `gallery/`: Static assets
- `docs/`: Generated documentation

## Version Control

### Files to Commit

- Source code (`*.py`)
- Configuration templates (`*.toml` templates)
- Documentation (`README.md`, `docs/`)
- Dependencies (`pyproject.toml`, `uv.lock`)

### Files to Ignore (already in .gitignore)

- `.streamlit/secrets.toml` (contains API tokens)
- `.venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `*.pyc` (compiled Python files)

## Performance Optimization

### Current Performance Considerations

- **API Calls**: Synchronous blocking (consider async for better UX)
- **Image Downloads**: On-demand (no caching)
- **Gallery Loading**: Static files (fast)

### Optimization Opportunities

- Implement image caching for generated images
- Add async API calls for non-blocking operations
- Cache gallery images for faster loading
- Use `@st.cache_data` for expensive computations

## Deployment Preparation

### Pre-Deployment Checklist

- [ ] API tokens configured securely
- [ ] Dependencies locked (`uv.lock` up to date)
- [ ] Configuration files reviewed
- [ ] Error handling tested
- [ ] Documentation updated

### Deployment Options

- **Streamlit Cloud**: Direct GitHub deployment
- **Docker**: Containerized deployment
- **Cloud Platforms**: AWS, GCP, Azure with Python support
- **Traditional Hosting**: Any Python web hosting service

See [architecture.md](./architecture.md) for deployment architecture details.

---

_Generated using BMAD Method `document-project` workflow_

