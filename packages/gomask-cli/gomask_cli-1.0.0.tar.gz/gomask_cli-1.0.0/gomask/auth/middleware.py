"""
Authentication middleware for API requests - simplified version
Just passes the secret to the backend, no local decryption
"""

from typing import Dict, Optional

from gomask.auth.secret import get_secret


def create_api_headers(
    secret: Optional[str] = None,
    additional_headers: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Create API headers with authentication

    Args:
        secret: Authentication secret (uses env var if not provided)
        additional_headers: Any additional headers to include

    Returns:
        Complete headers dictionary

    Raises:
        ValueError: If no secret is provided
    """
    # Get the secret
    secret_token = get_secret(secret)

    # Start with base headers
    headers = {
        'User-Agent': 'GoMask-CLI/1.0.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {secret_token}',
        'X-CLI-Version': '1.0.0'
    }

    # Add additional headers if provided
    if additional_headers:
        headers.update(additional_headers)

    return headers


def add_auth_headers(
    headers: Dict[str, str],
    secret: Optional[str] = None
) -> Dict[str, str]:
    """
    Add authentication headers to existing headers

    Args:
        headers: Existing headers dictionary
        secret: Optional encrypted secret (uses env var if not provided)

    Returns:
        Headers dictionary with authentication added

    Raises:
        ValueError: If no secret is provided
    """
    # Get the secret
    secret_token = get_secret(secret)

    # Add authentication header
    headers = headers.copy()  # Don't modify original
    headers['Authorization'] = f'Bearer {secret_token}'
    headers['X-CLI-Version'] = '1.0.0'

    return headers


def get_auth_context(secret: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    Get minimal authentication context

    Note: Full context is extracted server-side. This just returns the secret
    for backward compatibility with existing code.

    Args:
        secret: Secret string (uses env var if not provided)

    Returns:
        Minimal context dict or None if invalid
    """
    try:
        secret_token = get_secret(secret)
        return {'secret': secret_token}
    except ValueError:
        return None