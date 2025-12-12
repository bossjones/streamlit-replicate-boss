#!/usr/bin/env python3
"""
Validation script for models.yaml configuration file.
Validates YAML syntax and schema compliance.
"""
import yaml
import sys
from pathlib import Path

def validate_models_yaml(file_path: str) -> tuple[bool, list[str]]:
    """
    Validate models.yaml file for syntax and schema compliance.
    
    Returns:
        (is_valid, errors): Tuple of validation result and list of error messages
    """
    errors = []
    
    # Check file exists
    if not Path(file_path).exists():
        errors.append(f"File not found: {file_path}")
        return False, errors
    
    # Parse YAML
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"YAML syntax error: {e}")
        return False, errors
    
    # Validate root structure
    if not isinstance(data, dict):
        errors.append("Root element must be a dictionary")
        return False, errors
    
    if 'models' not in data:
        errors.append("Missing required 'models' key at root level")
        return False, errors
    
    if not isinstance(data['models'], list):
        errors.append("'models' must be an array")
        return False, errors
    
    if len(data['models']) < 3:
        errors.append(f"At least 3 models required, found {len(data['models'])}")
        return False, errors
    
    # Validate each model
    model_ids = set()
    for idx, model in enumerate(data['models']):
        if not isinstance(model, dict):
            errors.append(f"Model {idx + 1}: Must be a dictionary")
            continue
        
        # Required fields
        for field in ['id', 'name', 'endpoint']:
            if field not in model:
                errors.append(f"Model {idx + 1}: Missing required field '{field}'")
            elif not isinstance(model[field], str):
                errors.append(f"Model {idx + 1}: Field '{field}' must be a string")
        
        # Check unique IDs
        if 'id' in model:
            if model['id'] in model_ids:
                errors.append(f"Model {idx + 1}: Duplicate ID '{model['id']}'")
            model_ids.add(model['id'])
        
        # Optional fields validation
        if 'trigger_words' in model:
            if not isinstance(model['trigger_words'], (str, list)):
                errors.append(f"Model {idx + 1}: 'trigger_words' must be string or array")
        
        if 'default_settings' in model:
            if not isinstance(model['default_settings'], dict):
                errors.append(f"Model {idx + 1}: 'default_settings' must be an object")
    
    is_valid = len(errors) == 0
    return is_valid, errors

if __name__ == "__main__":
    file_path = "models.yaml"
    
    print(f"Validating {file_path}...")
    is_valid, errors = validate_models_yaml(file_path)
    
    if is_valid:
        print("✅ Validation passed!")
        print(f"  - YAML syntax: Valid")
        print(f"  - Schema structure: Valid")
        print(f"  - Required fields: Present")
        print(f"  - Model count: {len(yaml.safe_load(open(file_path))['models'])}")
        sys.exit(0)
    else:
        print("❌ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
