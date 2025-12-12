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

{{non_functional_requirements}}

---

## User Journeys

{{user_journeys}}

---

## UX Design Principles

{{ux_principles}}

---

## User Interface Design Goals

{{ui_design_goals}}

---

## Epic List

{{epic_list}}

> **Note:** Detailed epic breakdown with full story specifications is available in [epics.md](./epics.md)

---

## Out of Scope

{{out_of_scope}}
