"""
Default values for YAML configuration fields.
Single source of truth for both import (apply defaults) and export (omit defaults).
"""

# Column field aliases - maps alias -> canonical name
# Both synthetic and masking now use consistent masking-style canonical names:
#   is_nullable, is_unique, referenced_table, referenced_column, data_type, is_excluded
# Old synthetic-style names are accepted as aliases for backwards compatibility
COLUMN_ALIASES = {
    'nullable': 'is_nullable',
    'unique_constraint': 'is_unique',
    'reference_table': 'referenced_table',
    'reference_column': 'referenced_column',
    'original_data_type': 'data_type',
}

# Special aliases that require value inversion (enabled=true means is_excluded=false)
INVERTED_ALIASES = {
    'enabled': 'is_excluded',  # enabled=true -> is_excluded=false
}

# Keep separate constants for backwards compatibility (both point to same aliases now)
SYNTHETIC_COLUMN_ALIASES = COLUMN_ALIASES
MASKING_COLUMN_ALIASES = COLUMN_ALIASES


def normalize_column_aliases(column: dict, routine_type: str) -> dict:
    """
    Normalize column field aliases to canonical names.

    Args:
        column: Column configuration dict
        routine_type: 'synthetic' or 'masking'

    Returns:
        Column dict with aliases converted to canonical names
    """
    if routine_type == 'synthetic':
        aliases = SYNTHETIC_COLUMN_ALIASES
    elif routine_type == 'masking':
        aliases = MASKING_COLUMN_ALIASES
    else:
        return column

    # Get all canonical names (values in the alias map + inverted alias targets)
    canonical_names = set(aliases.values()) | set(INVERTED_ALIASES.values())

    result = {}
    for key, value in column.items():
        # If this key is a canonical name, use it directly
        if key in canonical_names:
            result[key] = value
        # If this is an inverted alias (e.g., enabled -> is_excluded with inversion)
        elif key in INVERTED_ALIASES:
            canonical = INVERTED_ALIASES[key]
            # Only use alias value if canonical isn't already in the original column
            if canonical not in column:
                # Invert boolean value: enabled=true -> is_excluded=false
                result[canonical] = not value if isinstance(value, bool) else value
        # If this is a regular alias, convert to canonical
        elif key in aliases:
            canonical = aliases[key]
            # Only use alias value if canonical isn't already in the original column
            if canonical not in column:
                result[canonical] = value
        else:
            # Not an alias, keep as-is
            result[key] = value
    return result


# Synthetic routine settings defaults
SYNTHETIC_SETTINGS_DEFAULTS = {
    'generation_mode': 'hierarchical',
    'batch_size': 1000,
    'parallel_workers': 4,
    'enforce_referential_integrity': True,
    'localization_language': 'en',
    'localization_region': 'US',
    'global_record_count': 1000,
}

# Synthetic table defaults
SYNTHETIC_TABLE_DEFAULTS = {
    'schema_name': 'public',
    'table_type': 'entity',
    'hierarchy_level': 0,
    'order_index': 0,
}

# Synthetic column defaults
# Uses masking-style names for consistency in CLI output
SYNTHETIC_COLUMN_DEFAULTS = {
    'is_excluded': False,  # masking-style (was: enabled=True, inverted)
    'is_primary_key': False,
    'is_foreign_key': False,
    'is_nullable': True,  # masking-style (was: nullable)
    'is_unique': False,   # masking-style (was: unique_constraint)
    'is_indexed': False,
    'order_index': 0,
}

# Masking routine settings defaults
MASKING_SETTINGS_DEFAULTS = {
    'batch_size': 1000,
    'parallel_workers': 4,
    'audit_reporting_enabled': True,
    'localization_language': 'en',
    'localization_region': 'US',
}

# Masking table defaults
MASKING_TABLE_DEFAULTS = {
    'schema_name': 'public',
}

# Masking column defaults
MASKING_COLUMN_DEFAULTS = {
    'is_excluded': False,
    'is_nullable': True,
    'is_primary_key': False,
    'is_foreign_key': False,
    'is_unique': False,
    'is_indexed': False,
    'sensitivity_level': 'low',
    'data_category': 'generic',
}


def omit_defaults(data: dict, defaults: dict) -> dict:
    """
    Remove fields from data that match their default values.

    Args:
        data: Dictionary of field values
        defaults: Dictionary of default values

    Returns:
        Dictionary with default-valued fields removed
    """
    return {k: v for k, v in data.items() if k not in defaults or v != defaults.get(k)}


def apply_defaults(data: dict, defaults: dict) -> dict:
    """
    Apply default values to missing fields in data.

    Args:
        data: Dictionary of field values (may have missing keys)
        defaults: Dictionary of default values

    Returns:
        Dictionary with defaults applied for missing fields
    """
    result = defaults.copy()
    result.update(data)
    return result


def apply_config_defaults(config: dict) -> dict:
    """
    Apply all default values to a routine configuration.
    Call this after loading YAML and before sending to API.

    Args:
        config: Routine configuration dictionary

    Returns:
        Configuration with all defaults applied
    """
    from copy import deepcopy
    result = deepcopy(config)

    routine = result.get('routine', {})
    routine_type = routine.get('type', 'synthetic')

    # Apply settings defaults
    if routine_type == 'synthetic':
        if 'settings' not in result:
            result['settings'] = {}
        result['settings'] = apply_defaults(result['settings'], SYNTHETIC_SETTINGS_DEFAULTS)
    elif routine_type == 'masking':
        if 'settings' not in result:
            result['settings'] = {}
        result['settings'] = apply_defaults(result['settings'], MASKING_SETTINGS_DEFAULTS)

    # Apply table and column defaults
    if 'tables' in result:
        if routine_type == 'synthetic':
            result['tables'] = _apply_synthetic_table_defaults(result['tables'])
        elif routine_type == 'masking':
            result['tables'] = _apply_masking_table_defaults(result['tables'])

    return result


def _apply_synthetic_table_defaults(tables: list) -> list:
    """Apply defaults to synthetic tables and columns."""
    result = []
    for idx, table in enumerate(tables):
        table_with_defaults = apply_defaults(table, SYNTHETIC_TABLE_DEFAULTS)
        # Auto-assign order_index if not specified
        if 'order_index' not in table:
            table_with_defaults['order_index'] = idx

        # Apply column defaults
        if 'columns' in table_with_defaults:
            table_with_defaults['columns'] = _apply_synthetic_column_defaults(
                table_with_defaults['columns']
            )
        result.append(table_with_defaults)
    return result


def _apply_synthetic_column_defaults(columns: list) -> list:
    """Apply defaults to synthetic columns."""
    result = []
    for idx, column in enumerate(columns):
        # Normalize aliases first (e.g., is_nullable -> nullable)
        normalized = normalize_column_aliases(column, 'synthetic')
        col_with_defaults = apply_defaults(normalized, SYNTHETIC_COLUMN_DEFAULTS)
        # Auto-assign order_index if not specified
        if 'order_index' not in column:
            col_with_defaults['order_index'] = idx
        result.append(col_with_defaults)
    return result


def _apply_masking_table_defaults(tables: list) -> list:
    """Apply defaults to masking tables and columns."""
    result = []
    for table in tables:
        table_with_defaults = apply_defaults(table, MASKING_TABLE_DEFAULTS)

        # Apply column defaults
        if 'columns' in table_with_defaults:
            table_with_defaults['columns'] = _apply_masking_column_defaults(
                table_with_defaults['columns']
            )
        result.append(table_with_defaults)
    return result


def _apply_masking_column_defaults(columns: list) -> list:
    """Apply defaults to masking columns."""
    result = []
    for column in columns:
        # Normalize aliases first (e.g., nullable -> is_nullable)
        normalized = normalize_column_aliases(column, 'masking')
        col_with_defaults = apply_defaults(normalized, MASKING_COLUMN_DEFAULTS)
        result.append(col_with_defaults)
    return result


# Fields to strip from function metadata on export
# These are redundant because they're stored in the database function definitions
FUNCTION_METADATA_FIELDS_TO_STRIP = {
    'name',
    'description',
    'category',
    'functionType',
    'function_type',
    'parameters',  # Schema definition, not actual values
}

# Fields to keep in function config
FUNCTION_CONFIG_FIELDS_TO_KEEP = {
    'type',  # library/custom/builtin
    'functionId',
    'function_id',
    'parameterValues',  # Actual user-provided values
    'code',  # For custom functions
    'mode',  # For column_reference
    'reference_table',
    'reference_column',
    'source_table',  # For random_existing_value
    'source_column',
}


def strip_function_metadata(config: dict):
    """
    Convert generation_parameters/masking_config to minimal CLI array format.

    All parameters are converted to unified array format:
    [
        {"name": "param1", "value": "simple_value"},
        {"name": "param2", "valueType": "reference", "columnReference": "col", "tableReference": "tbl"}
    ]

    Args:
        config: Function configuration dict (generation_parameters or masking_config)

    Returns:
        Array of parameter objects with name and either value or additional properties
    """
    if not config or not isinstance(config, dict):
        return config

    # Check if this is the old format (parameter schemas as direct keys from setup)
    if _is_parameter_schema_format(config):
        return _convert_parameter_schema_to_array(config)

    # New format with parameterValues - convert to array format
    # Check this BEFORE 'parameters' since 'parameters' may just contain schema definitions
    if 'parameterValues' in config and config['parameterValues']:
        # Get parameter schema to check for defaults
        param_schema = config.get('parameters', {})
        return _convert_param_values_to_array(config['parameterValues'], param_schema)

    # Handle 'parameters' object format (from function config with nested params and values)
    if 'parameters' in config and isinstance(config['parameters'], dict):
        return _convert_parameters_object_to_array(config['parameters'])

    # No parameters to export
    return []


def _is_parameter_schema_format(config: dict) -> bool:
    """
    Check if config is in the old parameter schema format.

    Old format looks like:
    {
        'param_name': {'name': 'param_name', 'type': 'string', 'defaultValue': ...},
        ...
    }

    New format has keys like 'type', 'functionId', 'parameterValues', etc.
    """
    # If it has known function config keys, it's the new format
    new_format_keys = {'type', 'functionId', 'function_id', 'parameterValues',
                       'code', 'mode', 'reference_table', 'source_table'}
    if any(key in config for key in new_format_keys):
        return False

    # Check if all values are dicts with parameter schema structure
    for key, value in config.items():
        if not isinstance(value, dict):
            return False
        # Parameter schemas have 'type' or 'defaultValue' or 'name'
        if not any(k in value for k in ('type', 'defaultValue', 'name')):
            return False

    return len(config) > 0


def _convert_parameter_schema_to_array(_config: dict) -> list:
    """
    Convert old parameter schema format to minimal array format.

    Input (old - from setup command):
    {
        'domain': {'name': 'domain', 'type': 'string', 'defaultValue': 'example.com'},
        'include_number': {'name': 'include_number', 'type': 'boolean', 'defaultValue': True}
    }

    Output: [] (empty - all are defaults, backend will use function definition)

    Note: The old format only contains schema/defaults, not user-customized values.
    """
    # Old format only has defaults - return empty list
    # Backend will use function definition for defaults
    return []


def _convert_param_values_to_array(param_values: dict, param_schema: dict = None) -> list:
    """
    Convert parameterValues dict to array of {name, value}, omitting defaults.

    Input:
    param_values: {'domain': 'custom.com', 'include_number': True}
    param_schema: {'domain': {'defaultValue': 'example.com'}, 'include_number': {'defaultValue': True}}

    Output (only non-default values):
    [{'name': 'domain', 'value': 'custom.com'}]
    # 'include_number' is omitted because it matches the default
    """
    if not param_values:
        return []

    result = []
    for name, value in param_values.items():
        # Check if value matches default
        if param_schema and name in param_schema:
            schema_def = param_schema[name]
            if isinstance(schema_def, dict) and 'defaultValue' in schema_def:
                if value == schema_def['defaultValue']:
                    # Skip this parameter - it's the default
                    continue

        result.append({'name': name, 'value': value})

    return result


def _convert_parameters_object_to_array(parameters: dict) -> list:
    """
    Convert parameters object (with nested param definitions) to minimal array format.

    Input (from function config):
    {
        "value": {
            "name": "value",
            "type": "string",
            "description": "...",
            "defaultValue": "",
            "valueType": "reference",
            "value": null,
            "columnReference": "assigned_at",
            "tableReference": "user_roles"
        }
    }

    Output (minimal - only non-schema fields):
    [
        {
            "name": "value",
            "valueType": "reference",
            "columnReference": "assigned_at",
            "tableReference": "user_roles"
        }
    ]

    Fields to strip: type, description, defaultValue, required (schema metadata)
    Fields to keep: name, value, valueType, columnReference, tableReference, mode, filter, etc.
    """
    if not parameters:
        return []

    result = []
    # Fields that are user-provided values to keep (not schema metadata)
    value_fields = {'value', 'valueType', 'columnReference', 'tableReference',
                    'mode', 'filter', 'sourceTable', 'sourceColumn',
                    'reference_table', 'reference_column', 'source_table', 'source_column'}

    for param_name, param_def in parameters.items():
        if not isinstance(param_def, dict):
            continue

        # Build minimal parameter object
        param_obj = {'name': param_name}

        # Check if this has a reference type
        has_reference = any(k in param_def for k in ('valueType', 'columnReference', 'tableReference'))

        if has_reference:
            # Complex parameter with reference - keep all value fields
            for key in value_fields:
                if key in param_def:
                    val = param_def[key]
                    # Skip None/null values and empty strings for optional fields
                    if val is not None and val != '':
                        param_obj[key] = val
        elif 'value' in param_def and param_def['value'] is not None:
            # Simple value parameter - check if it matches default
            if 'defaultValue' in param_def and param_def['value'] == param_def['defaultValue']:
                # Skip this parameter - it matches the default
                continue
            param_obj['value'] = param_def['value']
        else:
            # No value set - skip this parameter (will use default)
            continue

        # Only add if we have more than just the name
        if len(param_obj) > 1:
            result.append(param_obj)

    return result
