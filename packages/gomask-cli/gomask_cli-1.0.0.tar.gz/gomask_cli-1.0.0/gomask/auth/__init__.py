"""
Authentication and secret management for GoMask CLI
Simplified version - just checks for secret existence, backend handles decryption
"""

from gomask.auth.secret import (
    get_secret,
    get_secret_from_env,
    has_secret
)
from gomask.auth.middleware import (
    add_auth_headers,
    create_api_headers,
    get_auth_context
)

__all__ = [
    "get_secret",
    "get_secret_from_env",
    "has_secret",
    "add_auth_headers",
    "create_api_headers",
    "get_auth_context"
]