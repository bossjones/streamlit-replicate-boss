"""Module for loading and validating model configurations from YAML files."""
import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def load_models_config(file_path: str = "models.yaml") -> List[Dict[str, Any]]:
    """
    Load and parse models.yaml configuration file.
    
    Args:
        file_path: Path to the models.yaml file. Defaults to "models.yaml" at project root.
    
    Returns:
        List of model dictionaries with validated structure.
    
    Raises:
        FileNotFoundError: If the file doesn't exist and no fallback is available.
        yaml.YAMLError: If YAML syntax is invalid.
        ValueError: If the structure is invalid (missing 'models' key, wrong type, etc.).
    """
    file_path_obj = Path(file_path)
    
    # Handle missing file
    if not file_path_obj.exists():
        error_msg = (
            f"Configuration file not found: {file_path}. "
            "Please ensure models.yaml exists at the project root. "
            "The application will attempt to use fallback configuration from secrets.toml."
        )
        logger.error(f"models.yaml not found at {file_path}. Error: {error_msg}")
        raise FileNotFoundError(error_msg)
    
    # Parse YAML
    try:
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        error_msg = f"Invalid YAML syntax in {file_path}"
        if hasattr(e, 'problem_mark') and e.problem_mark:
            mark = e.problem_mark
            error_msg += f" at line {mark.line + 1}, column {mark.column + 1}"
        error_msg += f": {str(e)}"
        logger.error(f"YAML parsing error in {file_path}: {error_msg}", exc_info=True)
        raise yaml.YAMLError(error_msg) from e
    
    # Validate root structure
    if not isinstance(data, dict):
        error_msg = f"Root element must be a dictionary, got {type(data).__name__}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if 'models' not in data:
        error_msg = "Missing required 'models' key at root level"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not isinstance(data['models'], list):
        error_msg = f"'models' must be a list, got {type(data['models']).__name__}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Validate each model
    models = []
    for idx, model in enumerate(data['models']):
        if not isinstance(model, dict):
            error_msg = f"Model {idx + 1}: Must be a dictionary, got {type(model).__name__}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate required fields
        required_fields = ['id', 'name', 'endpoint']
        missing_fields = [field for field in required_fields if field not in model]
        if missing_fields:
            model_id = model.get('id', f'Model {idx + 1}')
            model_name = model.get('name', 'Unknown')
            error_msg = (
                f"Model '{model_name}' (id: {model_id}): Missing required fields: {', '.join(missing_fields)}. "
                f"Please ensure all models in models.yaml have 'id', 'name', and 'endpoint' fields."
            )
            logger.error(f"Validation error for model at index {idx + 1}: {error_msg}")
            raise ValueError(error_msg)
        
        # Validate field types
        for field in required_fields:
            if not isinstance(model[field], str):
                error_msg = f"Model {idx + 1}: Field '{field}' must be a string, got {type(model[field]).__name__}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Validate optional fields if present
        if 'trigger_words' in model:
            if not isinstance(model['trigger_words'], (str, list)):
                error_msg = f"Model {idx + 1}: 'trigger_words' must be string or list, got {type(model['trigger_words']).__name__}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        if 'default_settings' in model:
            if not isinstance(model['default_settings'], dict):
                error_msg = f"Model {idx + 1}: 'default_settings' must be a dictionary, got {type(model['default_settings']).__name__}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        models.append(model)
    
    logger.info(f"Successfully loaded {len(models)} model(s) from {file_path}")
    return models


def validate_model_config(model: Dict[str, Any]) -> bool:
    """
    Validate individual model configuration dictionary.
    
    Args:
        model: Model configuration dictionary to validate.
    
    Returns:
        True if valid.
    
    Raises:
        ValueError: If validation fails, with details about what's invalid.
    """
    if not isinstance(model, dict):
        raise ValueError(f"Model must be a dictionary, got {type(model).__name__}")
    
    # Check required fields
    required_fields = ['id', 'name', 'endpoint']
    missing_fields = [field for field in required_fields if field not in model]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Validate field types
    if not isinstance(model['id'], str):
        raise ValueError(f"Field 'id' must be a string, got {type(model['id']).__name__}")
    
    if not isinstance(model['name'], str):
        raise ValueError(f"Field 'name' must be a string, got {type(model['name']).__name__}")
    
    if not isinstance(model['endpoint'], str):
        raise ValueError(f"Field 'endpoint' must be a string, got {type(model['endpoint']).__name__}")
    
    # Validate endpoint format: contains '/' (basic format check)
    if '/' not in model['endpoint']:
        model_id = model.get('id', 'Unknown')
        model_name = model.get('name', 'Unknown')
        error_msg = (
            f"Model '{model_name}' (id: {model_id}): Invalid endpoint format '{model['endpoint']}'. "
            f"Endpoint must contain '/' character. Expected format: owner/model:version "
            f"(e.g., 'stability-ai/sdxl:2b017d9b67edd2ee1401238df49d75da53c523f36e363881e057f5dc3ed3c5b2')"
        )
        raise ValueError(error_msg)
    
    # Validate optional fields if present
    if 'trigger_words' in model:
        if not isinstance(model['trigger_words'], (str, list)):
            raise ValueError(
                f"Field 'trigger_words' must be string or list, got {type(model['trigger_words']).__name__}"
            )
    
    if 'default_settings' in model:
        if not isinstance(model['default_settings'], dict):
            raise ValueError(
                f"Field 'default_settings' must be a dictionary, got {type(model['default_settings']).__name__}"
            )
    
    return True
