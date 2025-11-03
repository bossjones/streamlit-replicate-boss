# streamlit-replicate-boss - Component Inventory

**Date:** 2025-11-02

## Overview

This document catalogs the UI components, functions, and reusable elements in the Streamlit application.

## Core Functions

### `configure_sidebar()`
**Location:** `streamlit_app.py:30-88`  
**Type:** UI Configuration Function  
**Purpose:** Sets up and displays the sidebar form with user input controls  
**Parameters:** None  
**Returns:** Tuple of 12 values: `(submitted, width, height, num_outputs, scheduler, num_inference_steps, guidance_scale, prompt_strength, refine, high_noise_frac, prompt, negative_prompt)`

**Components:**
- Form container (`st.form("my_form")`)
- Info message with emoji icon
- Expandable advanced settings section
- Number inputs for width/height
- Slider for number of outputs (1-4)
- Selectbox for scheduler type
- Slider for inference steps (1-500)
- Slider for guidance scale (1.0-50.0)
- Slider for prompt strength (0.0-1.0)
- Selectbox for refine style
- Slider for high noise fraction (0.0-1.0)
- Text areas for prompt and negative prompt
- Submit button
- Resource links section
- Social media credits

**Reusability:** Core UI component, called on every page load

### `main_page()`
**Location:** `streamlit_app.py:91-200`  
**Type:** Main Application Logic  
**Purpose:** Handles image generation, display, and download functionality  
**Parameters:** 12 form values from sidebar configuration

**Components:**
- Status indicator for image generation
- Replicate API integration
- Image display containers
- Batch download ZIP creation
- Gallery component with image selector

**Reusability:** Main page logic, executed when form is submitted

### `main()`
**Location:** `streamlit_app.py:203-213`  
**Type:** Application Entry Point  
**Purpose:** Orchestrates sidebar and main page components  
**Parameters:** None  
**Returns:** None

**Components:**
- Calls `configure_sidebar()` to get user inputs
- Passes inputs to `main_page()` for rendering

**Reusability:** Bootstrap function, called once on app load

## Utility Components

### `utils.icon.show_icon()`
**Location:** `utils/icon.py:4-15`  
**Type:** UI Utility Function  
**Purpose:** Displays emoji as large Notion-style page icon  
**Parameters:** `emoji` (str) - emoji name like ":balloon:"  
**Returns:** None (renders HTML directly)

**Implementation:**
- Uses `@st.cache_data` decorator for caching
- Renders large emoji (78px) using HTML span with custom styling
- Uses `unsafe_allow_html=True` for HTML rendering

**Reusability:** Utility function, used once at app startup

## Streamlit UI Components Used

### Form Components
- **`st.form()`**: Main form container for sidebar inputs
- **`st.form_submit_button()`**: Primary submit button with container width
- **`st.number_input()`**: Width and height controls
- **`st.slider()`**: Range inputs for outputs, steps, scales
- **`st.selectbox()`**: Dropdown selectors for scheduler and refine options
- **`st.text_area()`**: Multi-line text inputs for prompts
- **`st.expander()`**: Collapsible section for advanced settings
- **`st.info()`**: Informational message box

### Display Components
- **`st.image()`**: Displays generated images with captions
- **`st.status()`**: Status indicator during API calls
- **`st.toast()`**: Success notification when images generated
- **`st.error()`**: Error messages for failed operations
- **`st.empty()`**: Placeholder containers for dynamic content
- **`st.markdown()`**: Formatted text with emoji and HTML support
- **`st.divider()`**: Visual separator

### Download Components
- **`st.download_button()`**: ZIP file download button with custom styling

### Third-Party Components
- **`streamlit_image_select.image_select()`**: Image gallery selector component
  - Location: Gallery display section
  - Features: Image grid, captions, click-to-select
  - Configuration: `use_container_width=True` for responsive layout

## UI Layout Structure

```
Application Layout
├── Page Header
│   ├── Page Icon (emoji via utils.icon)
│   └── Title ("Text-to-Image Artistry Studio")
├── Sidebar (configure_sidebar)
│   ├── Form Container
│   │   ├── Info Message
│   │   ├── Advanced Settings (expandable)
│   │   │   ├── Width Input
│   │   │   ├── Height Input
│   │   │   ├── Output Count Slider
│   │   │   ├── Scheduler Selectbox
│   │   │   ├── Inference Steps Slider
│   │   │   ├── Guidance Scale Slider
│   │   │   ├── Prompt Strength Slider
│   │   │   ├── Refine Selectbox
│   │   │   └── High Noise Fraction Slider
│   │   ├── Prompt Text Area
│   │   ├── Negative Prompt Text Area
│   │   └── Submit Button
│   ├── Divider
│   └── Resources & Credits
└── Main Content (main_page)
    ├── Generated Images Container (dynamic)
    │   ├── Status Indicator (during generation)
    │   ├── Image Display (after generation)
    │   └── Download Button (ZIP)
    └── Gallery Container
        └── Image Selector Component
```

## Component Patterns

### State Management Pattern
- Uses `st.session_state` for client-side data persistence
- `st.session_state.generated_image`: Stores current generation result
- `st.session_state.all_images`: Accumulates images for batch download

### Dynamic Content Pattern
- Uses `st.empty()` containers for placeholder content
- Updates containers dynamically based on user actions
- Conditional rendering based on form submission state

### API Integration Pattern
- Synchronous API calls within status context
- Error handling with try-except blocks
- Toast notifications for user feedback

### Image Handling Pattern
- Downloads images via HTTP requests
- Creates ZIP archives in-memory using `io.BytesIO`
- Provides download button with ZIP data

## Reusable Elements

### Configuration Constants
- **`REPLICATE_API_TOKEN`**: Loaded from secrets
- **`REPLICATE_MODEL_ENDPOINTSTABILITY`**: Model endpoint from secrets
- **`replicate_text`, `replicate_link`, `replicate_logo`**: Resource metadata

### UI Placeholders
- **`generated_images_placeholder`**: Container for generated images
- **`gallery_placeholder`**: Container for gallery display

### Gallery Assets
- **Image Paths**: Defined in `image_select()` component
- **Captions**: Matching prompts for each example image
- **Location**: `/gallery/` directory with 7 example images

## Component Dependencies

```
streamlit_app.py
├── replicate (external library)
├── streamlit (framework)
├── requests (external library)
├── zipfile (standard library)
├── io (standard library)
└── utils.icon (local module)
    └── streamlit (framework)
```

## Design System

### Color Scheme
- **Theme**: Light mode (configured in `.streamlit/config.toml`)
- **Font**: Monospace
- **Accents**: Rainbow text effects (`:rainbow[...]`)
- **Emoji Icons**: Used extensively for visual communication

### Typography
- **Headings**: Markdown H1 with emoji and rainbow effects
- **Body**: Standard markdown formatting
- **Code**: Inline code backticks for technical terms

### Interaction Patterns
- **Form Submission**: Single submit button triggers entire generation flow
- **Loading States**: Status indicator with messages during API calls
- **Success Feedback**: Toast notification on completion
- **Error Feedback**: Error messages with emoji icons

## Notes for Extension

### Adding New UI Components
- Follow Streamlit component patterns
- Use `st.empty()` for dynamic content areas
- Leverage session state for data persistence
- Cache expensive operations with `@st.cache_data`

### Modifying Gallery
- Add images to `/gallery/` directory
- Update `image_select()` images and captions arrays
- Maintain caption-prompt correspondence

### Enhancing Forms
- Add new inputs within `configure_sidebar()` function
- Pass new values through to `main_page()` function
- Update API call parameters accordingly

---

_Generated using BMAD Method `document-project` workflow_

