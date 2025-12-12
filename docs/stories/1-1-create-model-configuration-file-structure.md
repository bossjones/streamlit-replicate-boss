# Story 1.1: Create Model Configuration File Structure

Status: drafted

## Story

As a developer,
I want a standardized configuration file format for defining multiple models,
So that models can be easily added and managed without code changes.

## Acceptance Criteria

1. Create `models.yaml` file in project root with YAML structure
2. Define schema: `models` array with items containing `id`, `name`, `endpoint`, `trigger_words` (optional), `default_settings` (optional)
3. Include at least 3 models: Stability AI SDXL (existing), helldiver, starship-trooper
4. File structure is valid YAML and follows defined schema
5. Document configuration format in comments or README

## Tasks / Subtasks

- [ ] Task 1: Create models.yaml file structure (AC: 1, 2)
  - [ ] Create `models.yaml` file in project root directory
  - [ ] Define YAML structure with `models` array as root element
  - [ ] Define schema documentation in file comments or separate README section
  - [ ] Ensure YAML syntax is valid and follows standard YAML 1.2 specification
  - [ ] Testing: Verify YAML file parses without errors using Python yaml library

- [ ] Task 2: Define model schema with required and optional fields (AC: 2)
  - [ ] Define required fields: `id` (string, unique identifier), `name` (string, display name), `endpoint` (string, Replicate API endpoint)
  - [ ] Define optional fields: `trigger_words` (string or array, model-specific trigger words), `default_settings` (object, default parameter values)
  - [ ] Document field types and constraints in comments
  - [ ] Testing: Validate schema structure matches requirements

- [ ] Task 3: Add initial model configurations (AC: 3)
  - [ ] Add Stability AI SDXL model entry with endpoint from existing secrets.toml configuration
  - [ ] Add helldiver model entry with appropriate endpoint
  - [ ] Add starship-trooper model entry with appropriate endpoint
  - [ ] Ensure each model has unique `id` value
  - [ ] Testing: Verify all 3 models are present and have required fields

- [ ] Task 4: Validate YAML structure and schema compliance (AC: 4)
  - [ ] Verify YAML file is syntactically valid (no parse errors)
  - [ ] Verify all models have required fields (id, name, endpoint)
  - [ ] Verify optional fields use correct data types if present
  - [ ] Testing: Create validation script or manual check to ensure schema compliance

- [ ] Task 5: Document configuration format (AC: 5)
  - [ ] Add inline comments in models.yaml explaining schema structure
  - [ ] OR create/update README.md with configuration format documentation
  - [ ] Include examples of model entries
  - [ ] Document how to add new models following the schema
  - [ ] Testing: Verify documentation is clear and complete

## Dev Notes

### Architecture Patterns and Constraints

- **File-based Configuration**: Following PRD requirement FR002, configuration uses YAML file storage rather than database. This aligns with the MVP scope and simplifies deployment. [Source: docs/PRD.md#Model-Management--Configuration]

- **YAML Format**: YAML chosen for human-readability and ease of editing. Python's `yaml` library (likely via PyYAML) will be used for parsing. [Source: docs/architecture.md#Data-Architecture]

- **Project Root Location**: File should be placed in project root (`{project-root}/models.yaml`) to match standard configuration file conventions and ensure easy discovery. [Source: docs/epics.md#Story-1.1]

- **Schema Design**: Schema must support current requirements (id, name, endpoint) while allowing extensibility for future features (trigger_words, default_settings). Optional fields enable progressive enhancement without breaking existing configurations. [Source: docs/epics.md#Story-1.1]

- **Backward Compatibility Consideration**: While not required in this story, the schema design should anticipate Epic 2's backward compatibility requirements (FR020) where existing secrets.toml configuration may need to coexist. [Source: docs/PRD.md#Integration--API]

### Project Structure Notes

- **File Location**: `models.yaml` should be created at project root level (`/Users/bossjones/dev/bossjones/streamlit-replicate-boss/models.yaml`), not in `.streamlit/` or `docs/` directories, to maintain clear separation between runtime configuration and application configuration.

- **No Code Changes Required**: This story focuses solely on configuration file creation. No Python code modifications are needed. Future stories (1.2+) will implement loading and validation logic.

### References

- Epic breakdown and story requirements: [Source: docs/epics.md#Story-1.1]
- PRD functional requirements for model configuration: [Source: docs/PRD.md#Model-Management--Configuration]
- Architecture documentation for data storage patterns: [Source: docs/architecture.md#Data-Architecture]
- Current Replicate API integration pattern: [Source: docs/architecture.md#API-Design]

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
