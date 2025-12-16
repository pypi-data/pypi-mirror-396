"""
YAML parser with environment variable support
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union

import yaml
from dotenv import load_dotenv

from gomask.utils.logger import logger


class YAMLParseError(Exception):
    """Custom exception for YAML parsing errors"""
    pass


def substitute_env_vars(content: str, env_vars: Optional[Dict[str, str]] = None) -> str:
    """
    Substitute environment variables in YAML content

    Supports:
    - ${VAR} - Simple substitution
    - ${VAR:-default} - With default value
    - ${VAR:?error message} - Error if not set

    Args:
        content: YAML content string
        env_vars: Optional dictionary of environment variables (defaults to os.environ)

    Returns:
        Content with environment variables substituted

    Raises:
        YAMLParseError: If a required variable is not set
    """
    if env_vars is None:
        env_vars = os.environ

    def replace_var(match):
        full_match = match.group(0)
        var_expr = match.group(1)

        # Handle ${VAR:-default}
        if ':-' in var_expr:
            var_name, default_value = var_expr.split(':-', 1)
            return env_vars.get(var_name.strip(), default_value)

        # Handle ${VAR:?error message}
        if ':?' in var_expr:
            var_name, error_msg = var_expr.split(':?', 1)
            var_name = var_name.strip()
            if var_name not in env_vars:
                raise YAMLParseError(f"Required environment variable not set: {var_name}. {error_msg}")
            return env_vars.get(var_name)

        # Simple ${VAR}
        var_name = var_expr.strip()
        if var_name not in env_vars:
            logger.warning(f"Environment variable not found: {var_name}, keeping placeholder {full_match}")
            return full_match
        return env_vars.get(var_name, full_match)

    # Pattern to match ${VAR} with optional :- or :? operators
    pattern = r'\$\{([^}]+)\}'
    result = re.sub(pattern, replace_var, content)

    return result


def parse_yaml_with_env(
    yaml_content: str,
    env_file: Optional[Path] = None,
    override_env: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Parse YAML content with environment variable substitution

    Args:
        yaml_content: YAML content string
        env_file: Optional .env file to load
        override_env: Optional dictionary of environment variables to override

    Returns:
        Parsed YAML data as dictionary

    Raises:
        YAMLParseError: If parsing fails
    """
    # Load .env file if specified
    if env_file and env_file.exists():
        load_dotenv(env_file)
        logger.debug(f"Loaded environment variables from {env_file}")

    # Build environment dictionary
    env_vars = dict(os.environ)
    if override_env:
        env_vars.update(override_env)

    # Substitute environment variables
    try:
        processed_content = substitute_env_vars(yaml_content, env_vars)
    except YAMLParseError:
        raise
    except Exception as e:
        raise YAMLParseError(f"Failed to substitute environment variables: {e}")

    # Parse YAML
    try:
        data = yaml.safe_load(processed_content)
    except yaml.YAMLError as e:
        raise YAMLParseError(f"Invalid YAML syntax: {e}")

    if data is None:
        raise YAMLParseError("YAML file is empty")

    if not isinstance(data, dict):
        raise YAMLParseError("YAML root must be a dictionary")

    return data


def parse_yaml_file(
    file_path: Union[str, Path],
    env_file: Optional[Union[str, Path]] = None,
    override_env: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Parse a YAML file with environment variable substitution

    Args:
        file_path: Path to YAML file
        env_file: Optional .env file to load
        override_env: Optional dictionary of environment variables to override

    Returns:
        Parsed YAML data as dictionary

    Raises:
        YAMLParseError: If file cannot be read or parsed
    """
    file_path = Path(file_path)
    env_file = Path(env_file) if env_file else None

    # Check if file exists
    if not file_path.exists():
        raise YAMLParseError(f"File not found: {file_path}")

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise YAMLParseError(f"Failed to read file {file_path}: {e}")

    # Look for .env file in same directory if not specified
    if not env_file:
        potential_env = file_path.parent / '.env'
        if potential_env.exists():
            env_file = potential_env
            logger.debug(f"Found .env file in same directory: {env_file}")

    return parse_yaml_with_env(content, env_file, override_env)


def validate_yaml_structure(data: Dict[str, Any]) -> None:
    """
    Validate basic YAML structure for routine configuration

    Args:
        data: Parsed YAML data

    Raises:
        YAMLParseError: If structure is invalid
    """
    required_fields = ['version', 'kind', 'metadata', 'connector']

    for field in required_fields:
        if field not in data:
            raise YAMLParseError(f"Missing required field: {field}")

    # Validate kind
    valid_kinds = ['SyntheticRoutine', 'MaskingRoutine']
    if data['kind'] not in valid_kinds:
        raise YAMLParseError(f"Invalid kind: {data['kind']}. Must be one of {valid_kinds}")

    # Validate metadata
    if not isinstance(data['metadata'], dict):
        raise YAMLParseError("metadata must be a dictionary")

    if 'id' not in data['metadata']:
        raise YAMLParseError("metadata.id is required")

    if 'name' not in data['metadata']:
        raise YAMLParseError("metadata.name is required")