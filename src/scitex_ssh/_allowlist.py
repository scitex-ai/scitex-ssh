"""Per-host policy for gating sensitive features (currently: tunnels).

Config file: ~/.scitex/ssh/config.yaml

Schema:
  default:
    tunnels: deny           # default policy for unlisted hosts
  hosts:
    mba:    {tunnels: allow}
    nas:    {tunnels: allow}
    spartan: {tunnels: deny}

If the file does not exist: default policy is `deny` (fail-closed).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal


class PolicyError(RuntimeError):
    """Raised when an action is denied by the allowlist."""


CONFIG_PATH = Path.home() / ".scitex" / "ssh" / "config.yaml"


def is_allowed(host: str, feature: Literal["tunnels"]) -> bool:
    cfg = _load()
    if cfg is None:
        return False  # fail-closed when no config
    hosts = cfg.get("hosts") or {}
    host_cfg = hosts.get(host) or {}
    if feature in host_cfg:
        return host_cfg[feature] == "allow"
    default_cfg = cfg.get("default") or {}
    return default_cfg.get(feature) == "allow"


def require(host: str, feature: Literal["tunnels"]) -> None:
    if not is_allowed(host, feature):
        raise PolicyError(
            f"feature {feature!r} is not allowed for host {host!r}. "
            f"Edit {CONFIG_PATH} to add 'hosts.{host}.{feature}: allow' "
            f"if your environment permits it."
        )


def _load() -> dict | None:
    if not CONFIG_PATH.exists():
        return None
    try:
        import yaml
    except ImportError:
        # yaml not installed — treat as no config
        return None
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


# EOF
