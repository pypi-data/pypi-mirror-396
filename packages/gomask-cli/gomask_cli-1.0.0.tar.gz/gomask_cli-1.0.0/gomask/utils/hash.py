"""
Hashing utilities for configuration change detection
"""

import hashlib
import json
from typing import Dict, Any, Optional


def calculate_config_hash(config_data: Dict[str, Any], exclude_metadata: bool = True) -> str:
    """
    Calculate SHA-256 hash of configuration data

    Args:
        config_data: Configuration dictionary
        exclude_metadata: Whether to exclude metadata section from hash

    Returns:
        SHA-256 hash as hex string
    """
    # Create a copy to avoid modifying original
    data_to_hash = config_data.copy()

    # Exclude metadata section if requested (since it contains version, description, etc.)
    if exclude_metadata and 'metadata' in data_to_hash:
        # Keep only the unique ID from metadata for consistency
        metadata = data_to_hash.get('metadata', {})
        data_to_hash['metadata'] = {'id': metadata.get('id')}

    # Sort keys for consistent hashing
    normalized_data = normalize_dict_for_hash(data_to_hash)

    # Convert to JSON string with sorted keys
    json_string = json.dumps(normalized_data, sort_keys=True, separators=(',', ':'))

    # Calculate SHA-256 hash
    hash_object = hashlib.sha256(json_string.encode('utf-8'))
    return hash_object.hexdigest()


def normalize_dict_for_hash(data: Any) -> Any:
    """
    Normalize data structure for consistent hashing

    Args:
        data: Data to normalize

    Returns:
        Normalized data
    """
    if isinstance(data, dict):
        # Sort dictionary keys and recursively normalize values
        return {k: normalize_dict_for_hash(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        # Recursively normalize list items
        return [normalize_dict_for_hash(item) for item in data]
    elif isinstance(data, (str, int, float, bool, type(None))):
        return data
    else:
        # Convert other types to string
        return str(data)


def verify_config_changed(
    current_hash: str,
    stored_hash: Optional[str]
) -> bool:
    """
    Check if configuration has changed based on hash comparison

    Args:
        current_hash: Hash of current configuration
        stored_hash: Hash stored in database

    Returns:
        True if configuration has changed, False otherwise
    """
    if stored_hash is None:
        return True

    return current_hash != stored_hash


def hash_password(password: str) -> str:
    """
    Hash a password for secure comparison (not for storage)

    Args:
        password: Password to hash

    Returns:
        SHA-256 hash of password
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def hash_secret_key(team_id: int, routine_id: str) -> str:
    """
    Generate a deterministic hash key for secrets

    Args:
        team_id: Team ID
        routine_id: Routine unique ID

    Returns:
        Hash key for secret storage
    """
    key_string = f"team:{team_id}:routine:{routine_id}"
    return hashlib.sha256(key_string.encode('utf-8')).hexdigest()[:16]