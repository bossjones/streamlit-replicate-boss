"""Tests for config.model_loader module."""
import pytest
import yaml
import tempfile
import os
from pathlib import Path
from config.model_loader import load_models_config, validate_model_config


# Test fixtures
@pytest.fixture
def valid_models_yaml():
    """Create a valid models.yaml content."""
    return """
models:
  - id: "test-model-1"
    name: "Test Model 1"
    endpoint: "owner/model:version"
    trigger_words: ["test"]
    default_settings:
      width: 1024
      height: 1024
  - id: "test-model-2"
    name: "Test Model 2"
    endpoint: "owner/model2:version2"
"""


@pytest.fixture
def temp_yaml_file(valid_models_yaml):
    """Create a temporary YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(valid_models_yaml)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


class TestLoadModelsConfig:
    """Tests for load_models_config() function."""
    
    def test_load_valid_models_yaml(self, temp_yaml_file):
        """Test loading valid models.yaml file (AC1, AC2, AC5)."""
        models = load_models_config(temp_yaml_file)
        
        assert isinstance(models, list)
        assert len(models) == 2
        assert models[0]['id'] == "test-model-1"
        assert models[0]['name'] == "Test Model 1"
        assert models[0]['endpoint'] == "owner/model:version"
        assert models[1]['id'] == "test-model-2"
    
    def test_load_missing_file(self):
        """Test handling of missing file (AC3)."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_models_config("nonexistent_file.yaml")
        
        assert "Configuration file not found" in str(exc_info.value)
        assert "nonexistent_file.yaml" in str(exc_info.value)
    
    def test_load_invalid_yaml_syntax(self):
        """Test handling of invalid YAML syntax (AC4)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [unclosed")
            temp_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_models_config(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_missing_models_key(self):
        """Test handling of missing 'models' key (AC4)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("other_key: value")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_models_config(temp_path)
            assert "Missing required 'models' key" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_load_models_not_list(self):
        """Test handling of 'models' not being a list (AC4)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("models: not_a_list")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_models_config(temp_path)
            assert "'models' must be a list" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_load_missing_required_fields(self):
        """Test handling of missing required fields in model (AC4)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
models:
  - id: "test"
    name: "Test"
    # endpoint missing
""")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_models_config(temp_path)
            error_msg = str(exc_info.value)
            assert "Missing required fields" in error_msg
            assert "endpoint" in error_msg
            # Verify model context is included (Story 1.7)
            assert "Test" in error_msg or "test" in error_msg
        finally:
            os.unlink(temp_path)
    
    def test_load_missing_required_fields_with_model_context(self):
        """Test error message includes model name and id for missing fields (Story 1.7, AC: 1)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
models:
  - id: "my-model"
    name: "My Test Model"
    # endpoint missing
  - id: "another-model"
    name: "Another Model"
    # name missing
""")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_models_config(temp_path)
            error_msg = str(exc_info.value)
            # Verify model context is included
            assert "My Test Model" in error_msg or "my-model" in error_msg
            assert "endpoint" in error_msg
        finally:
            os.unlink(temp_path)
    
    def test_load_returns_list_dict_structure(self, temp_yaml_file):
        """Test that function returns List[Dict] structure ready for session state (AC5)."""
        models = load_models_config(temp_yaml_file)
        
        assert isinstance(models, list)
        assert all(isinstance(model, dict) for model in models)
        assert all('id' in model and 'name' in model and 'endpoint' in model for model in models)


class TestValidateModelConfig:
    """Tests for validate_model_config() function."""
    
    def test_validate_valid_model(self):
        """Test validation of valid model config (AC2)."""
        model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version'
        }
        assert validate_model_config(model) is True
    
    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields (AC2)."""
        model = {
            'id': 'test-model',
            'name': 'Test Model'
            # endpoint missing
        }
        with pytest.raises(ValueError) as exc_info:
            validate_model_config(model)
        assert "Missing required fields" in str(exc_info.value)
        assert "endpoint" in str(exc_info.value)
    
    def test_validate_invalid_endpoint_format(self):
        """Test validation of invalid endpoint format (AC2)."""
        model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'invalid_endpoint_format'  # missing '/'
        }
        with pytest.raises(ValueError) as exc_info:
            validate_model_config(model)
        error_msg = str(exc_info.value)
        assert "endpoint" in error_msg.lower()
        assert "/" in error_msg or "format" in error_msg.lower()
        # Verify model context is included (Story 1.7)
        assert "Test Model" in error_msg or "test-model" in error_msg
    
    def test_validate_invalid_endpoint_format_with_example(self):
        """Test error message includes example format for invalid endpoint (Story 1.7, AC: 1)."""
        model = {
            'id': 'my-model',
            'name': 'My Model',
            'endpoint': 'invalidformat'  # missing '/'
        }
        with pytest.raises(ValueError) as exc_info:
            validate_model_config(model)
        error_msg = str(exc_info.value)
        # Verify example format is included
        assert "owner/model:version" in error_msg or "format" in error_msg.lower()
        assert "My Model" in error_msg or "my-model" in error_msg
    
    def test_validate_optional_trigger_words_string(self):
        """Test validation with optional trigger_words as string (AC2)."""
        model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version',
            'trigger_words': 'test'
        }
        assert validate_model_config(model) is True
    
    def test_validate_optional_trigger_words_list(self):
        """Test validation with optional trigger_words as list (AC2)."""
        model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version',
            'trigger_words': ['test', 'word']
        }
        assert validate_model_config(model) is True
    
    def test_validate_optional_default_settings(self):
        """Test validation with optional default_settings (AC2)."""
        model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version',
            'default_settings': {'width': 1024, 'height': 1024}
        }
        assert validate_model_config(model) is True
    
    def test_validate_invalid_trigger_words_type(self):
        """Test validation with invalid trigger_words type (AC2)."""
        model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version',
            'trigger_words': 123  # invalid type
        }
        with pytest.raises(ValueError) as exc_info:
            validate_model_config(model)
        assert "trigger_words" in str(exc_info.value).lower()
    
    def test_validate_invalid_default_settings_type(self):
        """Test validation with invalid default_settings type (AC2)."""
        model = {
            'id': 'test-model',
            'name': 'Test Model',
            'endpoint': 'owner/model:version',
            'default_settings': 'not_a_dict'  # invalid type
        }
        with pytest.raises(ValueError) as exc_info:
            validate_model_config(model)
        assert "default_settings" in str(exc_info.value).lower()


class TestPerformance:
    """Tests for performance requirements."""
    
    def test_load_performance_requirement(self):
        """Test that loading completes in <500ms with 10+ models (AC6)."""
        import time
        
        # Create a YAML file with 10+ models
        models_content = "models:\n"
        for i in range(15):
            models_content += f"""  - id: "model-{i}"
    name: "Model {i}"
    endpoint: "owner/model{i}:version{i}"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(models_content)
            temp_path = f.name
        
        try:
            start_time = time.time()
            models = load_models_config(temp_path)
            elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            assert len(models) >= 10
            assert elapsed_time < 500, f"Loading took {elapsed_time:.2f}ms, expected <500ms"
        finally:
            os.unlink(temp_path)


class TestLogging:
    """Tests for logging functionality."""
    
    def test_logging_successful_load(self, temp_yaml_file, caplog):
        """Test that successful load logs info message with model count (AC7)."""
        import logging
        from config import model_loader
        
        # Configure logger for the module
        logger = logging.getLogger('config.model_loader')
        logger.setLevel(logging.INFO)
        
        with caplog.at_level(logging.INFO, logger='config.model_loader'):
            models = load_models_config(temp_yaml_file)
        
        assert len(models) == 2
        assert any("Successfully loaded" in record.message and "model" in record.message.lower()
                  for record in caplog.records)
    
    def test_logging_missing_file(self, caplog):
        """Test that missing file logs warning (AC7)."""
        import logging
        logging.basicConfig(level=logging.WARNING)
        
        try:
            load_models_config("nonexistent_file.yaml")
        except FileNotFoundError:
            pass
        
        assert any("models.yaml not found" in record.message or "not found" in record.message.lower()
                  for record in caplog.records)
    
    def test_logging_invalid_structure(self, caplog):
        """Test that invalid structure logs error (AC7)."""
        import logging
        logging.basicConfig(level=logging.ERROR)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("models: not_a_list")
            temp_path = f.name
        
        try:
            try:
                load_models_config(temp_path)
            except ValueError:
                pass
            
            assert any("error" in record.levelname.lower() for record in caplog.records)
        finally:
            os.unlink(temp_path)
    
    def test_logging_yaml_syntax_error_with_line_number(self, caplog):
        """Test that YAML syntax errors log with line number context (Story 1.7, AC: 1, 5)."""
        import logging
        logging.basicConfig(level=logging.ERROR)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
models:
  - id: "test"
    name: "Test"
    endpoint: "owner/model:version"
  - id: "test2"
    name: "Test 2"
    endpoint: "owner/model2:version" [unclosed bracket
""")
            temp_path = f.name
        
        try:
            try:
                load_models_config(temp_path)
            except yaml.YAMLError:
                pass
            
            # Verify error was logged with context
            assert any("error" in record.levelname.lower() for record in caplog.records)
        finally:
            os.unlink(temp_path)