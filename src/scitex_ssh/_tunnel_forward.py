#!/usr/bin/env python3
"""Discovery-driven forward tunnel: read an endpoint file, exec a blocking ssh.

This is the client-side half of the qwen cross-host reachability seam agreed
with scitex-hpc. A service (e.g. qwen/LiteLLM) runs on an EPHEMERAL Spartan
compute node whose hostname changes on every reschedule; scitex-hpc publishes
a discovery JSON on Spartan shared storage and rewrites it on each (re)launch:

    {"node": "spartan-gpgpu014", "litellm_port": 4000, "vllm_port": 8765,
     "model": "qwen36-35b-a3b", "key": "sk-clew-local", "updated_at": "<ISO>"}

`resolve_forward_spec` reads that file FRESH and builds a
:class:`~scitex_ssh._tunnel_render.TunnelSpec` for a forward tunnel:

    ssh -N -L <local_host>:<local_port>:<node>:<remote_port> <via>

with ``via`` a STABLE login alias (e.g. ``spartan``) — the ephemeral ``node``
resolves on the login host's internal network (verified reachable by
scitex-hpc: ``curl http://<node>:4000/v1/models`` from the login node).

Re-pointing is intentionally NOT a loop here. scitex-hpc's generic
tunnel-supervisor owns keepalive: it runs ``scitex-ssh tunnel forward
--discovery <path>`` as an opaque, foreground-blocking ``command`` and
relaunches it on exit / endpoint-health failure. Because THIS command
re-reads the discovery file every time it starts, each supervisor relaunch
picks up the current ``node`` — so the supervisor's restart IS the re-point.
Hence :func:`exec_forward` uses ``os.execvp`` (replace the process, block,
propagate signals) rather than spawning a child or looping.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from ._tunnel_render import Endpoint, TunnelSpec, render_argv, render_command

# Discovery-file keys that name a port. Kept as an explicit allowlist so a
# typo'd --port-field fails loudly instead of tunnelling an arbitrary field.
PORT_FIELDS = ("litellm_port", "vllm_port")

DEFAULT_VIA = "spartan"
DEFAULT_LOCAL_HOST = "127.0.0.1"
DEFAULT_PORT_FIELD = "litellm_port"


class DiscoveryError(RuntimeError):
    """Raised when the discovery file is missing, unparseable, or incomplete."""


def load_discovery(discovery_path: str) -> dict:
    """Read and parse the discovery JSON file.

    Fails LOUD (raises :class:`DiscoveryError`) on a missing file or invalid
    JSON — the supervisor treats a non-zero exit as "command died" and
    relaunches, so a transient missing file self-heals once it appears.
    """
    try:
        with open(discovery_path) as fh:
            raw = fh.read()
    except OSError as exc:
        raise DiscoveryError(
            f"discovery file unreadable: {discovery_path} ({exc})"
        ) from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DiscoveryError(
            f"discovery file is not valid JSON: {discovery_path} ({exc})"
        ) from exc
    if not isinstance(data, dict):
        raise DiscoveryError(
            f"discovery file must be a JSON object, got {type(data).__name__}"
        )
    return data


def resolve_forward_spec(
    discovery_path: str,
    *,
    via: str = DEFAULT_VIA,
    via_user: Optional[str] = None,
    via_port: Optional[int] = None,
    local_host: str = DEFAULT_LOCAL_HOST,
    local_port: Optional[int] = None,
    remote_port: Optional[int] = None,
    port_field: str = DEFAULT_PORT_FIELD,
    identity: Optional[str] = None,
) -> TunnelSpec:
    """Build a forward :class:`TunnelSpec` from the discovery file.

    ``remote_port`` (if given) wins over ``port_field``; ``local_port``
    defaults to the resolved remote port (so ``127.0.0.1:4000`` maps to the
    node's 4000 by default).
    """
    if port_field not in PORT_FIELDS:
        raise DiscoveryError(
            f"unknown port_field {port_field!r}; expected one of {PORT_FIELDS}"
        )
    data = load_discovery(discovery_path)

    node = data.get("node")
    if not node:
        raise DiscoveryError("discovery file missing required key 'node'")

    if remote_port is not None:
        rport = int(remote_port)
    else:
        if port_field not in data:
            raise DiscoveryError(
                f"discovery file missing port field {port_field!r} "
                f"(and no --remote-port given)"
            )
        rport = int(data[port_field])

    lport = int(local_port) if local_port is not None else rport

    return TunnelSpec(
        direction="forward",
        listen=Endpoint(local_host, lport),
        target=Endpoint(str(node), rport),
        via=via,
        via_user=via_user,
        via_port=via_port,
        identity=identity,
    )


def exec_forward(spec: TunnelSpec) -> "None":  # pragma: no cover - replaces process
    """Replace the current process with the blocking ``ssh`` for ``spec``.

    Never returns on success (``os.execvp`` overlays the process image). This
    is what makes the command a proper foreground-blocking ``command`` for
    scitex-hpc's supervisor loop.
    """
    argv = render_argv(spec)
    os.execvp(argv[0], argv)


def forward_command(spec: TunnelSpec) -> str:
    """Return the ssh command string that :func:`exec_forward` would run
    (used by ``--dry-run`` and for putting into a supervisor profile)."""
    return render_command(spec)


# EOF
