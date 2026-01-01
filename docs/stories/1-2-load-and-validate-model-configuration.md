# Story 1.2: Load and Validate Model Configuration

Status: drafted

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

- [ ] Task 1: Create config module structure (AC: 1)
  - [ ] Create `config/` directory at project root
  - [ ] Create `config/__init__.py` to make it a Python package
  - [ ] Create `config/model_loader.py` module file
  - [ ] Testing: Verify module can be imported

- [ ] Task 2: Install PyYAML dependency (AC: 1, 2)
  - [ ] Add `pyyaml>=6.0.1` to `pyproject.toml` dependencies
  - [ ] Run `uv sync` to install dependency
  - [ ] Verify PyYAML can be imported in Python
  - [ ] Testing: Import yaml module successfully

- [ ] Task 3: Implement load_models_config() function (AC: 1, 2, 5)
  - [ ] Create `load_models_config(file_path: str = "models.yaml") -> List[Dict]` function
  - [ ] Use `yaml.safe_load()` to parse YAML file
  - [ ] Validate structure: check for `models` key, ensure it's a list
  - [ ] Validate each model: required fields (`id`, `name`, `endpoint`) present
  - [ ] Return list of model dictionaries
  - [ ] Testing: Test with valid models.yaml file

- [ ] Task 4: Implement validate_model_config() function (AC: 2)
  - [ ] Create `validate_model_config(model: Dict) -> bool` function
  - [ ] Check required fields: `id` (str), `name` (str), `endpoint` (str)
  - [ ] Validate endpoint format: contains `/` (basic format check)
  - [ ] Validate optional fields if present: `trigger_words` (str or list), `default_settings` (dict)
  - [ ] Return True if valid, raise ValueError with details if invalid
  - [ ] Testing: Test with valid and invalid model configs

- [ ] Task 5: Implement error handling for missing file (AC: 3)
  - [ ] Handle FileNotFoundError when models.yaml doesn't exist
  - [ ] Return empty list or raise descriptive error
  - [ ] Log warning message appropriately
  - [ ] Check secrets.toml fallback (for backward compatibility - Story 1.7)
  - [ ] Testing: Test with missing models.yaml file

- [ ] Task 6: Implement error handling for invalid YAML (AC: 4)
  - [ ] Handle yaml.YAMLError exceptions
  - [ ] Provide descriptive error message with line number if available
  - [ ] Log error appropriately
  - [ ] Testing: Test with invalid YAML syntax

- [ ] Task 7: Implement error handling for invalid structure (AC: 4)
  - [ ] Handle missing `models` key
  - [ ] Handle `models` not being a list
  - [ ] Handle missing required fields in model objects
  - [ ] Provide specific field error messages
  - [ ] Testing: Test with various invalid structure scenarios

- [ ] Task 8: Ensure performance requirement (AC: 6)
  - [ ] Measure configuration loading time
  - [ ] Optimize if needed (efficient YAML parsing, minimal validation overhead)
  - [ ] Verify loading completes in <500ms with 10+ models
  - [ ] Testing: Performance test with multiple models

- [ ] Task 9: Implement logging (AC: 7)
  - [ ] Log successful configuration load with model count
  - [ ] Log warnings for missing file or fallback scenarios
  - [ ] Log errors for invalid YAML or structure
  - [ ] Use appropriate log levels (info, warning, error)
  - [ ] Testing: Verify logs appear correctly

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

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
