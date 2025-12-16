"""
Secret management for CLI authentication - simplified version
Only checks for existence of secret, actual decryption happens server-side
"""

import os
from typing import Optional


def get_secret_from_env() -> Optional[str]:
    """
    Get the secret from environment variable

    Returns:
        Secret string or None if not set
    """
    return os.getenv('GOMASK_SECRET')


def get_secret(secret: Optional[str] = None) -> str:
    """
    Get the authentication secret

    Args:
        secret: Optional secret string (uses env var if not provided)

    Returns:
        Secret string

    Raises:
        ValueError: If no secret is provided
    """
    # Get secret from parameter or environment
    secret = secret or get_secret_from_env()

    if not secret:
        raise ValueError(
            "No authentication secret provided. "
            "Set GOMASK_SECRET environment variable or use --secret flag."
        )

    return secret.strip()


def has_secret(secret: Optional[str] = None) -> bool:
    """
    Check if a secret is available

    Args:
        secret: Optional secret string (uses env var if not provided)

    Returns:
        True if secret is available, False otherwise
    """
    try:
        get_secret(secret)
        return True
    except ValueError:
        return False