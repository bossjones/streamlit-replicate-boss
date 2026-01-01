"""Tests for utils.preset_manager module."""
import pytest
import yaml
import tempfile
import os
import time
from pathlib import Path
from utils.preset_manager import load_presets_config, validate_preset_config


# Test fixtures
@pytest.fixture
def valid_presets_yaml():
    """Create a valid presets.yaml content."""
    return """
presets:
  - id: "test-preset-1"
    name: "Test Preset 1"
    model_id: "test-model-1"
    trigger_words: ["test"]
    settings:
      width: 1024
      height: 1024
  - id: "test-preset-2"
    name: "Test Preset 2"
    model_id: "test-model-2"
    trigger_words: "single-trigger"
    settings:
      width: 512
      height: 512
  - id: "test-preset-3"
    name: "Test Preset 3"
    model_id: "test-model-1"
"""


@pytest.fixture
def valid_models_yaml():
    """Create a valid models.yaml content for model_id validation."""
    return """
models:
  - id: "test-model-1"
    name: "Test Model 1"
    endpoint: "owner/model:version"
  - id: "test-model-2"
    name: "Test Model 2"
    endpoint: "owner/model2:version2"
  - id: "test-model-3"
    name: "Test Model 3"
    endpoint: "owner/model3:version3"
"""


@pytest.fixture
def temp_presets_file(valid_presets_yaml):
    """Create a temporary presets.yaml file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(valid_presets_yaml)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def temp_models_file(valid_models_yaml, tmp_path):
    """Create a temporary models.yaml file for validation."""
    models_file = tmp_path / "models.yaml"
    with open(models_file, 'w') as f:
        f.write(valid_models_yaml)
    return str(models_file)


class TestLoadPresetsConfig:
    """Tests for load_presets_config() function (AC: 1, 2, 4, 5, 6)."""
    
    def test_load_valid_presets_yaml(self, temp_presets_file):
        """Test loading valid presets.yaml file (AC: 1, 2)."""
        presets = load_presets_config(temp_presets_file, validate_model_ids=False)
        
        assert isinstance(presets, dict)
        assert "test-model-1" in presets
        assert "test-model-2" in presets
        assert len(presets["test-model-1"]) == 2  # test-preset-1 and test-preset-3
        assert len(presets["test-model-2"]) == 1  # test-preset-2
        assert presets["test-model-1"][0]["id"] == "test-preset-1"
        assert presets["test-model-1"][1]["id"] == "test-preset-3"
        assert presets["test-model-2"][0]["id"] == "test-preset-2"
    
    def test_load_missing_file(self):
        """Test handling of missing file (AC: 4)."""
        presets = load_presets_config("nonexistent_file.yaml", validate_model_ids=False)
        
        assert isinstance(presets, dict)
        assert len(presets) == 0
        assert presets == {}
    
    def test_load_invalid_yaml_syntax(self):
        """Test handling of invalid YAML syntax (AC: 5)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [unclosed")
            temp_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_presets_config(temp_path, validate_model_ids=False)
        finally:
            os.unlink(temp_path)
    
    def test_load_missing_presets_key(self):
        """Test handling of missing 'presets' key (AC: 5)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("other_key: value")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_presets_config(temp_path, validate_model_ids=False)
            assert "Missing required 'presets' key" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_load_presets_not_list(self):
        """Test handling of 'presets' not being a list (AC: 5)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("presets: not_a_list")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_presets_config(temp_path, validate_model_ids=False)
            assert "'presets' must be a list" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_load_missing_required_fields(self):
        """Test handling of missing required fields in preset (AC: 5)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
presets:
  - id: "test-preset"
    name: "Test Preset"
    # Missing model_id
""")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_presets_config(temp_path, validate_model_ids=False)
            assert "Missing required fields" in str(exc_info.value)
            assert "model_id" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_load_invalid_field_types(self):
        """Test handling of invalid field types (AC: 5)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
presets:
  - id: 123  # Should be string
    name: "Test Preset"
    model_id: "test-model"
""")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_presets_config(temp_path, validate_model_ids=False)
            assert "must be a string" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_load_invalid_trigger_words_type(self):
        """Test handling of invalid trigger_words type (AC: 5)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
presets:
  - id: "test-preset"
    name: "Test Preset"
    model_id: "test-model"
    trigger_words: 123  # Should be string or list
""")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_presets_config(temp_path, validate_model_ids=False)
            assert "trigger_words" in str(exc_info.value)
            assert "must be string or list" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_load_invalid_settings_type(self):
        """Test handling of invalid settings type (AC: 5)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
presets:
  - id: "test-preset"
    name: "Test Preset"
    model_id: "test-model"
    settings: "not-a-dict"  # Should be dict
""")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_presets_config(temp_path, validate_model_ids=False)
            assert "settings" in str(exc_info.value)
            assert "must be a dictionary" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_load_presets_grouped_by_model_id(self, temp_presets_file):
        """Test that presets are grouped by model_id (AC: 1, 2)."""
        presets = load_presets_config(temp_presets_file, validate_model_ids=False)
        
        # Verify grouping structure
        assert isinstance(presets, dict)
        assert "test-model-1" in presets
        assert "test-model-2" in presets
        # test-preset-1 and test-preset-3 both have model_id "test-model-1"
        assert len(presets["test-model-1"]) == 2
        assert len(presets["test-model-2"]) == 1
    
    def test_load_performance_requirement(self, tmp_path):
        """Test preset loading completes efficiently (<500ms) (AC: 6)."""
        # Create presets.yaml with 10+ presets
        presets_content = "presets:\n"
        for i in range(15):
            presets_content += f"""  - id: "preset-{i}"
    name: "Preset {i}"
    model_id: "model-{i % 3}"
"""
        presets_file = tmp_path / "presets.yaml"
        with open(presets_file, 'w') as f:
            f.write(presets_content)
        
        start_time = time.time()
        presets = load_presets_config(str(presets_file), validate_model_ids=False)
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        assert elapsed_time < 500, f"Preset loading took {elapsed_time:.2f}ms, expected <500ms"
        assert len(presets) == 3  # Grouped into 3 models
    
    def test_load_with_model_id_validation_valid(self, temp_presets_file, temp_models_file, monkeypatch):
        """Test model_id validation with valid model IDs (AC: 2)."""
        # Mock models.yaml location
        import config.model_loader
        original_load = config.model_loader.load_models_config
        
        def mock_load_models_config(file_path):
            if file_path == "models.yaml":
                # Load from temp file
                with open(temp_models_file, 'r') as f:
                    data = yaml.safe_load(f)
                return data['models']
            return original_load(file_path)
        
        monkeypatch.setattr(config.model_loader, 'load_models_config', mock_load_models_config)
        
        presets = load_presets_config(temp_presets_file, validate_model_ids=True)
        
        assert isinstance(presets, dict)
        assert "test-model-1" in presets
        assert "test-model-2" in presets
    
    def test_load_with_model_id_validation_invalid(self, temp_models_file, monkeypatch):
        """Test model_id validation with invalid model ID (AC: 2, 5)."""
        # Create preset with invalid model_id
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
presets:
  - id: "test-preset"
    name: "Test Preset"
    model_id: "invalid-model-id"
""")
            temp_path = f.name
        
        # Mock models.yaml location
        import config.model_loader
        original_load = config.model_loader.load_models_config
        
        def mock_load_models_config(file_path):
            if file_path == "models.yaml":
                with open(temp_models_file, 'r') as f:
                    data = yaml.safe_load(f)
                return data['models']
            return original_load(file_path)
        
        monkeypatch.setattr(config.model_loader, 'load_models_config', mock_load_models_config)
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_presets_config(temp_path, validate_model_ids=True)
            assert "Invalid model_id" in str(exc_info.value)
            assert "invalid-model-id" in str(exc_info.value)
        finally:
            os.unlink(temp_path)


class TestValidatePresetConfig:
    """Tests for validate_preset_config() function (AC: 2)."""
    
    def test_validate_valid_preset(self):
        """Test validation of valid preset (AC: 2)."""
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': 'test-model',
            'trigger_words': ['test'],
            'settings': {'width': 1024}
        }
        
        result = validate_preset_config(preset, valid_model_ids=None)
        assert result is True
    
    def test_validate_preset_missing_required_fields(self):
        """Test validation catches missing required fields (AC: 2)."""
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset'
            # Missing model_id
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_preset_config(preset)
        assert "Missing required fields" in str(exc_info.value)
        assert "model_id" in str(exc_info.value)
    
    def test_validate_preset_invalid_field_types(self):
        """Test validation catches invalid field types (AC: 2)."""
        preset = {
            'id': 123,  # Should be string
            'name': 'Test Preset',
            'model_id': 'test-model'
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_preset_config(preset)
        assert "must be a string" in str(exc_info.value)
    
    def test_validate_preset_invalid_model_id_reference(self):
        """Test validation catches invalid model_id references (AC: 2)."""
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': 'invalid-model-id'
        }
        
        valid_model_ids = ['test-model-1', 'test-model-2']
        
        with pytest.raises(ValueError) as exc_info:
            validate_preset_config(preset, valid_model_ids=valid_model_ids)
        assert "Invalid model_id" in str(exc_info.value)
        assert "invalid-model-id" in str(exc_info.value)
        assert "test-model-1" in str(exc_info.value)  # Should list valid IDs
    
    def test_validate_preset_valid_model_id_reference(self):
        """Test validation accepts valid model_id references (AC: 2)."""
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': 'test-model-1'
        }
        
        valid_model_ids = ['test-model-1', 'test-model-2']
        
        result = validate_preset_config(preset, valid_model_ids=valid_model_ids)
        assert result is True
    
    def test_validate_preset_invalid_trigger_words_type(self):
        """Test validation catches invalid trigger_words type (AC: 2)."""
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': 'test-model',
            'trigger_words': 123  # Should be string or list
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_preset_config(preset)
        assert "trigger_words" in str(exc_info.value)
        assert "must be string or list" in str(exc_info.value)
    
    def test_validate_preset_valid_trigger_words_string(self):
        """Test validation accepts trigger_words as string (AC: 2)."""
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': 'test-model',
            'trigger_words': 'single-trigger'
        }
        
        result = validate_preset_config(preset)
        assert result is True
    
    def test_validate_preset_valid_trigger_words_list(self):
        """Test validation accepts trigger_words as list (AC: 2)."""
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': 'test-model',
            'trigger_words': ['trigger1', 'trigger2']
        }
        
        result = validate_preset_config(preset)
        assert result is True
    
    def test_validate_preset_invalid_settings_type(self):
        """Test validation catches invalid settings type (AC: 2)."""
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': 'test-model',
            'settings': 'not-a-dict'  # Should be dict
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_preset_config(preset)
        assert "settings" in str(exc_info.value)
        assert "must be a dictionary" in str(exc_info.value)
    
    def test_validate_preset_valid_settings(self):
        """Test validation accepts valid settings dict (AC: 2)."""
        preset = {
            'id': 'test-preset',
            'name': 'Test Preset',
            'model_id': 'test-model',
            'settings': {'width': 1024, 'height': 1024}
        }
        
        result = validate_preset_config(preset)
        assert result is True
