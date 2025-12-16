"""
Validation utilities for YAML configurations
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

import yaml
from pydantic import ValidationError

from gomask.schema.models import (
    SyntheticRoutineConfig,
    MaskingRoutineConfig,
    RoutineKind,
    validate_unique_id
)
from gomask.utils.logger import logger


class ValidationResult:
    """Container for validation results"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.is_valid: bool = True

    def add_error(self, message: str) -> None:
        """Add an error message"""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message"""
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        """Add an info message"""
        self.info.append(message)

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """Get a summary of the validation results"""
        lines = []

        if self.errors:
            lines.append("❌ Errors:")
            for error in self.errors:
                lines.append(f"  - {error}")

        if self.warnings:
            lines.append("⚠️  Warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        if self.info:
            lines.append("ℹ️  Info:")
            for info_msg in self.info:
                lines.append(f"  - {info_msg}")

        if not self.errors and not self.warnings:
            lines.append("✅ Configuration is valid")

        return "\n".join(lines)


class YAMLValidator:
    """Validator for YAML routine configurations"""

    def __init__(self):
        self.result = ValidationResult()

    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Validate a YAML configuration file

        Args:
            file_path: Path to the YAML file

        Returns:
            ValidationResult with errors, warnings, and info
        """
        self.result = ValidationResult()

        # Check if file exists
        if not file_path.exists():
            self.result.add_error(f"File not found: {file_path}")
            return self.result

        # Check file extension
        if file_path.suffix.lower() not in ['.yaml', '.yml']:
            self.result.add_warning(f"File extension is not .yaml or .yml: {file_path}")

        # Try to load and parse YAML
        try:
            with open(file_path, 'r') as f:
                yaml_content = f.read()
        except Exception as e:
            self.result.add_error(f"Failed to read file: {e}")
            return self.result

        return self.validate_content(yaml_content)

    def validate_content(self, yaml_content: str) -> ValidationResult:
        """
        Validate YAML content string

        Args:
            yaml_content: YAML content as string

        Returns:
            ValidationResult with errors, warnings, and info
        """
        self.result = ValidationResult()

        # Parse YAML
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            self.result.add_error(f"Invalid YAML syntax: {e}")
            return self.result

        if not isinstance(data, dict):
            self.result.add_error("YAML must contain a dictionary at root level")
            return self.result

        return self.validate_data(data)

    def validate_data(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate parsed YAML data

        Args:
            data: Parsed YAML dictionary

        Returns:
            ValidationResult with errors, warnings, and info
        """
        self.result = ValidationResult()

        # Check required fields
        if 'version' not in data:
            self.result.add_error("Missing required field: version")

        if 'kind' not in data:
            self.result.add_error("Missing required field: kind")
        else:
            kind = data.get('kind')
            if kind not in [RoutineKind.SYNTHETIC.value, RoutineKind.MASKING.value]:
                self.result.add_error(
                    f"Invalid kind: {kind}. Must be 'SyntheticRoutine' or 'MaskingRoutine'"
                )

        if 'metadata' not in data:
            self.result.add_error("Missing required field: metadata")
        else:
            self._validate_metadata(data['metadata'])

        if 'connector' not in data:
            self.result.add_error("Missing required field: connector")
        else:
            self._validate_connector(data['connector'])

        # Validate based on kind
        kind = data.get('kind')
        if kind == RoutineKind.SYNTHETIC.value:
            self._validate_synthetic_config(data)
        elif kind == RoutineKind.MASKING.value:
            self._validate_masking_config(data)

        # Try to parse with Pydantic models for complete validation
        if not self.result.has_errors():
            try:
                if kind == RoutineKind.SYNTHETIC.value:
                    SyntheticRoutineConfig(**data)
                elif kind == RoutineKind.MASKING.value:
                    MaskingRoutineConfig(**data)
                self.result.add_info("Configuration passed Pydantic model validation")
            except ValidationError as e:
                for error in e.errors():
                    field_path = " -> ".join(str(loc) for loc in error['loc'])
                    self.result.add_error(f"{field_path}: {error['msg']}")

        return self.result

    def _validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """Validate metadata section"""
        if not isinstance(metadata, dict):
            self.result.add_error("metadata must be a dictionary")
            return

        if 'id' not in metadata:
            self.result.add_error("metadata.id is required")
        else:
            unique_id = metadata['id']
            if not validate_unique_id(unique_id):
                self.result.add_error(
                    f"Invalid metadata.id: {unique_id}. "
                    "Must be 3-255 characters, alphanumeric with hyphens, underscores, and forward slashes. "
                    "Must start and end with alphanumeric character."
                )

        if 'name' not in metadata:
            self.result.add_error("metadata.name is required")

        # Check for recommended fields
        if 'description' not in metadata:
            self.result.add_info("Consider adding metadata.description for better documentation")

        if 'version' in metadata:
            version = metadata['version']
            if not re.match(r'^\d+\.\d+\.\d+(-[\w.]+)?(\+[\w.]+)?$', version):
                self.result.add_warning(
                    f"metadata.version '{version}' doesn't follow semantic versioning (e.g., 1.0.0)"
                )

    def _validate_connector(self, connector: Dict[str, Any]) -> None:
        """Validate connector section"""
        if not isinstance(connector, dict):
            self.result.add_error("connector must be a dictionary")
            return

        # Check if it's a reference or inline
        has_ref = 'ref' in connector
        has_inline = any(key in connector for key in ['type', 'host', 'database'])

        if not has_ref and not has_inline:
            self.result.add_error("connector must have either 'ref' for existing connector or inline configuration")
        elif has_ref and has_inline:
            self.result.add_warning("connector has both 'ref' and inline fields; 'ref' will take precedence")

        if has_inline and not has_ref:
            # Validate inline connector
            required_fields = ['type', 'host', 'port', 'database', 'username', 'password']
            for field in required_fields:
                if field not in connector:
                    self.result.add_error(f"connector.{field} is required for inline configuration")

            # Validate port
            if 'port' in connector:
                port = connector['port']
                if not isinstance(port, int) or port < 1 or port > 65535:
                    self.result.add_error(f"connector.port must be an integer between 1 and 65535")

            # Check for environment variables in sensitive fields
            if 'password' in connector and not connector['password'].startswith('${'):
                self.result.add_warning(
                    "Consider using environment variable for connector.password (e.g., ${DB_PASSWORD})"
                )

    def _validate_synthetic_config(self, data: Dict[str, Any]) -> None:
        """Validate synthetic routine specific configuration"""
        if 'tables' not in data:
            self.result.add_error("'tables' section is required for SyntheticRoutine")
            return

        tables = data.get('tables', [])
        if not isinstance(tables, list):
            self.result.add_error("'tables' must be a list")
            return

        if len(tables) == 0:
            self.result.add_error("At least one table must be defined")
            return

        # Validate each table
        table_names = set()
        hierarchy_levels = {}

        for i, table in enumerate(tables):
            if not isinstance(table, dict):
                self.result.add_error(f"Table at index {i} must be a dictionary")
                continue

            # Check table name
            if 'name' not in table:
                self.result.add_error(f"Table at index {i} missing required field: name")
            else:
                table_name = table['name']
                if table_name in table_names:
                    self.result.add_error(f"Duplicate table name: {table_name}")
                table_names.add(table_name)

            # Check hierarchy level
            hierarchy_level = table.get('hierarchy_level', 0)
            if table_name:
                hierarchy_levels[table_name] = hierarchy_level

            # Check parent table reference
            if 'parent_table' in table:
                parent = table['parent_table']
                if parent and parent not in table_names:
                    self.result.add_warning(
                        f"Table '{table.get('name', i)}' references unknown parent table: {parent}"
                    )

            # Check columns
            if 'columns' not in table:
                self.result.add_error(f"Table '{table.get('name', i)}' missing required field: columns")
            else:
                self._validate_table_columns(table['columns'], table.get('name', f'table_{i}'))

    def _validate_masking_config(self, data: Dict[str, Any]) -> None:
        """Validate masking routine specific configuration"""
        if 'masking' not in data:
            self.result.add_error("'masking' section is required for MaskingRoutine")
            return

        masking = data.get('masking', {})
        if not isinstance(masking, dict):
            self.result.add_error("'masking' must be a dictionary")
            return

        if 'tables' not in masking:
            self.result.add_error("masking.tables is required")
            return

        tables = masking.get('tables', [])
        if not isinstance(tables, list):
            self.result.add_error("masking.tables must be a list")
            return

        if len(tables) == 0:
            self.result.add_error("At least one table must be defined for masking")
            return

        # Validate each table
        for i, table in enumerate(tables):
            if not isinstance(table, dict):
                self.result.add_error(f"Masking table at index {i} must be a dictionary")
                continue

            if 'name' not in table:
                self.result.add_error(f"Masking table at index {i} missing required field: name")

            if 'columns' not in table:
                self.result.add_error(f"Masking table '{table.get('name', i)}' missing required field: columns")
            else:
                self._validate_masking_columns(table['columns'], table.get('name', f'table_{i}'))

    def _validate_table_columns(self, columns: List[Dict[str, Any]], table_name: str) -> None:
        """Validate synthetic table columns"""
        if not isinstance(columns, list):
            self.result.add_error(f"Table '{table_name}' columns must be a list")
            return

        if len(columns) == 0:
            self.result.add_warning(f"Table '{table_name}' has no columns defined")
            return

        column_names = set()
        for i, column in enumerate(columns):
            if not isinstance(column, dict):
                self.result.add_error(f"Column at index {i} in table '{table_name}' must be a dictionary")
                continue

            if 'name' not in column:
                self.result.add_error(f"Column at index {i} in table '{table_name}' missing required field: name")
            else:
                col_name = column['name']
                if col_name in column_names:
                    self.result.add_error(f"Duplicate column name '{col_name}' in table '{table_name}'")
                column_names.add(col_name)

            # Check that column has either function, reference, or value
            has_generator = any(key in column for key in ['function', 'reference', 'value'])
            if not has_generator:
                self.result.add_warning(
                    f"Column '{column.get('name', i)}' in table '{table_name}' has no data generator"
                )

    def _validate_masking_columns(self, columns: List[Dict[str, Any]], table_name: str) -> None:
        """Validate masking table columns"""
        if not isinstance(columns, list):
            self.result.add_error(f"Masking table '{table_name}' columns must be a list")
            return

        if len(columns) == 0:
            self.result.add_warning(f"Masking table '{table_name}' has no columns defined")
            return

        for i, column in enumerate(columns):
            if not isinstance(column, dict):
                self.result.add_error(f"Column at index {i} in masking table '{table_name}' must be a dictionary")
                continue

            if 'name' not in column:
                self.result.add_error(f"Column at index {i} in masking table '{table_name}' missing required field: name")

            if 'function' not in column:
                self.result.add_error(
                    f"Column '{column.get('name', i)}' in masking table '{table_name}' missing required field: function"
                )