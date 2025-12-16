"""
Pydantic models for YAML configuration validation
"""

import re
from typing import Optional, Dict, Any, List, Union, Literal
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field, validator, ValidationError, ConfigDict


class RoutineKind(str, Enum):
    """Routine types supported by the CLI"""
    SYNTHETIC = "SyntheticRoutine"
    MASKING = "MaskingRoutine"


class RoutineType(str, Enum):
    """Routine types for database storage"""
    SYNTHETIC = "synthetic"
    MASKING = "masking"
    AI_SCENARIO = "ai_scenario"


class SourceType(str, Enum):
    """Source of routine creation"""
    UI = "ui"
    CLI = "cli"
    API = "api"


class Metadata(BaseModel):
    """Metadata for routine identification"""
    id: str = Field(..., description="Unique identifier for the routine")
    name: str = Field(..., description="Human-readable name")
    description: Optional[str] = Field(None, description="Detailed description")
    version: Optional[str] = Field("1.0.0", description="Semantic version")
    type: Optional[RoutineType] = Field(None, description="Routine type")

    @validator('id')
    def validate_id(cls, v):
        """Validate unique ID format"""
        if not validate_unique_id(v):
            raise ValueError(
                f"Invalid ID format: {v}. "
                "Must be 3-255 characters, alphanumeric with hyphens, underscores, and forward slashes. "
                "Must start and end with alphanumeric character."
            )
        return v

    @validator('version')
    def validate_version(cls, v):
        """Validate semantic version format"""
        if v and not re.match(r'^\d+\.\d+\.\d+(-[\w.]+)?(\+[\w.]+)?$', v):
            raise ValueError(f"Invalid version format: {v}. Use semantic versioning (e.g., 1.0.0)")
        return v


class ConnectorRef(BaseModel):
    """Reference to an existing connector"""
    ref: str = Field(..., description="Name of the existing connector")


class ConnectorConfig(BaseModel):
    """Inline connector configuration"""
    name: str = Field(..., description="Connector name")
    type: str = Field(..., description="Database type")
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    ssl_mode: Optional[str] = Field("prefer", description="SSL mode")
    additional_params: Optional[Dict[str, Any]] = Field({}, description="Additional parameters")


class Connector(BaseModel):
    """Connector configuration - either reference or inline"""
    ref: Optional[str] = Field(None, description="Reference to existing connector")
    name: Optional[str] = Field(None, description="Connector name (for inline)")
    type: Optional[str] = Field(None, description="Database type")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: Optional[str] = Field(None, description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")
    ssl_mode: Optional[str] = Field("prefer", description="SSL mode")

    @validator('port')
    def validate_port(cls, v):
        """Validate port number"""
        if v is not None and (v < 1 or v > 65535):
            raise ValueError(f"Invalid port number: {v}. Must be between 1 and 65535.")
        return v

    def is_reference(self) -> bool:
        """Check if this is a connector reference"""
        return self.ref is not None

    def is_inline(self) -> bool:
        """Check if this is an inline connector configuration"""
        return self.name is not None and self.type is not None


class RuntimeParameter(BaseModel):
    """Runtime parameter definition"""
    type: Literal["integer", "float", "string", "boolean"] = Field(..., description="Parameter type")
    default: Any = Field(None, description="Default value")
    description: Optional[str] = Field(None, description="Parameter description")
    min: Optional[Union[int, float]] = Field(None, description="Minimum value (numeric types)")
    max: Optional[Union[int, float]] = Field(None, description="Maximum value (numeric types)")
    pattern: Optional[str] = Field(None, description="Regex pattern (string type)")
    choices: Optional[List[Any]] = Field(None, description="List of valid choices")


class FunctionCall(BaseModel):
    """Function call for column data generation"""
    function: str = Field(..., description="Function name")
    parameters: Optional[Dict[str, Any]] = Field({}, description="Function parameters")


class ColumnReference(BaseModel):
    """Reference to another table's column"""
    table: str = Field(..., description="Referenced table name")
    column: str = Field(..., description="Referenced column name")


class ColumnDefinition(BaseModel):
    """Column definition for synthetic data generation"""
    name: str = Field(..., description="Column name")
    function: Optional[str] = Field(None, description="Generation function")
    parameters: Optional[Dict[str, Any]] = Field({}, description="Function parameters")
    reference: Optional[ColumnReference] = Field(None, description="Foreign key reference")
    value: Optional[Any] = Field(None, description="Constant value")


class MaskingColumn(BaseModel):
    """Column masking configuration"""
    name: str = Field(..., description="Column name")
    function: str = Field(..., description="Masking function")
    parameters: Optional[Dict[str, Any]] = Field({}, description="Function parameters")


class TableDefinition(BaseModel):
    """Table definition for synthetic data generation"""
    model_config = ConfigDict(populate_by_name=True)  # Allow both 'schema' and 'db_schema'

    name: str = Field(..., description="Table name")
    db_schema: str = Field("public", alias="schema", description="Database schema")
    hierarchy_level: int = Field(0, description="Generation hierarchy level")
    parent_table: Optional[str] = Field(None, description="Parent table for foreign keys")
    record_count: Optional[Union[int, str]] = Field(None, description="Number of records or formula")
    record_count_formula: Optional[str] = Field(None, description="Record count formula")
    columns: List[ColumnDefinition] = Field(..., description="Column definitions")


class MaskingTable(BaseModel):
    """Table masking configuration"""
    model_config = ConfigDict(populate_by_name=True)  # Allow both 'schema' and 'db_schema'

    name: str = Field(..., description="Table name")
    db_schema: str = Field("public", alias="schema", description="Database schema")
    columns: List[MaskingColumn] = Field(..., description="Column masking configurations")


class SyntheticGeneration(BaseModel):
    """Synthetic data generation configuration"""
    mode: Literal["incremental", "replace"] = Field("incremental", description="Generation mode")
    batch_size: int = Field(1000, description="Batch size for processing")
    global_record_count: Optional[int] = Field(1, description="Global record multiplier")


class MaskingConfiguration(BaseModel):
    """Data masking configuration"""
    tables: List[MaskingTable] = Field(..., description="Tables to mask")


class ExecutionConfig(BaseModel):
    """Execution configuration"""
    timeout: Optional[int] = Field(3600, description="Execution timeout in seconds")
    batch_size: Optional[int] = Field(1000, description="Processing batch size")


class SyntheticRoutineConfig(BaseModel):
    """Complete synthetic routine configuration"""
    model_config = ConfigDict(extra="allow")  # Allow additional fields for forward compatibility

    version: str = Field("1.0", description="Configuration version")
    kind: Literal["SyntheticRoutine"] = Field(..., description="Routine kind")
    metadata: Metadata = Field(..., description="Routine metadata")
    connector: Connector = Field(..., description="Database connector")
    runtime_parameters: Optional[Dict[str, RuntimeParameter]] = Field({}, description="Runtime parameters")
    generation: Optional[SyntheticGeneration] = Field(None, description="Generation settings")
    synthetic: Optional[SyntheticGeneration] = Field(None, description="Alternative generation settings key")
    tables: List[TableDefinition] = Field(..., description="Table definitions")
    execution: Optional[ExecutionConfig] = Field(None, description="Execution configuration")


class MaskingRoutineConfig(BaseModel):
    """Complete masking routine configuration"""
    model_config = ConfigDict(extra="allow")  # Allow additional fields for forward compatibility

    version: str = Field("1.0", description="Configuration version")
    kind: Literal["MaskingRoutine"] = Field(..., description="Routine kind")
    metadata: Metadata = Field(..., description="Routine metadata")
    connector: Connector = Field(..., description="Database connector")
    runtime_parameters: Optional[Dict[str, RuntimeParameter]] = Field({}, description="Runtime parameters")
    masking: MaskingConfiguration = Field(..., description="Masking configuration")
    execution: Optional[ExecutionConfig] = Field(None, description="Execution configuration")


def validate_unique_id(unique_id: str) -> bool:
    """
    Validate the unique ID format

    Args:
        unique_id: The unique ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not unique_id or len(unique_id) < 3 or len(unique_id) > 255:
        return False

    # Pattern: start with alphanumeric, contain alphanumeric/hyphen/underscore/slash, end with alphanumeric
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-_/]*[a-zA-Z0-9]$'

    # Handle single or two character IDs
    if len(unique_id) < 3:
        pattern = r'^[a-zA-Z0-9]+$'

    return bool(re.match(pattern, unique_id))


def parse_routine_config(yaml_data: Dict[str, Any]) -> Union[SyntheticRoutineConfig, MaskingRoutineConfig]:
    """
    Parse YAML data into the appropriate routine configuration model

    Args:
        yaml_data: Parsed YAML dictionary

    Returns:
        Validated routine configuration

    Raises:
        ValidationError: If the configuration is invalid
    """
    kind = yaml_data.get('kind')

    if kind == RoutineKind.SYNTHETIC.value:
        return SyntheticRoutineConfig(**yaml_data)
    elif kind == RoutineKind.MASKING.value:
        return MaskingRoutineConfig(**yaml_data)
    else:
        raise ValidationError(
            f"Invalid routine kind: {kind}. Must be either 'SyntheticRoutine' or 'MaskingRoutine'"
        )