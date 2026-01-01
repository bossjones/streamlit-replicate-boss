"""Module for loading and validating preset configurations from YAML files."""
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def load_presets_config(file_path: str = "presets.yaml", validate_model_ids: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load and parse presets.yaml configuration file.
    
    Args:
        file_path: Path to the presets.yaml file. Defaults to "presets.yaml" at project root.
    
    Returns:
        Dictionary grouped by model_id: {model_id: [preset1, preset2, ...]}.
        Returns empty dict {} if file is missing (graceful degradation).
    
    Raises:
        yaml.YAMLError: If YAML syntax is invalid.
        ValueError: If the structure is invalid (missing 'presets' key, wrong type, etc.).
    """
    file_path_obj = Path(file_path)
    
    # Handle missing file gracefully (AC: 4)
    if not file_path_obj.exists():
        logger.warning(f"Presets configuration file not found: {file_path}. Application will continue without presets.")
        return {}
    
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
    
    if 'presets' not in data:
        error_msg = "Missing required 'presets' key at root level"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not isinstance(data['presets'], list):
        error_msg = f"'presets' must be a list, got {type(data['presets']).__name__}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Load valid model IDs for cross-reference validation (AC: 2)
    valid_model_ids: Optional[List[str]] = None
    if validate_model_ids:
        try:
            from config.model_loader import load_models_config
            models = load_models_config("models.yaml")
            valid_model_ids = [model['id'] for model in models]
            logger.debug(f"Loaded {len(valid_model_ids)} valid model ID(s) for preset validation")
        except (FileNotFoundError, ValueError, yaml.YAMLError) as e:
            logger.warning(f"Could not load models.yaml for preset validation: {e}. Skipping model_id validation.")
            valid_model_ids = None
    
    # Validate and group presets by model_id
    presets_by_model: Dict[str, List[Dict[str, Any]]] = {}
    
    for idx, preset in enumerate(data['presets']):
        if not isinstance(preset, dict):
            error_msg = f"Preset {idx + 1}: Must be a dictionary, got {type(preset).__name__}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate required fields
        required_fields = ['id', 'name', 'model_id']
        missing_fields = [field for field in required_fields if field not in preset]
        if missing_fields:
            preset_id = preset.get('id', f'Preset {idx + 1}')
            preset_name = preset.get('name', 'Unknown')
            error_msg = (
                f"Preset '{preset_name}' (id: {preset_id}): Missing required fields: {', '.join(missing_fields)}. "
                f"Please ensure all presets in presets.yaml have 'id', 'name', and 'model_id' fields."
            )
            logger.error(f"Validation error for preset at index {idx + 1}: {error_msg}")
            raise ValueError(error_msg)
        
        # Validate field types
        for field in required_fields:
            if not isinstance(preset[field], str):
                error_msg = f"Preset {idx + 1}: Field '{field}' must be a string, got {type(preset[field]).__name__}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Validate optional fields if present
        if 'trigger_words' in preset:
            if not isinstance(preset['trigger_words'], (str, list)):
                error_msg = f"Preset {idx + 1}: 'trigger_words' must be string or list, got {type(preset['trigger_words']).__name__}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        if 'settings' in preset:
            if not isinstance(preset['settings'], dict):
                error_msg = f"Preset {idx + 1}: 'settings' must be a dictionary, got {type(preset['settings']).__name__}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Validate model_id references against models.yaml (cross-reference check - AC: 2)
        if valid_model_ids is not None:
            model_id = preset['model_id']
            if model_id not in valid_model_ids:
                preset_id = preset.get('id', f'Preset {idx + 1}')
                preset_name = preset.get('name', 'Unknown')
                error_msg = (
                    f"Preset '{preset_name}' (id: {preset_id}): Invalid model_id '{model_id}'. "
                    f"model_id must reference a valid model.id from models.yaml. "
                    f"Valid model IDs: {', '.join(valid_model_ids)}"
                )
                logger.error(f"Validation error for preset at index {idx + 1}: {error_msg}")
                raise ValueError(error_msg)
        
        # Group by model_id (single-pass grouping for efficiency - AC: 6)
        model_id = preset['model_id']
        if model_id not in presets_by_model:
            presets_by_model[model_id] = []
        presets_by_model[model_id].append(preset)
    
    logger.info(f"Successfully loaded {len(data['presets'])} preset(s) from {file_path}, grouped into {len(presets_by_model)} model(s)")
    return presets_by_model


def validate_preset_config(preset: Dict[str, Any], valid_model_ids: List[str] = None) -> bool:
    """
    Validate individual preset configuration dictionary.
    
    Args:
        preset: Preset configuration dictionary to validate.
        valid_model_ids: Optional list of valid model IDs for cross-reference validation.
                         If provided, validates that preset['model_id'] exists in this list.
    
    Returns:
        True if valid.
    
    Raises:
        ValueError: If validation fails, with details about what's invalid.
    """
    if not isinstance(preset, dict):
        raise ValueError(f"Preset must be a dictionary, got {type(preset).__name__}")
    
    # Check required fields
    required_fields = ['id', 'name', 'model_id']
    missing_fields = [field for field in required_fields if field not in preset]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Validate field types
    if not isinstance(preset['id'], str):
        raise ValueError(f"Field 'id' must be a string, got {type(preset['id']).__name__}")
    
    if not isinstance(preset['name'], str):
        raise ValueError(f"Field 'name' must be a string, got {type(preset['name']).__name__}")
    
    if not isinstance(preset['model_id'], str):
        raise ValueError(f"Field 'model_id' must be a string, got {type(preset['model_id']).__name__}")
    
    # Validate model_id references against models.yaml (cross-reference check - AC: 2)
    if valid_model_ids is not None:
        if preset['model_id'] not in valid_model_ids:
            preset_id = preset.get('id', 'Unknown')
            preset_name = preset.get('name', 'Unknown')
            error_msg = (
                f"Preset '{preset_name}' (id: {preset_id}): Invalid model_id '{preset['model_id']}'. "
                f"model_id must reference a valid model.id from models.yaml. "
                f"Valid model IDs: {', '.join(valid_model_ids)}"
            )
            raise ValueError(error_msg)
    
    # Validate optional fields if present
    if 'trigger_words' in preset:
        if not isinstance(preset['trigger_words'], (str, list)):
            raise ValueError(
                f"Field 'trigger_words' must be string or list, got {type(preset['trigger_words']).__name__}"
            )
    
    if 'settings' in preset:
        if not isinstance(preset['settings'], dict):
            raise ValueError(
                f"Field 'settings' must be a dictionary, got {type(preset['settings']).__name__}"
            )
    
    return True
