# streamlit-replicate-boss - Technical Specification

**Author:** bossjones
**Date:** 2025-01-27
**Project Level:** 2
**Project Type:** software
**Development Context:** brownfield

**Related Documents:**
- [Product Requirements Document (PRD)](./PRD.md) - Business requirements and user journeys
- [Epic Breakdown](./epics.md) - Detailed story breakdown and sequencing

---

## Source Tree Structure

### New Files to Create

```
streamlit-replicate-boss/
├── config/
│   ├── __init__.py                    # NEW: Config module initialization
│   └── model_loader.py                 # NEW: Model configuration loading and validation
├── presets.yaml                        # NEW: Preset configuration file (Epic 2)
└── utils/
    └── preset_manager.py               # NEW: Preset loading and application logic
```

### Files to Modify

```
streamlit-replicate-boss/
├── streamlit_app.py                    # MODIFY: Add model selector, switching, preset integration
├── models.yaml                         # EXISTS: Already created (Story 1.1), may need updates
└── .streamlit/
    └── secrets.toml                    # MODIFY: Maintain backward compatibility (optional)
```

### File Change Summary

**streamlit_app.py** - Major refactoring:
- Add model configuration loading at startup
- Add model selector UI component in sidebar
- Implement model switching with state preservation
- Integrate preset system (Epic 2)
- Update API calls to use selected model endpoint
- Add error handling for configuration and API failures

**config/model_loader.py** - New module:
- `load_models_config()` - Load and parse models.yaml
- `validate_model_config()` - Validate model structure
- `get_default_model()` - Determine default model selection
- `handle_config_errors()` - Error handling and fallback logic

**utils/preset_manager.py** - New module (Epic 2):
- `load_presets_config()` - Load and parse presets.yaml
- `get_preset_for_model()` - Retrieve preset by model_id
- `apply_preset()` - Apply preset trigger words and settings
- `merge_preset_with_user_input()` - Handle manual overrides

**presets.yaml** - New configuration file (Epic 2):
- YAML structure linking presets to models
- Default presets for each model
- Trigger words and default settings per preset

---

## Technical Approach

### Architecture Pattern

**Layered Architecture with Session State Management:**

1. **Configuration Layer** (Startup)
   - Load models.yaml at application startup
   - Validate configuration structure
   - Initialize session state with model data
   - Handle configuration errors gracefully

2. **UI Layer** (Sidebar)
   - Model selector dropdown (top of sidebar)
   - Model information display (trigger words, description)
   - Preset selector (if multiple presets per model - future enhancement)
   - Existing prompt and settings controls (preserved)

3. **State Management Layer** (Session State)
   - `st.session_state.selected_model` - Current model object
   - `st.session_state.model_configs` - All loaded models
   - `st.session_state.presets` - All loaded presets (Epic 2)
   - `st.session_state.preset_applied` - Track preset application state

4. **Business Logic Layer** (Functions)
   - Model switching logic with state preservation
   - Preset application logic (Epic 2)
   - API endpoint selection based on selected model

5. **Integration Layer** (API Calls)
   - Use selected model endpoint for Replicate API calls
   - Error handling for API failures
   - Backward compatibility with existing secrets.toml

### Implementation Strategy

**Epic 1 (Foundation):**
- Implement file-based model configuration loading
- Add model selector UI
- Implement basic model switching with state preservation
- Integrate selected model endpoint with API calls
- Add comprehensive error handling

**Epic 2 (Preset System):**
- Create preset configuration structure
- Implement preset loading and storage
- Add auto-apply preset on model selection
- Enable manual override of preset values
- Enhance UI updates for model switching

### State Preservation Strategy

When switching models:
1. Capture current prompt text → `st.session_state.current_prompt`
2. Capture current settings → `st.session_state.current_settings`
3. Update selected model → `st.session_state.selected_model`
4. Apply preset (if available) → Merge with preserved state
5. Update UI to reflect new model and preserved/preset values

### Backward Compatibility Strategy

1. Check for `models.yaml` existence
2. If missing, check `REPLICATE_MODEL_ENDPOINTSTABILITY` in secrets.toml
3. If found in secrets, create single-model config automatically
4. Fallback to existing hardcoded behavior if neither exists
5. Both configurations can coexist (secrets as fallback)

---

## Implementation Stack

### Core Dependencies (Existing)

- **Python:** 3.13 (specified in `.python-version` and `pyproject.toml`)
- **Streamlit:** 1.50.0+ (UI framework)
- **Replicate:** 1.0.7+ (API client for model inference)
- **PyYAML:** 6.0.1 (YAML parsing - needs to be added to dependencies)
- **Requests:** 2.32.5+ (HTTP requests for image downloads)

### New Dependencies to Add

```toml
# Add to pyproject.toml dependencies:
"pyyaml>=6.0.1",  # For parsing models.yaml and presets.yaml
```

### Configuration File Format

**models.yaml** (YAML format):
- Schema validation using Python dict structure
- Required fields: `id`, `name`, `endpoint`
- Optional fields: `trigger_words` (string or array), `default_settings` (object)
- File location: Project root (`{project-root}/models.yaml`)

**presets.yaml** (YAML format - Epic 2):
- Schema: `presets` array with `id`, `name`, `model_id`, `trigger_words`, `settings`
- File location: Project root (`{project-root}/presets.yaml`)

### Session State Structure

```python
# Model Management
st.session_state.model_configs = [
    {
        'id': 'sdxl',
        'name': 'Stability AI SDXL',
        'endpoint': 'stability-ai/sdxl:...',
        'trigger_words': [],
        'default_settings': {}
    },
    # ... more models
]

st.session_state.selected_model = {
    'id': 'sdxl',
    'name': 'Stability AI SDXL',
    'endpoint': 'stability-ai/sdxl:...',
    'trigger_words': [],
    'default_settings': {}
}

# Preset Management (Epic 2)
st.session_state.presets = {
    'sdxl': [
        {
            'id': 'default',
            'name': 'Default SDXL',
            'trigger_words': [],
            'settings': {'width': 1024, 'height': 1024}
        }
    ],
    # ... more presets by model_id
}

st.session_state.preset_applied = False  # Track if preset was auto-applied
```

---

## Technical Details

### Model Configuration Loading (Story 1.2)

**File:** `config/model_loader.py`

**Function:** `load_models_config(file_path: str = "models.yaml") -> List[Dict]`

**Implementation:**
1. Use `yaml.safe_load()` to parse YAML file
2. Validate structure: check for `models` key, ensure it's a list
3. Validate each model: required fields (`id`, `name`, `endpoint`) present
4. Handle errors:
   - FileNotFoundError → Return empty list, log warning, check secrets.toml fallback
   - yaml.YAMLError → Raise with descriptive message
   - ValidationError → Raise with specific field errors
5. Return list of model dictionaries
6. Performance: Complete in <500ms (NFR002)

**Function:** `validate_model_config(model: Dict) -> bool`

**Implementation:**
1. Check required fields: `id` (str), `name` (str), `endpoint` (str)
2. Validate endpoint format: contains `/` (basic format check)
3. Validate optional fields if present: `trigger_words` (str or list), `default_settings` (dict)
4. Return True if valid, raise ValueError with details if invalid

### Model Selector UI (Story 1.4)

**File:** `streamlit_app.py`

**Location:** Top of sidebar, before prompt input (in `configure_sidebar()` function)

**Implementation:**
```python
# In configure_sidebar() function, before prompt input:
if 'model_configs' in st.session_state and st.session_state.model_configs:
    model_options = {model['name']: model for model in st.session_state.model_configs}
    selected_model_name = st.selectbox(
        "Select Model",
        options=list(model_options.keys()),
        index=0 if 'selected_model' not in st.session_state else 
               next((i for i, m in enumerate(st.session_state.model_configs) 
                     if m['id'] == st.session_state.selected_model['id']), 0),
        key="model_selector"
    )
    st.session_state.selected_model = model_options[selected_model_name]
else:
    st.warning("No models configured. Please check models.yaml file.")
```

### Model Switching (Story 1.5)

**File:** `streamlit_app.py`

**Implementation:**
1. Model selector dropdown updates `st.session_state.selected_model` on change
2. Preserve current state:
   - `st.session_state.preserved_prompt = prompt` (before switch)
   - `st.session_state.preserved_settings = {...}` (before switch)
3. On model change:
   - Update `st.session_state.selected_model`
   - Trigger preset application (Epic 2) or restore preserved state
4. UI updates immediately via Streamlit's reactive framework
5. Performance: <1 second (NFR001) - achieved through session state, no API calls

### API Integration (Story 1.6)

**File:** `streamlit_app.py`

**Function:** `main_page()` - Modify API call

**Current Code:**
```python
output = replicate.run(
    REPLICATE_MODEL_ENDPOINTSTABILITY,  # HARDCODED
    input={...}
)
```

**New Code:**
```python
selected_endpoint = st.session_state.selected_model['endpoint']
output = replicate.run(
    selected_endpoint,  # DYNAMIC
    input={...}
)
```

**Error Handling:**
- If `selected_model` missing → Fallback to `REPLICATE_MODEL_ENDPOINTSTABILITY` from secrets
- If endpoint invalid → Show error message, don't crash
- If API fails → Show user-friendly error with model name

### Preset System (Epic 2)

**File:** `utils/preset_manager.py`

**Function:** `load_presets_config(file_path: str = "presets.yaml") -> Dict[str, List[Dict]]`

**Implementation:**
1. Load and parse presets.yaml using `yaml.safe_load()`
2. Validate structure: `presets` array, each with `id`, `name`, `model_id`, `trigger_words`, `settings`
3. Group presets by `model_id` for efficient lookup
4. Return dict: `{model_id: [preset1, preset2, ...]}`
5. Handle missing file gracefully (return empty dict, app still works)

**Function:** `apply_preset(model_id: str, preset: Dict, current_prompt: str, current_settings: Dict) -> Tuple[str, Dict]`

**Implementation:**
1. Extract trigger words from preset
2. Inject trigger words into prompt (prepend by default, configurable)
3. Merge preset settings with current settings (preset values override)
4. Return updated prompt and settings
5. Set `st.session_state.preset_applied = True`

**Auto-Apply Logic (Story 2.4):**
- Triggered on model selection change
- Find preset for selected model (default preset if multiple exist)
- Apply preset to prompt and settings
- Visual indication: Show info message or update UI

### Error Handling (Story 1.7)

**Configuration Errors:**
- Missing `models.yaml`: Show warning, check secrets.toml, create single-model config
- Invalid YAML: Show error with line number, suggest fix
- Missing required fields: Show specific field names, suggest schema
- Invalid endpoint format: Show model name and endpoint, suggest correct format

**API Errors:**
- Invalid endpoint: Show model name, suggest checking endpoint URL
- API failure: Show user-friendly message, preserve application state
- Network errors: Show retry suggestion, maintain UI state

**Error Display:**
- Use `st.error()` for critical errors
- Use `st.warning()` for non-critical issues
- Log errors to console for debugging
- Never crash application - always provide fallback

---

## Development Setup

### Prerequisites

1. **Python 3.13** (already configured in `.python-version`)
2. **uv** package manager (already in use)
3. **Existing dependencies** installed via `uv sync`

### Setup Steps

1. **Install new dependency:**
   ```bash
   uv add pyyaml>=6.0.1
   ```

2. **Create config module:**
   ```bash
   mkdir -p config
   touch config/__init__.py
   ```

3. **Create preset manager module:**
   ```bash
   touch utils/preset_manager.py
   ```

4. **Verify models.yaml exists:**
   - Already created (Story 1.1)
   - Location: `{project-root}/models.yaml`
   - Contains at least 3 models: sdxl, helldiver, starship-trooper

5. **Create presets.yaml (Epic 2):**
   - Location: `{project-root}/presets.yaml`
   - Structure defined in Story 2.1

### Development Environment

- **IDE:** Any Python IDE (VS Code, PyCharm, etc.)
- **Testing:** Manual testing in Streamlit (run `uv run streamlit run streamlit_app.py`)
- **Version Control:** Git (already initialized)
- **Package Management:** uv (already configured)

---

## Implementation Guide

### Implementation Sequence (Follow Epic Order)

**Epic 1: Multi-Model Foundation**

1. **Story 1.2:** Create `config/model_loader.py` with `load_models_config()` and `validate_model_config()`
2. **Story 1.3:** Initialize session state in `streamlit_app.py` main() function
3. **Story 1.4:** Add model selector UI to `configure_sidebar()` function
4. **Story 1.5:** Implement model switching logic (preserve state, update session state)
5. **Story 1.6:** Modify API call in `main_page()` to use selected model endpoint
6. **Story 1.7:** Add comprehensive error handling throughout

**Epic 2: Preset System**

1. **Story 2.1:** Create `presets.yaml` file with default presets for each model
2. **Story 2.2:** Create `utils/preset_manager.py` with `load_presets_config()`
3. **Story 2.3:** Add model information display to sidebar
4. **Story 2.4:** Implement auto-apply preset on model selection
5. **Story 2.5:** Allow manual override of preset values
6. **Story 2.6:** Implement backward compatibility with secrets.toml
7. **Story 2.7:** Enhance UI updates for model switching

### Code Organization

**Module Structure:**
```
streamlit_app.py          # Main application, UI, orchestration
config/
  __init__.py            # Config module
  model_loader.py        # Model configuration loading
utils/
  __init__.py            # Utils module (exists)
  preset_manager.py      # Preset management (Epic 2)
```

**Function Responsibilities:**
- `main()` - Application entry point, initialize session state
- `configure_sidebar()` - UI setup, model selector, form inputs
- `main_page()` - Image generation logic, API calls
- `load_models_config()` - Configuration loading (config/model_loader.py)
- `apply_preset()` - Preset application (utils/preset_manager.py)

### Testing Strategy

**Manual Testing Checklist:**
1. Application starts with models.yaml loaded
2. Model selector displays all models
3. Model switching works instantly
4. Prompt and settings preserved on switch
5. API calls use selected model endpoint
6. Error handling works for missing/invalid config
7. Backward compatibility with secrets.toml works
8. Presets auto-apply on model selection (Epic 2)
9. Manual override of presets works (Epic 2)

**Test Scenarios:**
- Normal flow: Select model → Generate image → Switch model → Generate again
- Error scenarios: Missing models.yaml, invalid YAML, missing required fields
- Edge cases: Empty models list, rapid model switching, API failures
- Backward compatibility: No models.yaml, only secrets.toml

---

## Testing Approach

### Unit Testing (Recommended but not required for MVP)

**Test Files to Create:**
- `tests/test_model_loader.py` - Test configuration loading and validation
- `tests/test_preset_manager.py` - Test preset loading and application

**Test Cases:**
- Valid models.yaml loads correctly
- Invalid YAML raises appropriate error
- Missing required fields raises validation error
- Preset application merges correctly with user input
- Backward compatibility fallback works

### Integration Testing

**Manual Integration Tests:**
1. Start application → Verify models load
2. Select model → Verify UI updates
3. Generate image → Verify correct endpoint used
4. Switch model → Verify state preservation
5. Apply preset → Verify trigger words injected (Epic 2)

### Performance Testing

**Performance Requirements (from PRD):**
- NFR001: Model switching <1 second ✅ (Achieved via session state)
- NFR002: Config loading <500ms ✅ (Achieved via efficient YAML parsing)

**Validation:**
- Measure config load time (should be <500ms)
- Measure model switch time (should be <1 second, no API calls)
- Profile YAML parsing if performance issues arise

---

## Deployment Strategy

### Deployment Steps

1. **Update Dependencies:**
   ```bash
   uv sync  # Installs pyyaml>=6.0.1
   ```

2. **Deploy Configuration Files:**
   - `models.yaml` → Deploy to production root directory
   - `presets.yaml` → Deploy to production root directory (Epic 2)

3. **Deploy Code Changes:**
   - `streamlit_app.py` → Updated with model selector and switching
   - `config/model_loader.py` → New module
   - `utils/preset_manager.py` → New module (Epic 2)

4. **Verify Backward Compatibility:**
   - If `models.yaml` missing, app should fallback to secrets.toml
   - Existing single-model behavior should still work

### Migration Path

**For Existing Users:**
1. App continues to work with existing secrets.toml
2. User can optionally create `models.yaml` to enable multi-model
3. Both configurations can coexist (secrets as fallback)

**For New Users:**
1. Create `models.yaml` with desired models
2. App automatically uses multi-model configuration
3. No secrets.toml required (unless using single-model fallback)

### Rollback Plan

**If Issues Arise:**
1. Remove `models.yaml` → App falls back to secrets.toml
2. Revert `streamlit_app.py` to previous version
3. Remove new modules (`config/`, `utils/preset_manager.py`)

**Backward Compatibility Ensures:**
- Existing deployments continue to work
- No breaking changes for single-model users
- Gradual migration possible

---

## Technical Decisions

### Decision: YAML for Configuration

**Rationale:**
- Human-readable and editable
- Supports comments (important for documentation)
- Easy to version control
- Python has excellent YAML support (PyYAML)

**Alternatives Considered:**
- JSON: Less readable, no comments
- TOML: Good but less common for nested structures
- Database: Overkill for MVP, file-based is simpler

### Decision: Session State for Model Management

**Rationale:**
- Streamlit's built-in state management
- Persists across page interactions
- No external dependencies
- Simple and reliable

**Alternatives Considered:**
- Cookies: More complex, browser-dependent
- URL parameters: Visible, not ideal for model IDs
- External state management: Unnecessary complexity

### Decision: Preset Auto-Application

**Rationale:**
- Maximizes workflow continuity (PRD goal)
- Reduces manual entry (user value)
- Can be overridden manually (flexibility)

**Alternatives Considered:**
- Manual preset selection: More steps, less seamless
- No presets: Doesn't meet PRD requirements
- Preset templates: Future enhancement, not MVP

---

## Dependencies on PRD Requirements

This technical specification implements the following PRD requirements:

**Functional Requirements:**
- FR001: Multi-model support → Model configuration loading
- FR002: File-based config → `models.yaml` and `config/model_loader.py`
- FR003: Model config structure → Defined in models.yaml schema
- FR004: Model selector UI → `configure_sidebar()` model selector
- FR005: Config validation → `validate_model_config()` function
- FR006: Default model → `get_default_model()` function
- FR007: Model switching → Model switching logic in `streamlit_app.py`
- FR008: State preservation → State preservation in model switching
- FR009: UI updates → UI update logic on model switch
- FR010: Parameter handling → Settings update based on model/preset
- FR011: Session persistence → Session state management
- FR012-FR016: Preset system → `utils/preset_manager.py` and presets.yaml
- FR017: API integration → Modified API call in `main_page()`
- FR018-FR020: Error handling and compatibility → Comprehensive error handling

**Non-Functional Requirements:**
- NFR001: Model switching <1 second → Achieved via session state
- NFR002: Config loading <500ms → Efficient YAML parsing
- NFR003: Data integrity → State preservation logic
- NFR004: Error handling → Comprehensive error handling
- NFR005: Workflow continuity → Preset auto-application

---

## Next Steps

1. **Review this tech spec** with development team
2. **Begin Epic 1 implementation** following story sequence
3. **Test each story** before proceeding to next
4. **Proceed to Epic 2** after Epic 1 completion
5. **Update workflow status** after tech-spec completion

**Related Documents:**
- [PRD](./PRD.md) - Business requirements
- [Epic Breakdown](./epics.md) - Story details and sequencing
- [Workflow Status](./bmm-workflow-status.yaml) - Project tracking
