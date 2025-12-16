# GoMask CLI Configuration Schemas

## Overview

This directory contains JSON Schema definitions for GoMask routine configurations. These schemas validate YAML configuration files used by the GoMask CLI to create and manage data masking and synthetic data generation routines.

## Schema Files

### Core Schemas

1. **`masking-routine-schema.json`** - Complete schema for data masking routines
2. **`synthetic-routine-schema.json`** - Complete schema for synthetic data generation routines
3. **`unified-routine-schema.json`** - Unified schema that supports both routine types

### Schema Structure to Database Mapping

The schemas are designed to directly map to the database tables populated by the routine setup orchestrator:

## Data Masking Schema → Database Mapping

| YAML Section | Database Table | Key Fields |
|--------------|---------------|------------|
| `routine.*` | `routines` | `name`, `description`, `type`, `connector_id` |
| `settings.*` | `masking_settings` | `batch_size`, `parallel_workers`, `audit_reporting_enabled`, `localization_*` |
| `tables[]` | `routine_tables` | `table_name`, `schema_name`, `status` |
| `tables[].columns[]` | `routine_columns` | `column_name`, `data_type`, `sensitivity_level`, `data_category` |
| `tables[].columns[].masking_config` | `routine_columns.masking_config` (JSON) | Complex masking function configuration |

### Masking Config JSON Structure

The `masking_config` field in `routine_columns` table stores:

```json
{
  "type": "library|custom|builtin",
  "name": "function_name",
  "function_id": 123,
  "code": "custom code if type=custom",
  "parameters": {
    "param1": "value1",
    "param2": {
      "valueType": "static|column",
      "value": "actual_value",
      "columnReference": "referenced_column",
      "defaultValue": "default_value"
    }
  }
}
```

## Synthetic Data Schema → Database Mapping

| YAML Section | Database Table | Key Fields |
|--------------|---------------|------------|
| `routine.*` | `routines` | `name`, `description`, `type`, `connector_id` |
| `settings.*` | `synthetic_data_settings` | `generation_mode`, `batch_size`, `parallel_workers`, `enforce_referential_integrity` |
| `settings.runtime_parameters` | `synthetic_data_settings.runtime_parameter_definitions` (JSON) | Runtime parameter schemas |
| `table_hierarchy.*` | `synthetic_table_hierarchy` | Parent-child relationships and generation order |
| `tables[]` | `routine_tables` + `synthetic_table_hierarchy` | Table metadata and hierarchy |
| `tables[].columns[]` | `routine_columns` + `synthetic_column_config` | Column metadata and generation config |
| `tables[].record_distribution` | `synthetic_record_distribution` | Child record distribution patterns |
| `tables[].columns[].generation_parameters` | `synthetic_column_config.generation_parameters` (JSON) | Generation function configuration |

### Generation Parameters JSON Structures

#### Standard Function Configuration
```json
{
  "type": "library",
  "functionId": 123,
  "name": "generate_first_name",
  "description": "Generates random first names",
  "category": "personal",
  "functionType": "generator",
  "parameters": {
    "gender": {"type": "string", "defaultValue": "any"},
    "locale": {"type": "string", "defaultValue": "en_US"}
  },
  "parameterValues": {
    "gender": "female",
    "locale": "fr_FR"
  }
}
```

#### Foreign Key Reference (within routine)
```json
{
  "mode": "column_reference",
  "reference_table": "parent_table",
  "reference_column": "id_column"
}
```

#### Random Existing Value (external table or self-reference)
```json
{
  "source_table": "referenced_table",
  "source_column": "referenced_column",
  "filter": "is_active = true"
}
```

## Usage

### 1. Validate a Configuration File

```bash
# Using a JSON Schema validator
npx ajv validate -s gomask/schema/masking-routine-schema.json -d my-masking-config.yaml --spec=draft7

# Or with Python
python -m jsonschema -i my-masking-config.yaml gomask/schema/masking-routine-schema.json
```

### 2. Import Configuration via CLI

```bash
# Import a masking routine
gomask import routine my-masking-config.yaml

# Import a synthetic data routine
gomask import routine synthetic-config.yaml

# Validate without importing
gomask validate routine my-config.yaml
```

### 3. Export Existing Routine

```bash
# Export routine configuration to YAML
gomask export routine <routine_id> -o exported-routine.yaml
```

## Key Features

### Type Safety
- Enums for all categorical values (sensitivity levels, data categories, etc.)
- Proper type definitions for all fields
- Required field validation

### Foreign Key Intelligence

The schemas handle three types of foreign key scenarios:

1. **Parent-Child within Routine**: Uses `column_reference` mode
2. **Self-Referencing**: Uses `random_existing_value` to avoid circular references
3. **External References**: Uses `random_existing_value` from source table

### Hierarchical Generation

For synthetic data, tables are organized in hierarchy levels:
- Level 0: Root tables (no foreign keys to other tables in routine)
- Level 1: Direct children of root tables
- Level 2+: Nested relationships

### Distribution Patterns

Synthetic data supports multiple distribution types for child records:
- `uniform`: Even distribution between min and max
- `normal`: Bell curve distribution
- `poisson`: Poisson distribution for realistic patterns
- `custom`: User-defined weights and values
- `fixed`: Exact number per parent

### Localization Support

Both schemas support localization settings:
- Language codes (ISO 639-1)
- Region codes (ISO 3166-1)
- Affects generated names, addresses, phone numbers, etc.

## Examples

See the `/examples` directory for complete working examples:
- `masking-routine-example.yaml` - Comprehensive masking configuration
- `synthetic-routine-example.yaml` - E-commerce test data generation

## Validation Rules

### Masking Routines
- At least one table must be defined
- Each column must have either `exclude: true` or a masking function
- Sensitive columns should have `sensitivity_level` defined
- Custom functions must include valid code

### Synthetic Routines
- Tables must form a valid hierarchy
- Foreign keys must reference existing tables
- Primary keys should have `enabled: false` (auto-generated)
- Distribution weights must sum to a positive number

## Extension Points

### Custom Functions

Both schemas support custom function definitions:

```yaml
# Masking custom function
masking_config:
  type: "custom"
  code: |
    def mask(value):
        # Custom masking logic
        return masked_value

# Synthetic custom function
generation_parameters:
  type: "custom"
  code: |
    def generate():
        # Custom generation logic
        return generated_value
```

### Runtime Parameters

Synthetic routines support runtime parameters:

```yaml
runtime_parameters:
  scale_factor:
    type: "float"
    defaultValue: 1.0
    description: "Multiply all record counts"
    min: 0.1
    max: 10.0
```

### Post-Processing

Both schemas support post-processing steps:

```yaml
post_processing:
  - type: "sql"
    sql: "UPDATE table SET column = value"
  - type: "validation"
    sql: "SELECT COUNT(*) FROM table WHERE condition"
```

## Best Practices

1. **Start Small**: Begin with a subset of tables and expand
2. **Test Thoroughly**: Validate configurations before production use
3. **Use Profiles**: Define data profiles for different test scenarios
4. **Document Functions**: Include descriptions for custom functions
5. **Version Control**: Store configurations in version control
6. **Parameterize**: Use runtime parameters for flexibility

## Schema Versioning

The schemas use semantic versioning:
- Current version: `v1.0.0`
- Breaking changes increment major version
- New features increment minor version
- Bug fixes increment patch version

## Contributing

To modify or extend the schemas:

1. Update the JSON schema files
2. Update examples to demonstrate new features
3. Test with multiple validators
4. Update this documentation
5. Increment version numbers appropriately

## Related Documentation

- [Routine Setup Orchestrator Analysis](../../ROUTINE_SETUP_TABLES_ANALYSIS.md)
- [Database Schema Documentation](../../db-service/docs/database-schema.md)
- [API Documentation](../../db-service/docs/api.md)