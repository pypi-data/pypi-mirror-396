"""
Execute routine from YAML configuration
"""

from pathlib import Path
from typing import Dict, Any, Optional
import time

import click

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.api.routines import RoutinesAPI
from gomask.api.execution import ExecutionAPI, ExecutionStatus
from gomask.validators import (
    load_yaml_file,
    validate_routine_config,
    determine_routine_type,
    get_validation_errors,
    suggest_fixes
)
from gomask.utils.output import (
    console, print_success, print_error, print_warning, spinner, progress_bar
)
from gomask.utils.logger import logger


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
        param_type = 'string'

        if value.lower() == 'true':
            parsed_value = True
            param_type = 'boolean'
        elif value.lower() == 'false':
            parsed_value = False
            param_type = 'boolean'
        elif value.isdigit():
            parsed_value = int(value)
            param_type = 'integer'
        else:
            try:
                parsed_value = float(value)
                param_type = 'float'
            except ValueError:
                pass  # Keep as string, param_type is already 'string'

        # Apply to runtime parameters in settings
        if 'settings' not in config:
            config['settings'] = {}
        if 'runtime_parameter_definitions' not in config['settings']:
            config['settings']['runtime_parameter_definitions'] = []

        # Update or add the parameter (runtime_parameter_definitions is an array)
        params_list = config['settings']['runtime_parameter_definitions']

        # Find existing parameter by key
        existing_param = None
        for param in params_list:
            if param.get('key') == key:
                existing_param = param
                break

        if existing_param:
            # Update existing parameter
            existing_param['defaultValue'] = parsed_value
            existing_param['type'] = param_type
        else:
            # Add new parameter
            params_list.append({
                'key': key,
                'name': key,
                'type': param_type,
                'defaultValue': parsed_value,
                'description': f'Runtime parameter set via CLI'
            })

    return config


@click.command()
@click.argument(
    'yaml_file',
    type=click.Path(exists=True, readable=True, path_type=Path)
)
@click.option(
    '--watch',
    '-w',
    is_flag=True,
    help='Watch execution progress'
)
@click.option(
    '--param',
    '-p',
    'params',
    multiple=True,
    help='Override runtime parameters (format: key=value)'
)
@click.option(
    '--env-file',
    type=click.Path(exists=True, readable=True, path_type=Path),
    help='Path to .env file for environment variables'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Validate and show execution plan without running'
)
@click.option(
    '--timeout',
    type=int,
    default=3600,
    help='Execution timeout in seconds'
)
@click.pass_context
def run(
    ctx: click.Context,
    yaml_file: Path,
    watch: bool,
    params: tuple,
    env_file: Optional[Path],
    dry_run: bool,
    timeout: int
) -> None:
    """
    Execute a routine from YAML configuration

    Validates the configuration, imports it if needed, and starts execution.
    Can monitor progress and display logs in real-time.

    Examples:
        gomask run routine.yaml
        gomask run routine.yaml --watch
        gomask run routine.yaml --param record_count=5000
        gomask run routine.yaml --param customer_count=1000 --param order_multiplier=2.5
    """
    try:
        console.print(f"[cyan]Loading configuration from:[/cyan] {yaml_file}")

        # Load YAML file with optional env file support
        try:
            config = load_yaml_file(str(yaml_file), env_file)
        except Exception as e:
            print_error(f"Failed to load YAML: {e}")
            ctx.exit(1)

        # Apply runtime parameters if provided
        if params:
            config = apply_runtime_parameters(config, params)

        # Validate configuration against schema
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
        routine = config.get('routine', {})
        unique_id = routine.get('unique_id')
        name = routine.get('name', 'Unnamed')
        description = routine.get('description', '')

        console.print(f"\n[bold]Routine: {name}[/bold]")
        if unique_id:
            console.print(f"Unique ID: {unique_id}")
        console.print(f"Type: {routine_type}")
        if description:
            console.print(f"Description: {description}")

        if dry_run:
            console.print("\n[yellow]DRY RUN MODE - No execution will occur[/yellow]")
            console.print("\n[bold]Execution Plan:[/bold]")

            # Show tables to process
            tables = config.get('tables', [])
            if routine_type == 'synthetic':
                console.print(f"  - Tables to generate: {len(tables)}")
                for table in tables:
                    record_count = table.get('record_count', 'dynamic')
                    console.print(f"    - {table['table_name']}: {record_count} records")
            elif routine_type == 'masking':
                console.print(f"  - Tables to mask: {len(tables)}")
                for table in tables:
                    console.print(f"    - {table['table_name']}: {len(table.get('columns', []))} columns")

            # Show parameters from settings
            settings = config.get('settings', {})
            runtime_params_def = settings.get('runtime_parameter_definitions', {})
            if runtime_params_def:
                console.print("\n  - Runtime Parameters:")
                # Handle both dict and list formats
                if isinstance(runtime_params_def, dict):
                    for key, param_def in runtime_params_def.items():
                        value = param_def.get('defaultValue', param_def.get('default'))
                        console.print(f"    - {key}: {value}")
                elif isinstance(runtime_params_def, list):
                    for param_def in runtime_params_def:
                        if isinstance(param_def, dict):
                            name = param_def.get('name', 'unnamed')
                            value = param_def.get('defaultValue', param_def.get('default'))
                            console.print(f"    - {name}: {value}")

            print_success("Dry run complete - ready to execute")
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
            execution_api = ExecutionAPI(client)

            # Import or update routine using the new schema format
            console.print("\nPreparing routine...")
            with spinner("Importing configuration"):
                result = routines_api.import_yaml(config)
                routine_id = result.get('id')

            console.print(f"[green] Routine ID: {routine_id}")

            # Extract runtime parameters if any were defined
            runtime_params = {}
            if 'settings' in config and 'runtime_parameter_definitions' in config['settings']:
                runtime_params_def = config['settings']['runtime_parameter_definitions']
                # Handle both dict and list formats
                if isinstance(runtime_params_def, dict):
                    for key, param_def in runtime_params_def.items():
                        runtime_params[key] = param_def.get('defaultValue', param_def.get('default'))
                elif isinstance(runtime_params_def, list):
                    for param_def in runtime_params_def:
                        if isinstance(param_def, dict):
                            name = param_def.get('name')
                            if name:
                                runtime_params[name] = param_def.get('defaultValue', param_def.get('default'))

            # Start execution
            console.print("\nStarting execution...")
            execution_result = execution_api.start_execution(
                routine_id=routine_id,
                parameters=runtime_params,
                wait=False
            )

            execution_id = execution_result.get('execution_id')
            console.print(f"[green] Execution ID: {execution_id}")

            if not watch:
                print_success("Execution started successfully")
                console.print(f"\nTo monitor progress, run:")
                console.print(f"  gomask executions show {execution_id}")
                return

            # Monitor execution
            console.print("\n[bold]Monitoring execution...[/bold]")
            start_time = time.time()
            last_status = None

            try:
                while True:
                    # Get status
                    status_info = execution_api.get_status(execution_id)
                    status = status_info.get('status')

                    # Display status change
                    if status != last_status:
                        if status == ExecutionStatus.RUNNING:
                            console.print("⚡ Execution running...")
                        elif status == ExecutionStatus.COMPLETED:
                            print_success("Execution completed successfully!")
                        elif status == ExecutionStatus.FAILED:
                            print_error("Execution failed!")
                        elif status == ExecutionStatus.CANCELLED:
                            print_warning("Execution was cancelled")
                        last_status = status

                    # Display progress
                    progress_info = execution_api.get_progress(execution_id)
                    if progress_info:
                        percent = progress_info.get('percent', 0)
                        current_table = progress_info.get('current_table', 'unknown')
                        records = progress_info.get('records_processed', 0)

                        console.print(
                            f"  Progress: {percent}% | Table: {current_table} | "
                            f"Records: {records:,}",
                            end='\r'
                        )

                    # Check if complete
                    if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                        break

                    # Check timeout
                    if time.time() - start_time > timeout:
                        print_error(f"Execution timed out after {timeout} seconds")
                        execution_api.cancel(execution_id)
                        ctx.exit(1)

                    time.sleep(2)

                # Display summary
                summary = execution_api.get_summary(execution_id)
                console.print("\n[bold]Execution Summary:[/bold]")
                console.print(f"  - Duration: {summary.get('duration', 'unknown')}")
                console.print(f"  - Records Processed: {summary.get('total_records', 0):,}")
                console.print(f"  - Tables Processed: {summary.get('tables_processed', 0)}")

                if status == ExecutionStatus.FAILED:
                    error_msg = summary.get('error_message', 'Unknown error')
                    print_error(f"Error: {error_msg}")
                    ctx.exit(1)

            except KeyboardInterrupt:
                console.print("\n[yellow]Execution monitoring cancelled[/yellow]")
                if click.confirm("Cancel the execution?"):
                    execution_api.cancel(execution_id)
                    print_warning("Execution cancelled")
                ctx.exit(130)

    except Exception as e:
        print_error(f"Execution failed: {e}")
        logger.exception("Error in run command")
        ctx.exit(1)