"""
Export routine from database to YAML
"""

from pathlib import Path
from typing import Optional

import click

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.api.routines import RoutinesAPI
from gomask.parser.export import export_routine_to_yaml, _clean_schema_data
from gomask.validators import validate_routine_config
from gomask.utils.output import console, print_success, print_error, print_warning
from gomask.utils.logger import logger


@click.command()
@click.argument('routine_identifier')
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path),
    help='Output file path (prints to stdout if not specified)'
)
@click.option(
    '--force',
    '-f',
    is_flag=True,
    help='Overwrite existing file'
)
@click.option(
    '--validate',
    is_flag=True,
    help='Validate exported YAML configuration'
)
@click.pass_context
def export(
    ctx: click.Context,
    routine_identifier: str,
    output: Optional[Path],
    force: bool,
    validate: bool
) -> None:
    """
    Export a routine from database to YAML format

    The routine can be identified by either its numeric ID or unique ID.
    Exports the complete configuration including tables, columns, and settings.

    Examples:
        gomask export 123 -o routine.yaml
        gomask export customer-data-prod -o routine.yaml
        gomask export routine-id  # Prints to stdout
    """
    try:
        # Check authentication
        secret = ctx.obj.get('SECRET')
        api_url = ctx.obj.get('API_URL')

        if not secret:
            print_error("Authentication required. Set GOMASK_SECRET environment variable.")
            ctx.exit(1)

        # Connect to API
        with GoMaskAPIClient(base_url=api_url, secret=secret) as client:
            routines_api = RoutinesAPI(client)

            # Try to get routine
            routine_data = None
            routine_id = None

            # Check if identifier is numeric (routine ID)
            if routine_identifier.isdigit():
                routine_id = int(routine_identifier)
                console.print(f"Fetching routine by ID: {routine_id}")
                try:
                    routine_data = routines_api.get_routine(routine_id)
                except APIError as e:
                    if e.status_code == 404:
                        print_error(f"Routine with ID {routine_id} not found")
                        ctx.exit(1)
                    raise
            else:
                # Try as unique ID
                console.print(f"Fetching routine by unique ID: {routine_identifier}")
                routine_data = routines_api.get_routine_by_unique_id(routine_identifier)

                if not routine_data:
                    print_error(f"Routine with unique ID '{routine_identifier}' not found")
                    ctx.exit(1)

                routine_id = routine_data.get('id')

            # Export to YAML
            console.print(f"Exporting routine: {routine_data.get('name')}")

            try:
                # Get full export data
                yaml_data = routines_api.export_yaml(routine_id)

                # Validate the exported YAML if requested
                if validate:
                    console.print("[cyan]Validating exported configuration...[/cyan]")
                    # Validate the CLEANED data, not the raw API response
                    # The cleaned data has generation_parameters converted to array format
                    cleaned_data = _clean_schema_data(yaml_data) if 'routine' in yaml_data else yaml_data
                    is_valid, error_msg = validate_routine_config(cleaned_data)

                    if not is_valid:
                        print_warning("Exported YAML failed validation:")
                        console.print(error_msg)
                        console.print("\n[yellow]Warning: The exported YAML may not be importable.[/yellow]")
                    else:
                        console.print("[green][VALID][/green] Exported configuration is valid")

                # Output to file or stdout
                if output:
                    # Check if file exists
                    if output.exists() and not force:
                        if not click.confirm(f"File {output} already exists. Overwrite?"):
                            print_error("Operation cancelled")
                            ctx.exit(1)

                    # Write to file using the export function properly
                    yaml_content = export_routine_to_yaml(yaml_data, output)
                    print_success(f"Exported routine to {output}")

                    # Display summary using the exported data
                    console.print("\n[bold]Export Summary:[/bold]")

                    # Extract routine info from the exported yaml_data
                    if isinstance(yaml_data, dict) and 'routine' in yaml_data:
                        routine_info = yaml_data.get('routine', {})
                        console.print(f"  - Routine ID: {routine_id}")
                        console.print(f"  - Name: {routine_info.get('name', 'N/A')}")
                        console.print(f"  - Unique ID: {routine_info.get('unique_id', 'N/A')}")
                        console.print(f"  - Type: {routine_info.get('type', 'N/A')}")
                        console.print(f"  - Connector ID: {routine_info.get('connector_id', 'N/A')}")

                        # Show table count
                        tables = yaml_data.get('tables', [])
                        console.print(f"  - Tables: {len(tables)}")

                        # Show settings info if present
                        settings = yaml_data.get('settings', {})
                        if settings:
                            runtime_params = settings.get('runtime_parameter_definitions', [])
                            if runtime_params:
                                if isinstance(runtime_params, list):
                                    console.print(f"  - Runtime Parameters: {len(runtime_params)}")
                                elif isinstance(runtime_params, dict):
                                    console.print(f"  - Runtime Parameters: {len(runtime_params)}")
                    else:
                        # Fallback to routine_data if export format is different
                        console.print(f"  - Routine ID: {routine_id}")
                        console.print(f"  - Name: {routine_data.get('name', 'N/A')}")
                        console.print(f"  - Unique ID: {routine_data.get('unique_id', 'N/A')}")
                        console.print(f"  - Type: {routine_data.get('type', 'N/A')}")

                    console.print(f"  - File: {output}")

                    if validate:
                        if 'is_valid' in locals() and is_valid:
                            console.print(f"  - Validation: Passed")
                        else:
                            console.print(f"  - Validation: Failed")
                else:
                    # Convert to YAML string and print to stdout
                    yaml_content = export_routine_to_yaml(yaml_data)
                    console.print(yaml_content)

            except APIError as e:
                print_error(f"Failed to export routine: {e}")
                ctx.exit(1)

    except Exception as e:
        print_error(f"Export failed: {e}")
        logger.exception("Error in export command")
        ctx.exit(1)