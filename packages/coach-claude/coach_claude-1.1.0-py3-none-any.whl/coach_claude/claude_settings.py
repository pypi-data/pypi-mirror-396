"""Claude Code settings manager for Coach Claude."""

import json
import shutil
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .config import DEFAULT_PORT

# MCP configuration for Coach Claude
MCP_CONFIG = {"type": "sse", "url": f"http://localhost:{DEFAULT_PORT}/sse"}

MCP_NAME = "coach-claude"


def get_settings_path() -> Path:
    """Get the Claude settings file path."""
    return Path.home() / ".claude" / "settings.json"


def backup_settings() -> Optional[Path]:
    """Create a timestamped backup of the settings file.

    Returns the backup path, or None if no settings file exists.
    """
    settings_path = get_settings_path()
    if not settings_path.exists():
        return None

    timestamp = int(time.time())
    backup_path = settings_path.parent / f"settings.json.backup.{timestamp}"
    shutil.copy2(settings_path, backup_path)
    return backup_path


def read_settings() -> Dict[str, Any]:
    """Read the current settings file.

    Returns an empty dict if the file doesn't exist.
    """
    settings_path = get_settings_path()
    if not settings_path.exists():
        return {}

    try:
        with open(settings_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def write_settings(settings: Dict[str, Any]) -> None:
    """Write settings to the settings file."""
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")  # Trailing newline


def is_mcp_configured() -> bool:
    """Check if the coach-claude MCP server is configured."""
    settings = read_settings()
    mcp_servers = settings.get("mcpServers", {})
    return MCP_NAME in mcp_servers


def get_mcp_config() -> Optional[Dict[str, Any]]:
    """Get the current MCP configuration for coach-claude."""
    settings = read_settings()
    mcp_servers = settings.get("mcpServers", {})
    return mcp_servers.get(MCP_NAME)


def add_mcp_config(port: int = DEFAULT_PORT) -> Path:
    """Add the coach-claude MCP configuration.

    Creates a backup before modifying.
    Returns the backup path.
    """
    # Backup first
    backup_path = backup_settings()

    # Read current settings
    settings = read_settings()

    # Ensure mcpServers exists
    if "mcpServers" not in settings:
        settings["mcpServers"] = {}

    # Add or update coach-claude config
    settings["mcpServers"][MCP_NAME] = {"type": "sse", "url": f"http://localhost:{port}/sse"}

    # Write back
    write_settings(settings)

    return backup_path


def remove_mcp_config() -> None:
    """Remove the coach-claude MCP configuration."""
    settings = read_settings()

    if "mcpServers" in settings and MCP_NAME in settings["mcpServers"]:
        del settings["mcpServers"][MCP_NAME]

        # Clean up empty mcpServers
        if not settings["mcpServers"]:
            del settings["mcpServers"]

        write_settings(settings)


def get_mcp_config_json(port: int = DEFAULT_PORT, for_devcontainer: bool = False) -> str:
    """Get the MCP config as a JSON string for display.

    Args:
        port: The port number
        for_devcontainer: If True, use host.docker.internal instead of localhost
    """
    host = "host.docker.internal" if for_devcontainer else "localhost"
    config = {"mcpServers": {MCP_NAME: {"type": "sse", "url": f"http://{host}:{port}/sse"}}}
    return json.dumps(config, indent=2)
