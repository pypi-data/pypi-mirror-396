"""Agent flow management utilities."""

import json
import os
import sys
from typing import Any


def _resolve_dotted_path(data: dict[str, Any], path: str) -> tuple[bool, Any]:
    """Resolve a dotted path in nested dictionary.

    Args:
        data: Dictionary to search
        path: Dotted path like 'user.email' or simple key like 'name'

    Returns:
        Tuple of (found: bool, value: Any)
    """
    if not isinstance(data, dict):
        return False, None

    # Handle simple key (no dots)
    if "." not in path:
        if path in data:
            return True, data[path]
        return False, None

    # Traverse nested path
    keys = path.split(".")
    current = data

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return False, None
        current = current[key]

    return True, current


def get_flow_variable(variable_name: str | None = None, default_value: Any = None) -> Any:
    """Retrieve flow variable from execution context.

    Supports both simple keys and dotted paths for nested variables.

    Args:
        variable_name: Variable name or dotted path (e.g., 'user.email').
                      If None, returns all variables.
        default_value: Value to return if variable not found (default: None)

    Returns:
        Variable value if found, otherwise default_value

    Examples:
        >>> get_flow_variable('user.email')
        'user@example.com'

        >>> get_flow_variable('user.name', 'Anonymous')
        'John Doe'

        >>> get_flow_variable()  # Returns all variables
        {'user': {'email': '...', 'name': '...'}, ...}
    """
    try:
        # Extract payload file path from command-line arguments
        if len(sys.argv) < 3:
            return default_value

        payload_file_path = sys.argv[2]

        if not os.path.exists(payload_file_path):
            return default_value

        with open(payload_file_path) as f:
            payload = json.load(f)

        if not payload:
            return default_value

        # Return all variables if no specific variable requested
        if variable_name is None:
            return payload

        # Try dotted path resolution first (handles nested variables)
        found, value = _resolve_dotted_path(payload, variable_name)
        if found:
            return value

        # Fall back to flat key lookup for backwards compatibility
        if variable_name in payload:
            return payload[variable_name]

        return default_value

    except Exception:
        return default_value


def get_workspace_slug(default_value: Any = None) -> Any:
    """Retrieve current workspace slug"""
    try:
        return get_flow_variable("workspace_slug", default_value=default_value)
    except Exception:
        return default_value


def get_thread_id(default_value: Any = None) -> Any:
    """Retrieve current thread id"""
    try:
        return get_flow_variable("thread_id", default_value=default_value)
    except Exception:
        return default_value


def get_agent_id(default_value: Any = None) -> Any:
    """Retrieve current agent id"""
    try:
        return get_flow_variable("agent_id", default_value=default_value)
    except Exception:
        return default_value


def get_workspace_data_dir(
    variable_name: str | None = None, default_workspace_slug: Any = None
) -> Any:
    """Retrieve flow variable"""
    try:
        import os

        workspace_slug = get_workspace_slug(default_value=default_workspace_slug)
        realtimex_dir = os.path.join(os.path.expanduser("~"), ".realtimex.ai")
        realtimex_storage_dir = os.path.realpath(
            os.path.join(realtimex_dir, "Resources", "server", "storage")
        )

        if not os.path.exists(realtimex_storage_dir):
            return None

        workspace_data_dir = os.path.join(realtimex_storage_dir, "working-data", workspace_slug)

        if not os.path.exists(workspace_data_dir):
            os.makedirs(workspace_data_dir, exist_ok=True)

        return workspace_data_dir

    except Exception:
        return None


__all__ = [
    "get_agent_id",
    "get_flow_variable",
    "get_thread_id",
    "get_workspace_data_dir",
    "get_workspace_slug",
]
