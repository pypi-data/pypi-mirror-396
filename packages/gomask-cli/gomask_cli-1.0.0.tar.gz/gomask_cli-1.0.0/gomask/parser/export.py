"""
Export database routines to YAML format
"""

import re
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from gomask.schema.models import RoutineKind
from gomask.schema.defaults import (
    SYNTHETIC_SETTINGS_DEFAULTS,
    SYNTHETIC_TABLE_DEFAULTS,
    SYNTHETIC_COLUMN_DEFAULTS,
    MASKING_SETTINGS_DEFAULTS,
    MASKING_TABLE_DEFAULTS,
    MASKING_COLUMN_DEFAULTS,
    omit_defaults,
    strip_function_metadata,
)
from gomask.utils.logger import logger


class RoutineExporter:
    """Export routines from database to YAML format"""

    def __init__(self):
        self.yaml_dumper = yaml.SafeDumper
        # Configure YAML output format
        self.yaml_dumper.add_representer(
            type(None),
            lambda dumper, value: dumper.represent_scalar('tag:yaml.org,2002:null', '')
        )

    def export_routine(self, routine_data: Dict[str, Any]) -> str:
        """
        Export a routine from database format to YAML string

        Args:
            routine_data: Routine data from database

        Returns:
            YAML string representation
        """
        # Determine routine kind based on type
        routine_type = routine_data.get('type', 'synthetic')
        if routine_type == 'synthetic':
            yaml_data = self._build_synthetic_yaml(routine_data)
        elif routine_type == 'masking':
            yaml_data = self._build_masking_yaml(routine_data)
        else:
            raise ValueError(f"Unsupported routine type: {routine_type}")

        # Convert to YAML string
        return self._dict_to_yaml(yaml_data)

    def _build_synthetic_yaml(self, routine_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build YAML structure for synthetic routine"""
        yaml_data = {
            'version': '1.0',
            'kind': RoutineKind.SYNTHETIC.value,
            'metadata': self._build_metadata(routine_data),
            'connector': self._build_connector(routine_data),
        }

        # Add runtime parameters if present
        if routine_data.get('runtime_parameters'):
            yaml_data['runtime_parameters'] = routine_data['runtime_parameters']

        # Add generation settings
        if routine_data.get('generation'):
            yaml_data['generation'] = routine_data['generation']
        else:
            yaml_data['generation'] = {
                'mode': 'incremental',
                'batch_size': 1000
            }

        # Add tables
        yaml_data['tables'] = self._build_synthetic_tables(routine_data)

        # Add execution config if present
        if routine_data.get('execution'):
            yaml_data['execution'] = routine_data['execution']

        return yaml_data

    def _build_masking_yaml(self, routine_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build YAML structure for masking routine"""
        yaml_data = {
            'version': '1.0',
            'kind': RoutineKind.MASKING.value,
            'metadata': self._build_metadata(routine_data),
            'connector': self._build_connector(routine_data),
        }

        # Add runtime parameters if present
        if routine_data.get('runtime_parameters'):
            yaml_data['runtime_parameters'] = routine_data['runtime_parameters']

        # Add masking configuration
        yaml_data['masking'] = {
            'tables': self._build_masking_tables(routine_data)
        }

        # Add execution config if present
        if routine_data.get('execution'):
            yaml_data['execution'] = routine_data['execution']

        return yaml_data

    def _build_metadata(self, routine_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata section"""
        metadata = {
            'id': routine_data.get('unique_id') or f"routine-{routine_data.get('id')}",
            'name': routine_data.get('name', 'Unnamed Routine'),
        }

        if routine_data.get('description'):
            metadata['description'] = routine_data['description']

        if routine_data.get('version'):
            metadata['version'] = routine_data['version']

        return metadata

    def _build_connector(self, routine_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build connector section"""
        # If connector details are provided, use them
        if routine_data.get('connector'):
            connector = routine_data['connector']
            if isinstance(connector, dict):
                if connector.get('name'):
                    # Use reference to existing connector
                    return {'ref': connector['name']}
                else:
                    # Inline connector configuration
                    return {
                        'type': connector.get('type'),
                        'host': connector.get('host'),
                        'port': connector.get('port'),
                        'database': connector.get('database'),
                        'username': connector.get('username'),
                        'password': '${DB_PASSWORD}',  # Use env var for password
                    }

        # Default to reference by ID
        return {'ref': f"connector-{routine_data.get('connector_id')}"}

    def _build_synthetic_tables(self, routine_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build tables section for synthetic routine"""
        tables = []
        table_data = routine_data.get('tables', [])

        for table in table_data:
            table_config = {
                'name': table.get('name'),
                'schema': table.get('schema', 'public'),
                'hierarchy_level': table.get('hierarchy_level', 0),
            }

            if table.get('parent_table'):
                table_config['parent_table'] = table['parent_table']

            if table.get('record_count'):
                table_config['record_count'] = table['record_count']

            # Add columns
            table_config['columns'] = self._build_columns(table.get('columns', []))

            tables.append(table_config)

        return tables

    def _build_masking_tables(self, routine_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build tables section for masking routine"""
        tables = []
        table_data = routine_data.get('tables', [])

        for table in table_data:
            table_config = {
                'name': table.get('name'),
                'schema': table.get('schema', 'public'),
                'columns': []
            }

            # Add masking columns
            for column in table.get('columns', []):
                if column.get('masking_function'):
                    col_config = {
                        'name': column['column_name'],
                        'function': column['masking_function']
                    }
                    if column.get('masking_config'):
                        col_config['parameters'] = column['masking_config']
                    table_config['columns'].append(col_config)

            if table_config['columns']:  # Only add table if it has masked columns
                tables.append(table_config)

        return tables

    def _build_columns(self, columns_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build columns configuration"""
        columns = []

        for column in columns_data:
            col_config = {'name': column.get('column_name') or column.get('name')}

            # Add generation function
            if column.get('function'):
                col_config['function'] = column['function']
                if column.get('parameters'):
                    col_config['parameters'] = column['parameters']
            elif column.get('reference'):
                col_config['reference'] = column['reference']
            elif column.get('value') is not None:
                col_config['value'] = column['value']

            columns.append(col_config)

        return columns

    def _dict_to_yaml(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to formatted YAML string"""
        # Custom representer to format lists nicely
        def represent_list(dumper, data):
            if len(data) == 0:
                return dumper.represent_list([])
            return dumper.represent_list(data)

        self.yaml_dumper.add_representer(list, represent_list)

        return yaml.dump(
            data,
            Dumper=self.yaml_dumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
            indent=2
        )

    def export_to_file(self, routine_data: Dict[str, Any], file_path: Path) -> None:
        """
        Export routine to YAML file

        Args:
            routine_data: Routine data from database
            file_path: Path to save YAML file
        """
        yaml_content = self.export_routine(routine_data)

        # Add header comments
        header = f"""# GoMask Routine Configuration
# Generated: {datetime.now().isoformat()}
# Routine ID: {routine_data.get('id')}
# Name: {routine_data.get('name')}

"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(yaml_content)

        logger.info(f"Exported routine to {file_path}")


def export_routine_to_yaml(routine_data: Dict[str, Any], file_path: Optional[Path] = None) -> str:
    """
    Export a routine to YAML format

    Args:
        routine_data: Routine data from database (in schema format)
        file_path: Optional path to save the YAML file

    Returns:
        YAML string representation
    """
    # Check if data is in schema format (with 'routine' key)
    if 'routine' in routine_data:
        # This is the schema format from backend, convert it to simple YAML
        return export_schema_to_yaml(routine_data, file_path)
    else:
        # Old format, use the existing exporter
        exporter = RoutineExporter()
        if file_path:
            exporter.export_to_file(routine_data, file_path)
            return f"Exported to {file_path}"
        else:
            return exporter.export_routine(routine_data)


def export_schema_to_yaml(data: Dict[str, Any], file_path: Optional[Path] = None) -> str:
    """
    Export routine data in schema format to YAML

    Args:
        data: Routine data in schema format (with routine, settings, tables keys)
        file_path: Optional path to save the YAML file

    Returns:
        YAML string representation
    """
    # Create header
    routine = data.get('routine', {})
    header = f"""# GoMask Routine Configuration
# Generated: {datetime.now().isoformat()}
# Routine ID: {routine.get('unique_id')}
# Name: {routine.get('name')}
# Type: {routine.get('type')}

"""

    # Clean data by omitting default values
    cleaned_data = _clean_schema_data(data)

    # Convert the data to YAML
    yaml_content = yaml.dump(
        cleaned_data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
        indent=2
    )

    # Combine header and content
    full_content = header + yaml_content

    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        logger.info(f"Exported routine to {file_path}")
        return f"Exported to {file_path}"
    else:
        return full_content


def _clean_schema_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove default values from schema data to produce minimal YAML.
    """
    result = {}
    routine = data.get('routine', {})
    routine_type = routine.get('type', 'synthetic')

    # Copy routine section (required fields)
    result['routine'] = routine.copy()

    # Clean settings section
    if 'settings' in data:
        if routine_type == 'synthetic':
            cleaned_settings = omit_defaults(data['settings'], SYNTHETIC_SETTINGS_DEFAULTS)
        else:
            cleaned_settings = omit_defaults(data['settings'], MASKING_SETTINGS_DEFAULTS)
        # Only include settings if there are non-default values
        if cleaned_settings:
            result['settings'] = cleaned_settings

    # Clean tables section
    if 'tables' in data:
        if routine_type == 'synthetic':
            result['tables'] = _clean_synthetic_tables(data['tables'])
        else:
            result['tables'] = _clean_masking_tables(data['tables'])

    return result


def _clean_synthetic_tables(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean synthetic tables by omitting default values."""
    cleaned_tables = []

    for table in tables:
        cleaned_table = {}

        # Required field
        cleaned_table['table_name'] = table.get('table_name')

        # Only include non-default table fields
        table_fields = omit_defaults(table, SYNTHETIC_TABLE_DEFAULTS)
        for key in ['schema_name', 'table_type', 'hierarchy_level', 'order_index']:
            if key in table_fields:
                cleaned_table[key] = table_fields[key]

        # Include other non-default fields
        for key in ['parent_table_name', 'target_record_count', 'record_distribution']:
            if key in table and table[key] is not None:
                cleaned_table[key] = table[key]

        # Clean columns
        if 'columns' in table:
            cleaned_table['columns'] = _clean_synthetic_columns(table['columns'])

        cleaned_tables.append(cleaned_table)

    return cleaned_tables


def _clean_synthetic_columns(columns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean synthetic columns by omitting default values.

    Uses masking-style field names for consistency:
    - is_excluded (not enabled - inverted logic)
    - is_nullable (not nullable)
    - is_unique (not unique_constraint)
    - data_type (not original_data_type)
    - referenced_table/referenced_column (not reference_table/reference_column)
    """
    cleaned_columns = []

    for column in columns:
        cleaned_col = {}

        # Required field
        cleaned_col['column_name'] = column.get('column_name')

        # Normalize to masking-style names before processing
        # Handle both old (nullable) and new (is_nullable) field names
        normalized = {}
        for key, value in column.items():
            # Map old synthetic-style names to masking-style
            if key == 'enabled':
                # Invert: enabled=true -> is_excluded=false
                normalized['is_excluded'] = not value if isinstance(value, bool) else value
            elif key == 'nullable':
                normalized['is_nullable'] = value
            elif key == 'unique_constraint':
                normalized['is_unique'] = value
            elif key == 'original_data_type':
                normalized['data_type'] = value
            elif key == 'reference_table':
                normalized['referenced_table'] = value
            elif key == 'reference_column':
                normalized['referenced_column'] = value
            else:
                normalized[key] = value

        # Only include non-default boolean/metadata fields
        col_fields = omit_defaults(normalized, SYNTHETIC_COLUMN_DEFAULTS)
        for key in ['is_excluded', 'is_primary_key', 'is_foreign_key', 'is_nullable',
                    'is_unique', 'is_indexed', 'order_index']:
            if key in col_fields:
                cleaned_col[key] = col_fields[key]

        # Include other relevant fields (no defaults) - use masking-style names
        for key in ['data_type', 'generation_function',
                    'referenced_table', 'referenced_column', 'max_length', 'precision',
                    'scale', 'default_value', 'enum_values']:
            if key in normalized and normalized[key] is not None:
                cleaned_col[key] = normalized[key]

        # Strip function metadata from generation_parameters
        if 'generation_parameters' in column and column['generation_parameters'] is not None:
            cleaned_params = strip_function_metadata(column['generation_parameters'])
            if cleaned_params:  # Only include if there's something left
                cleaned_col['generation_parameters'] = cleaned_params

        cleaned_columns.append(cleaned_col)

    return cleaned_columns


def _clean_masking_tables(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean masking tables by omitting default values."""
    cleaned_tables = []

    for table in tables:
        cleaned_table = {}

        # Required field
        cleaned_table['table_name'] = table.get('table_name')

        # Only include non-default table fields
        table_fields = omit_defaults(table, MASKING_TABLE_DEFAULTS)
        if 'schema_name' in table_fields:
            cleaned_table['schema_name'] = table_fields['schema_name']

        # Clean columns
        if 'columns' in table:
            cleaned_table['columns'] = _clean_masking_columns(table['columns'])

        cleaned_tables.append(cleaned_table)

    return cleaned_tables


def _clean_masking_columns(columns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean masking columns by omitting default values."""
    cleaned_columns = []

    for column in columns:
        cleaned_col = {}

        # Required field
        cleaned_col['column_name'] = column.get('column_name')

        # Only include non-default boolean/metadata fields
        col_fields = omit_defaults(column, MASKING_COLUMN_DEFAULTS)
        for key in ['is_excluded', 'is_nullable', 'is_primary_key', 'is_foreign_key',
                    'is_unique', 'is_indexed', 'sensitivity_level', 'data_category']:
            if key in col_fields:
                cleaned_col[key] = col_fields[key]

        # Include other relevant fields (no defaults)
        for key in ['data_type', 'max_length', 'precision', 'scale', 'default_value',
                    'enum_values', 'masking_function']:
            if key in column and column[key] is not None:
                cleaned_col[key] = column[key]

        # Strip function metadata from masking_config
        if 'masking_config' in column and column['masking_config'] is not None:
            cleaned_config = strip_function_metadata(column['masking_config'])
            if cleaned_config:  # Only include if there's something left
                cleaned_col['masking_config'] = cleaned_config

        cleaned_columns.append(cleaned_col)

    return cleaned_columns


def create_yaml_from_template(
    routine_type: str,
    name: str,
    unique_id: Optional[str] = None
) -> str:
    """
    Create a new YAML configuration from template

    Args:
        routine_type: Type of routine ('synthetic' or 'masking')
        name: Name for the routine
        unique_id: Optional unique ID (will be generated if not provided)

    Returns:
        YAML string from template
    """
    if not unique_id:
        # Generate a unique ID from name
        unique_id = name.lower().replace(' ', '-').replace('_', '-')
        unique_id = re.sub(r'[^a-z0-9\-]', '', unique_id)

    if routine_type == 'synthetic':
        template = _get_synthetic_template(name, unique_id)
    elif routine_type == 'masking':
        template = _get_masking_template(name, unique_id)
    else:
        raise ValueError(f"Invalid routine type: {routine_type}")

    return template


def _get_synthetic_template(name: str, unique_id: str) -> str:
    """Get minimal synthetic routine template - defaults are applied automatically"""
    return f"""# GoMask Synthetic Data Generation Routine
# Generated: {datetime.now().isoformat()}
# Name: {name}
# Type: synthetic
#
# NOTE: Most fields have sensible defaults and can be omitted.
# generation_parameters uses array format: [{{"name": "param", "value": "val"}}]

routine:
  type: synthetic
  name: {name}
  unique_id: {unique_id}
  connector_id: 1  # CHANGE THIS: Set to your connector ID

settings:
  generation_mode: hierarchical
  batch_size: 1000
  parallel_workers: 4

tables:
  - table_name: customers
    target_record_count: 1000
    columns:
      # Primary keys: set is_primary_key and enabled: false
      - column_name: customer_id
        is_primary_key: true
        enabled: false

      # Regular columns: just specify generation function
      # generation_parameters is optional - omit to use function defaults
      - column_name: email
        generation_function: generate_email

      - column_name: first_name
        generation_function: generate_first_name

  # Child table example
  - table_name: orders
    parent_table_name: customers
    hierarchy_level: 1
    record_distribution:
      min_records_per_parent: 1
      max_records_per_parent: 5
    columns:
      - column_name: order_id
        is_primary_key: true
        enabled: false

      # Foreign key column - use column reference
      - column_name: customer_id
        is_foreign_key: true
        reference_table: customers
        reference_column: customer_id
        generation_function: return_value
        generation_parameters:
          - name: value
            valueType: reference
            columnReference: customer_id
            tableReference: customers
"""


def _get_masking_template(name: str, unique_id: str) -> str:
    """Get minimal masking routine template - defaults are applied automatically"""
    return f"""# GoMask Data Masking Routine
# Generated: {datetime.now().isoformat()}
# Name: {name}
# Type: masking
#
# NOTE: Most fields have sensible defaults and can be omitted.
# masking_config uses array format: [{{"name": "param", "value": "val"}}]

routine:
  type: masking
  name: {name}
  unique_id: {unique_id}
  connector_id: 1  # CHANGE THIS: Set to your connector ID

settings:
  batch_size: 1000
  parallel_workers: 4
  audit_reporting_enabled: true

tables:
  - table_name: example_table
    columns:
      # Exclude columns you don't want to mask (e.g., PKs)
      - column_name: id
        is_excluded: true

      # Columns to mask: specify masking_function
      # masking_config is optional - omit to use function defaults
      - column_name: email
        masking_function: generate_email

      - column_name: first_name
        masking_function: generate_first_name

      # Columns without masking_function are excluded by default
      - column_name: created_at
        is_excluded: true
"""