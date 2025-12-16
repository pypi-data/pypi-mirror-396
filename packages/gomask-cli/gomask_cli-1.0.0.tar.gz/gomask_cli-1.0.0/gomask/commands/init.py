"""
Initialize GoMask CLI configuration
"""

import re
from pathlib import Path
from typing import Optional

import click

from gomask.utils.output import console, print_success, print_error, print_warning
from gomask.utils.logger import logger


@click.command()
@click.option(
    '--secret',
    help='GoMask API secret (will be prompted if not provided)'
)
@click.option(
    '--api-url',
    default='https://cli.gomask.ai/api/v1',
    help='GoMask API URL (default: https://cli.gomask.ai)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    default='gomask.toml',
    help='Output file path (default: gomask.toml)'
)
@click.option(
    '--force',
    '-f',
    is_flag=True,
    help='Overwrite existing configuration file'
)
@click.pass_context
def init(
    ctx: click.Context,
    secret: Optional[str],
    api_url: str,
    output: str,
    force: bool
) -> None:
    """
    Initialize GoMask CLI configuration

    Creates a gomask.toml configuration file with your API credentials.
    This allows you to use the CLI without setting environment variables.

    Examples:
        gomask init
        gomask init --secret "your-secret-key"
        gomask init --api-url https://api.gomask.ai
    """
    try:
        output_path = Path(output)

        # Check if file exists
        if output_path.exists() and not force:
            console.print(f"[yellow]Configuration file already exists: {output_path}[/yellow]")
            if not click.confirm("Overwrite existing configuration?", default=False):
                print_error("Initialization cancelled")
                ctx.exit(1)

        console.print("\n[bold cyan]GoMask CLI Configuration Setup[/bold cyan]\n")

        # Check if secret was explicitly provided but is empty
        if secret is not None and (not secret or not secret.strip()):
            print_error("API secret cannot be empty")
            ctx.exit(1)

        # Prompt for secret if not provided
        if secret is None:
            console.print("[cyan]To generate an API secret:[/cyan]")
            console.print("  1. Go to [link=https://app.gomask.ai/settings/api-keys]https://app.gomask.ai/settings/api-keys[/link]")
            console.print("  2. Click 'Create New Key'")
            console.print("  3. Copy the generated secret\n")

            secret = click.prompt(
                "Enter your GoMask API secret",
                type=str,
                hide_input=True
            )

            # Validate secret is not empty after prompting
            if not secret or not secret.strip():
                print_error("API secret cannot be empty")
                ctx.exit(1)

        # Validate API URL format
        if not api_url.startswith('http://') and not api_url.startswith('https://'):
            print_error("API URL must start with http:// or https://")
            ctx.exit(1)

        # Create TOML content
        toml_content = f'''# GoMask CLI Configuration
# This file contains your API credentials for the GoMask platform
# Keep this file secure and do not commit it to version control

[gomask]
# Your GoMask API secret (generated from https://app.gomask.ai/settings/api-keys)
secret = "{secret}"

# GoMask API URL (default: https://cli.gomask.ai)
api_url = "{api_url}"

# Optional: Set to true to enable debug logging
# debug = false
'''

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(toml_content)

        # Set appropriate permissions (readable only by owner on Unix-like systems)
        try:
            output_path.chmod(0o600)
        except Exception:
            # Windows doesn't support chmod in the same way, ignore errors
            pass

        # Success message
        print_success(f"Configuration file created: {output_path}")
        console.print("\n[bold]Configuration Details:[/bold]")
        console.print(f"  - API URL: {api_url}")
        console.print(f"  - Secret: {'*' * 20} (hidden)")
        console.print(f"  - Config file: {output_path.absolute()}")

        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print("1. Test your configuration:")
        console.print(f"   [dim]gomask connectors list[/dim]")
        console.print("\n2. Create your first routine:")
        console.print(f"   [dim]gomask example --type synthetic --name 'My Routine'[/dim]")

        console.print("\n[yellow]! Important:[/yellow]")
        console.print("- Keep your gomask.toml file secure")
        console.print("- Add 'gomask.toml' to your .gitignore")
        console.print("- Do not share your API secret")

    except click.Abort:
        print_error("\nInitialization cancelled")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to create configuration: {e}")
        logger.exception("Error in init command")
        ctx.exit(1)
