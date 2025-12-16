"""
Manage routine executions
"""

from typing import Optional
import click

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.api.execution import ExecutionAPI, ExecutionStatus
from gomask.utils.output import (
    console, print_success, print_error, print_warning
)
from gomask.utils.logger import logger


@click.group()
@click.pass_context
def executions(ctx: click.Context) -> None:
    """
    Manage routine executions

    View execution status, logs, and history for your routines.
    """
    pass


@executions.command('list')
@click.option('--routine-id', type=int, help='Filter by routine ID')
@click.option('--status', help='Filter by status (pending, running, completed, failed, cancelled)')
@click.option('--limit', type=int, default=20, help='Maximum number of executions to return')
@click.option('--offset', type=int, default=0, help='Pagination offset')
@click.pass_context
def list_executions(
    ctx: click.Context,
    routine_id: Optional[int],
    status: Optional[str],
    limit: int,
    offset: int
) -> None:
    """
    List routine executions

    Examples:
        gomask executions list
        gomask executions list --routine-id 123
        gomask executions list --status completed
        gomask executions list --limit 50
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
            execution_api = ExecutionAPI(client)

            # Get executions
            executions_list = execution_api.list_executions(
                routine_id=routine_id,
                status=status,
                limit=limit,
                offset=offset
            )

            if not executions_list:
                console.print("No executions found")
                return

            # Display table header
            console.print("\n[bold]Executions:[/bold]")
            console.print("")

            # Display executions
            for execution in executions_list:
                exec_id = execution.get('id', '-')
                exec_status = execution.get('status', '-')
                routine_name = execution.get('routine_name', '-')
                routine_id_str = execution.get('routine_id', '-')
                started_at = execution.get('started_at', '-')
                completed_at = execution.get('completed_at', '-')

                # Status color
                status_color = {
                    'pending': 'yellow',
                    'running': 'cyan',
                    'completed': 'green',
                    'failed': 'red',
                    'cancelled': 'yellow'
                }.get(exec_status.lower(), 'white')

                console.print(f"[bold]Execution ID {exec_id}[/bold]")
                console.print(f"  Routine: {routine_name} (ID: {routine_id_str})")
                console.print(f"  Status: [{status_color}]{exec_status}[/{status_color}]")
                console.print(f"  Started: {started_at}")
                if completed_at and completed_at != '-':
                    console.print(f"  Completed: {completed_at}")
                console.print("")

            console.print(f"Showing {len(executions_list)} execution(s)")
            if offset > 0:
                console.print(f"Offset: {offset}")

    except APIError as e:
        print_error(f"Failed to list executions: {e}")
        logger.exception("Error in list executions command")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to list executions: {e}")
        logger.exception("Error in list executions command")
        ctx.exit(1)


@executions.command('show')
@click.argument('execution_id', type=int)
@click.option('--logs', is_flag=True, help='Show execution logs')
@click.pass_context
def show_execution(
    ctx: click.Context,
    execution_id: int,
    logs: bool
) -> None:
    """
    Show detailed execution information

    Examples:
        gomask executions show 456
        gomask executions show 456 --logs
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
            execution_api = ExecutionAPI(client)

            # Get execution status
            status_info = execution_api.get_status(execution_id)

            if not status_info:
                print_error(f"Execution {execution_id} not found")
                ctx.exit(1)

            # Display execution details
            exec_status = status_info.get('status', '-')
            routine_name = status_info.get('routine_name', '-')
            routine_id = status_info.get('routine_id', '-')
            started_at = status_info.get('started_at', '-')
            completed_at = status_info.get('completed_at', '-')

            # Status color
            status_color = {
                'pending': 'yellow',
                'running': 'cyan',
                'completed': 'green',
                'failed': 'red',
                'cancelled': 'yellow'
            }.get(exec_status.lower(), 'white')

            console.print(f"\n[bold]Execution ID: {execution_id}[/bold]")
            console.print(f"  Routine: {routine_name} (ID: {routine_id})")
            console.print(f"  Status: [{status_color}]{exec_status}[/{status_color}]")
            console.print(f"  Started: {started_at}")
            if completed_at and completed_at != '-':
                console.print(f"  Completed: {completed_at}")

            # Get progress if running
            if exec_status.lower() == 'running':
                try:
                    progress_info = execution_api.get_progress(execution_id)
                    if progress_info:
                        percent = progress_info.get('percent', 0)
                        current_table = progress_info.get('current_table', 'unknown')
                        records = progress_info.get('records_processed', 0)

                        console.print(f"\n[bold]Progress:[/bold]")
                        console.print(f"  {percent}% complete")
                        console.print(f"  Current table: {current_table}")
                        console.print(f"  Records processed: {records:,}")
                except Exception as e:
                    logger.debug(f"Could not fetch progress: {e}")

            # Get summary if completed or failed
            if exec_status.lower() in ['completed', 'failed']:
                try:
                    summary = execution_api.get_summary(execution_id)
                    if summary:
                        console.print(f"\n[bold]Summary:[/bold]")

                        duration = summary.get('duration', 'unknown')
                        total_records = summary.get('total_records', 0)
                        tables_processed = summary.get('tables_processed', 0)

                        console.print(f"  Duration: {duration}")
                        console.print(f"  Records processed: {total_records:,}")
                        console.print(f"  Tables processed: {tables_processed}")

                        if exec_status.lower() == 'failed':
                            error_msg = summary.get('error_message', 'Unknown error')
                            console.print(f"\n[red]Error: {error_msg}[/red]")
                except Exception as e:
                    logger.debug(f"Could not fetch summary: {e}")

            # Show logs if requested
            if logs:
                console.print(f"\n[bold]Logs:[/bold]")
                try:
                    for log_entry in execution_api.stream_logs(execution_id, follow=False):
                        console.print(f"  {log_entry}")
                except Exception as e:
                    print_warning(f"Could not fetch logs: {e}")

            # Suggest next steps
            if exec_status.lower() == 'running':
                console.print(f"\n[bold]Next steps:[/bold]")
                console.print(f"  Watch progress: gomask executions show {execution_id}")
                console.print(f"  View logs: gomask executions show {execution_id} --logs")
                console.print(f"  Cancel: gomask executions cancel {execution_id}")

    except APIError as e:
        if e.status_code == 404:
            print_error(f"Execution {execution_id} not found")
        else:
            print_error(f"Failed to show execution: {e}")
        logger.exception("Error in show execution command")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to show execution: {e}")
        logger.exception("Error in show execution command")
        ctx.exit(1)


@executions.command('cancel')
@click.argument('execution_id', type=int)
@click.pass_context
def cancel_execution(
    ctx: click.Context,
    execution_id: int
) -> None:
    """
    Cancel a running execution

    Examples:
        gomask executions cancel 456
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
            execution_api = ExecutionAPI(client)

            # Cancel execution
            console.print(f"Cancelling execution {execution_id}...")
            execution_api.cancel(execution_id)
            print_success(f"Execution {execution_id} cancelled")

    except APIError as e:
        if e.status_code == 404:
            print_error(f"Execution {execution_id} not found")
        else:
            print_error(f"Failed to cancel execution: {e}")
        logger.exception("Error in cancel execution command")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to cancel execution: {e}")
        logger.exception("Error in cancel execution command")
        ctx.exit(1)


@executions.command('logs')
@click.argument('execution_id', type=int)
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.pass_context
def show_logs(
    ctx: click.Context,
    execution_id: int,
    follow: bool
) -> None:
    """
    Show execution logs

    Examples:
        gomask executions logs 456
        gomask executions logs 456 --follow
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
            execution_api = ExecutionAPI(client)

            # Stream logs
            console.print(f"[bold]Logs for execution {execution_id}:[/bold]\n")

            try:
                for log_entry in execution_api.stream_logs(execution_id, follow=follow):
                    console.print(log_entry)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped following logs[/yellow]")
                ctx.exit(130)

    except APIError as e:
        if e.status_code == 404:
            print_error(f"Execution {execution_id} not found")
        else:
            print_error(f"Failed to show logs: {e}")
        logger.exception("Error in show logs command")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to show logs: {e}")
        logger.exception("Error in show logs command")
        ctx.exit(1)
