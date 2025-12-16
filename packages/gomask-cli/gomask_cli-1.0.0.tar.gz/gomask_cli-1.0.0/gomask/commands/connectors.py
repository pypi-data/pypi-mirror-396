"""
Manage database connectors
"""

from typing import Optional
import getpass

import click

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.api.connectors import ConnectorsAPI
from gomask.utils.output import (
    console, print_success, print_error, print_warning,
    print_connector_table, prompt, confirm
)
from gomask.utils.logger import logger


@click.group()
@click.pass_context
def connectors(ctx: click.Context) -> None:
    """
    Manage database connectors

    Connectors define the database connections used by routines.
    You can create, list, test, and delete connectors.
    """
    pass


@connectors.command('list')
@click.pass_context
def list_connectors(ctx: click.Context) -> None:
    """
    List all connectors for your team

    Examples:
        gomask connectors list
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
            connectors_api = ConnectorsAPI(client)

            # Get connectors
            connector_list = connectors_api.list_connectors()

            if not connector_list:
                console.print("No connectors found for your team")
                console.print("\nCreate a new connector with:")
                console.print("  gomask connectors create")
                return

            # Display table
            print_connector_table(connector_list)

            console.print(f"\nTotal connectors: {len(connector_list)}")

    except Exception as e:
        print_error(f"Failed to list connectors: {e}")
        logger.exception("Error in list connectors command")
        ctx.exit(1)


@connectors.command('create')
@click.option('--name', required=True, help='Connector name')
@click.option(
    '--type',
    'db_type',
    required=True,
    type=click.Choice(['postgresql', 'mysql', 'oracle', 'sqlserver', 'mongodb']),
    help='Database type'
)
@click.option('--host', required=True, help='Database host')
@click.option('--port', type=int, help='Database port (uses default if not specified)')
@click.option('--database', required=True, help='Database name')
@click.option('--username', required=True, help='Database username')
@click.option('--password', help='Database password (will prompt if not provided)')
@click.option('--password-env', help='Environment variable containing password')
@click.option(
    '--ssl-mode',
    type=click.Choice(['require', 'prefer', 'disable']),
    default='prefer',
    help='SSL connection mode'
)
@click.option('--skip-test', is_flag=True, default=False, help='Skip connection test')
@click.pass_context
def create_connector(
    ctx: click.Context,
    name: str,
    db_type: str,
    host: str,
    port: Optional[int],
    database: str,
    username: str,
    password: Optional[str],
    password_env: Optional[str],
    ssl_mode: str,
    skip_test: bool
) -> None:
    """
    Create a new database connector

    Examples:
        gomask connectors create --name prod-db --type postgresql --host localhost --database mydb --username user
        gomask connectors create --name test-mysql --type mysql --host db.example.com --port 3306 --database testdb --username root --password-env DB_PASSWORD
    """
    try:
        # Get password
        if password_env:
            import os
            password = os.getenv(password_env)
            if not password:
                print_error(f"Environment variable {password_env} not set")
                ctx.exit(1)
        elif not password:
            password = getpass.getpass("Database password: ")

        # Set default port based on database type
        if not port:
            default_ports = {
                'postgresql': 5432,
                'mysql': 3306,
                'oracle': 1521,
                'sqlserver': 1433,
                'mongodb': 27017
            }
            port = default_ports.get(db_type, 5432)

        # Check authentication
        secret = ctx.obj.get('SECRET')
        api_url = ctx.obj.get('API_URL')

        if not secret:
            print_error("Authentication required. Set GOMASK_SECRET environment variable.")
            ctx.exit(1)

        # Connect to API
        with GoMaskAPIClient(base_url=api_url, secret=secret) as client:
            connectors_api = ConnectorsAPI(client)

            # Check if connector with same name exists
            existing = connectors_api.get_connector_by_name(name)
            if existing:
                print_error(f"Connector with name '{name}' already exists")
                ctx.exit(1)

            # Map CLI types to backend types
            type_mapping = {
                'postgresql': 'postgres',
                'mysql': 'mysql',
                'oracle': 'oracle',
                'sqlserver': 'sqlserver',
                'mongodb': 'mongodb'
            }
            backend_type = type_mapping.get(db_type, db_type)

            # Prepare connector data
            connector_data = {
                'name': name,
                'type': backend_type,
                'host': host,
                'port': port,
                'database': database,
                'username': username,
                'password': password,
                'ssl': ssl_mode
            }

            console.print(f"Creating connector: {name}")

            # Test connection unless explicitly skipped
            if not skip_test:
                console.print("Testing connection...")
                test_result = connectors_api.test_connector_config(connector_data)

                if test_result.get('status') != 'success':
                    print_error(f"Connection test failed: {test_result.get('message')}")
                    # In non-interactive mode, exit on test failure
                    # In interactive mode, ask for confirmation
                    try:
                        if not confirm("Create connector anyway?"):
                            ctx.exit(1)
                    except EOFError:
                        # Non-interactive mode, exit on test failure
                        print_error("Connection test failed. Use --skip-test to skip test.")
                        ctx.exit(1)
                else:
                    print_success("Connection test successful")

            # Create connector
            result = connectors_api.create_connector(connector_data)
            connector_id = result.get('id')

            print_success(f"Created connector ID {connector_id}")

            # Display summary
            console.print("\n[bold]Connector Details:[/bold]")
            console.print(f"  - ID: {connector_id}")
            console.print(f"  - Name: {name}")
            console.print(f"  - Type: {db_type}")
            console.print(f"  - Host: {host}:{port}")
            console.print(f"  - Database: {database}")
            console.print(f"  - Status: {result.get('status', 'active')}")

    except Exception as e:
        print_error(f"Failed to create connector: {e}")
        logger.exception("Error in create connector command")
        ctx.exit(1)


@connectors.command('test')
@click.argument('connector_id_or_name')
@click.pass_context
def test_connector(ctx: click.Context, connector_id_or_name: str) -> None:
    """
    Test a connector connection

    Examples:
        gomask connectors test prod-db
        gomask connectors test 123
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
            connectors_api = ConnectorsAPI(client)

            # Get connector - try by ID first if numeric, then by name
            connector = None
            if connector_id_or_name.isdigit():
                try:
                    connector = connectors_api.get_connector(int(connector_id_or_name))
                except APIError as e:
                    if e.status_code != 404:
                        raise

            # If not found by ID or not numeric, try by name
            if not connector:
                connector = connectors_api.get_connector_by_name(connector_id_or_name)

            if not connector:
                print_error(f"Connector '{connector_id_or_name}' not found")
                ctx.exit(1)

            connector_id = connector.get('id')
            connector_name = connector.get('name')

            console.print(f"Testing connector: {connector_name}")

            # Test connection
            result = connectors_api.test_connector(connector_id)

            if result.get('status') == 'success':
                print_success("Connection test successful!")

                # Display connection info
                if result.get('info'):
                    console.print("\n[bold]Connection Info:[/bold]")
                    for key, value in result['info'].items():
                        console.print(f"  - {key}: {value}")
            else:
                print_error(f"Connection test failed: {result.get('message')}")
                ctx.exit(1)

    except Exception as e:
        print_error(f"Failed to test connector: {e}")
        logger.exception("Error in test connector command")
        ctx.exit(1)


@connectors.command('show')
@click.argument('connector_id_or_name')
@click.pass_context
def show_connector(ctx: click.Context, connector_id_or_name: str) -> None:
    """
    Show connector details (without sensitive data)

    Examples:
        gomask connectors show prod-db
        gomask connectors show 123
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
            connectors_api = ConnectorsAPI(client)

            # Get connector - try by ID first if numeric, then by name
            connector = None
            if connector_id_or_name.isdigit():
                try:
                    connector = connectors_api.get_connector(int(connector_id_or_name))
                except APIError as e:
                    if e.status_code != 404:
                        raise

            # If not found by ID or not numeric, try by name
            if not connector:
                connector = connectors_api.get_connector_by_name(connector_id_or_name)

            if not connector:
                print_error(f"Connector '{connector_id_or_name}' not found")
                ctx.exit(1)

            connector_name = connector.get('name')

            # Display details
            console.print(f"\n[bold]Connector: {connector_name}[/bold]")
            console.print(f"  - ID: {connector.get('id')}")
            console.print(f"  - Type: {connector.get('type')}")
            console.print(f"  - Host: {connector.get('host')}")
            console.print(f"  - Port: {connector.get('port')}")
            console.print(f"  - Database: {connector.get('database')}")
            console.print(f"  - Username: {connector.get('username')}")
            console.print(f"  - SSL Mode: {connector.get('ssl', 'prefer')}")
            console.print(f"  - Status: {connector.get('status', 'unknown')}")

            if connector.get('last_tested'):
                console.print(f"  - Last Tested: {connector['last_tested']}")

            if connector.get('created_at'):
                console.print(f"  - Created: {connector['created_at']}")

    except Exception as e:
        print_error(f"Failed to show connector: {e}")
        logger.exception("Error in show connector command")
        ctx.exit(1)


@connectors.command('delete')
@click.argument('connector_id_or_name')
@click.option('--force', '-f', is_flag=True, help='Delete without confirmation')
@click.pass_context
def delete_connector(ctx: click.Context, connector_id_or_name: str, force: bool) -> None:
    """
    Delete a connector

    Examples:
        gomask connectors delete test-db
        gomask connectors delete 123 --force
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
            connectors_api = ConnectorsAPI(client)

            # Get connector - try by ID first if numeric, then by name
            connector = None
            if connector_id_or_name.isdigit():
                try:
                    connector = connectors_api.get_connector(int(connector_id_or_name))
                except APIError as e:
                    if e.status_code != 404:
                        raise

            # If not found by ID or not numeric, try by name
            if not connector:
                connector = connectors_api.get_connector_by_name(connector_id_or_name)

            if not connector:
                print_error(f"Connector '{connector_id_or_name}' not found")
                ctx.exit(1)

            connector_id = connector.get('id')
            connector_name = connector.get('name')

            # Confirm deletion
            if not force:
                if not confirm(f"Delete connector '{connector_name}'? This cannot be undone."):
                    print_warning("Deletion cancelled")
                    return

            # Delete connector
            console.print(f"Deleting connector: {connector_name}")
            connectors_api.delete_connector(connector_id)

            print_success(f"Deleted connector '{connector_name}'")

    except Exception as e:
        print_error(f"Failed to delete connector: {e}")
        logger.exception("Error in delete connector command")
        ctx.exit(1)