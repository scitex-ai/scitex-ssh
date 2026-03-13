#!/usr/bin/env python3
"""SciTeX Tunnel - Persistent SSH reverse tunnel for NAT traversal."""

from __future__ import annotations

import os
import subprocess

from importlib.metadata import PackageNotFoundError as _PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("scitex-tunnel")
except _PackageNotFoundError:
    from pathlib import Path as _Path

    _pyproject = _Path(__file__).parent.parent.parent / "pyproject.toml"
    __version__ = "0.0.0"
    if _pyproject.exists():
        with open(_pyproject) as _f:
            for _line in _f:
                if _line.startswith("version"):
                    __version__ = _line.split('"')[1]
                    break

AVAILABLE = True

_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")


def _run_script(
    script_name: str, args: list[str] | None = None
) -> subprocess.CompletedProcess:
    """Run a bundled bash script."""
    script_path = os.path.join(_SCRIPTS_DIR, script_name)
    cmd = ["bash", script_path] + (args or [])
    return subprocess.run(cmd, capture_output=True, text=True)


def setup(
    port: int,
    bastion_server: str | None = None,
    secret_key_path: str | None = None,
) -> dict:
    """Set up a persistent SSH reverse tunnel.

    Parameters
    ----------
    port : int
        The remote port to forward (e.g. 2222).
    bastion_server : str, optional
        The bastion/relay server hostname or IP.
        Falls back to SCITEX_TUNNEL_BASTION_SERVER env var.
    secret_key_path : str, optional
        Path to the SSH private key for authentication.
        Falls back to SCITEX_TUNNEL_SECRET_KEY_PATH env var.

    Returns
    -------
    dict
        Result with 'success', 'stdout', 'stderr' keys.

    Raises
    ------
    ValueError
        If bastion_server or secret_key_path is not provided and
        the corresponding environment variable is not set.
    """
    bastion_server = bastion_server or os.environ.get("SCITEX_TUNNEL_BASTION_SERVER")
    secret_key_path = secret_key_path or os.environ.get("SCITEX_TUNNEL_SECRET_KEY_PATH")

    if not bastion_server:
        raise ValueError(
            "bastion_server is required. Provide it as an argument or set "
            "SCITEX_TUNNEL_BASTION_SERVER environment variable."
        )
    if not secret_key_path:
        raise ValueError(
            "secret_key_path is required. Provide it as an argument or set "
            "SCITEX_TUNNEL_SECRET_KEY_PATH environment variable."
        )

    result = _run_script(
        "setup-autossh-service.sh",
        ["-p", str(port), "-b", bastion_server, "-s", secret_key_path],
    )
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def remove(port: int) -> dict:
    """Remove a persistent SSH reverse tunnel.

    Parameters
    ----------
    port : int
        The remote port of the tunnel to remove.

    Returns
    -------
    dict
        Result with 'success', 'stdout', 'stderr' keys.
    """
    result = _run_script("remove-autossh-service.sh", ["-p", str(port)])
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def status(port: int | None = None) -> dict:
    """Check status of SSH reverse tunnels.

    Parameters
    ----------
    port : int, optional
        Specific port to check. If None, shows all tunnels.

    Returns
    -------
    dict
        Result with 'success', 'stdout', 'stderr' keys.
    """
    if port:
        cmd = [
            "systemctl",
            "status",
            f"autossh-tunnel-{port}.service",
            "--no-pager",
        ]
    else:
        cmd = ["systemctl", "list-units", "autossh-tunnel-*", "--no-pager"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def get_version() -> str:
    """Get scitex-tunnel version."""
    return __version__


# EOF
