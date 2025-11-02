# streamlit-replicate-boss - Project Overview

**Date:** 2025-11-02
**Type:** Web Application
**Architecture:** Single-Page Application (SPA) with Streamlit

## Executive Summary

This is a Streamlit web application that generates images using the Replicate API and Stability AI's SDXL model. The application provides an intuitive interface for users to create AI-generated images from text prompts, with customizable parameters for fine-tuning the generation process.

## Project Classification

- **Repository Type:** Monolith
- **Project Type(s):** Web (Python-based Streamlit)
- **Primary Language(s):** Python 3.13
- **Architecture Pattern:** Component-based Single-Page Application

## Technology Stack Summary

| Category | Technology | Version | Justification |
|----------|------------|---------|---------------|
| Runtime | Python | 3.13+ | Core language for Streamlit applications |
| Web Framework | Streamlit | ≥1.50.0 | Primary UI framework providing declarative interface |
| Package Manager | uv | Latest | Modern Python package manager for dependency management |
| API Client | replicate | ≥1.0.7 | Client library for Replicate API integration |
| HTTP Client | requests | ≥2.32.5 | For downloading generated images |
| UI Component | streamlit-image-select | ≥0.6.0 | Image gallery selector component |
| File Watching | watchdog | ≥6.0.0 | File system monitoring utility |
| AI Model | Stability AI SDXL | 2b017d9... | Text-to-image generation model via Replicate |

## Key Features

- **Text-to-Image Generation**: Transform text prompts into AI-generated images using Stability AI's SDXL model
- **Customizable Parameters**: Adjustable width, height, scheduler, inference steps, guidance scale, and more
- **Batch Generation**: Generate multiple images (1-4) from a single prompt
- **Image Gallery**: Curated collection of example images for inspiration
- **Batch Download**: Download all generated images as a ZIP file
- **Streamlit UI**: Clean, responsive interface with sidebar controls and main content area

## Architecture Highlights

- **Entry Point**: `streamlit_app.py` serves as the main application file
- **Component Structure**: Two main functions (`configure_sidebar()` and `main_page()`) handle UI and logic
- **State Management**: Uses Streamlit's session state for storing generated images
- **API Integration**: Direct integration with Replicate API for model inference
- **Asset Management**: Static image gallery stored in `/gallery` directory
- **Configuration**: Streamlit config and secrets managed via `.streamlit/` directory

## Development Overview

### Prerequisites

- Python 3.13 or higher
- uv package manager
- Replicate API token

### Getting Started

1. Install dependencies: `uv sync`
2. Configure secrets: Copy `.streamlit/example_secrets.toml` to `.streamlit/secrets.toml` and add API token
3. Run application: `make run` or `uv run streamlit run streamlit_app.py`

### Key Commands

- **Install:** `uv sync`
- **Dev:** `make run` or `uv run streamlit run streamlit_app.py`
- **Build:** N/A (no build step required)
- **Test:** N/A (no test suite detected)

## Repository Structure

```
streamlit-replicate-boss/
├── streamlit_app.py       # Main application entry point
├── utils/                 # Utility modules (icon display)
├── gallery/              # Static example images
├── .streamlit/           # Streamlit configuration and secrets
├── docs/                  # Generated documentation
├── pyproject.toml        # Project dependencies and metadata
└── Makefile              # Development commands
```

## Documentation Map

For detailed information, see:

- [index.md](./index.md) - Master documentation index
- [architecture.md](./architecture.md) - Detailed architecture
- [source-tree-analysis.md](./source-tree-analysis.md) - Directory structure
- [development-guide.md](./development-guide.md) - Development workflow

---

_Generated using BMAD Method `document-project` workflow_

