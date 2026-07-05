#!/usr/bin/env python3
"""Render an ``ssh`` forward/reverse-tunnel invocation from a declarative spec.

This is the scitex-ssh side of the tunnel-supervisor seam agreed with
scitex-hpc: scitex-ssh owns ALL ``ssh -L``/``-R`` argv construction; a
generic keepalive supervisor (scitex-hpc's ``tunnel_supervisor``) runs the
rendered command string as an opaque, foreground-blocking ``command`` and
owns restart/health-check. Nothing tunnel-shaped is baked into the
supervisor; nothing supervisor-shaped is baked in here.

Design invariants (contract with the supervisor):

  * ``-N`` is ALWAYS emitted — the rendered command runs no remote command,
    so it BLOCKS until the tunnel dies. The supervisor's keep-alive loop
    depends on this (a backgrounding form would break its ``wait``).
  * A single ``ssh`` invocation — no ``autossh`` wrapper. Keep-alive is the
    supervisor's job. (The persistent NAT-traversal reverse tunnel installed
    by ``tunnel setup`` keeps its own autossh+systemd path; that is separate.)
  * The rendered string is a single shell-safe line (built with
    :func:`shlex.join`), because the supervisor splices ``command`` raw into
    ``( {command} ) & wait`` under ``set -u``.

Topology note (the detail that makes ephemeral endpoints work): with
``-L local:target_host:target_port``, ``target_host`` is resolved from the
network of the DESTINATION host ssh connects to (``via``) — NOT from the
local machine and NOT from a ``-J`` ProxyJump hop. So to reach an ephemeral
Spartan compute node from off-cluster, ``via`` is the STABLE login alias
(e.g. ``spartan``) and ``target`` is ``<compute-node>:<port>`` resolved on
Spartan's internal net. ``jump`` (``-J``) is an optional, separate hop and
is NOT a substitute for ``via``: ``ssh -J spartan -L …`` with no destination
host is invalid.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence

# Sane defaults, merged UNDER any caller-supplied ssh_opts (caller wins).
# ExitOnForwardFailure makes ssh exit (rather than silently continue) when the
# forward can't be established — critical so the supervisor sees a dead command
# and restarts instead of holding a live PID with no working tunnel.
DEFAULT_SSH_OPTS: dict[str, str] = {
    "ExitOnForwardFailure": "yes",
    "ServerAliveInterval": "15",
    "ServerAliveCountMax": "3",
    "StrictHostKeyChecking": "accept-new",
}

FORWARD = "forward"
REVERSE = "reverse"
_DIRECTIONS = (FORWARD, REVERSE)


@dataclass(frozen=True)
class Endpoint:
    """A ``host:port`` pair. ``host`` may be empty for a reverse bind (means
    "all interfaces on the remote side")."""

    host: str
    port: int

    @classmethod
    def from_obj(cls, obj: "Endpoint | Mapping | Sequence") -> "Endpoint":
        if isinstance(obj, Endpoint):
            return obj
        if isinstance(obj, Mapping):
            return cls(host=str(obj.get("host", "")), port=int(obj["port"]))
        # sequence form: [host, port] or (port,)
        seq = list(obj)
        if len(seq) == 1:
            return cls(host="", port=int(seq[0]))
        return cls(host=str(seq[0]), port=int(seq[1]))


@dataclass(frozen=True)
class TunnelSpec:
    """Declarative description of one ssh tunnel to render.

    Fields
    ------
    direction
        ``"forward"`` (``-L``) or ``"reverse"`` (``-R``).
    listen
        The bind side. Forward: the LOCAL bind (e.g. ``127.0.0.1:4000``).
        Reverse: the REMOTE bind on ``via`` (host may be empty).
    target
        The endpoint the tunnel reaches, resolved on ``via``'s network.
    via
        REQUIRED. The host ssh connects to (a stable SSH alias / login host).
        This is the destination, distinct from ``jump``.
    via_user, via_port
        Optional user / port for ``via``.
    jump
        Optional ``-J`` ProxyJump chain, verbatim (e.g. ``"bastion"`` or
        ``"user@bastion:2222,inner"``). A SEPARATE hop from ``via``.
    identity
        Optional path to a private key (``-i``).
    ssh_opts
        ``-o KEY=VALUE`` options; merged under :data:`DEFAULT_SSH_OPTS`
        (caller-supplied keys win).
    extra_argv
        Escape hatch: extra ssh options appended verbatim BEFORE the
        destination host.
    """

    direction: str
    listen: Endpoint
    target: Endpoint
    via: str
    via_user: Optional[str] = None
    via_port: Optional[int] = None
    jump: Optional[str] = None
    identity: Optional[str] = None
    ssh_opts: Mapping[str, str] = field(default_factory=dict)
    extra_argv: Sequence[str] = ()

    def __post_init__(self) -> None:
        if self.direction not in _DIRECTIONS:
            raise ValueError(
                f"direction must be one of {_DIRECTIONS!r}, got {self.direction!r}"
            )
        if not self.via:
            raise ValueError(
                "via (destination host ssh connects to) is required; "
                "`-J jump` is a separate hop and cannot replace it"
            )

    @classmethod
    def from_dict(cls, d: Mapping) -> "TunnelSpec":
        """Build a spec from a plain dict (e.g. parsed JSON profile)."""
        if "direction" not in d:
            raise ValueError("profile missing required key 'direction'")
        for req in ("listen", "target", "via"):
            if req not in d:
                raise ValueError(f"profile missing required key {req!r}")
        return cls(
            direction=str(d["direction"]),
            listen=Endpoint.from_obj(d["listen"]),
            target=Endpoint.from_obj(d["target"]),
            via=str(d["via"]),
            via_user=(str(d["via_user"]) if d.get("via_user") else None),
            via_port=(int(d["via_port"]) if d.get("via_port") else None),
            jump=(str(d["jump"]) if d.get("jump") else None),
            identity=(str(d["identity"]) if d.get("identity") else None),
            ssh_opts=dict(d.get("ssh_opts") or {}),
            extra_argv=tuple(d.get("extra_argv") or ()),
        )


def _forward_spec(listen: Endpoint, target: Endpoint) -> str:
    # -L [bind_address:]port:host:hostport
    bind = f"{listen.host}:" if listen.host else ""
    return f"{bind}{listen.port}:{target.host}:{target.port}"


def _reverse_spec(listen: Endpoint, target: Endpoint) -> str:
    # -R [bind_address:]port:host:hostport
    bind = f"{listen.host}:" if listen.host else ""
    return f"{bind}{listen.port}:{target.host}:{target.port}"


def render_argv(spec: TunnelSpec) -> list[str]:
    """Return the ssh invocation for ``spec`` as an argv list.

    All options precede the destination host (ssh requires this). The
    destination host is always last.
    """
    argv: list[str] = ["ssh", "-N"]

    if spec.via_port is not None:
        argv += ["-p", str(spec.via_port)]
    if spec.identity:
        argv += ["-i", spec.identity]

    opts = {**DEFAULT_SSH_OPTS, **dict(spec.ssh_opts)}
    for key in opts:
        argv += ["-o", f"{key}={opts[key]}"]

    if spec.jump:
        argv += ["-J", spec.jump]

    if spec.direction == FORWARD:
        argv += ["-L", _forward_spec(spec.listen, spec.target)]
    else:
        argv += ["-R", _reverse_spec(spec.listen, spec.target)]

    argv += list(spec.extra_argv)

    dest = f"{spec.via_user}@{spec.via}" if spec.via_user else spec.via
    argv += [dest]
    return argv


def render_command(spec: TunnelSpec) -> str:
    """Return the ssh invocation as a single shell-safe line.

    This is the string that drops into scitex-hpc's supervisor ``command``
    field. Built with :func:`shlex.join` so it is safe to splice raw into a
    ``bash`` subshell under ``set -u``.
    """
    return shlex.join(render_argv(spec))


# EOF
