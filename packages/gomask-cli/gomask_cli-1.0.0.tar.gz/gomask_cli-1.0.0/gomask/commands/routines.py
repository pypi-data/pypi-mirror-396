"""
Manage routines
"""

from typing import Optional

import click

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.api.routines import RoutinesAPI
from gomask.utils.output import (
    console, print_success, print_error, print_warning,
    print_routine_table, print_info
)
from gomask.utils.logger import logger


@click.group()
@click.pass_context
def routines(ctx: click.Context) -> None:
    """
    Manage routines

    Routines define synthetic data generation and masking operations.
    You can list routines and view their details including tables.
    """
    pass


@routines.command('list')
@click.option('--limit', type=int, default=100, help='Maximum number of routines to return')
@click.option('--offset', type=int, default=0, help='Pagination offset')
@click.pass_context
def list_routines(ctx: click.Context, limit: int, offset: int) -> None:
    """
    List all routines for your team

    Examples:
        gomask routines list
        gomask routines list --limit 50
        gomask routines list --limit 20 --offset 20
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

            # Get routines
            routine_list = routines_api.list_routines(limit=limit, offset=offset)

            if not routine_list:
                console.print("No routines found for your team")
                console.print("\nCreate a new routine with:")
                console.print("  gomask routines create")
                return

            # Display table
            print_routine_table(routine_list)

            console.print(f"\nShowing {len(routine_list)} routine(s)")
            if offset > 0:
                console.print(f"Offset: {offset}")

    except APIError as e:
        print_error(f"Failed to list routines: {e}")
        logger.exception("Error in list routines command")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to list routines: {e}")
        logger.exception("Error in list routines command")
        ctx.exit(1)


@routines.command('show')
@click.argument('routine_identifier', required=False)
@click.option('--id', type=int, help='Show routine by ID')
@click.option('--name', help='Show routine by name')
@click.pass_context
def show_routine(
    ctx: click.Context,
    routine_identifier: Optional[str],
    id: Optional[int],
    name: Optional[str]
) -> None:
    """
    Show detailed information about a routine

    You can specify the routine by:
    - ID as argument (e.g., "123")
    - Name as argument (e.g., "Customer Data")
    - --id flag (e.g., --id 123)
    - --name flag (e.g., --name "Customer Data")

    Examples:
        gomask routines show 123
        gomask routines show "Customer Data"
        gomask routines show --id 123
        gomask routines show --name "Customer Data"
    """
    try:
        # Check authentication
        secret = ctx.obj.get('SECRET')
        api_url = ctx.obj.get('API_URL')

        if not secret:
            print_error("Authentication required. Set GOMASK_SECRET environment variable.")
            ctx.exit(1)

        # Determine how to identify the routine
        routine = None

        # Connect to API
        with GoMaskAPIClient(base_url=api_url, secret=secret) as client:
            routines_api = RoutinesAPI(client)

            # Priority: --id flag, --name flag, then argument
            if id:
                routine = routines_api.get_routine(id)
            elif name:
                routine = routines_api.get_routine_by_name(name)
            elif routine_identifier:
                # Try to parse as ID first
                try:
                    routine_id = int(routine_identifier)
                    routine = routines_api.get_routine(routine_id)
                except ValueError:
                    # Not an ID, treat as name
                    routine = routines_api.get_routine_by_name(routine_identifier)
            else:
                print_error("Please specify a routine ID or name")
                console.print("\nExamples:")
                console.print('  gomask routines show 123')
                console.print('  gomask routines show "Customer Data"')
                console.print('  gomask routines show --id 123')
                console.print('  gomask routines show --name "Customer Data"')
                ctx.exit(1)

            if not routine:
                print_error("Routine not found")
                ctx.exit(1)

            # Display routine details
            console.print(f"\n[bold]Routine: {routine.get('name', 'Unknown')}[/bold]")
            console.print(f"  - ID: {routine.get('id', '-')}")
            console.print(f"  - Type: {routine.get('type', '-')}")
            console.print(f"  - Status: {routine.get('status', '-')}")

            if routine.get('description'):
                console.print(f"  - Description: {routine['description']}")

            console.print(f"  - Created: {routine.get('created_at', '-')}")
            console.print(f"  - Modified: {routine.get('modified_at', '-')}")

            # Display execution statistics if available
            if routine.get('last_executed'):
                console.print(f"  - Last Executed: {routine['last_executed']}")
            if routine.get('execution_count'):
                console.print(f"  - Execution Count: {routine['execution_count']}")

            # Display table information if available
            if routine.get('tables'):
                console.print(f"\n[bold]Tables ({len(routine['tables'])})[/bold]")

                if routine.get('type') == 'synthetic':
                    # Display synthetic table hierarchy
                    for table in routine['tables']:
                        table_name = table.get('table_name', '-')
                        schema_name = table.get('schema_name', 'public')
                        target_rows = table.get('target_row_count', 0)
                        hierarchy_level = table.get('hierarchy_level', 0)
                        table_type = table.get('table_type', 'entity')

                        # Calculate indentation based on hierarchy level
                        base_indent = "  "
                        level_indent = "  " * hierarchy_level
                        table_indent = base_indent + level_indent
                        detail_indent = base_indent + level_indent + "  "

                        console.print(f"{table_indent}- {schema_name}.{table_name}")
                        console.print(f"{detail_indent}Type: {table_type}, Target rows: {target_rows}")

                        if table.get('parent_table_id'):
                            console.print(f"{detail_indent}Parent table ID: {table['parent_table_id']}")
                else:
                    # Display masking routine tables
                    for table in routine['tables']:
                        table_name = table.get('table_name', '-')
                        schema_name = table.get('schema_name', 'public')
                        row_count = table.get('row_count', 0)
                        status = table.get('status', '-')

                        console.print(f"  - {schema_name}.{table_name}")
                        console.print(f"    Rows: {row_count}, Status: {status}")

                        if table.get('error_message'):
                            console.print(f"    [red]Error: {table['error_message']}[/red]")
                        if table.get('processed_at'):
                            console.print(f"    Processed: {table['processed_at']}")
            else:
                console.print("\n[bold]Tables:[/bold] No tables configured")

            # Display connectors if available
            if routine.get('connectors'):
                console.print(f"\n[bold]Connectors ({len(routine['connectors'])})[/bold]")
                for conn in routine['connectors']:
                    console.print(f"  - {conn.get('name', '-')} ({conn.get('type', '-')})")
            elif routine.get('connector_count'):
                console.print(f"\n[bold]Connectors:[/bold] {routine['connector_count']}")

            # Suggest next steps
            console.print("\n[bold]Next Steps:[/bold]")
            console.print(f"  - Execute: gomask run execute {routine.get('id')}")
            console.print(f"  - Export: gomask export routine --id {routine.get('id')}")
            console.print(f"  - Validate: gomask validate routine --id {routine.get('id')}")

    except APIError as e:
        if e.status_code == 404:
            print_error("Routine not found")
        else:
            print_error(f"Failed to show routine: {e}")
        logger.exception("Error in show routine command")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to show routine: {e}")
        logger.exception("Error in show routine command")
        ctx.exit(1)