"""
Output formatting utilities using Rich library
"""

from typing import Any, Dict, List, Optional
from contextlib import contextmanager
import time

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree
from rich import box


# Create a shared console instance
console = Console()


def print_success(message: str) -> None:
    """Print a success message with green checkmark"""
    # Use ASCII-safe characters for Windows compatibility
    console.print(f"[OK] {message}", style="green")


def print_error(message: str) -> None:
    """Print an error message with red X"""
    # Use ASCII-safe characters for Windows compatibility
    console.print(f"[X] {message}", style="red")


def print_warning(message: str) -> None:
    """Print a warning message with yellow warning sign"""
    # Use ASCII-safe characters for Windows compatibility
    console.print(f"[!] {message}", style="yellow")


def print_info(message: str) -> None:
    """Print an info message with blue info icon"""
    # Use ASCII-safe characters for Windows compatibility
    console.print(f"[i] {message}", style="blue")


def print_yaml(yaml_content: str, title: Optional[str] = None) -> None:
    """Print YAML content with syntax highlighting"""
    syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=False)
    if title:
        panel = Panel(syntax, title=title, box=box.ROUNDED)
        console.print(panel)
    else:
        console.print(syntax)


def print_json(json_content: str, title: Optional[str] = None) -> None:
    """Print JSON content with syntax highlighting"""
    syntax = Syntax(json_content, "json", theme="monokai", line_numbers=False)
    if title:
        panel = Panel(syntax, title=title, box=box.ROUNDED)
        console.print(panel)
    else:
        console.print(syntax)


def create_table(title: str, columns: List[str]) -> Table:
    """Create a formatted table"""
    table = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold magenta")
    for column in columns:
        table.add_column(column)
    return table


def print_routine_table(routines: List[Dict[str, Any]]) -> None:
    """Print a table of routines"""
    table = create_table("Routines", ["ID", "Name", "Type", "Status", "Last Modified"])

    for routine in routines:
        table.add_row(
            str(routine.get("id", "-")),
            routine.get("name", "-"),
            routine.get("type", "-"),
            routine.get("status", "-"),
            routine.get("modified_at", "-")
        )

    console.print(table)


def print_connector_table(connectors: List[Dict[str, Any]]) -> None:
    """Print a table of connectors"""
    table = create_table("Connectors", ["Name", "Type", "Host", "Database", "Status"])

    for conn in connectors:
        table.add_row(
            conn.get("name", "-"),
            conn.get("type", "-"),
            conn.get("host", "-"),
            conn.get("database", "-"),
            "[green]Active[/green]" if conn.get("status") == "active" else "[red]Inactive[/red]"
        )

    console.print(table)


@contextmanager
def spinner(text: str = "Processing..."):
    """Context manager for showing a spinner during long operations"""
    with Progress(
        SpinnerColumn(spinner_name="line"),  # Use ASCII-safe spinner for Windows compatibility
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description=text, total=None)
        yield


@contextmanager
def progress_bar(total: int, description: str = "Processing"):
    """Context manager for showing a progress bar"""
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task(description, total=total)

        def update(advance: int = 1):
            progress.update(task, advance=advance)

        yield update


def print_tree(data: Dict[str, Any], title: str = "Tree") -> None:
    """Print data as a tree structure"""
    tree = Tree(title)

    def add_branch(node: Tree, obj: Any, key: Optional[str] = None):
        """Recursively add branches to tree"""
        if key is not None:
            node = node.add(f"[bold]{key}[/bold]")

        if isinstance(obj, dict):
            for k, v in obj.items():
                add_branch(node, v, k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                add_branch(node, item, f"[{i}]")
        else:
            node.add(str(obj))

    add_branch(tree, data)
    console.print(tree)


def confirm(message: str, default: bool = False) -> bool:
    """Ask user for confirmation"""
    default_str = "Y/n" if default else "y/N"
    response = console.input(f"{message} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ['y', 'yes']


def prompt(message: str, default: Optional[str] = None, password: bool = False) -> str:
    """Prompt user for input"""
    prompt_msg = f"{message}"
    if default:
        prompt_msg += f" [{default}]"
    prompt_msg += ": "

    if password:
        from getpass import getpass
        value = getpass(prompt_msg)
    else:
        value = console.input(prompt_msg)

    return value.strip() if value else (default or "")


def print_panel(content: str, title: Optional[str] = None, style: str = "blue") -> None:
    """Print content in a panel"""
    panel = Panel(content, title=title, box=box.ROUNDED, style=style)
    console.print(panel)