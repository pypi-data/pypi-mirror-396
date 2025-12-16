"""
Guided setup command for creating routines interactively
"""

import time
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

import click
import yaml
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.columns import Columns
from rich import print as rprint

from ..api.client import GoMaskAPIClient
from ..api.routines import RoutinesAPI
from ..parser.export import export_routine_to_yaml, _clean_schema_data
from ..validators import validate_routine_config

console = Console()


def export_routine(client: GoMaskAPIClient, routine_id: int, export_path: Path, format: str = "yaml", validate: bool = True) -> bool:
    """Fetch and export a routine to a file with optional validation

    Returns:
        True if export was successful and validation passed (or was skipped)
        False if validation failed
    """
    # Fetch routine data using the export endpoint
    response = client.get(f"/cli/routines/{routine_id}/export-yaml")

    # Export to YAML (this cleans the data by omitting defaults and stripping function metadata)
    yaml_content = export_routine_to_yaml(response, export_path)
    console.print(f"[green]> Exported {len(yaml_content)} bytes to {export_path}[/green]")

    # Validate the exported YAML if requested
    if validate:
        console.print("[cyan]Validating exported configuration...[/cyan]")
        # Validate the CLEANED data, not the raw API response
        # The cleaned data has generation_parameters converted to array format
        cleaned_data = _clean_schema_data(response) if 'routine' in response else response
        is_valid, error_msg = validate_routine_config(cleaned_data)

        if is_valid:
            console.print("[green]> Exported configuration is valid[/green]")
            return True
        else:
            console.print(f"[yellow]WARNING: Exported configuration has validation issues:[/yellow]")
            console.print(f"[yellow]{error_msg}[/yellow]")
            console.print("[yellow]The routine has been exported but may need manual adjustments.[/yellow]")
            return False

    return True


def prompt_for_connector(client: GoMaskAPIClient) -> Optional[Dict[str, Any]]:
    """Prompt user to select a connector"""
    console.print("\n[cyan]Step 1: Select Database Connection[/cyan]")
    console.print("Fetching available connectors...")

    try:
        response = client.get("/cli/connectors")
        connectors = response if isinstance(response, list) else []

        if not connectors:
            console.print("[yellow]No connectors found. Please create a connector first.[/yellow]")
            return None

        # Display connectors in a table
        table = Table(title="Available Connectors", show_lines=True)
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Database", style="magenta")
        table.add_column("Status", style="blue")

        for conn in connectors:
            status_style = "green" if conn.get("status") == "active" else "red"
            table.add_row(
                str(conn["id"]),
                conn["name"],
                conn["type"],
                conn.get("database", "N/A"),
                f"[{status_style}]{conn.get('status', 'unknown')}[/{status_style}]"
            )

        console.print(table)

        # Prompt for selection
        while True:
            choice = Prompt.ask(
                "\nSelect connector by ID or Name",
                default=str(connectors[0]["id"]) if connectors else ""
            )

            # Try to find by ID first
            if choice.isdigit():
                connector = next((c for c in connectors if c["id"] == int(choice)), None)
                if connector:
                    return connector

            # Try to find by name
            connector = next((c for c in connectors if c["name"].lower() == choice.lower()), None)
            if connector:
                return connector

            console.print(f"[red]Invalid selection: {choice}[/red]")
            if not Confirm.ask("Try again?", default=True):
                return None

    except Exception as e:
        console.print(f"[red]Error fetching connectors: {e}[/red]")
        return None


def prompt_for_schema(client: GoMaskAPIClient, connector_id: int) -> str:
    """Prompt user to select database schema"""
    console.print("\n[cyan]Step 2: Select Database Schema[/cyan]")

    try:
        response = client.get(f"/cli/connectors/{connector_id}/schemas")
        schemas = response if isinstance(response, list) else ["public"]

        if len(schemas) == 1:
            schema = schemas[0]
            console.print(f"Using schema: [green]{schema}[/green]")
            return schema

        console.print("Available schemas:")
        for i, schema in enumerate(schemas, 1):
            console.print(f"  {i}. {schema}")

        while True:
            choice = Prompt.ask(
                "Select schema",
                default=schemas[0] if schemas else "public"
            )

            # Check if numeric selection
            if choice.isdigit() and 1 <= int(choice) <= len(schemas):
                return schemas[int(choice) - 1]

            # Check if schema name
            if choice in schemas:
                return choice

            console.print(f"[red]Invalid schema: {choice}[/red]")

    except Exception as e:
        console.print(f"[yellow]Could not fetch schemas: {e}[/yellow]")
        return Prompt.ask("Enter schema name", default="public")


def prompt_for_tables(client: GoMaskAPIClient, connector_id: int, schema: str) -> List[str]:
    """Prompt user to select tables (multi-select)"""
    console.print("\n[cyan]Step 3: Select Tables[/cyan]")
    console.print("Fetching available tables...")

    try:
        response = client.get(f"/cli/connectors/{connector_id}/tables", params={"schema_name": schema})
        tables = response if isinstance(response, list) else []

        if not tables:
            console.print("[yellow]No tables found in the selected schema.[/yellow]")
            return []

        # Display tables
        console.print(f"\nFound [green]{len(tables)}[/green] tables in schema [cyan]{schema}[/cyan]:")

        # Group tables in columns for better display
        table_names = [t["name"] for t in tables]

        # Display in columns
        if len(table_names) > 10:
            # Split into columns
            col_size = (len(table_names) + 2) // 3  # 3 columns
            cols = []
            for i in range(0, len(table_names), col_size):
                col_items = table_names[i:i+col_size]
                col_text = "\n".join(f"  {j+i+1:3}. {name}" for j, name in enumerate(col_items))
                cols.append(col_text)
            console.print(Columns(cols))
        else:
            for i, name in enumerate(table_names, 1):
                console.print(f"  {i:3}. {name}")

        # Prompt for selection
        console.print("\n[yellow]Enter table numbers, names, ranges (e.g., 1-5, users, orders), or 'all'[/yellow]")
        console.print("[yellow]You can mix numbers and names (e.g., '1, 3, users, products')[/yellow]")
        selection = Prompt.ask("Select tables", default="all")

        if selection.lower() == "all":
            return table_names

        # Parse selection
        selected_indices = set()
        selected_names = set()

        for part in selection.split(","):
            part = part.strip()

            if not part:
                continue

            if "-" in part and part[0].isdigit():
                # Range (e.g., 1-5)
                try:
                    start, end = map(int, part.split("-"))
                    selected_indices.update(range(start, end + 1))
                except ValueError:
                    console.print(f"[red]Invalid range: {part}[/red]")
            elif part.isdigit():
                # Single number
                selected_indices.add(int(part))
            else:
                # Try to match as table name (case-insensitive)
                matched = False
                for table_name in table_names:
                    if table_name.lower() == part.lower():
                        selected_names.add(table_name)
                        matched = True
                        break

                if not matched:
                    console.print(f"[yellow]Warning: Table '{part}' not found, skipping[/yellow]")

        # Convert indices to table names
        selected_tables = []
        for idx in sorted(selected_indices):
            if 1 <= idx <= len(table_names):
                selected_tables.append(table_names[idx - 1])

        # Add tables selected by name
        selected_tables.extend(sorted(selected_names))

        if not selected_tables:
            console.print("[red]No valid tables selected.[/red]")
            return []

        console.print(f"\nSelected [green]{len(selected_tables)}[/green] tables:")
        for table in selected_tables[:5]:
            console.print(f"  - {table}")
        if len(selected_tables) > 5:
            console.print(f"  ... and {len(selected_tables) - 5} more")

        return selected_tables

    except Exception as e:
        console.print(f"[red]Error fetching tables: {e}[/red]")
        return []


def prompt_for_routine_details() -> Dict[str, Any]:
    """Prompt for routine type and metadata"""
    console.print("\n[cyan]Step 4: Configure Routine[/cyan]")

    # Routine type
    routine_types = ["masking", "synthetic", "ai_scenario"]
    console.print("\nRoutine types:")
    console.print("  1. masking - Mask sensitive data in existing database")
    console.print("  2. synthetic - Generate synthetic test data")
    console.print("  3. ai_scenario - AI-powered scenario generation")

    while True:
        type_choice = Prompt.ask("Select routine type", choices=["1", "2", "3", "masking", "synthetic", "ai_scenario"], default="1")

        if type_choice in ["1", "masking"]:
            routine_type = "masking"
            break
        elif type_choice in ["2", "synthetic"]:
            routine_type = "synthetic"
            break
        elif type_choice in ["3", "ai_scenario"]:
            routine_type = "ai_scenario"
            break

    # Optional name and description
    name = Prompt.ask("Routine name (optional, press Enter to auto-generate)", default="")
    description = Prompt.ask("Description (optional)", default="")

    return {
        "routine_type": routine_type,
        "name": name if name else None,
        "description": description if description else None
    }


def wait_for_setup_completion(client: GoMaskAPIClient, job_id: int, routine_id: int) -> bool:
    """Poll job status until completion"""
    console.print(f"\n[cyan]Setting up routine {routine_id}...[/cyan]")

    with Progress(
        SpinnerColumn(spinner_name="line"),  # Use ASCII-safe spinner for Windows compatibility
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=False
    ) as progress:
        task = progress.add_task("Waiting for setup to complete...", total=None)

        last_phase = None
        last_progress = 0
        max_wait_time = 300  # 5 minutes max
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            try:
                response = client.get(f"/cli/job-executions/{job_id}/status")

                status = response.get("status", "unknown")
                phase = response.get("phase", "")
                job_progress = response.get("progress", 0)
                tables_processed = response.get("tables_processed", 0)
                total_tables = response.get("total_tables", 0)

                # Update progress description
                if phase != last_phase or job_progress != last_progress:
                    if total_tables > 0:
                        desc = f"[yellow]{phase}[/yellow] - Tables: {tables_processed}/{total_tables} ({job_progress}%)"
                    else:
                        desc = f"[yellow]{phase}[/yellow] ({job_progress}%)"
                    progress.update(task, description=desc)
                    last_phase = phase
                    last_progress = job_progress

                # Check completion
                if status == "completed":
                    progress.update(task, description="[green]> Setup completed successfully![/green]")
                    return True
                elif status == "failed":
                    error_msg = response.get("error_message", "Unknown error")
                    progress.update(task, description=f"[red]ERROR: Setup failed: {error_msg}[/red]")
                    return False
                elif status == "cancelled":
                    progress.update(task, description="[yellow]Setup cancelled[/yellow]")
                    return False

                # Wait before next poll
                time.sleep(2)

            except Exception as e:
                progress.update(task, description=f"[red]Error checking status: {e}[/red]")
                return False

        progress.update(task, description="[yellow]Setup timed out after 5 minutes[/yellow]")
        return False


@click.command(name="setup")
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output file for the generated routine YAML"
)
@click.option(
    "--no-wait",
    is_flag=True,
    help="Don't wait for setup to complete"
)
@click.option(
    "--export-immediately",
    is_flag=True,
    help="Export routine immediately after creation (without waiting for setup)"
)
@click.option(
    "--skip-validation",
    is_flag=True,
    help="Skip validation of the exported YAML configuration"
)
@click.pass_context
def setup_cmd(ctx, output: Optional[Path], no_wait: bool, export_immediately: bool, skip_validation: bool):
    """Interactive guided setup for creating new routines.

    This command guides you through:
    1. Selecting a database connection
    2. Choosing a schema
    3. Selecting tables (multi-select)
    4. Configuring routine type and details
    5. Running the setup process
    6. Exporting the configured routine
    """
    try:
        # Welcome message
        console.print(Panel.fit(
            "[bold cyan]GoMask CLI - Guided Routine Setup[/bold cyan]\n"
            "This wizard will help you create a new data routine",
            border_style="cyan"
        ))

        # Get API configuration from context
        api_url = ctx.obj.get('API_URL', 'http://localhost:8000')
        secret = ctx.obj.get('SECRET')

        # Initialize API client
        with GoMaskAPIClient(base_url=api_url, secret=secret) as client:
            routines_api = RoutinesAPI(client)

            # Step 1: Select connector
            connector = prompt_for_connector(client)
            if not connector:
                console.print("[red]Setup cancelled - no connector selected[/red]")
                return

            console.print(f"[green]> Selected connector: {connector['name']} (ID: {connector['id']})[/green]")

            # Step 2: Select schema
            schema = prompt_for_schema(client, connector["id"])
            console.print(f"[green]> Selected schema: {schema}[/green]")

            # Step 3: Select tables
            tables = prompt_for_tables(client, connector["id"], schema)
            if not tables:
                console.print("[red]Setup cancelled - no tables selected[/red]")
                return

            console.print(f"[green]> Selected {len(tables)} tables[/green]")

            # Step 4: Configure routine
            routine_details = prompt_for_routine_details()
            console.print(f"[green]> Routine type: {routine_details['routine_type']}[/green]")

            # Confirm setup
            console.print("\n[bold]Ready to create routine with:[/bold]")
            console.print(f"  - Connector: {connector['name']}")
            console.print(f"  - Schema: {schema}")
            console.print(f"  - Tables: {len(tables)} selected")
            console.print(f"  - Type: {routine_details['routine_type']}")
            if routine_details.get('name'):
                console.print(f"  - Name: {routine_details['name']}")

            if not Confirm.ask("\nProceed with setup?", default=True):
                console.print("[yellow]Setup cancelled by user[/yellow]")
                return

            # Call guided setup API
            console.print("\n[cyan]Creating routine and starting setup...[/cyan]")

            setup_request = {
                "connector_id": connector["id"],
                "schema_name": schema,
                "selected_tables": tables,
                "routine_type": routine_details["routine_type"],
                "name": routine_details.get("name"),
                "description": routine_details.get("description"),
                "configuration": {}
            }

            response = client.post("/cli/routines/guided-setup", data=setup_request)

            if not response.get("success"):
                console.print(f"[red]Setup failed: {response.get('message', 'Unknown error')}[/red]")
                return

            routine_id = response["routine_id"]
            job_id = response["job_execution_id"]

            console.print(f"[green]> Routine created with ID: {routine_id}[/green]")
            console.print(f"[green]> Setup job started with ID: {job_id}[/green]")

            # Export immediately if requested
            if export_immediately:
                console.print("\n[cyan]Exporting routine configuration...[/cyan]")
                try:
                    export_path = output or Path(f"routine_{routine_id}_setup.yaml")
                    # Skip validation for immediate export since setup might not be complete
                    export_routine(client, routine_id, export_path, format="yaml", validate=False)
                    console.print(f"[green]> Routine exported to: {export_path}[/green]")
                    console.print("[yellow]Note: Configuration may be incomplete - setup is still in progress[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not export immediately: {e}[/yellow]")

            # Wait for completion unless --no-wait
            if not no_wait:
                success = wait_for_setup_completion(client, job_id, routine_id)

                if success:
                    # Export the completed routine
                    console.print("\n[cyan]Exporting completed routine configuration...[/cyan]")

                    if not export_immediately:  # Only export if not already done
                        try:
                            export_path = output or Path(f"routine_{routine_id}_complete.yaml")
                            # Validate the completed routine configuration unless skipped
                            validation_passed = export_routine(client, routine_id, export_path, format="yaml", validate=not skip_validation)

                            console.print(f"[green]> Routine successfully exported to: {export_path}[/green]")

                            if skip_validation:
                                console.print("\n[bold green]Setup completed![/bold green]")
                                console.print("[yellow]Validation was skipped. Verify the configuration before running.[/yellow]")
                                console.print(f"You can run this routine using: [cyan]gomask run {export_path}[/cyan]")
                            elif validation_passed:
                                console.print("\n[bold green]Setup completed successfully![/bold green]")
                                console.print(f"You can now run this routine using: [cyan]gomask run {export_path}[/cyan]")
                            else:
                                console.print("\n[yellow]Setup completed with validation warnings[/yellow]")
                                console.print("[yellow]The exported configuration may need manual adjustments before running.[/yellow]")
                                console.print(f"Review the file at: [cyan]{export_path}[/cyan]")
                        except Exception as e:
                            console.print(f"[red]Error exporting routine: {e}[/red]")
                else:
                    console.print("\n[red]Setup failed or timed out[/red]")
                    console.print("You can check the status later or review logs in the web interface")
            else:
                console.print("\n[yellow]Not waiting for completion (--no-wait flag)[/yellow]")
                console.print(f"You can check the setup progress using: [cyan]gomask executions show {job_id}[/cyan]")
                if not export_immediately:
                    console.print(f"Once complete, export using: [cyan]gomask export {routine_id} -o {output or 'routine.yaml'}[/cyan]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Setup interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if ctx.obj.get("debug"):
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)