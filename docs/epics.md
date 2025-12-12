# streamlit-replicate-boss - Epic Breakdown

**Author:** bossjones
**Date:** 2025-01-27
**Project Level:** 2
**Target Scale:** Level 2

---

## Overview

This document provides the detailed epic breakdown for streamlit-replicate-boss, expanding on the high-level epic list in the [PRD](./PRD.md).

Each epic includes:

- Expanded goal and value proposition
- Complete story breakdown with user stories
- Acceptance criteria for each story
- Story sequencing and dependencies

**Epic Sequencing Principles:**

- Epic 1 establishes foundational infrastructure and initial functionality
- Subsequent epics build progressively, each delivering significant end-to-end value
- Stories within epics are vertically sliced and sequentially ordered
- No forward dependencies - each story builds only on previous work

---

## Epic 1: Multi-Model Foundation & Configuration

**Expanded Goal:** Establish the foundational infrastructure for multi-model support by implementing file-based model configuration, model selector UI, basic model switching capability, and API integration. This epic delivers the core capability to select and use different Replicate models within the application, eliminating the hardcoded single-model limitation.

**Value Proposition:** Users can now access multiple AI image generation models (including custom-trained models) from a unified interface, setting the foundation for seamless model switching and preset management in Epic 2.

**Story Breakdown:**

### Story 1.1: Create Model Configuration File Structure

As a developer,
I want a standardized configuration file format for defining multiple models,
So that models can be easily added and managed without code changes.

**Acceptance Criteria:**
1. Create `models.yaml` file in project root with YAML structure
2. Define schema: `models` array with items containing `id`, `name`, `endpoint`, `trigger_words` (optional), `default_settings` (optional)
3. Include at least 3 models: Stability AI SDXL (existing), helldiver, starship-trooper
4. File structure is valid YAML and follows defined schema
5. Document configuration format in comments or README

**Prerequisites:** None (foundation story)

---

### Story 1.2: Load and Validate Model Configuration

As a user,
I want the application to load model configurations at startup,
So that all available models are ready to use when I open the app.

**Acceptance Criteria:**
1. Create function to load `models.yaml` file at application startup
2. Parse YAML and validate structure (required fields present, valid types)
3. Handle missing file gracefully with clear error message
4. Handle invalid YAML/format with descriptive error messages
5. Store loaded models in memory (list/dict structure)
6. Configuration loading completes in <500ms (NFR002)
7. Log successful load or errors appropriately

**Prerequisites:** Story 1.1

---

### Story 1.3: Initialize Session State for Model Management

As a user,
I want my model selection to persist during my session,
So that I don't lose my selection when interacting with the app.

**Acceptance Criteria:**
1. Initialize `st.session_state.selected_model` on first app load
2. Set default model (first model from config or explicitly designated)
3. Initialize `st.session_state.model_configs` with loaded model data
4. Session state persists across page interactions (form submissions, etc.)
5. Handle session state initialization edge cases (missing config, empty models)

**Prerequisites:** Story 1.2

---

### Story 1.4: Create Model Selector UI Component

As a user,
I want to see and select from available models in the sidebar,
So that I can choose which model to use for image generation.

**Acceptance Criteria:**
1. Add model selector dropdown/selectbox to sidebar (top of form, before prompt)
2. Display all models from configuration with their display names
3. Show currently selected model in dropdown
4. Model selector is always visible (not in expander)
5. UI updates immediately when selection changes
6. Handle empty model list gracefully (show message, disable selector)

**Prerequisites:** Story 1.3

---

### Story 1.5: Implement Basic Model Switching

As a user,
I want to switch between models instantly,
So that I can use different models without leaving the application.

**Acceptance Criteria:**
1. Model selection in dropdown updates `st.session_state.selected_model`
2. Switching happens instantly (<1 second, NFR001) without page reload
3. Current prompt and settings are preserved when switching (FR008)
4. UI reflects selected model (dropdown shows current selection)
5. Switching works reliably across multiple rapid selections
6. Handle edge cases: switching before config loads, invalid model selection

**Prerequisites:** Story 1.4

---

### Story 1.6: Integrate Selected Model Endpoint with API Calls

As a user,
I want image generation to use the selected model's endpoint,
So that I can generate images with different models.

**Acceptance Criteria:**
1. Modify API call to use `st.session_state.selected_model['endpoint']` instead of hardcoded endpoint
2. API call uses correct model endpoint for selected model
3. Generated images display correctly for all models
4. Error handling for invalid/missing endpoint
5. Maintain backward compatibility: if no model selected, fallback to default or existing behavior
6. Test with at least 2 different models (standard + custom)

**Prerequisites:** Story 1.5

---

### Story 1.7: Handle Configuration Errors and Edge Cases

As a user,
I want clear error messages when something goes wrong,
So that I understand what happened and how to fix it.

**Acceptance Criteria:**
1. Display user-friendly error messages for:
   - Missing `models.yaml` file
   - Invalid YAML syntax
   - Missing required fields in model config
   - Invalid model endpoint format
   - API errors when using selected model
2. Provide fallback behavior: if config fails, use existing single-model behavior (backward compatibility)
3. Errors don't crash the application
4. Error messages are visible in UI (not just console)
5. Log errors appropriately for debugging

**Prerequisites:** Story 1.6

---

## Epic 2: Preset System & Enhanced Model Switching

**Expanded Goal:** Implement a comprehensive preset management system that automatically applies model-specific configurations (trigger words, default settings) when models are selected. Enhance model switching with state preservation and UI updates to show model-specific information. This epic delivers the full value proposition of seamless model switching with automated configuration management.

**Value Proposition:** Users can now switch between models with presets automatically applied, eliminating manual re-entry of trigger words and optimal settings. This maximizes workflow continuity and makes custom models as easy to use as standard models.

**Story Breakdown:**

### Story 2.1: Create Preset Configuration File Structure

As a developer,
I want a standardized preset configuration format,
So that model-specific settings can be stored and automatically applied.

**Acceptance Criteria:**
1. Create `presets.yaml` file with structure linking presets to models via `model_id`
2. Define schema: `presets` array with items containing `id`, `name`, `model_id`, `trigger_words`, `settings`
3. Create at least one default preset for each model (helldiver, starship-trooper, Stability AI SDXL)
4. Preset structure supports trigger words and default parameter values
5. File structure is valid YAML and follows defined schema

**Prerequisites:** Epic 1 complete (needs model configuration structure)

---

### Story 2.2: Load and Store Preset Configurations

As a user,
I want presets to be available when I select a model,
So that optimal settings are ready to apply automatically.

**Acceptance Criteria:**
1. Create function to load `presets.yaml` at application startup
2. Parse and validate preset structure
3. Store presets in `st.session_state.presets` linked by `model_id`
4. Handle missing preset file gracefully (no presets, but app still works)
5. Handle invalid preset format with clear error messages
6. Preset loading completes efficiently (<500ms)

**Prerequisites:** Story 2.1

---

### Story 2.3: Display Model Information in Sidebar

As a user,
I want to see information about the selected model,
So that I understand what model I'm using and its trigger words.

**Acceptance Criteria:**
1. Display selected model name prominently in sidebar (below model selector)
2. Show model trigger words if available (from model config or preset)
3. Display model description if provided in config
4. Model info updates immediately when model selection changes
5. Handle models without trigger words/description gracefully
6. Information is clearly visible but doesn't clutter the UI

**Prerequisites:** Story 1.5 (model switching)

---

### Story 2.4: Auto-Apply Preset on Model Selection

As a user,
I want presets to automatically load when I select a model,
So that I don't have to manually enter trigger words and settings each time.

**Acceptance Criteria:**
1. When model is selected, find matching preset by `model_id`
2. If preset found, apply preset settings:
   - Inject trigger words into prompt field (prepend or append based on preset config)
   - Apply default parameter values (width, height, scheduler, etc.) from preset
3. Preset application happens automatically (<1 second)
4. User can see that preset was applied (visual indication)
5. Handle models without presets gracefully (no preset applied, use defaults)
6. Preset application doesn't overwrite user-entered values if user has already customized

**Prerequisites:** Story 2.2, Story 2.3

---

### Story 2.5: Allow Manual Override of Preset Values

As a user,
I want to modify preset values after they're applied,
So that I can customize settings for my specific needs.

**Acceptance Criteria:**
1. User can edit prompt field even after trigger words are auto-injected
2. User can modify any setting (width, height, scheduler, etc.) after preset applies
3. Manual changes persist when switching models and switching back
4. Preset values don't re-apply automatically after manual override (until model switch)
5. Clear visual distinction between preset-applied values and user-modified values (optional enhancement)

**Prerequisites:** Story 2.4

---

### Story 2.6: Implement Backward Compatibility with Existing Configuration

As a user,
I want the app to still work with my existing single-model setup,
So that I can migrate gradually without breaking current functionality.

**Acceptance Criteria:**
1. If `models.yaml` doesn't exist, check for `REPLICATE_MODEL_ENDPOINTSTABILITY` in secrets.toml
2. If found, create single-model configuration automatically from secrets
3. App functions normally with single model from secrets (no errors)
4. User can add `models.yaml` later to enable multi-model without code changes
5. Migration path is documented
6. Both configurations can coexist (secrets as fallback)

**Prerequisites:** Story 1.6 (API integration)

---

### Story 2.7: Enhanced UI Updates for Model Switching

As a user,
I want the UI to clearly show what changed when I switch models,
So that I understand the current configuration state.

**Acceptance Criteria:**
1. When model switches, update all relevant UI elements:
   - Model selector shows new selection
   - Model info section updates
   - Prompt field updates with new trigger words (if preset applied)
   - Settings update if preset has different defaults
2. UI updates are smooth and immediate (<1 second)
3. Visual feedback indicates model switch occurred (optional: brief message/toast)
4. All UI elements stay in sync with selected model state
5. Handle rapid model switching gracefully (no UI flicker or state confusion)

**Prerequisites:** Story 2.4, Story 2.5

---

## Story Guidelines Reference

**Story Format:**

```
**Story [EPIC.N]: [Story Title]**

As a [user type],
I want [goal/desire],
So that [benefit/value].

**Acceptance Criteria:**
1. [Specific testable criterion]
2. [Another specific criterion]
3. [etc.]

**Prerequisites:** [Dependencies on previous stories, if any]
```

**Story Requirements:**

- **Vertical slices** - Complete, testable functionality delivery
- **Sequential ordering** - Logical progression within epic
- **No forward dependencies** - Only depend on previous work
- **AI-agent sized** - Completable in 2-4 hour focused session
- **Value-focused** - Integrate technical enablers into value-delivering stories

---

**For implementation:** Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown.
