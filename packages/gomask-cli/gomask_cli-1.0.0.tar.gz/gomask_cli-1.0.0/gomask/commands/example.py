"""
Create example routine configuration from template
"""

import re
from pathlib import Path
from typing import Optional

import click

from gomask.parser.export import create_yaml_from_template
from gomask.validators import validate_routine_config, load_yaml_file
from gomask.utils.output import console, print_success, print_error, print_warning, prompt
from gomask.utils.logger import logger
import yaml


@click.command()
@click.option(
    '--type',
    'routine_type',
    type=click.Choice(['synthetic', 'masking'], case_sensitive=False),
    required=True,
    help='Type of routine to create'
)
@click.option(
    '--name',
    prompt=True,
    help='Name for the routine'
)
@click.option(
    '--id',
    'unique_id',
    help='Unique identifier (generated from name if not provided)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output file path (defaults to <id>.yaml)'
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
    default=True,
    help='Validate generated template (enabled by default)'
)
@click.pass_context
def example(
    ctx: click.Context,
    routine_type: str,
    name: str,
    unique_id: Optional[str],
    output: Optional[str],
    force: bool,
    validate: bool
) -> None:
    """
    Create an example routine configuration from template

    Creates a YAML template file for either synthetic data generation
    or data masking routines. The generated file includes example
    configurations and documentation.

    Examples:
        gomask example --type synthetic --name "Customer Data"
        gomask example --type masking --name "PII Masking" --id pii-mask-prod
    """
    try:
        # Generate unique ID if not provided
        if not unique_id:
            # Create ID from name: lowercase, replace spaces and underscores with hyphens
            unique_id = name.lower().replace(' ', '-').replace('_', '-')
            # Remove non-alphanumeric characters except hyphens
            unique_id = re.sub(r'[^a-z0-9\-]', '', unique_id)
            # Remove duplicate hyphens
            unique_id = re.sub(r'-+', '-', unique_id)
            # Trim hyphens from start and end
            unique_id = unique_id.strip('-')

            if not unique_id:
                unique_id = "routine-1"

            logger.debug(f"Generated unique ID: {unique_id}")

        # Validate unique ID format
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\-_/]*[a-zA-Z0-9]$', unique_id) and len(unique_id) >= 3:
            if len(unique_id) < 3:
                print_error(f"Unique ID must be at least 3 characters long: {unique_id}")
            else:
                print_error(f"Invalid unique ID format: {unique_id}")
            print_error("ID must start and end with alphanumeric, can contain hyphens, underscores, slashes")
            ctx.exit(1)

        # Determine output file path
        if not output:
            output = f"{unique_id}.yaml"

        output_path = Path(output)

        # Check if file exists
        if output_path.exists() and not force:
            if not click.confirm(f"File {output_path} already exists. Overwrite?"):
                print_error("Operation cancelled")
                ctx.exit(1)

        # Create template
        console.print(f"Creating {routine_type} routine template...")
        template = create_yaml_from_template(routine_type, name, unique_id)

        # Validate the generated template if requested
        if validate:
            console.print("[cyan]Validating generated template...[/cyan]")
            try:
                # Parse the YAML to validate it
                template_config = yaml.safe_load(template)
                is_valid, error_msg = validate_routine_config(template_config)

                if not is_valid:
                    print_warning("Generated template failed validation:")
                    console.print(error_msg)
                    console.print("\n[yellow]Warning: Template may need adjustments before importing.[/yellow]")
                else:
                    console.print("[green][VALID][/green] Generated template is valid")
            except Exception as e:
                print_warning(f"Could not validate template: {e}")

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)

        # Success message
        print_success(f"Created {routine_type} routine template: {output_path}")
        console.print(f"\nRoutine Details:")
        console.print(f"  - Name: {name}")
        console.print(f"  - Unique ID: {unique_id}")
        console.print(f"  - Type: {routine_type}")
        console.print(f"  - File: {output_path}")

        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"1. Edit {output_path} to configure your routine")
        console.print(f"2. Set up your database connector in the file")
        console.print(f"3. Run: gomask validate {output_path}")
        console.print(f"4. Run: gomask import {output_path}")
        console.print(f"5. Run: gomask run {output_path}")

    except Exception as e:
        print_error(f"Failed to create template: {e}")
        logger.exception("Error in example command")
        ctx.exit(1)