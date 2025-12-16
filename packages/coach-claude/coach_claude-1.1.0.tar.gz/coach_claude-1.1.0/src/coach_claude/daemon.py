"""Cross-platform daemon management for Coach Claude."""

import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .config import get_db_path, DEFAULT_PORT

# Service identifiers
MACOS_LABEL = "com.clutch.coach-claude"
LINUX_SERVICE = "coach-claude"


def get_executable_path() -> Optional[Path]:
    """Find the coach-claude executable."""
    # Try shutil.which first
    exe = shutil.which("coach-claude")
    if exe:
        return Path(exe)

    # Try common locations
    for path in [
        Path(sys.prefix) / "bin" / "coach-claude",
        Path.home() / ".local" / "bin" / "coach-claude",
        Path("/usr/local/bin/coach-claude"),
    ]:
        if path.exists():
            return path

    return None


def get_logs_path() -> Path:
    """Get the logs directory path."""
    logs_dir = Path.home() / ".coach-claude" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_system() -> str:
    """Get the current operating system."""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        return "unsupported"


# --- macOS (launchd) ---


def _get_plist_path() -> Path:
    """Get the launchd plist file path."""
    return Path.home() / "Library" / "LaunchAgents" / f"{MACOS_LABEL}.plist"


def _generate_plist(exe_path: Path, port: int = DEFAULT_PORT) -> str:
    """Generate launchd plist content."""
    logs_dir = get_logs_path()
    db_path = get_db_path()

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{MACOS_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
        <string>run</string>
        <string>--transport</string>
        <string>sse</string>
        <string>--port</string>
        <string>{port}</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>COACH_CLAUDE_DB</key>
        <string>{db_path}</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{logs_dir}/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>{logs_dir}/stderr.log</string>
</dict>
</plist>
"""


def _macos_is_installed() -> bool:
    """Check if the daemon is installed on macOS."""
    return _get_plist_path().exists()


def _macos_is_running() -> bool:
    """Check if the daemon is running on macOS."""
    try:
        result = subprocess.run(["launchctl", "list", MACOS_LABEL], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def _macos_install(port: int = DEFAULT_PORT) -> None:
    """Install the daemon on macOS."""
    exe_path = get_executable_path()
    if not exe_path:
        raise RuntimeError("coach-claude executable not found")

    plist_path = _get_plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    # Stop and unload if already installed
    if _macos_is_installed():
        _macos_uninstall()

    # Write plist
    plist_content = _generate_plist(exe_path, port)
    plist_path.write_text(plist_content)

    # Load and start
    subprocess.run(["launchctl", "load", str(plist_path)], check=True)


def _macos_uninstall() -> None:
    """Uninstall the daemon on macOS."""
    plist_path = _get_plist_path()

    if plist_path.exists():
        # Unload (stops the service)
        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
        plist_path.unlink()


def _macos_start() -> None:
    """Start the daemon on macOS."""
    if not _macos_is_installed():
        raise RuntimeError("Daemon not installed. Run 'coach-claude install' first.")
    subprocess.run(["launchctl", "start", MACOS_LABEL], check=True)


def _macos_stop() -> None:
    """Stop the daemon on macOS."""
    subprocess.run(["launchctl", "stop", MACOS_LABEL], capture_output=True)


# --- Linux (systemd) ---


def _get_systemd_path() -> Path:
    """Get the systemd user service file path."""
    return Path.home() / ".config" / "systemd" / "user" / f"{LINUX_SERVICE}.service"


def _generate_systemd_unit(exe_path: Path, port: int = DEFAULT_PORT) -> str:
    """Generate systemd unit file content."""
    logs_dir = get_logs_path()
    db_path = get_db_path()

    return f"""[Unit]
Description=Coach Claude MCP Server
After=network.target

[Service]
Type=simple
ExecStart={exe_path} run --transport sse --port {port}
Environment="COACH_CLAUDE_DB={db_path}"
Restart=on-failure
RestartSec=5s
StandardOutput=append:{logs_dir}/stdout.log
StandardError=append:{logs_dir}/stderr.log

[Install]
WantedBy=default.target
"""


def _linux_is_installed() -> bool:
    """Check if the daemon is installed on Linux."""
    return _get_systemd_path().exists()


def _linux_is_running() -> bool:
    """Check if the daemon is running on Linux."""
    try:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", LINUX_SERVICE], capture_output=True, text=True
        )
        return result.stdout.strip() == "active"
    except Exception:
        return False


def _linux_install(port: int = DEFAULT_PORT) -> None:
    """Install the daemon on Linux."""
    exe_path = get_executable_path()
    if not exe_path:
        raise RuntimeError("coach-claude executable not found")

    unit_path = _get_systemd_path()
    unit_path.parent.mkdir(parents=True, exist_ok=True)

    # Stop and disable if already installed
    if _linux_is_installed():
        _linux_uninstall()

    # Write unit file
    unit_content = _generate_systemd_unit(exe_path, port)
    unit_path.write_text(unit_content)

    # Reload, enable, and start
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", LINUX_SERVICE], check=True)
    subprocess.run(["systemctl", "--user", "start", LINUX_SERVICE], check=True)


def _linux_uninstall() -> None:
    """Uninstall the daemon on Linux."""
    unit_path = _get_systemd_path()

    # Stop and disable
    subprocess.run(["systemctl", "--user", "stop", LINUX_SERVICE], capture_output=True)
    subprocess.run(["systemctl", "--user", "disable", LINUX_SERVICE], capture_output=True)

    if unit_path.exists():
        unit_path.unlink()

    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)


def _linux_start() -> None:
    """Start the daemon on Linux."""
    if not _linux_is_installed():
        raise RuntimeError("Daemon not installed. Run 'coach-claude install' first.")
    subprocess.run(["systemctl", "--user", "start", LINUX_SERVICE], check=True)


def _linux_stop() -> None:
    """Stop the daemon on Linux."""
    subprocess.run(["systemctl", "--user", "stop", LINUX_SERVICE], capture_output=True)


# --- Public API ---


def is_installed() -> bool:
    """Check if the daemon is installed."""
    system = get_system()
    if system == "macos":
        return _macos_is_installed()
    elif system == "linux":
        return _linux_is_installed()
    return False


def is_running() -> bool:
    """Check if the daemon is running."""
    system = get_system()
    if system == "macos":
        return _macos_is_running()
    elif system == "linux":
        return _linux_is_running()
    return False


def install(port: int = DEFAULT_PORT) -> None:
    """Install and start the daemon."""
    system = get_system()
    if system == "macos":
        _macos_install(port)
    elif system == "linux":
        _linux_install(port)
    else:
        raise RuntimeError(f"Unsupported operating system: {platform.system()}")


def uninstall() -> None:
    """Stop and remove the daemon."""
    system = get_system()
    if system == "macos":
        _macos_uninstall()
    elif system == "linux":
        _linux_uninstall()
    else:
        raise RuntimeError(f"Unsupported operating system: {platform.system()}")


def start() -> None:
    """Start the daemon."""
    system = get_system()
    if system == "macos":
        _macos_start()
    elif system == "linux":
        _linux_start()
    else:
        raise RuntimeError(f"Unsupported operating system: {platform.system()}")


def stop() -> None:
    """Stop the daemon."""
    system = get_system()
    if system == "macos":
        _macos_stop()
    elif system == "linux":
        _linux_stop()


def status() -> dict:
    """Get daemon status information."""
    system = get_system()
    exe_path = get_executable_path()

    return {
        "system": system,
        "installed": is_installed(),
        "running": is_running(),
        "executable": str(exe_path) if exe_path else None,
        "logs_path": str(get_logs_path()),
        "db_path": str(get_db_path()),
        "service_file": str(_get_plist_path() if system == "macos" else _get_systemd_path()),
    }
