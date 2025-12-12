# streamlit-replicate-boss Product Requirements Document (PRD)

**Author:** bossjones
**Date:** 2025-01-27
**Project Level:** 2
**Target Scale:** Level 2

---

## Goals and Background Context

### Goals

1. Enable seamless multi-model access — support multiple Replicate model endpoints (including custom models) in a unified interface
2. Eliminate context switching — allow model switching without leaving the application or losing workflow continuity
3. Automate configuration management — implement preset system to auto-apply model-specific settings (trigger words, optimal parameters)
4. Maximize custom model utilization — make custom-trained models (helldiver, starship-trooper, firebeardjones) as accessible as standard models

### Background Context

The application is currently hardcoded to a single Replicate model endpoint, forcing users to navigate between different Replicate pages to access different models. This breaks creative flow and wastes 2-5 minutes per model switch. Custom-trained models remain underutilized due to access friction. The solution transforms this into a flexible multi-model creative platform that preserves workflow continuity and maximizes the value of custom model investments through unified access and automated preset management.

---

## Requirements

### Functional Requirements

**Model Management & Configuration**

- FR001: The system must support multiple Replicate model endpoints, including standard models (e.g., Stability AI SDXL) and custom-trained models (helldiver, starship-trooper, firebeardjones)
- FR002: The system must load model configurations from a file-based storage system (YAML or JSON) at application startup
- FR003: Each model configuration must include: unique identifier, display name, Replicate endpoint URL, optional trigger words, and default parameter settings
- FR004: The system must provide a model selector UI component (dropdown/selectbox) in the sidebar that displays all available models
- FR005: The system must validate configuration file format and structure on load, providing clear error messages if invalid
- FR006: The system must select a default model on initial app load (first model in config or explicitly designated default)

**Model Switching & State Management**

- FR007: The system must allow users to switch between models instantly without page reload or navigation
- FR008: When switching models, the system must preserve the current prompt text and user-entered settings (width, height, scheduler, etc.)
- FR009: The system must update the UI to reflect the selected model, displaying model-specific information (trigger words, description) in the sidebar
- FR010: The system must handle model-specific parameter differences by showing/hiding relevant controls based on the selected model's supported parameters
- FR011: The system must persist the selected model in session state, maintaining selection across page interactions within the same session

**Preset Management**

- FR012: The system must support preset configurations that store trigger words and default settings per model
- FR013: The system must automatically load and apply a preset when a model is selected, injecting trigger words into the prompt field
- FR014: The system must allow users to manually override preset values (prompt, settings) after preset application
- FR015: The system must store presets in a file-based storage system (YAML or JSON) linked to models via model identifier
- FR016: The system must support at least one preset per model (default preset), with optional additional named presets per model

**Integration & API**

- FR017: The system must use the selected model's endpoint when making Replicate API calls for image generation
- FR018: The system must validate model endpoints before making API calls and provide user feedback for API errors
- FR019: The system must handle missing or invalid configuration files gracefully, with fallback to a default model if available, or clear error message if no models are configured
- FR020: The system must maintain backward compatibility with existing single-model configuration (secrets.toml) while supporting new multi-model configuration

**Implementation Dependencies:**

The functional requirements have the following critical dependency chain for implementation:

1. **Foundation Layer** (Must be implemented first):
   - FR002 (Config Load) → FR003 (Data Structure) → FR005 (Validation) → FR006 (Default Selection)
   - FR020 (Backward Compatibility) should be considered early to avoid refactoring

2. **Core Model Management** (Builds on foundation):
   - FR001 (Multi-model support) enabled by FR002/FR003
   - FR004 (Model Selector UI) depends on FR002/FR003/FR006

3. **State Management** (Enables switching):
   - FR011 (Session State) → FR007 (Model Switching) → FR008 (State Preservation)

4. **UI Updates** (Depends on switching):
   - FR009 (UI Reflection) and FR010 (Parameter Handling) depend on FR007

5. **Preset System** (Can be developed in parallel with switching):
   - FR015 (Preset Storage) → FR012 (Preset Support) → FR016 (Default Presets) → FR013 (Auto-apply) → FR014 (Manual Override)

6. **API Integration** (Final layer):
   - FR017 (Use Selected Endpoint) → FR018/FR019 (Error Handling)

**Critical Path:** FR002 → FR003 → FR005 → FR006 → FR011 → FR004 → FR007 → FR009 → FR015 → FR012 → FR013 → FR017

### Non-Functional Requirements

**Performance Requirements:**

- NFR001: Model switching must complete in less than 1 second without page reload or visible UI blocking
- NFR002: Configuration file loading at application startup must complete in less than 500ms, even with 10+ model definitions

**Reliability Requirements:**

- NFR003: The system must maintain data integrity during model switching, preserving all user-entered data (prompt, settings) without loss or corruption
- NFR004: The system must handle API failures gracefully, providing clear error messages to the user without crashing or losing application state

**Usability Requirements:**

- NFR005: The system must maintain workflow continuity, allowing users to switch models and continue creative work without external navigation or context re-establishment

---

## User Journeys

### Primary Use Case: Multi-Model Creative Workflow

**User:** bossjones (Creative professional using AI image generation)

**Goal:** Generate images using multiple custom models without leaving the application

**Journey Steps:**

1. **Application Launch**
   - User opens the Streamlit application
   - System loads model configurations and displays default model (e.g., Stability AI SDXL)
   - Model selector appears in sidebar with all available models

2. **Initial Model Selection**
   - User selects "helldiver tactical armor" from model dropdown
   - System instantly switches to selected model (<1 second)
   - Preset automatically loads: trigger words injected into prompt field, optimal settings applied
   - UI updates to show model-specific information (trigger words visible in sidebar)

3. **First Image Generation**
   - User reviews auto-populated prompt (with trigger words)
   - User adjusts prompt text and settings as needed
   - User clicks "Generate Image"
   - System uses helldiver model endpoint for API call
   - Generated image displays in main area

4. **Model Switch (Core Value)**
   - User wants to try different style, selects "starship trooper uniform" from dropdown
   - System instantly switches (<1 second, no page reload)
   - Current prompt text and settings are preserved
   - New preset auto-loads: starship trooper trigger words injected, settings updated
   - UI updates to reflect new model

5. **Continued Creative Work**
   - User adjusts prompt for starship trooper context
   - Generates image with new model
   - User switches to third model (firebeardjones) seamlessly
   - Creative workflow continues uninterrupted

6. **Session Completion**
   - User has generated images with multiple models
   - All work completed within single application session
   - No external navigation or context switching required

**Success Criteria:**
- ✅ Zero external navigation during creative session
- ✅ Model switching completes in <1 second
- ✅ All prompts and settings preserved across switches
- ✅ Presets auto-apply correctly for each model
- ✅ Workflow continuity maintained throughout session

---

## UX Design Principles

1. **Workflow Continuity First** - Eliminate context switching and maintain creative flow. All model-related actions should happen within the application without external navigation.

2. **Progressive Disclosure** - Present information in order of frequency and importance: Model selection → Preset → Prompt → Settings. Hide advanced options until needed.

3. **Context Preservation** - Always show active model configuration (model name, trigger words, preset) alongside prompt input so users understand what they're working with.

4. **Instant Feedback** - Model switching and preset application should provide immediate visual feedback (<1 second) with clear indication of what changed.

---

## User Interface Design Goals

### Platform & Screens

**Platform:** Web application (Streamlit) - Desktop and tablet browsers

**Core Screen Structure:**
- **Sidebar (Left):** Model selection, preset management, prompt inputs, generation controls, settings
- **Main Area (Right):** Generated images display, gallery for inspiration

### Information Architecture

**Sidebar Hierarchy (Top to Bottom):**

1. **Model Selection Section** (Top Priority - Always Visible)
   - Model selector dropdown (prominent placement)
   - Model information display (trigger words, description) - visible when model selected
   - Preset selector (if multiple presets available per model)

2. **Generation Controls** (Primary Actions)
   - Prompt input field (with auto-injected trigger words visible/editable)
   - Negative prompt input
   - Submit/Generate button (primary action)

3. **Settings Section** (Secondary - Collapsible)
   - Basic settings (width, height, num_outputs) - always visible
   - Advanced settings (scheduler, inference steps, guidance scale, etc.) - in expander

4. **Resources** (Tertiary - Bottom)
   - Model links and credits

### Key Interaction Patterns

- **Model Switching:** Dropdown selection → instant UI update → preset auto-applies → prompt updates with trigger words
- **Preset Application:** Automatic on model selection, with manual override capability
- **State Preservation:** All user inputs (prompt, settings) preserved during model switches
- **Visual Feedback:** Clear indication of active model, applied preset, and any auto-injected trigger words

### Design Constraints

- **Streamlit Framework Limitations:** Must work within Streamlit's component library and layout constraints
- **Browser Support:** Modern browsers (Chrome, Firefox, Safari, Edge) - latest 2 versions
- **No Custom CSS/JS:** Rely on Streamlit's native styling and components
- **Responsive Design:** Sidebar collapses on mobile, but primary use case is desktop/tablet

---

## Epic List

**Epic 1: Multi-Model Foundation & Configuration**
- **Goal:** Establish multi-model infrastructure with configuration loading, model selector, and basic switching capability
- **Estimated Stories:** 6-8 stories
- **Delivers:** File-based model configuration, model selector UI, basic model switching, session state management, API integration with selected model endpoint

**Epic 2: Preset System & Enhanced Model Switching**
- **Goal:** Implement preset management system with auto-application and enhanced model switching with state preservation
- **Estimated Stories:** 5-7 stories
- **Delivers:** Preset storage and loading, auto-apply presets, trigger word injection, enhanced UI updates, backward compatibility with existing single-model configuration

> **Note:** Detailed epic breakdown with full story specifications is available in [epics.md](./epics.md)

---

## Out of Scope

**Model Management Features:**
- Custom model management UI (add/edit models via form — MVP uses config file only)
- Model favorites/starring system
- Model search/filter by tags
- Model grouping/categories
- Model history tracking
- Model comparison mode (side-by-side generation)
- Batch generation across multiple models

**Preset Management Features:**
- Preset sharing/export functionality
- Preset marketplace
- Preset tags/categories
- Preset templates
- Settings diff view (compare current vs. saved preset)
- Version control for presets

**Discovery and Inspiration:**
- Example gallery per model (pull from Replicate)
- "Try this prompt" button
- Model preview cards
- Model metadata display (runs, cost, examples from Replicate)

**Advanced Features:**
- AI-powered preset recommendations
- Workflow templates
- Mobile/tablet optimized interface
- API access for programmatic image generation
- Integration with other AI platforms beyond Replicate

**Infrastructure:**
- Database for configuration storage (MVP uses file-based storage)
- Multi-user support (personal tool only)
- Authentication/user management
- Cloud storage for generated images

**Rationale:** MVP focuses on core functionality (model switching + presets). Advanced features can be added post-MVP based on usage patterns and needs.
