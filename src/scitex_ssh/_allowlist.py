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


def is_allowed(
    host: str,
    feature: Literal["tunnels"],
    *,
    config_path: Path | None = None,
) -> bool:
    """Return True iff `host` is allowed to use `feature`.

    Parameters
    ----------
    config_path : Path, optional
        Override the config file location. Defaults to ``CONFIG_PATH``
        (``~/.scitex/ssh/config.yaml``). Used by tests to point at a
        real config in ``tmp_path`` without patching module globals.
    """
    cfg = _load(config_path if config_path is not None else CONFIG_PATH)
    if cfg is None:
        return False  # fail-closed when no config
    hosts = cfg.get("hosts") or {}
    host_cfg = hosts.get(host) or {}
    if feature in host_cfg:
        return host_cfg[feature] == "allow"
    default_cfg = cfg.get("default") or {}
    return default_cfg.get(feature) == "allow"


def require(
    host: str,
    feature: Literal["tunnels"],
    *,
    config_path: Path | None = None,
) -> None:
    if not is_allowed(host, feature, config_path=config_path):
        path_for_msg = config_path if config_path is not None else CONFIG_PATH
        raise PolicyError(
            f"feature {feature!r} is not allowed for host {host!r}. "
            f"Edit {path_for_msg} to add 'hosts.{host}.{feature}: allow' "
            f"if your environment permits it."
        )


def _load(config_path: Path) -> dict | None:
    if not config_path.exists():
        return None
    try:
        import yaml
    except ImportError:
        # yaml not installed — treat as no config
        return None
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


# EOF
