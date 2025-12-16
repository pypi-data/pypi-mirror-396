"""
YAML schema validation for GoMask routines.

This module provides validation functions for YAML configuration files
against the JSON schemas defined for masking and synthetic routines.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import yaml
import jsonref
from jsonschema import validate, ValidationError, Draft7Validator
from jsonschema.validators import RefResolver
from rich.console import Console
from rich.panel import Panel

from gomask.parser.yaml_parser import parse_yaml_file as parse_yaml_with_env

console = Console()


def get_schema_dir() -> Path:
    """Get the schemas directory path."""
    # Schemas are now inside the gomask package at gomask/schema
    return Path(__file__).parent / "schema"


def load_yaml_file(file_path: str, env_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Load and parse a YAML file with optional environment variable support.

    Args:
        file_path: Path to the YAML file
        env_file: Optional path to .env file for environment variables

    Returns:
        Parsed YAML content as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    # If env_file is specified, use the parser with env var support
    if env_file is not None:
        try:
            return parse_yaml_with_env(file_path, env_file)
        except Exception as e:
            raise yaml.YAMLError(f"Failed to load YAML with environment variables: {e}")

    # Otherwise use the simple loader (backward compatibility)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML file: {e}")


def load_schema_with_refs(schema_name: str) -> Dict[str, Any]:
    """
    Load a JSON schema with resolved references.

    Args:
        schema_name: Name of the schema file (e.g., 'unified-routine-schema.json')

    Returns:
        Loaded schema with resolved $ref references

    Raises:
        FileNotFoundError: If schema file doesn't exist
    """
    schema_dir = get_schema_dir()
    schema_path = schema_dir / schema_name

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    # Use jsonref to automatically resolve $ref references
    # The base_uri ensures relative refs are resolved correctly
    base_uri = schema_path.parent.as_uri() + '/'

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_content = json.load(f)

    # Load with reference resolution
    resolved_schema = jsonref.loads(
        json.dumps(schema_content),
        base_uri=base_uri,
        jsonschema=True
    )

    return resolved_schema


def determine_routine_type(config: Dict[str, Any]) -> Optional[str]:
    """
    Determine the routine type from the configuration.

    Args:
        config: Parsed YAML configuration

    Returns:
        Routine type ('masking', 'synthetic', 'ai_scenario') or None
    """
    # Database format: config['routine']['type']
    if 'routine' in config and 'type' in config['routine']:
        return config['routine']['type']

    # User-friendly format: config['kind'] or config['metadata']['type']
    if 'kind' in config:
        kind = config['kind']
        if kind == 'SyntheticRoutine':
            return 'synthetic'
        elif kind == 'MaskingRoutine':
            return 'masking'

    # Also check metadata.type for user-friendly format
    if 'metadata' in config and isinstance(config['metadata'], dict):
        if 'type' in config['metadata']:
            return config['metadata']['type']

    return None


def validate_routine_config(
    config: Dict[str, Any],
    schema_name: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate a routine configuration against the appropriate schema.

    Args:
        config: Parsed YAML configuration dictionary
        schema_name: Optional schema name to use. If not provided,
                    determines from routine type.

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if validation passed
        - error_message: Error details if validation failed, None otherwise
    """
    try:
        # Check if this is user-friendly format (has 'kind' field)
        # If so, use Pydantic validation instead of JSON Schema
        if 'kind' in config:
            from gomask.schema.models import SyntheticRoutineConfig, MaskingRoutineConfig
            from pydantic import ValidationError as PydanticValidationError

            try:
                kind = config['kind']
                if kind == 'SyntheticRoutine':
                    SyntheticRoutineConfig(**config)
                    return True, None
                elif kind == 'MaskingRoutine':
                    MaskingRoutineConfig(**config)
                    return True, None
                else:
                    return False, f"Unknown routine kind: {kind}"
            except PydanticValidationError as e:
                # Format Pydantic errors
                error_messages = []
                for error in e.errors():
                    loc = '.'.join(str(l) for l in error['loc'])
                    error_messages.append(f"  - {loc}: {error['msg']}")
                return False, "Configuration validation failed:\n" + '\n'.join(error_messages)

        # Otherwise use JSON Schema validation for database format
        # Determine which schema to use
        if schema_name is None:
            routine_type = determine_routine_type(config)
            if routine_type is None:
                return False, "Missing or invalid routine.type field"

            # Map routine type to schema
            schema_map = {
                'masking': 'masking-routine-schema.json',
                'synthetic': 'synthetic-routine-schema.json',
                'ai_scenario': 'synthetic-routine-schema.json'  # AI scenario uses simplified synthetic
            }

            if routine_type not in schema_map:
                return False, f"Unknown routine type: {routine_type}"

            schema_name = schema_map[routine_type]

        # Load the schema with resolved references
        schema = load_schema_with_refs(schema_name)

        # Create a validator with custom resolver for $ref
        schema_dir = get_schema_dir()
        resolver = RefResolver(
            base_uri=schema_dir.as_uri() + '/',
            referrer=schema
        )

        validator = Draft7Validator(schema, resolver=resolver)

        # Validate the configuration
        errors = list(validator.iter_errors(config))

        if errors:
            # Format error messages
            error_messages = []
            for error in errors[:5]:  # Limit to first 5 errors
                path = '.'.join(str(p) for p in error.absolute_path) if error.absolute_path else 'root'
                error_messages.append(f"  - {path}: {error.message}")

            if len(errors) > 5:
                error_messages.append(f"  ... and {len(errors) - 5} more errors")

            return False, "Schema validation failed:\n" + '\n'.join(error_messages)

        return True, None

    except FileNotFoundError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_yaml_file(
    file_path: str,
    schema_name: Optional[str] = None,
    verbose: bool = True
) -> bool:
    """
    Validate a YAML file against the appropriate schema.

    Args:
        file_path: Path to the YAML file to validate
        schema_name: Optional schema name. Auto-detected if not provided.
        verbose: Whether to print validation results

    Returns:
        True if validation passed, False otherwise
    """
    try:
        # Load the YAML file
        if verbose:
            console.print(f"[cyan]Loading YAML file:[/cyan] {file_path}")

        config = load_yaml_file(file_path)

        # Determine routine type for display
        routine_type = determine_routine_type(config)
        if verbose and routine_type:
            console.print(f"[cyan]Routine type:[/cyan] {routine_type}")

        # Validate the configuration
        is_valid, error_msg = validate_routine_config(config, schema_name)

        if is_valid:
            if verbose:
                console.print(Panel(
                    "[green]Validation successful![/green]\n"
                    f"Configuration is valid for {routine_type or 'routine'} type.",
                    title="[bold green]Valid Configuration[/bold green]",
                    border_style="green"
                ))
            return True
        else:
            if verbose:
                console.print(Panel(
                    f"[red]Validation failed![/red]\n\n{error_msg}",
                    title="[bold red]Invalid Configuration[/bold red]",
                    border_style="red"
                ))
            return False

    except FileNotFoundError as e:
        if verbose:
            console.print(f"[red]Error:[/red] {e}")
        return False
    except yaml.YAMLError as e:
        if verbose:
            console.print(f"[red]YAML parsing error:[/red] {e}")
        return False
    except Exception as e:
        if verbose:
            console.print(f"[red]Unexpected error:[/red] {e}")
        return False


def get_validation_errors(config: Dict[str, Any]) -> list:
    """
    Get detailed validation errors for a configuration.

    Args:
        config: Configuration dictionary to validate

    Returns:
        List of validation error dictionaries with path and message
    """
    routine_type = determine_routine_type(config)
    if routine_type is None:
        return [{"path": "routine.type", "message": "Missing required field"}]

    schema_map = {
        'masking': 'masking-routine-schema.json',
        'synthetic': 'synthetic-routine-schema.json',
        'ai_scenario': 'synthetic-routine-schema.json'
    }

    if routine_type not in schema_map:
        return [{"path": "routine.type", "message": f"Unknown type: {routine_type}"}]

    try:
        schema = load_schema_with_refs(schema_map[routine_type])
        schema_dir = get_schema_dir()
        resolver = RefResolver(
            base_uri=schema_dir.as_uri() + '/',
            referrer=schema
        )

        validator = Draft7Validator(schema, resolver=resolver)

        errors = []
        for error in validator.iter_errors(config):
            path = '.'.join(str(p) for p in error.absolute_path) if error.absolute_path else 'root'
            errors.append({
                "path": path,
                "message": error.message,
                "validator": error.validator,
                "value": error.instance
            })

        return errors

    except Exception as e:
        return [{"path": "root", "message": f"Validation error: {str(e)}"}]


def suggest_fixes(errors: list) -> list:
    """
    Suggest fixes for common validation errors.

    Args:
        errors: List of validation error dictionaries

    Returns:
        List of suggested fixes
    """
    suggestions = []

    for error in errors:
        path = error.get('path', '')
        message = error.get('message', '')

        # Common error patterns and suggestions
        if 'is a required property' in message:
            field = message.split("'")[1] if "'" in message else path.split('.')[-1]
            suggestions.append(f"Add the required field '{field}' to {path}")

        elif 'is not valid under any of the given schemas' in message:
            if 'generation_parameters' in path:
                suggestions.append(
                    f"Check {path} - it should match one of: "
                    "library function, column_reference, random_existing_value, or custom"
                )
            elif 'masking_config' in path:
                suggestions.append(
                    f"Check {path} - ensure 'type' is 'library', 'custom', or 'builtin'"
                )

        elif 'is not of type' in message:
            expected_type = message.split('type')[1].strip().strip("'")
            suggestions.append(f"Change {path} to type {expected_type}")

        elif 'is not one of' in message:
            valid_values = message.split('[')[1].split(']')[0] if '[' in message else ''
            suggestions.append(f"Change {path} to one of: {valid_values}")

        elif 'Additional properties are not allowed' in message:
            extra_props = message.split("(")[1].split(")")[0] if "(" in message else ''
            suggestions.append(f"Remove unexpected properties: {extra_props}")

    return suggestions


# Export public API
__all__ = [
    'validate_yaml_file',
    'validate_routine_config',
    'load_yaml_file',
    'get_validation_errors',
    'suggest_fixes'
]