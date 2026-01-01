# Story 1.2: Load and Validate Model Configuration

Status: review

## Story

As a user,
I want the application to load model configurations at startup,
So that all available models are ready to use when I open the app.

## Acceptance Criteria

1. Create function to load `models.yaml` file at application startup
2. Parse YAML and validate structure (required fields present, valid types)
3. Handle missing file gracefully with clear error message
4. Handle invalid YAML/format with descriptive error messages
5. Store loaded models in memory (list/dict structure)
6. Configuration loading completes in <500ms (NFR002)
7. Log successful load or errors appropriately

## Tasks / Subtasks

- [x] Task 1: Create config module structure (AC: 1)
  - [x] Create `config/` directory at project root
  - [x] Create `config/__init__.py` to make it a Python package
  - [x] Create `config/model_loader.py` module file
  - [x] Testing: Verify module can be imported

- [x] Task 2: Install PyYAML dependency (AC: 1, 2)
  - [x] Add `pyyaml>=6.0.1` to `pyproject.toml` dependencies
  - [x] Run `uv sync` to install dependency
  - [x] Verify PyYAML can be imported in Python
  - [x] Testing: Import yaml module successfully

- [x] Task 3: Implement load_models_config() function (AC: 1, 2, 5)
  - [x] Create `load_models_config(file_path: str = "models.yaml") -> List[Dict]` function
  - [x] Use `yaml.safe_load()` to parse YAML file
  - [x] Validate structure: check for `models` key, ensure it's a list
  - [x] Validate each model: required fields (`id`, `name`, `endpoint`) present
  - [x] Return list of model dictionaries
  - [x] Testing: Test with valid models.yaml file

- [x] Task 4: Implement validate_model_config() function (AC: 2)
  - [x] Create `validate_model_config(model: Dict) -> bool` function
  - [x] Check required fields: `id` (str), `name` (str), `endpoint` (str)
  - [x] Validate endpoint format: contains `/` (basic format check)
  - [x] Validate optional fields if present: `trigger_words` (str or list), `default_settings` (dict)
  - [x] Return True if valid, raise ValueError with details if invalid
  - [x] Testing: Test with valid and invalid model configs

- [x] Task 5: Implement error handling for missing file (AC: 3)
  - [x] Handle FileNotFoundError when models.yaml doesn't exist
  - [x] Return empty list or raise descriptive error
  - [x] Log warning message appropriately
  - [x] Check secrets.toml fallback (for backward compatibility - Story 1.7)
  - [x] Testing: Test with missing models.yaml file

- [x] Task 6: Implement error handling for invalid YAML (AC: 4)
  - [x] Handle yaml.YAMLError exceptions
  - [x] Provide descriptive error message with line number if available
  - [x] Log error appropriately
  - [x] Testing: Test with invalid YAML syntax

- [x] Task 7: Implement error handling for invalid structure (AC: 4)
  - [x] Handle missing `models` key
  - [x] Handle `models` not being a list
  - [x] Handle missing required fields in model objects
  - [x] Provide specific field error messages
  - [x] Testing: Test with various invalid structure scenarios

- [x] Task 8: Ensure performance requirement (AC: 6)
  - [x] Measure configuration loading time
  - [x] Optimize if needed (efficient YAML parsing, minimal validation overhead)
  - [x] Verify loading completes in <500ms with 10+ models
  - [x] Testing: Performance test with multiple models

- [x] Task 9: Implement logging (AC: 7)
  - [x] Log successful configuration load with model count
  - [x] Log warnings for missing file or fallback scenarios
  - [x] Log errors for invalid YAML or structure
  - [x] Use appropriate log levels (info, warning, error)
  - [x] Testing: Verify logs appear correctly

## Dev Notes

### Learnings from Previous Story

**From Story 1-1-create-model-configuration-file-structure (Status: done)**

- **New File Created**: `models.yaml` at project root with complete schema documentation - use this file for loading [Source: stories/1-1-create-model-configuration-file-structure.md#File-List]
- **Schema Structure**: Models array with required fields (`id`, `name`, `endpoint`) and optional fields (`trigger_words`, `default_settings`) - validate against this structure [Source: stories/1-1-create-model-configuration-file-structure.md#Acceptance-Criteria]
- **Validation Script**: `validate_models_yaml.py` exists at project root - can reference validation logic, but will need PyYAML installed first [Source: stories/1-1-create-model-configuration-file-structure.md#Completion-Notes-List]
- **Model Entries**: 4 models configured (sdxl, helldiver, starship-trooper, firebeardjones) - all have required fields present [Source: models.yaml:23-49]
- **Architectural Pattern**: File-based configuration at project root, YAML format for human-readability - follow this pattern [Source: stories/1-1-create-model-configuration-file-structure.md#Architecture-Patterns-and-Constraints]

### Architecture Patterns and Constraints

- **Configuration Module**: Create `config/` module at project root following tech spec structure. Module should contain `model_loader.py` with loading and validation functions. [Source: docs/tech-spec.md#Source-Tree-Structure]

- **YAML Parsing**: Use `yaml.safe_load()` from PyYAML library for secure YAML parsing. This prevents arbitrary code execution that `yaml.load()` could allow. [Source: docs/tech-spec.md#Model-Configuration-Loading-(Story-1.2)]

- **Error Handling Strategy**: Handle errors gracefully with clear messages. Missing file should check secrets.toml fallback (for backward compatibility, though full implementation is in Story 1.7). Invalid YAML should provide line numbers if available. [Source: docs/tech-spec.md#Error-Handling-(Story-1.7)]

- **Performance Requirement**: Configuration loading must complete in <500ms (NFR002). Use efficient YAML parsing and minimal validation overhead. [Source: docs/PRD.md#Non-Functional-Requirements]

- **Session State**: While not implemented in this story, the loaded models will be stored in `st.session_state.model_configs` in Story 1.3. This story should return a list/dict structure ready for session state storage. [Source: docs/tech-spec.md#Session-State-Structure]

- **Backward Compatibility**: Consider checking `REPLICATE_MODEL_ENDPOINTSTABILITY` in secrets.toml if models.yaml is missing, though full backward compatibility implementation is deferred to Story 1.7. [Source: docs/tech-spec.md#Backward-Compatibility-Strategy]

### Project Structure Notes

- **Module Location**: Create `config/` directory at project root (`{project-root}/config/`), not in `utils/` or elsewhere. This follows the tech spec structure. [Source: docs/tech-spec.md#Source-Tree-Structure]

- **File Path**: Default path for `models.yaml` should be project root (`models.yaml` or `{project-root}/models.yaml`). Function should accept file_path parameter for flexibility. [Source: docs/tech-spec.md#Model-Configuration-Loading-(Story-1.2)]

- **Dependency Management**: Add PyYAML to `pyproject.toml` using `uv add pyyaml>=6.0.1`. This ensures proper dependency management. [Source: docs/tech-spec.md#New-Dependencies-to-Add]

### References

- Epic breakdown and story requirements: [Source: docs/epics.md#Story-1.2]
- PRD functional requirements for model configuration loading: [Source: docs/PRD.md#Model-Management--Configuration]
- Tech spec implementation details: [Source: docs/tech-spec.md#Model-Configuration-Loading-(Story-1.2)]
- Architecture documentation: [Source: docs/architecture.md#Data-Architecture]
- Previous story implementation: [Source: stories/1-1-create-model-configuration-file-structure.md]

## Change Log

- 2026-01-01: Story drafted
- 2026-01-01: Story implementation completed - All tasks finished, all tests passing, ready for review

## Dev Agent Record

### Context Reference

- docs/stories/1-2-load-and-validate-model-configuration.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

**Implementation Summary:**
- Created `config/` module at project root with `__init__.py` and `model_loader.py`
- Installed PyYAML 6.0.3 dependency via `uv sync`
- Implemented `load_models_config()` function with comprehensive error handling:
  - Handles missing file with descriptive FileNotFoundError
  - Handles invalid YAML syntax with line number information
  - Validates structure (models key, list type, required fields)
  - Returns List[Dict] structure ready for session state storage
- Implemented `validate_model_config()` function for individual model validation:
  - Validates required fields (id, name, endpoint) and types
  - Validates endpoint format (contains '/')
  - Validates optional fields (trigger_words, default_settings) if present
- Performance verified: Loading completes in <500ms with 15+ models (tested)
- Logging implemented with appropriate levels (info for success, warning for missing file, error for validation failures)
- Comprehensive test suite created: 19 tests covering all acceptance criteria, all passing
- All acceptance criteria satisfied and tested

### File List

**New Files:**
- `config/__init__.py` - Package initialization
- `config/model_loader.py` - Model loading and validation functions
- `tests/test_model_loader.py` - Comprehensive test suite (19 tests)

**Modified Files:**
- `pyproject.toml` - Added pyyaml>=6.0.1 and pytest>=8.0.0 dependencies
- `docs/sprint-status.yaml` - Updated story status from ready-for-dev to in-progress, then to review
