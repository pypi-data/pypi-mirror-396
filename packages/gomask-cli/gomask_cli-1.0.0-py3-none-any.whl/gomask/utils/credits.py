"""
Credit usage checking and warnings for CLI commands
"""

from typing import Optional, Dict, Any
from rich.panel import Panel

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.utils.output import console
from gomask.utils.logger import logger


def check_credit_status(api_url: str, secret: str, show_warning: bool = True) -> Optional[Dict[str, Any]]:
    """
    Check credit status and optionally display warning if approaching limit

    Args:
        api_url: API URL
        secret: Authentication secret
        show_warning: Whether to display warning message if approaching limit

    Returns:
        Credit status dict if successful, None if check failed
    """
    logger.debug(f"check_credit_status called with api_url={api_url}, show_warning={show_warning}")

    try:
        client = GoMaskAPIClient(base_url=api_url, secret=secret)

        # Call the credit-status endpoint
        logger.debug(f"Checking credit status at {api_url}/api/v1/credit-status")
        status_data = client.get("/cli/credit-status")
        logger.debug(f"Credit status response: {status_data}")

        usage = status_data.get('usage', {})
        status = status_data.get('status', {})
        organization = status_data.get('organization', {})
        plan_limits = status_data.get('plan_limits', {})

        current = usage.get('current', 0)
        limit = usage.get('limit', -1)
        percentage = usage.get('percentage', 0)
        remaining = usage.get('remaining', -1)

        warning = status.get('warning', False)
        allowed = status.get('allowed', True)
        message = status.get('message')

        plan_name = organization.get('plan_name', 'Unknown')
        org_name = organization.get('name', 'Unknown')

        # Log for debugging
        logger.debug(f"Credit status: {current:,}/{limit:,} ({percentage:.1f}%) - {plan_name}")

        # Display warning if approaching limit and warnings are enabled
        if show_warning and (warning or not allowed):
            # Format the warning message
            if limit == -1:
                limit_display = "Unlimited"
                remaining_display = "Unlimited"
            else:
                limit_display = f"{limit:,}"
                remaining_display = f"{remaining:,}" if remaining > 0 else "0"

            current_display = f"{current:,}"

            # Choose color based on severity
            if not allowed:
                color = "red"
                icon = "🚫"
                title = "Monthly Credit Limit Reached"
            elif percentage >= 90:
                color = "red"
                icon = "⚠️ "
                title = "Monthly Credit Limit Warning"
            else:
                color = "yellow"
                icon = "⚠️ "
                title = "Monthly Credit Usage Warning"

            # Build warning text
            warning_text = f"""[bold]{icon} {title}[/bold]

[{color}]Organization:[/{color}] {org_name}
[{color}]Plan:[/{color}] {plan_name}
[{color}]Credits Used:[/{color}] {current_display} / {limit_display} ({percentage:.1f}%)
[{color}]Remaining:[/{color}] {remaining_display}

"""

            if message:
                warning_text += f"[{color}]{message}[/{color}]\n"

            if not allowed:
                warning_text += f"\n[bold {color}]You have exceeded your monthly credit limit.[/bold {color}]"
                warning_text += f"\n[{color}]Upgrade your plan or wait for the monthly reset.[/{color}]"
            elif percentage >= 90:
                warning_text += f"\n[{color}]Consider upgrading your plan to avoid service interruption.[/{color}]"

            # Display panel
            console.print(Panel(
                warning_text.strip(),
                border_style=color,
                padding=(1, 2)
            ))
            console.print()  # Add spacing

            # If limit exceeded, return False to indicate failure
            if not allowed:
                return None

        return status_data

    except APIError as e:
        # Don't fail the command if credit check fails, just log
        logger.debug(f"Failed to check credit status: {e}")
        if e.status_code:
            logger.debug(f"Status code: {e.status_code}")
        return None
    except Exception as e:
        # Catch any other errors
        logger.error(f"Unexpected error checking credit status: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None


def format_credit_display(current: int, limit: int, percentage: float) -> str:
    """
    Format credit usage for display

    Args:
        current: Current usage
        limit: Credit limit (-1 for unlimited)
        percentage: Usage percentage

    Returns:
        Formatted string
    """
    if limit == -1:
        return f"{current:,} (Unlimited)"

    return f"{current:,} / {limit:,} ({percentage:.1f}%)"
