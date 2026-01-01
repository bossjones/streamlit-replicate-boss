"""Unit tests for validate_models_yaml.py validation script.

Tests cover all validation paths for YAML model configuration files including:
- File existence checks
- YAML syntax validation
- Root structure validation
- Model count requirements
- Per-model field validation
- Duplicate ID detection
- Optional field type validation
"""
import pytest
import tempfile
import os

from validate_models_yaml import validate_models_yaml


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_yaml_path():
    """Create a temporary YAML file path and clean up after test."""
    fd, path = tempfile.mkstemp(suffix='.yaml')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def create_yaml_file(temp_yaml_path):
    """Factory fixture to create temp YAML files with specified content."""
    def _create(content: str) -> str:
        with open(temp_yaml_path, 'w') as f:
            f.write(content)
        return temp_yaml_path
    return _create


@pytest.fixture
def valid_three_models_yaml():
    """Return valid YAML content with exactly 3 models (minimum required)."""
    return """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version1"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version2"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version3"
"""


@pytest.fixture
def valid_complete_yaml():
    """Return valid YAML content with all optional fields."""
    return """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version1"
    trigger_words: "word1"
    default_settings:
      width: 1024
      height: 1024
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version2"
    trigger_words:
      - "word1"
      - "word2"
    default_settings:
      width: 512
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version3"
"""


# =============================================================================
# TestFileExistence
# =============================================================================


class TestFileExistence:
    """Tests for file existence validation."""

    @pytest.mark.unit
    def test_file_not_found_returns_false_with_error(self):
        """[P0] Test that non-existent file returns False with appropriate error."""
        # GIVEN: A path to a file that does not exist
        nonexistent_path = "/nonexistent/path/to/models.yaml"

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(nonexistent_path)

        # THEN: Should return False with file not found error
        assert is_valid is False
        assert len(errors) == 1
        assert "File not found" in errors[0]
        assert nonexistent_path in errors[0]

    @pytest.mark.unit
    def test_file_not_found_error_message_contains_path(self):
        """[P1] Test that error message includes the specific file path."""
        # GIVEN: A custom path to a non-existent file
        custom_path = "/custom/missing/config.yaml"

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(custom_path)

        # THEN: Error message should contain the exact path
        assert is_valid is False
        assert custom_path in errors[0]


# =============================================================================
# TestYamlSyntax
# =============================================================================


class TestYamlSyntax:
    """Tests for YAML syntax validation."""

    @pytest.mark.unit
    def test_invalid_yaml_syntax_unclosed_bracket(self, create_yaml_file):
        """[P0] Test that unclosed bracket causes syntax error."""
        # GIVEN: A YAML file with unclosed bracket
        content = "models: [unclosed"
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with YAML syntax error
        assert is_valid is False
        assert len(errors) == 1
        assert "YAML syntax error" in errors[0]

    @pytest.mark.unit
    def test_invalid_yaml_syntax_bad_indentation(self, create_yaml_file):
        """[P1] Test that incorrect indentation causes syntax error."""
        # GIVEN: A YAML file with bad indentation (tab mixed with spaces)
        content = "models:\n- id: test\n\t  name: bad"
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with YAML syntax error
        assert is_valid is False
        assert "YAML syntax error" in errors[0]

    @pytest.mark.unit
    def test_invalid_yaml_syntax_colon_in_value(self, create_yaml_file):
        """[P2] Test that unquoted colon in value causes issues."""
        # GIVEN: A YAML file with unquoted colon in value
        content = """models:
  - id: test:model
    name: Test
    endpoint: owner/model:version
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False (parsing error or validation fails)
        assert is_valid is False

    @pytest.mark.unit
    def test_empty_file_is_invalid(self, create_yaml_file):
        """[P1] Test that empty file is invalid."""
        # GIVEN: An empty YAML file
        content = ""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False (root is None, not dict)
        assert is_valid is False
        assert len(errors) >= 1


# =============================================================================
# TestRootStructure
# =============================================================================


class TestRootStructure:
    """Tests for root structure validation."""

    @pytest.mark.unit
    def test_root_not_dict_list_instead(self, create_yaml_file):
        """[P0] Test that list as root element returns error."""
        # GIVEN: A YAML file with list as root
        content = """- item1
- item2
- item3
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with root structure error
        assert is_valid is False
        assert len(errors) == 1
        assert "Root element must be a dictionary" in errors[0]

    @pytest.mark.unit
    def test_root_is_scalar_string(self, create_yaml_file):
        """[P1] Test that scalar string as root returns error."""
        # GIVEN: A YAML file with scalar as root
        content = "just a plain string"
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with root structure error
        assert is_valid is False
        assert "Root element must be a dictionary" in errors[0]

    @pytest.mark.unit
    def test_missing_models_key_returns_error(self, create_yaml_file):
        """[P0] Test that missing 'models' key returns error."""
        # GIVEN: A YAML file without 'models' key
        content = """other_key: value
another_key:
  - item1
  - item2
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with missing key error
        assert is_valid is False
        assert len(errors) == 1
        assert "Missing required 'models' key at root level" in errors[0]

    @pytest.mark.unit
    def test_models_not_list_returns_error(self, create_yaml_file):
        """[P0] Test that 'models' not being a list returns error."""
        # GIVEN: A YAML file with 'models' as a string
        content = "models: not_a_list"
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with type error
        assert is_valid is False
        assert len(errors) == 1
        assert "'models' must be an array" in errors[0]


# =============================================================================
# TestModelCount
# =============================================================================


class TestModelCount:
    """Tests for minimum model count validation."""

    @pytest.mark.unit
    def test_zero_models_returns_error(self, create_yaml_file):
        """[P0] Test that empty models list returns error."""
        # GIVEN: A YAML file with empty models list
        content = "models: []"
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with model count error
        assert is_valid is False
        assert len(errors) == 1
        assert "At least 3 models required" in errors[0]
        assert "found 0" in errors[0]

    @pytest.mark.unit
    def test_one_model_returns_error(self, create_yaml_file):
        """[P0] Test that single model returns error."""
        # GIVEN: A YAML file with only 1 model
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with model count error
        assert is_valid is False
        assert "At least 3 models required" in errors[0]
        assert "found 1" in errors[0]

    @pytest.mark.unit
    def test_two_models_returns_error(self, create_yaml_file):
        """[P0] Test that two models returns error."""
        # GIVEN: A YAML file with only 2 models
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with model count error
        assert is_valid is False
        assert "At least 3 models required" in errors[0]
        assert "found 2" in errors[0]


# =============================================================================
# TestRequiredFields
# =============================================================================


class TestRequiredFields:
    """Tests for required field validation (id, name, endpoint)."""

    @pytest.mark.unit
    def test_model_missing_id_field(self, create_yaml_file):
        """[P0] Test that missing 'id' field returns error."""
        # GIVEN: A YAML file with model missing 'id'
        content = """models:
  - name: "Model One"
    endpoint: "owner/model1:version"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with missing field error
        assert is_valid is False
        assert any("Missing required field 'id'" in e for e in errors)
        assert any("Model 1" in e for e in errors)

    @pytest.mark.unit
    def test_model_missing_name_field(self, create_yaml_file):
        """[P0] Test that missing 'name' field returns error."""
        # GIVEN: A YAML file with model missing 'name'
        content = """models:
  - id: "model-1"
    endpoint: "owner/model1:version"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with missing field error
        assert is_valid is False
        assert any("Missing required field 'name'" in e for e in errors)

    @pytest.mark.unit
    def test_model_missing_endpoint_field(self, create_yaml_file):
        """[P0] Test that missing 'endpoint' field returns error."""
        # GIVEN: A YAML file with model missing 'endpoint'
        content = """models:
  - id: "model-1"
    name: "Model One"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with missing field error
        assert is_valid is False
        assert any("Missing required field 'endpoint'" in e for e in errors)

    @pytest.mark.unit
    def test_model_missing_multiple_fields(self, create_yaml_file):
        """[P1] Test that model missing multiple fields reports all errors."""
        # GIVEN: A YAML file with model missing id and endpoint
        content = """models:
  - name: "Model One"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with multiple errors
        assert is_valid is False
        assert any("'id'" in e for e in errors)
        assert any("'endpoint'" in e for e in errors)

    @pytest.mark.unit
    def test_model_id_wrong_type(self, create_yaml_file):
        """[P1] Test that non-string 'id' field returns error."""
        # GIVEN: A YAML file with integer id
        content = """models:
  - id: 123
    name: "Model One"
    endpoint: "owner/model1:version"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with type error
        assert is_valid is False
        assert any("'id' must be a string" in e for e in errors)

    @pytest.mark.unit
    def test_model_name_wrong_type(self, create_yaml_file):
        """[P1] Test that non-string 'name' field returns error."""
        # GIVEN: A YAML file with list as name
        content = """models:
  - id: "model-1"
    name:
      - "Model"
      - "One"
    endpoint: "owner/model1:version"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with type error
        assert is_valid is False
        assert any("'name' must be a string" in e for e in errors)

    @pytest.mark.unit
    def test_model_endpoint_wrong_type(self, create_yaml_file):
        """[P1] Test that non-string 'endpoint' field returns error."""
        # GIVEN: A YAML file with dict as endpoint
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint:
      owner: "test"
      model: "version"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with type error
        assert is_valid is False
        assert any("'endpoint' must be a string" in e for e in errors)

    @pytest.mark.unit
    def test_model_not_dict_in_list(self, create_yaml_file):
        """[P1] Test that non-dict model entry returns error."""
        # GIVEN: A YAML file with string instead of dict for model
        content = """models:
  - "just a string"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with type error
        assert is_valid is False
        assert any("Must be a dictionary" in e for e in errors)


# =============================================================================
# TestDuplicateIds
# =============================================================================


class TestDuplicateIds:
    """Tests for duplicate model ID detection."""

    @pytest.mark.unit
    def test_duplicate_id_returns_error(self, create_yaml_file):
        """[P0] Test that duplicate model IDs return error."""
        # GIVEN: A YAML file with duplicate IDs
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version"
  - id: "model-1"
    name: "Model One Duplicate"
    endpoint: "owner/model1-dup:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with duplicate ID error
        assert is_valid is False
        assert any("Duplicate ID 'model-1'" in e for e in errors)

    @pytest.mark.unit
    def test_multiple_duplicate_ids(self, create_yaml_file):
        """[P1] Test that multiple sets of duplicate IDs are all reported."""
        # GIVEN: A YAML file with multiple duplicate ID sets
        content = """models:
  - id: "dup-1"
    name: "First"
    endpoint: "owner/model1:version"
  - id: "dup-1"
    name: "First Dup"
    endpoint: "owner/model1d:version"
  - id: "dup-2"
    name: "Second"
    endpoint: "owner/model2:version"
  - id: "dup-2"
    name: "Second Dup"
    endpoint: "owner/model2d:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with multiple duplicate errors
        assert is_valid is False
        assert any("Duplicate ID 'dup-1'" in e for e in errors)
        assert any("Duplicate ID 'dup-2'" in e for e in errors)

    @pytest.mark.unit
    def test_unique_ids_no_duplicate_error(self, create_yaml_file, valid_three_models_yaml):
        """[P2] Test that unique IDs do not produce duplicate errors."""
        # GIVEN: A YAML file with unique IDs
        file_path = create_yaml_file(valid_three_models_yaml)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should not have duplicate errors
        assert is_valid is True
        assert not any("Duplicate" in e for e in errors)


# =============================================================================
# TestOptionalFields
# =============================================================================


class TestOptionalFields:
    """Tests for optional field type validation."""

    @pytest.mark.unit
    def test_trigger_words_as_string_valid(self, create_yaml_file):
        """[P1] Test that trigger_words as string is valid."""
        # GIVEN: A YAML file with trigger_words as string
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version"
    trigger_words: "single word"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should be valid
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_trigger_words_as_list_valid(self, create_yaml_file):
        """[P1] Test that trigger_words as list is valid."""
        # GIVEN: A YAML file with trigger_words as list
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version"
    trigger_words:
      - "word1"
      - "word2"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should be valid
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_trigger_words_invalid_type_integer(self, create_yaml_file):
        """[P1] Test that trigger_words as integer returns error."""
        # GIVEN: A YAML file with trigger_words as integer
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version"
    trigger_words: 12345
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with type error
        assert is_valid is False
        assert any("'trigger_words' must be string or array" in e for e in errors)

    @pytest.mark.unit
    def test_trigger_words_invalid_type_dict(self, create_yaml_file):
        """[P2] Test that trigger_words as dict returns error."""
        # GIVEN: A YAML file with trigger_words as dict
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version"
    trigger_words:
      key: value
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with type error
        assert is_valid is False
        assert any("trigger_words" in e for e in errors)

    @pytest.mark.unit
    def test_default_settings_valid_dict(self, create_yaml_file):
        """[P1] Test that default_settings as dict is valid."""
        # GIVEN: A YAML file with default_settings as dict
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version"
    default_settings:
      width: 1024
      height: 1024
      guidance_scale: 7.5
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should be valid
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_default_settings_invalid_type_string(self, create_yaml_file):
        """[P1] Test that default_settings as string returns error."""
        # GIVEN: A YAML file with default_settings as string
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version"
    default_settings: "not a dict"
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return False with type error
        assert is_valid is False
        assert any("'default_settings' must be an object" in e for e in errors)


# =============================================================================
# TestValidYaml
# =============================================================================


class TestValidYaml:
    """Tests for valid YAML configurations."""

    @pytest.mark.unit
    def test_valid_minimal_yaml(self, create_yaml_file, valid_three_models_yaml):
        """[P0] Test that minimal valid YAML passes validation."""
        # GIVEN: A valid YAML file with minimum required content
        file_path = create_yaml_file(valid_three_models_yaml)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return True with no errors
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_valid_complete_yaml(self, create_yaml_file, valid_complete_yaml):
        """[P0] Test that complete YAML with all optional fields passes."""
        # GIVEN: A valid YAML file with all fields
        file_path = create_yaml_file(valid_complete_yaml)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should return True with no errors
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_valid_yaml_with_extra_fields(self, create_yaml_file):
        """[P2] Test that unknown extra fields are allowed (forward compatibility)."""
        # GIVEN: A valid YAML file with extra unknown fields
        content = """models:
  - id: "model-1"
    name: "Model One"
    endpoint: "owner/model1:version"
    unknown_field: "some value"
    another_extra: 123
  - id: "model-2"
    name: "Model Two"
    endpoint: "owner/model2:version"
  - id: "model-3"
    name: "Model Three"
    endpoint: "owner/model3:version"
"""
        file_path = create_yaml_file(content)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should still be valid (extra fields ignored)
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_valid_yaml_exactly_three_models(self, create_yaml_file, valid_three_models_yaml):
        """[P1] Test boundary condition: exactly 3 models is valid."""
        # GIVEN: A YAML file with exactly 3 models
        file_path = create_yaml_file(valid_three_models_yaml)

        # WHEN: Validating the file
        is_valid, errors = validate_models_yaml(file_path)

        # THEN: Should be valid (3 is minimum)
        assert is_valid is True
        assert len(errors) == 0
