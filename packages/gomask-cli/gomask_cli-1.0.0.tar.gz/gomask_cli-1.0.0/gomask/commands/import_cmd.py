"""
Import YAML configuration to database
"""

from pathlib import Path
from typing import Optional, Dict, Any

import click

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.api.routines import RoutinesAPI
from gomask.utils.output import console, print_success, print_error, print_warning
from gomask.utils.logger import logger
from gomask.validators import (
    load_yaml_file,
    validate_routine_config,
    get_validation_errors,
    suggest_fixes,
    determine_routine_type
)
from gomask.schema.defaults import apply_config_defaults


@click.command('import')
@click.argument(
    'yaml_file',
    type=click.Path(exists=True, readable=True, path_type=Path)
)
@click.option(
    '--env-file',
    type=click.Path(exists=True, readable=True, path_type=Path),
    help='Path to .env file for environment variables'
)
@click.option(
    '--update',
    '-u',
    is_flag=True,
    help='Update existing routine if unique ID exists'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Validate without importing'
)
@click.option(
    '--skip-validation',
    is_flag=True,
    help='Skip schema validation (not recommended)'
)
@click.option(
    '--param',
    multiple=True,
    help='Runtime parameter in format key=value'
)
@click.pass_context
def import_yaml(
    ctx: click.Context,
    yaml_file: Path,
    env_file: Optional[Path],
    update: bool,
    dry_run: bool,
    skip_validation: bool,
    param: tuple
) -> None:
    """
    Import a YAML routine configuration to the database

    Validates the configuration against JSON schemas and creates or updates
    the routine in the database.

    \b
    Examples:
        gomask import routine.yaml
        gomask import routine.yaml --update
        gomask import routine.yaml --dry-run
        gomask import routine.yaml --param record_count=1000
    """
    try:
        console.print(f"[cyan]Importing configuration from:[/cyan] {yaml_file}")

        # Load YAML file with optional env file support
        try:
            config = load_yaml_file(str(yaml_file), env_file)
        except Exception as e:
            print_error(f"Failed to load YAML: {e}")
            ctx.exit(1)

        # Apply default values to missing fields
        config = apply_config_defaults(config)

        # Apply runtime parameters if provided
        if param:
            config = apply_runtime_parameters(config, param)

        # Validate configuration against schema
        if not skip_validation:
            console.print("[cyan]Validating configuration...[/cyan]")
            is_valid, error_msg = validate_routine_config(config)

            if not is_valid:
                print_error("Configuration validation failed:")
                console.print(error_msg)

                # Show detailed errors and suggestions
                errors = get_validation_errors(config)
                if errors:
                    suggestions = suggest_fixes(errors)
                    if suggestions:
                        console.print("\n[yellow]Suggestions:[/yellow]")
                        for suggestion in suggestions[:5]:
                            console.print(f"  - {suggestion}")

                ctx.exit(1)

            console.print("[green][VALID][/green] Configuration is valid")

        # Extract routine info
        routine_type = determine_routine_type(config)
        routine_info = config.get('routine', {})
        name = routine_info.get('name', 'Unnamed')
        description = routine_info.get('description', '')

        console.print(f"\n[bold]Routine Information:[/bold]")
        console.print(f"  - Name: {name}")
        console.print(f"  - Type: {routine_type}")
        if description:
            console.print(f"  - Description: {description}")

        # Get table count
        tables = config.get('tables', [])
        console.print(f"  - Tables: {len(tables)}")

        if dry_run:
            print_success("Dry run complete - configuration is valid")
            console.print("\n[yellow]No changes made (dry run mode)[/yellow]")
            return


        # Check authentication
        secret = ctx.obj.get('SECRET')
        api_url = ctx.obj.get('API_URL')

        if not secret:
            print_error("Authentication required. Set GOMASK_SECRET environment variable.")
            ctx.exit(1)

        # Connect to API
        with GoMaskAPIClient(base_url=api_url, secret=secret) as client:
            routines_api = RoutinesAPI(client)

            # Import the routine using the new schema format
            try:
                # The import_yaml method handles checking for existing routines
                result = routines_api.import_yaml(config)

                # Extract result details
                routine_id = result.get('id')
                status = result.get('status', 'imported')
                message = result.get('message', 'Routine imported successfully')

                if status == 'updated' or update:
                    print_success(f"Updated routine ID {routine_id}")
                else:
                    print_success(f"Created routine ID {routine_id}")

                # Display summary
                console.print("\n[bold]Import Summary:[/bold]")
                console.print(f"  - Routine ID: {routine_id}")
                console.print(f"  - Name: {name}")
                console.print(f"  - Type: {routine_type}")
                console.print(f"  - Tables: {len(tables)}")
                console.print(f"  - Status: {status}")
                console.print(f"  - Message: {message}")

                # Show settings summary if present
                if 'settings' in config and config['settings']:
                    settings = config['settings']
                    console.print("\n[bold]Settings:[/bold]")
                    if routine_type == 'synthetic':
                        console.print(f"  - Generation Mode: {settings.get('generation_mode', 'hierarchical')}")
                        console.print(f"  - Global Record Count: {settings.get('global_record_count', 1000)}")
                        console.print(f"  - Batch Size: {settings.get('batch_size', 1000)}")
                    elif routine_type == 'masking':
                        console.print(f"  - Batch Size: {settings.get('batch_size', 1000)}")
                        console.print(f"  - Audit Reporting: {settings.get('audit_reporting_enabled', True)}")

                console.print("\n[bold]Next steps:[/bold]")
                console.print(f"1. View routine details: gomask routines show {routine_id}")
                console.print(f"2. Export to YAML: gomask export --routine-id {routine_id}")
                console.print(f"3. Run routine: gomask run <yaml_file> --watch")

            except APIError as e:
                print_error(f"Failed to import routine: {e.message if hasattr(e, 'message') else str(e)}")
                if hasattr(e, 'details'):
                    console.print("[yellow]Details:[/yellow]")
                    for detail in e.details:
                        console.print(f"  - {detail}")
                ctx.exit(1)

    except Exception as e:
        print_error(f"Import failed: {e}")
        logger.exception("Error in import command")
        ctx.exit(1)


def apply_runtime_parameters(config: Dict[str, Any], params: tuple) -> Dict[str, Any]:
    """
    Apply runtime parameters to the configuration.

    Args:
        config: The configuration dictionary
        params: Tuple of key=value parameter strings

    Returns:
        Updated configuration dictionary
    """
    if not params:
        return config

    console.print("[cyan]Applying runtime parameters:[/cyan]")

    for param_str in params:
        if '=' not in param_str:
            console.print(f"  [yellow]Skipping invalid parameter: {param_str}[/yellow]")
            continue

        key, value = param_str.split('=', 1)
        console.print(f"  - {key} = {value}")

        # Try to parse value as different types
        parsed_value = value
        if value.lower() == 'true':
            parsed_value = True
        elif value.lower() == 'false':
            parsed_value = False
        elif value.isdigit():
            parsed_value = int(value)
        else:
            try:
                parsed_value = float(value)
            except ValueError:
                pass  # Keep as string

        # Apply to runtime parameters in settings
        if 'settings' not in config:
            config['settings'] = {}
        if 'runtime_parameter_definitions' not in config['settings']:
            config['settings']['runtime_parameter_definitions'] = {}

        # Update or add the parameter
        if key in config['settings']['runtime_parameter_definitions']:
            config['settings']['runtime_parameter_definitions'][key]['defaultValue'] = parsed_value
        else:
            config['settings']['runtime_parameter_definitions'][key] = {
                'type': type(parsed_value).__name__,
                'defaultValue': parsed_value,
                'description': f'Runtime parameter set via CLI'
            }

    return config