#!/usr/bin/env python3
"""`scitex-ssh tunnel` command group — reverse tunnels + argv/forward tooling.

Extracted from ``_main.py`` (SoC: root CLI vs tunnel domain). Holds the
`tunnel` click group and every subcommand:

  * ``setup`` / ``remove`` / ``check-status`` — persistent reverse tunnel
    lifecycle (allowlist-gated autossh+systemd).
  * ``render-argv`` — pure ssh -L/-R argv rendering from a JSON spec.
  * ``forward`` — discovery-driven forward tunnel (exec a blocking ssh).

The shared helpers (`_default_host`, `_read_profile_arg`, `_deprecation_warn`,
`_do_tunnel_*`) live here and are imported back by ``_main`` for the
deprecated top-level aliases.
"""

from __future__ import annotations

import socket

import click


def _default_host() -> str:
    return socket.gethostname().split(".")[0]


def _read_profile_arg(profile: str) -> str:
    """Resolve a --profile value: inline JSON, ``@PATH`` for a file, or ``-``
    for stdin."""
    import sys

    if profile == "-":
        return sys.stdin.read()
    if profile.startswith("@"):
        with open(profile[1:]) as fh:
            return fh.read()
    return profile


def _deprecation_warn(old: str, new: str) -> None:
    click.secho(
        f"warning: `scitex-ssh {old}` is deprecated; use `scitex-ssh {new}`.",
        fg="yellow",
        err=True,
    )


# -----------------------------------------------------------------------
# Reverse-tunnel action helpers (call the production functions)
# -----------------------------------------------------------------------
def _do_tunnel_setup(port, bastion, secret_key, host, *, setup_fn=None):
    import scitex_ssh
    from scitex_ssh._allowlist import PolicyError

    if setup_fn is None:
        setup_fn = scitex_ssh.setup
    try:
        result = setup_fn(port, bastion, secret_key, host=host)
    except PolicyError as e:
        click.secho(f"ERROR: {e}", fg="red", err=True)
        raise SystemExit(2)
    except ValueError as e:
        click.secho(f"ERROR: {e}", fg="red", err=True)
        raise SystemExit(1)
    if result["success"]:
        click.secho(f"Tunnel on port {port} set up successfully.", fg="green")
        if result["stdout"]:
            click.echo(result["stdout"])
    else:
        click.secho(f"Failed to set up tunnel on port {port}.", fg="red", err=True)
        if result["stderr"]:
            click.echo(result["stderr"], err=True)
        raise SystemExit(1)


def _do_tunnel_remove(port, host, *, remove_fn=None):
    import scitex_ssh
    from scitex_ssh._allowlist import PolicyError

    if remove_fn is None:
        remove_fn = scitex_ssh.remove
    try:
        result = remove_fn(port, host=host)
    except PolicyError as e:
        click.secho(f"ERROR: {e}", fg="red", err=True)
        raise SystemExit(2)
    if result["success"]:
        click.secho(f"Tunnel on port {port} removed.", fg="green")
        if result["stdout"]:
            click.echo(result["stdout"])
    else:
        click.secho(f"Failed to remove tunnel on port {port}.", fg="red", err=True)
        if result["stderr"]:
            click.echo(result["stderr"], err=True)
        raise SystemExit(1)


def _do_tunnel_status(port, *, status_fn=None):
    import scitex_ssh

    if status_fn is None:
        status_fn = scitex_ssh.status
    result = status_fn(port)
    click.echo(result["stdout"])
    if result["stderr"]:
        click.echo(result["stderr"], err=True)


# -----------------------------------------------------------------------
# tunnel group
# -----------------------------------------------------------------------
@click.group("tunnel")
def tunnel():
    """Manage SSH tunnels (reverse lifecycle + argv/forward tooling)."""


@tunnel.command("setup")
@click.option("-p", "--port", required=True, type=int, help="Remote port to forward.")
@click.option(
    "-b",
    "--bastion",
    default=None,
    help="Bastion server hostname or IP. [env: SCITEX_SSH_BASTION_SERVER]",
)
@click.option(
    "-s",
    "--secret-key",
    default=None,
    help="Path to SSH private key. [env: SCITEX_SSH_SECRET_KEY_PATH]",
)
@click.option(
    "--host",
    default=None,
    help="Local host label for allowlist gating (default: local hostname).",
)
@click.option("--dry-run", is_flag=True, help="Print plan without setting up tunnel.")
@click.option(
    "-y", "--yes", is_flag=True, help="Suppress interactive confirmation (assume yes)."
)
def tunnel_setup(port, bastion, secret_key, host, dry_run, yes):
    """Set up a persistent SSH reverse tunnel.

    \b
    Example:
      $ scitex-ssh tunnel setup -p 8080 -b bastion.example.com
      $ scitex-ssh tunnel setup -p 8080 --dry-run
    """
    if dry_run:
        click.echo(
            f"DRY RUN — would set up SSH reverse tunnel "
            f"(port={port}, bastion={bastion}, host={host or _default_host()})"
        )
        return
    _do_tunnel_setup(port, bastion, secret_key, host or _default_host())


@tunnel.command("remove")
@click.option("-p", "--port", required=True, type=int, help="Port of tunnel to remove.")
@click.option(
    "--host",
    default=None,
    help="Local host label for allowlist gating (default: local hostname).",
)
@click.option("--dry-run", is_flag=True, help="Print plan without removing tunnel.")
@click.option(
    "-y", "--yes", is_flag=True, help="Suppress interactive confirmation (assume yes)."
)
def tunnel_remove(port, host, dry_run, yes):
    """Remove a persistent SSH reverse tunnel.

    \b
    Example:
      $ scitex-ssh tunnel remove -p 8080
      $ scitex-ssh tunnel remove -p 8080 --dry-run
    """
    if dry_run:
        click.echo(
            f"DRY RUN — would remove tunnel (port={port}, host={host or _default_host()})"
        )
        return
    _do_tunnel_remove(port, host or _default_host())


@tunnel.command("check-status")
@click.option(
    "-p",
    "--port",
    type=int,
    default=None,
    help="Specific port to check (default: all).",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def tunnel_status(port, as_json):
    """Check status of SSH reverse tunnels (informational; not gated).

    \b
    Example:
      $ scitex-ssh tunnel check-status
      $ scitex-ssh tunnel check-status -p 8080
      $ scitex-ssh tunnel check-status --json
    """
    if as_json:
        import json as _json

        import scitex_ssh

        result = scitex_ssh.status(port)
        click.echo(
            _json.dumps(
                {
                    "port": port,
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                },
                indent=2,
            )
        )
        return
    _do_tunnel_status(port)


@tunnel.command("status", hidden=True)
@click.option("-p", "--port", type=int, default=None)
@click.option("--json", "as_json", is_flag=True)
@click.pass_context
def tunnel_status_deprecated(ctx, port, as_json):
    """(deprecated) Use `tunnel check-status`."""
    _deprecation_warn("tunnel status", "tunnel check-status")
    ctx.invoke(tunnel_status, port=port, as_json=as_json)


@tunnel.command("render-argv")
@click.option(
    "--profile",
    required=True,
    help="Tunnel spec as JSON. Inline, or @PATH to read a file, or - for stdin.",
)
@click.option(
    "--as-json",
    "as_json",
    is_flag=True,
    help="Emit the argv array as JSON instead of a shell-ready string.",
)
def tunnel_render_argv(profile, as_json):
    """Render an ssh forward/reverse tunnel command from a JSON spec.

    \b
    Prints a single shell-safe `ssh -N ...` line (the default) suitable to
    drop into a keepalive supervisor's opaque, foreground-blocking command
    field; or the argv array as JSON with --as-json. This is pure string
    construction — it does NOT open any connection.

    \b
    Example:
      $ scitex-ssh tunnel render-argv --profile '{"direction":"forward",
          "listen":{"host":"127.0.0.1","port":4000},
          "target":{"host":"spartan-gpu-a017","port":4000},"via":"spartan"}'
      ssh -N -o ExitOnForwardFailure=yes ... -L 127.0.0.1:4000:spartan-gpu-a017:4000 spartan
    """
    import json as _json

    from scitex_ssh._tunnel_render import TunnelSpec, render_argv, render_command

    raw = _read_profile_arg(profile)
    try:
        data = _json.loads(raw)
    except _json.JSONDecodeError as e:
        click.secho(f"ERROR: --profile is not valid JSON: {e}", fg="red", err=True)
        raise SystemExit(2)
    try:
        spec = TunnelSpec.from_dict(data)
    except (ValueError, KeyError, TypeError) as e:
        click.secho(f"ERROR: invalid tunnel profile: {e}", fg="red", err=True)
        raise SystemExit(2)

    if as_json:
        click.echo(_json.dumps(render_argv(spec)))
    else:
        click.echo(render_command(spec))


@tunnel.command("forward")
@click.option(
    "--discovery",
    required=True,
    help="Path to the endpoint discovery JSON file (read fresh on each launch).",
)
@click.option(
    "--via",
    default="spartan",
    show_default=True,
    help="Stable SSH login alias to connect to (the discovery node resolves on ITS network).",
)
@click.option("--via-user", default=None, help="SSH user for --via.")
@click.option("--via-port", type=int, default=None, help="SSH port for --via.")
@click.option(
    "--local-host", default="127.0.0.1", show_default=True, help="Local bind host."
)
@click.option(
    "--local-port",
    type=int,
    default=None,
    help="Local bind port (default: same as the resolved remote port).",
)
@click.option(
    "--remote-port",
    type=int,
    default=None,
    help="Remote port to reach (default: read --port-field from discovery).",
)
@click.option(
    "--port-field",
    type=click.Choice(["litellm_port", "vllm_port"]),
    default="litellm_port",
    show_default=True,
    help="Which discovery-file port field to tunnel when --remote-port is unset.",
)
@click.option("--identity", default=None, help="SSH private key path (-i).")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print the resolved ssh command and exit, without connecting.",
)
def tunnel_forward(
    discovery,
    via,
    via_user,
    via_port,
    local_host,
    local_port,
    remote_port,
    port_field,
    identity,
    dry_run,
):
    """Open a forward tunnel to a service whose host is published in a discovery file.

    \b
    Reads --discovery FRESH, builds `ssh -N -L <local>:<node>:<remote>` (node
    from the file), and REPLACES this process with that blocking ssh. Designed
    to run as a keepalive supervisor's foreground command: because the file is
    re-read on every launch, each supervisor relaunch re-points to the current
    node — the restart IS the re-point (no loop here).

    \b
    Example (as a supervisor command for the ephemeral qwen node):
      $ scitex-ssh tunnel forward --discovery /data/.../qwen-endpoint.json
      $ scitex-ssh tunnel forward --discovery ./qwen-endpoint.json --dry-run
    """
    from scitex_ssh._tunnel_forward import (
        DiscoveryError,
        exec_forward,
        forward_command,
        resolve_forward_spec,
    )

    try:
        spec = resolve_forward_spec(
            discovery,
            via=via,
            via_user=via_user,
            via_port=via_port,
            local_host=local_host,
            local_port=local_port,
            remote_port=remote_port,
            port_field=port_field,
            identity=identity,
        )
    except DiscoveryError as e:
        click.secho(f"ERROR: {e}", fg="red", err=True)
        raise SystemExit(1)

    if dry_run:
        click.echo(forward_command(spec))
        return
    exec_forward(spec)  # replaces the process; never returns on success


# EOF
