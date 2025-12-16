"""
Validate YAML routine configuration
"""

from pathlib import Path
from typing import Optional, Dict, Any

import click
from rich.table import Table
from rich.panel import Panel

from gomask.validators import (
    load_yaml_file,
    validate_routine_config,
    get_validation_errors,
    suggest_fixes,
    determine_routine_type
)
from gomask.utils.output import console, print_success, print_error, print_warning
from gomask.utils.logger import logger


@click.command()
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
    '--skip-validation',
    is_flag=True,
    help='Skip schema validation (not recommended)'
)
@click.option(
    '--detailed',
    '-d',
    is_flag=True,
    help='Show detailed error information with suggestions'
)
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    help='Quiet mode - only return exit code'
)
@click.option(
    '--show-config',
    is_flag=True,
    help='Display the parsed configuration structure'
)
@click.option(
    '--param',
    multiple=True,
    help='Runtime parameter in format key=value'
)
@click.pass_context
def validate(
    ctx: click.Context,
    yaml_file: Path,
    env_file: Optional[Path],
    skip_validation: bool,
    detailed: bool,
    quiet: bool,
    show_config: bool,
    param: tuple
) -> None:
    """
    Validate a YAML routine configuration file

    Validates YAML configuration files for data masking, synthetic data
    generation, or AI scenario routines against their respective JSON schemas.

    \b
    Examples:
        gomask validate routine.yaml
        gomask validate routine.yaml --detailed
        gomask validate routine.yaml --skip-validation
        gomask validate routine.yaml --show-config
        gomask validate routine.yaml --param record_count=1000
    """
    try:
        if not quiet:
            console.print(f"\n[bold cyan]Validating routine configuration:[/bold cyan] {yaml_file.name}")
            console.print("=" * 60)

        # Load the YAML file with optional env file support
        try:
            config = load_yaml_file(str(yaml_file), env_file)
        except Exception as e:
            if not quiet:
                print_error(f"Failed to load YAML: {e}")
            ctx.exit(1)

        # Apply runtime parameters if provided
        if param:
            config = apply_runtime_parameters(config, param, quiet)

        # Show configuration structure if requested
        if show_config and not quiet:
            display_config_structure(config)

        # Validate configuration against schema
        if not skip_validation:
            if not quiet:
                console.print("[cyan]Validating configuration...[/cyan]")
            is_valid, error_msg = validate_routine_config(config)

            if not is_valid:
                if not quiet:
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

            if not quiet:
                console.print("[green][VALID][/green] Configuration is valid")

        # Display configuration summary
        if not quiet:
            display_summary(config)

        # Exit with appropriate code (success)
        return

    except Exception as e:
        if not quiet:
            print_error(f"Validation failed: {e}")
        logger.exception("Error in validate command")
        ctx.exit(1)


def display_config_structure(config: dict) -> None:
    """Display the configuration structure in a readable format."""
    console.print("\n[bold]Configuration Structure:[/bold]")

    def print_dict(d, indent=0):
        for key, value in d.items():
            prefix = "  " * indent + "- "
            if isinstance(value, dict):
                console.print(f"{prefix}[cyan]{key}:[/cyan]")
                print_dict(value, indent + 1)
            elif isinstance(value, list):
                console.print(f"{prefix}[cyan]{key}:[/cyan] [{len(value)} items]")
                if value and isinstance(value[0], dict):
                    console.print(f"{'  ' * (indent + 1)}[dim]First item:[/dim]")
                    print_dict(value[0], indent + 2)
            else:
                value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                console.print(f"{prefix}[cyan]{key}:[/cyan] {value_str}")

    print_dict(config)
    console.print()


def show_detailed_errors(config: dict) -> None:
    """Show detailed validation errors with suggestions."""
    errors = get_validation_errors(config)

    if not errors:
        return

    console.print("\n[bold red]Detailed Validation Errors:[/bold red]")

    # Create error table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Path", style="yellow", width=30)
    table.add_column("Error", style="red", width=50)
    table.add_column("Current Value", style="dim", width=20)

    for error in errors[:10]:  # Limit to first 10 errors
        path = error.get('path', 'root')
        message = error.get('message', '')
        value = error.get('value', '')

        # Truncate long values
        if isinstance(value, (dict, list)):
            value_str = f"<{type(value).__name__}>"
        else:
            value_str = str(value)[:20] + "..." if len(str(value)) > 20 else str(value)

        table.add_row(path, message, value_str)

    console.print(table)

    if len(errors) > 10:
        console.print(f"\n[dim]... and {len(errors) - 10} more errors[/dim]")

    # Show suggestions
    suggestions = suggest_fixes(errors)
    if suggestions:
        console.print("\n[bold yellow]Suggested Fixes:[/bold yellow]")
        for i, suggestion in enumerate(suggestions[:5], 1):
            console.print(f"  {i}. {suggestion}")


def display_summary(config: dict) -> None:
    """Display configuration summary."""
    routine_type = determine_routine_type(config)
    routine = config.get('routine', {})
    tables = config.get('tables', [])

    console.print("\n[bold]Configuration Summary:[/bold]")
    console.print(f"  - Type: {routine_type}")
    console.print(f"  - Name: {routine.get('name', 'Unnamed')}")

    if routine.get('description'):
        console.print(f"  - Description: {routine.get('description')}")

    console.print(f"  - Connector ID: {routine.get('connector_id', 'Not specified')}")
    console.print(f"  - Tables: {len(tables)}")

    # Show settings summary based on type
    settings = config.get('settings', {})
    if settings:
        console.print("\n[bold]Settings:[/bold]")
        if routine_type == 'masking':
            console.print(f"  - Batch Size: {settings.get('batch_size', 1000)}")
            console.print(f"  - Parallel Workers: {settings.get('parallel_workers', 4)}")
            console.print(f"  - Audit Reporting: {settings.get('audit_reporting_enabled', True)}")
        elif routine_type == 'synthetic':
            console.print(f"  - Generation Mode: {settings.get('generation_mode', 'hierarchical')}")
            console.print(f"  - Batch Size: {settings.get('batch_size', 1000)}")
            console.print(f"  - Global Record Count: {settings.get('global_record_count', 1000)}")
            runtime_params = settings.get('runtime_parameter_definitions', {})
            if runtime_params:
                console.print(f"  - Runtime Parameters: {', '.join(runtime_params.keys())}")


def apply_runtime_parameters(config: Dict[str, Any], params: tuple, quiet: bool = False) -> Dict[str, Any]:
    """
    Apply runtime parameters to the configuration.

    Args:
        config: The configuration dictionary
        params: Tuple of key=value parameter strings
        quiet: Whether to suppress output

    Returns:
        Updated configuration dictionary
    """
    if not params:
        return config

    if not quiet:
        console.print("[cyan]Applying runtime parameters:[/cyan]")

    for param_str in params:
        if '=' not in param_str:
            if not quiet:
                console.print(f"  [yellow]Skipping invalid parameter: {param_str}[/yellow]")
            continue

        key, value = param_str.split('=', 1)
        if not quiet:
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