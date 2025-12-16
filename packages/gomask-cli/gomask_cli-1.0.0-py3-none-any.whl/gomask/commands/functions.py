"""
Data Functions command - explore and discover available data generation and transformation functions
"""

from typing import Optional, List, Dict, Any
import json

import click

from gomask.api.client import GoMaskAPIClient
from gomask.api.functions import FunctionsAPI
from gomask.utils.output import (
    console, print_success, print_error, print_warning,
    print_info, create_table, print_json
)
from gomask.utils.logger import logger


@click.group()
@click.pass_context
def functions(ctx: click.Context) -> None:
    """
    Explore and discover data functions

    Data functions are the building blocks for synthetic data generation
    and data masking. They can be generators (create new data),
    transformers (mask existing data), or utilities (helper functions).
    """
    pass


@functions.command('list')
@click.option(
    '--type',
    'function_type',
    type=click.Choice(['generator', 'transformer', 'utility']),
    help='Filter by function type'
)
@click.option(
    '--data-type',
    help='Filter by data type (e.g., string, number, date)'
)
@click.option(
    '--tag',
    'tags',
    multiple=True,
    help='Filter by tags (can be specified multiple times)'
)
@click.option(
    '--category',
    help='Filter by category'
)
@click.option(
    '--search',
    help='Search in function names and descriptions'
)
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['table', 'json', 'names']),
    default='table',
    help='Output format'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Show detailed information'
)
@click.option(
    '--limit',
    '-l',
    type=int,
    default=None,
    help='Limit number of results'
)
@click.pass_context
def list_functions(
    ctx: click.Context,
    function_type: Optional[str],
    data_type: Optional[str],
    tags: tuple,
    category: Optional[str],
    search: Optional[str],
    output_format: str,
    verbose: bool,
    limit: Optional[int]
) -> None:
    """
    List available data functions

    Examples:
        # List all generator functions
        gomask functions list --type generator

        # Find functions for medical data
        gomask functions list --tag medical --tag healthcare

        # Search for email-related functions
        gomask functions list --search email

        # List functions for string data types
        gomask functions list --data-type string

        # Limit results
        gomask functions list --limit 10

        # Combine filters
        gomask functions list --type generator --data-type string --category personal --limit 20
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
            functions_api = FunctionsAPI(client)

            # Build filters
            if output_format != 'json':
                console.print("Fetching data functions...")

            # Convert tags tuple to list
            tags_list = list(tags) if tags else None

            # Get functions
            function_list = functions_api.list_functions(
                function_type=function_type,
                data_type=data_type,
                tags=tags_list,
                category=category,
                search=search,
                limit=limit
            )

            if not function_list:
                if output_format == 'json':
                    # Return empty JSON array - use plain print to avoid control characters
                    print(json.dumps([], indent=2))
                    return

                print_warning("No functions found matching the specified filters")
                if function_type:
                    console.print(f"  Type: {function_type}")
                if data_type:
                    console.print(f"  Data Type: {data_type}")
                if tags:
                    console.print(f"  Tags: {', '.join(tags)}")
                if category:
                    console.print(f"  Category: {category}")
                if search:
                    console.print(f"  Search: {search}")
                return

            # Format output
            if output_format == 'json':
                # Use plain print to avoid control characters in JSON
                print(json.dumps(function_list, indent=2))
            elif output_format == 'names':
                # Simple list of function names
                for func in function_list:
                    console.print(func.get('name', 'Unknown'))
            else:  # table format
                _print_function_table(function_list, verbose)

            # Summary and filters only for non-JSON output
            if output_format != 'json':
                console.print(f"\nTotal functions: {len(function_list)}")

                # Show applied filters
                if function_type or data_type or tags or category or search:
                    console.print("\n[dim]Applied filters:[/dim]")
                    if function_type:
                        console.print(f"  [dim]- Type: {function_type}[/dim]")
                    if data_type:
                        console.print(f"  [dim]- Data Type: {data_type}[/dim]")
                    if tags:
                        console.print(f"  [dim]- Tags: {', '.join(tags)}[/dim]")
                    if category:
                        console.print(f"  [dim]- Category: {category}[/dim]")
                    if search:
                        console.print(f"  [dim]- Search: {search}[/dim]")

    except Exception as e:
        print_error(f"Failed to list functions: {e}")
        logger.exception("Error in list functions command")
        ctx.exit(1)


@functions.command('show')
@click.argument('identifier')
@click.pass_context
def show_function(ctx: click.Context, identifier: str) -> None:
    """
    Show detailed information about a specific function

    You can specify either a function ID or name. If multiple functions
    have the same name, all will be displayed.

    Examples:
        gomask functions show faker_email
        gomask functions show 123
        gomask functions show mask_credit_card
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
            functions_api = FunctionsAPI(client)

            # Try to determine if identifier is an ID (integer) or name
            is_id = False
            try:
                int(identifier)
                is_id = True
            except ValueError:
                is_id = False

            # Get function details
            if is_id:
                # Search by ID - should return single result
                result = functions_api.get_function_by_id(identifier)
                functions_to_display = [result] if result else []
            else:
                # Search by name - may return multiple results
                result = functions_api.get_functions_by_name(identifier)
                functions_to_display = result if isinstance(result, list) else ([result] if result else [])

            if not functions_to_display:
                print_error(f"Function '{identifier}' not found")
                ctx.exit(1)

            # Display all matching functions
            for idx, function in enumerate(functions_to_display):
                if len(functions_to_display) > 1:
                    console.print(f"\n[bold cyan]{'=' * 80}[/bold cyan]")
                    console.print(f"[bold cyan]Function {idx + 1} of {len(functions_to_display)}[/bold cyan]")
                    console.print(f"[bold cyan]{'=' * 80}[/bold cyan]")

                # Display details
                console.print(f"\n[bold]{function.get('name', 'Unknown')} [dim](ID: {function.get('id', 'N/A')})[/dim][/bold]")
                console.print(f"{function.get('description', 'No description available')}\n")

                console.print("[bold]Details:[/bold]")
                console.print(f"  Type: {function.get('function_type', 'Unknown')}")
                console.print(f"  Category: {function.get('category', 'N/A')}")

                # Data types
                data_types = function.get('data_types', [])
                if data_types:
                    console.print(f"  Data Types: {', '.join(data_types)}")

                # Tags
                tags = function.get('tags', [])
                if tags:
                    console.print(f"  Tags: {', '.join(tags)}")

                # Team info (if custom function)
                is_builtin = function.get('is_builtin', False)
                is_public = function.get('is_public', False)
                if not is_builtin:
                    if is_public:
                        console.print(f"  Visibility: [green]Public[/green]")
                    else:
                        console.print(f"  Visibility: [yellow]Team-specific[/yellow]")

                # Parameters
                params = function.get('parameters', {})
                if params:
                    console.print("\n[bold]Parameters:[/bold]")
                    for param_name, param_info in params.items():
                        required = "[red]*[/red]" if param_info.get('required') else ""
                        param_type = param_info.get('type', 'any')
                        description = param_info.get('description', '')
                        default = param_info.get('default')

                        console.print(f"  {param_name}{required} ({param_type})")
                        if description:
                            console.print(f"    {description}")
                        if default is not None:
                            console.print(f"    Default: {default}")

                # Examples
                examples = function.get('examples', [])
                if examples:
                    console.print("\n[bold]Examples:[/bold]")
                    for example in examples:
                        console.print(f"  {example}")

                # Output
                output_info = function.get('output', {})
                if output_info and output_info.get('type'):
                    console.print("\n[bold]Output:[/bold]")
                    console.print(f"  Type: {output_info.get('type', 'Unknown')}")
                    if output_info.get('description'):
                        console.print(f"  {output_info['description']}")

                # Version
                version = function.get('version')
                if version:
                    console.print(f"\n[dim]Version: {version}[/dim]")

                # Python code (if available)
                python_code = function.get('python_code')
                if python_code:
                    console.print("\n[bold]Implementation:[/bold]")
                    console.print("[dim]This function is publicly available[/dim]")

            # Summary if multiple functions
            if len(functions_to_display) > 1:
                console.print(f"\n[bold cyan]Found {len(functions_to_display)} functions with name '{identifier}'[/bold cyan]")
                console.print("[dim]Tip: Use the ID to view a specific function[/dim]")

    except Exception as e:
        print_error(f"Failed to show function: {e}")
        logger.exception("Error in show function command")
        ctx.exit(1)


@functions.command('categories')
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['table', 'json'], case_sensitive=False),
    default='table',
    help='Output format'
)
@click.pass_context
def list_categories(ctx: click.Context, output_format: str) -> None:
    """
    List all available function categories

    Examples:
        gomask functions categories
        gomask functions categories --format json
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
            functions_api = FunctionsAPI(client)

            # Get categories
            categories = functions_api.get_function_categories()

            if not categories:
                if output_format == 'json':
                    # Use plain print to avoid control characters
                    print(json.dumps([], indent=2))
                    return
                print_warning("No categories found")
                return

            # Format output
            if output_format == 'json':
                # Use plain print to avoid control characters in JSON
                print(json.dumps(sorted(categories), indent=2))
            else:
                console.print("\n[bold]Available Categories:[/bold]")
                for category in sorted(categories):
                    console.print(f"  - {category}")

                console.print(f"\nTotal categories: {len(categories)}")

    except Exception as e:
        print_error(f"Failed to list categories: {e}")
        logger.exception("Error in list categories command")
        ctx.exit(1)


@functions.command('tags')
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['table', 'json'], case_sensitive=False),
    default='table',
    help='Output format'
)
@click.pass_context
def list_tags(ctx: click.Context, output_format: str) -> None:
    """
    List all available function tags

    Examples:
        gomask functions tags
        gomask functions tags --format json
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
            functions_api = FunctionsAPI(client)

            # Get tags
            tags = functions_api.get_function_tags()

            if not tags:
                if output_format == 'json':
                    # Use plain print to avoid control characters
                    print(json.dumps([], indent=2))
                    return
                print_warning("No tags found")
                return

            # Format output
            if output_format == 'json':
                # Use plain print to avoid control characters in JSON
                print(json.dumps(sorted(tags), indent=2))
            else:
                console.print("\n[bold]Available Tags:[/bold]")

                # Group tags by first letter for better readability
                grouped = {}
                for tag in sorted(tags):
                    first_letter = tag[0].upper()
                    if first_letter not in grouped:
                        grouped[first_letter] = []
                    grouped[first_letter].append(tag)

                for letter in sorted(grouped.keys()):
                    console.print(f"\n[dim]{letter}:[/dim]")
                    for tag in grouped[letter]:
                        console.print(f"  - {tag}")

                console.print(f"\nTotal tags: {len(tags)}")

    except Exception as e:
        print_error(f"Failed to list tags: {e}")
        logger.exception("Error in list tags command")
        ctx.exit(1)


def _print_function_table(functions: List[Dict[str, Any]], verbose: bool = False) -> None:
    """Print functions in a formatted table"""
    if verbose:
        # Detailed table with more columns
        table = create_table(
            "Data Functions",
            ["ID", "Name", "Type", "Category", "Data Types", "Tags", "Description"]
        )

        for func in functions:
            # Format data types
            data_types = func.get('data_types', [])
            data_types_str = ', '.join(data_types[:3])
            if len(data_types) > 3:
                data_types_str += f" (+{len(data_types)-3})"

            # Format tags
            tags = func.get('tags', [])
            tags_str = ', '.join(tags[:3])
            if len(tags) > 3:
                tags_str += f" (+{len(tags)-3})"

            # Truncate description
            desc = func.get('description', '')
            if len(desc) > 50:
                desc = desc[:47] + "..."

            table.add_row(
                str(func.get('id', '-')),
                func.get('name', 'Unknown'),
                func.get('function_type', '-'),
                func.get('category', '-'),
                data_types_str or '-',
                tags_str or '-',
                desc
            )
    else:
        # Simple table
        table = create_table(
            "Data Functions",
            ["ID", "Name", "Type", "Category", "Description"]
        )

        for func in functions:
            # Truncate description
            desc = func.get('description', '')
            if len(desc) > 60:
                desc = desc[:57] + "..."

            # Color code function types
            func_type = func.get('function_type', '-')
            if func_type == 'generator':
                func_type = f"[green]{func_type}[/green]"
            elif func_type == 'transformer':
                func_type = f"[yellow]{func_type}[/yellow]"
            elif func_type == 'utility':
                func_type = f"[blue]{func_type}[/blue]"

            table.add_row(
                str(func.get('id', '-')),
                func.get('name', 'Unknown'),
                func_type,
                func.get('category', '-'),
                desc
            )

    console.print(table)