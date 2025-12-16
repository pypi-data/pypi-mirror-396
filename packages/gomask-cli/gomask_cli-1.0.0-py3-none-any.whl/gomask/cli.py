#!/usr/bin/env python3
"""
Main CLI entry point for GoMask
"""

import sys
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.traceback import install as install_rich_traceback
from dotenv import load_dotenv

from gomask.utils.logger import setup_logging, logger
from gomask.utils.output import console
from gomask.utils.config import get_config
from gomask.utils.credits import check_credit_status
from gomask.commands import init as init_cmd
from gomask.commands import example as example_cmd
from gomask.commands import validate as validate_cmd
from gomask.commands import import_cmd
from gomask.commands import export as export_cmd
from gomask.commands import run as run_cmd
from gomask.commands import connectors as connectors_cmd
from gomask.commands import functions as functions_cmd
from gomask.commands import routines as routines_cmd
from gomask.commands import executions as executions_cmd
from gomask.commands import setup as setup_cmd
from gomask import __version__

# Install rich traceback handler for better error display
install_rich_traceback()

# Load environment variables from .env file if present
load_dotenv()
# Load configuration from gomask.toml
config = get_config()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--debug',
    is_flag=True,
    default=False,
    help='Enable debug logging'
)
@click.option(
    '--api-url',
    default=None,
    help='GoMask API URL (overrides config file and environment)'
)
@click.option(
    '--secret',
    default=None,
    help='Encrypted authentication secret from GoMask UI (overrides config file and environment)'
)
@click.version_option(version=__version__, prog_name="gomask")
@click.pass_context
def cli(ctx: click.Context, debug: bool, api_url: Optional[str], secret: Optional[str]) -> None:
    """
    GoMask CLI - Configuration as Code for Synthetic Data Generation and Masking

    Manage your data generation and masking routines through YAML configuration files.
    Enable version control, CI/CD integration, and team collaboration.

    Get started:
      gomask init                                            # Set up configuration
      gomask example --type synthetic --name "Customer Data" # Create example routine
      gomask validate routine.yaml                           # Validate configuration
      gomask import routine.yaml                             # Import to GoMask
      gomask run routine.yaml --watch                        # Run routine
    """
    # Setup logging (check config file first, then CLI flag)
    if not debug:
        debug = config.get_debug()
    setup_logging(debug)

    # Resolve configuration priority: CLI flag > config file > environment > default
    resolved_api_url = api_url or config.get_api_url()
    resolved_secret = secret or config.get_secret()

    # Store common options in context
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['API_URL'] = resolved_api_url
    ctx.obj['SECRET'] = resolved_secret

    # Check for authentication secret (skip for commands that don't need it)
    commands_without_auth = ['init', 'example', 'version', 'validate', None]
    if not resolved_secret and ctx.invoked_subcommand not in commands_without_auth:
        console.print(
            "[yellow]⚠️  Warning: No authentication secret provided.[/yellow]\n"
            "Run 'gomask init' to set up your configuration, or\n"
            "Set GOMASK_SECRET environment variable, or use --secret flag.\n"
            "Generate a CLI secret from https://app.gomask.ai/settings/api-keys",
            style="yellow"
        )
   
    # Check credit status if authenticated (skip for commands that don't need it)
    if resolved_secret and resolved_api_url and ctx.invoked_subcommand not in commands_without_auth:
        logger.debug(f"Running credit check for command: {ctx.invoked_subcommand}")
        check_credit_status(resolved_api_url, resolved_secret, show_warning=True)


# Register commands
cli.add_command(init_cmd.init)
cli.add_command(example_cmd.example)
cli.add_command(validate_cmd.validate)
cli.add_command(import_cmd.import_yaml, name='import')
cli.add_command(export_cmd.export)
cli.add_command(run_cmd.run)
cli.add_command(connectors_cmd.connectors)
cli.add_command(functions_cmd.functions)
cli.add_command(routines_cmd.routines)
cli.add_command(executions_cmd.executions)
cli.add_command(setup_cmd.setup_cmd, name='setup')


@cli.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Show version information"""
    console.print(f"GoMask CLI version {__version__}")
    console.print(f"API URL: {ctx.obj['API_URL']}")
    console.print(f"Debug mode: {'enabled' if ctx.obj['DEBUG'] else 'disabled'}")


def main() -> int:
    """Main entry point"""
    try:
        cli()
        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        return 130
    except Exception as e:
        if '--debug' in sys.argv or os.getenv('GOMASK_DEBUG'):
            raise
        console.print(f"[red]Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())