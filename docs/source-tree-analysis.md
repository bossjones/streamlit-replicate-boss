# streamlit-replicate-boss - Source Tree Analysis

**Date:** 2025-11-02

## Overview

This is a single-part Python web application built with Streamlit. The project follows a straightforward monolith structure with clear separation between application logic, utilities, configuration, and assets.

## Complete Directory Structure

```
streamlit-replicate-boss/
├── streamlit_app.py          # Main application entry point
├── main.py                   # Secondary entry point (simple hello script)
├── pyproject.toml            # Python project configuration and dependencies
├── Makefile                  # Development commands
├── README.md                 # Project documentation
├── LICENSE                   # License file
├── CLAUDE.md                 # Claude Code instructions
├── uv.lock                   # Dependency lock file
├── .streamlit/              # Streamlit configuration
│   ├── config.toml          # Streamlit theme and browser config
│   ├── secrets.toml         # API tokens and secrets (user-provided)
│   └── example_secrets.toml # Template for secrets configuration
├── utils/                   # Utility modules
│   ├── __init__.py         # Package initialization
│   └── icon.py             # Icon display utility function
├── gallery/                 # Static example images
│   ├── astro_on_unicorn.png
│   ├── cheetah.png
│   ├── farmer_sunset.png
│   ├── friends.png
│   ├── puppy.png
│   ├── viking.png
│   └── wizard.png
├── docs/                    # Generated documentation (output folder)
│   ├── bmm-workflow-status.yaml
│   └── stories/
├── bmad/                    # BMAD Method framework files
│   ├── _cfg/               # Configuration and manifests
│   ├── bmb/                # BMAD Builder module
│   ├── bmm/                # BMAD Method Module
│   ├── core/              # Core BMAD components
│   └── docs/             # BMAD documentation
├── ai_docs/               # AI-related documentation
├── logs/                  # Application logs
└── .envrc                 # Environment configuration
```

## Critical Directories

### `streamlit_app.py`

**Purpose:** Main application file and entry point  
**Contains:** 
- Streamlit application configuration
- Sidebar UI setup (`configure_sidebar()`)
- Main page logic (`main_page()`)
- Replicate API integration
- Image generation and download functionality

**Entry Points:** 
- `main()` function - Application bootstrap
- `if __name__ == "__main__"` - Direct execution entry

### `utils/`

**Purpose:** Shared utility functions  
**Contains:**
- `icon.py` - Streamlit icon display helper using emoji rendering

**Integration:** Imported by `streamlit_app.py` for UI utilities

### `.streamlit/`

**Purpose:** Streamlit framework configuration  
**Contains:**
- `config.toml` - Theme settings (light theme, monospace font, usage stats disabled)
- `secrets.toml` - API tokens and model endpoints (not in repo)
- `example_secrets.toml` - Template showing required secrets structure

**Integration:** Streamlit automatically loads configuration from this directory

### `gallery/`

**Purpose:** Static asset storage  
**Contains:** Pre-generated example images for inspiration and demonstration

**Integration:** Referenced by `streamlit_app.py` for gallery display using `streamlit-image-select`

## Entry Points

- **Main Entry:** `streamlit_app.py`
  - Execution: `streamlit run streamlit_app.py` or `make run`
  - Bootstrap: Streamlit framework handles HTTP server and routing

- **Secondary Entry:** `main.py`
  - Purpose: Simple test script (prints hello message)
  - Note: Not the primary application entry point

## File Organization Patterns

- **Application Code:** Root-level Python files (`streamlit_app.py`, `main.py`)
- **Utilities:** Grouped in `utils/` package
- **Configuration:** Centralized in `.streamlit/` directory
- **Assets:** Static files in `gallery/` directory
- **Documentation:** Generated docs in `docs/` folder

## Key File Types

### Python Application Files

- **Pattern:** `*.py`
- **Purpose:** Application logic and functionality
- **Examples:** `streamlit_app.py`, `utils/icon.py`, `main.py`

### Configuration Files

- **Pattern:** `*.toml`, `*.toml`, `Makefile`
- **Purpose:** Project settings, dependencies, and build configuration
- **Examples:** `pyproject.toml`, `.streamlit/config.toml`, `Makefile`

### Asset Files

- **Pattern:** `*.png`, `*.jpg`, etc.
- **Purpose:** Static images for gallery display
- **Examples:** `gallery/*.png`

## Asset Locations

- **Images**: `gallery/` (7 PNG files for example gallery)

## Configuration Files

- **`pyproject.toml`**: Python project metadata, dependencies (Streamlit, Replicate, etc.), Python version requirement (3.13+)
- **`.streamlit/config.toml`**: Streamlit UI configuration (theme: light, font: monospace, usage stats disabled)
- **`.streamlit/secrets.toml`**: API credentials (REPLICATE_API_TOKEN, REPLICATE_MODEL_ENDPOINTSTABILITY) - user-provided, not in repo
- **`Makefile`**: Development shortcuts (run command: `uv run streamlit run streamlit_app.py`)

## Notes for Development

- **Entry Point**: Always use `streamlit_app.py` as the main application file
- **Secrets Management**: Copy `.streamlit/example_secrets.toml` to `.streamlit/secrets.toml` and add API token
- **Package Management**: Use `uv` for dependency management (`uv sync` to install)
- **Running**: Use `make run` or direct `uv run streamlit run streamlit_app.py`
- **Configuration**: Streamlit auto-loads config from `.streamlit/` directory
- **Assets**: Add example images to `gallery/` directory for gallery feature
- **Utilities**: Add shared functions to `utils/` package following existing pattern

---

_Generated using BMAD Method `document-project` workflow_

