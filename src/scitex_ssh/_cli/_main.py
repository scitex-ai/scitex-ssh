#!/usr/bin/env python3
"""Main CLI entry point for scitex-ssh."""

import socket

import click

from ._introspect import list_python_apis
from ._mcp import mcp
from ._primitives import attach_cmd, copy_cmd, exec_cmd

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

COMMAND_CATEGORIES = [
    ("SSH Primitives", ["exec", "copy", "attach"]),
    ("Tunnel Management", ["tunnel"]),
    ("Integration", ["mcp", "list-python-apis"]),
]


class CategorizedGroup(click.Group):
    """Custom Click group that displays commands organized by category."""

    def format_commands(self, ctx, formatter):
        """Write categorized commands to the formatter."""
        commands = {}
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is not None and not cmd.hidden:
                commands[subcommand] = cmd

        if not commands:
            return

        displayed = set()

        for category_name, category_commands in COMMAND_CATEGORIES:
            category_items = []
            for name in category_commands:
                if name in commands and name not in displayed:
                    cmd = commands[name]
                    help_text = cmd.get_short_help_str(limit=formatter.width)
                    category_items.append((name, help_text))
                    displayed.add(name)

            if category_items:
                with formatter.section(category_name):
                    formatter.write_dl(category_items)

        uncategorized = [
            (name, commands[name].get_short_help_str(limit=formatter.width))
            for name in sorted(commands.keys())
            if name not in displayed
        ]
        if uncategorized:
            with formatter.section("Other"):
                formatter.write_dl(uncategorized)


def _show_recursive_help(ctx):
    """Recursively show help for all commands."""
    click.echo(ctx.get_help())
    click.echo()
    group = ctx.command
    if isinstance(group, click.Group):
        for name in sorted(group.list_commands(ctx)):
            cmd = group.get_command(ctx, name)
            sub_ctx = click.Context(cmd, parent=ctx, info_name=name)
            click.echo(f"{'=' * 60}")
            click.echo(f"Command: {name}")
            click.echo(f"{'=' * 60}")
            click.echo(sub_ctx.get_help())
            click.echo()
            if isinstance(cmd, click.Group):
                for sub_name in sorted(cmd.list_commands(sub_ctx)):
                    sub_cmd = cmd.get_command(sub_ctx, sub_name)
                    sub_sub_ctx = click.Context(
                        sub_cmd, parent=sub_ctx, info_name=sub_name
                    )
                    click.echo(f"  {'─' * 56}")
                    click.echo(f"  Subcommand: {name} {sub_name}")
                    click.echo(f"  {'─' * 56}")
                    click.echo(sub_sub_ctx.get_help())
                    click.echo()


def _get_version():
    """Read version from package."""
    from scitex_ssh import __version__

    return __version__


def _default_host() -> str:
    return socket.gethostname().split(".")[0]


@click.group(
    cls=CategorizedGroup,
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.option("--version", "-V", is_flag=True, help="Show version and exit.")
@click.option("--help-recursive", is_flag=True, help="Show help for all commands.")
@click.pass_context
def main(ctx, version, help_recursive):
    """scitex-ssh - SSH primitives (exec/copy/attach) and gated reverse tunnels."""
    if version:
        click.echo(f"scitex-ssh {_get_version()}")
        ctx.exit(0)

    if help_recursive:
        _show_recursive_help(ctx)
        ctx.exit(0)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# -----------------------------------------------------------------------
# Tunnel subgroup
# -----------------------------------------------------------------------


@main.group("tunnel")
def tunnel():
    """Manage persistent SSH reverse tunnels (allowlist-gated)."""


def _do_tunnel_setup(port, bastion, secret_key, host):
    import scitex_ssh
    from scitex_ssh._allowlist import PolicyError

    try:
        result = scitex_ssh.setup(port, bastion, secret_key, host=host)
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


def _do_tunnel_remove(port, host):
    import scitex_ssh
    from scitex_ssh._allowlist import PolicyError

    try:
        result = scitex_ssh.remove(port, host=host)
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


def _do_tunnel_status(port):
    import scitex_ssh

    result = scitex_ssh.status(port)
    click.echo(result["stdout"])
    if result["stderr"]:
        click.echo(result["stderr"], err=True)


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
def tunnel_setup(port, bastion, secret_key, host):
    """Set up a persistent SSH reverse tunnel."""
    _do_tunnel_setup(port, bastion, secret_key, host or _default_host())


@tunnel.command("remove")
@click.option("-p", "--port", required=True, type=int, help="Port of tunnel to remove.")
@click.option(
    "--host",
    default=None,
    help="Local host label for allowlist gating (default: local hostname).",
)
def tunnel_remove(port, host):
    """Remove a persistent SSH reverse tunnel."""
    _do_tunnel_remove(port, host or _default_host())


@tunnel.command("status")
@click.option(
    "-p",
    "--port",
    type=int,
    default=None,
    help="Specific port to check (default: all).",
)
def tunnel_status(port):
    """Check status of SSH reverse tunnels (informational; not gated)."""
    _do_tunnel_status(port)


# -----------------------------------------------------------------------
# Deprecated top-level aliases (hidden)
# -----------------------------------------------------------------------


def _deprecation_warn(old: str, new: str) -> None:
    click.secho(
        f"warning: `scitex-ssh {old}` is deprecated; use `scitex-ssh {new}`.",
        fg="yellow",
        err=True,
    )


@main.command("setup-tunnel", hidden=True)
@click.option("-p", "--port", required=True, type=int)
@click.option("-b", "--bastion", default=None)
@click.option("-s", "--secret-key", default=None)
@click.option("--host", default=None)
def setup_tunnel_deprecated(port, bastion, secret_key, host):
    """(deprecated) Use `tunnel setup`."""
    _deprecation_warn("setup-tunnel", "tunnel setup")
    _do_tunnel_setup(port, bastion, secret_key, host or _default_host())


@main.command("remove-tunnel", hidden=True)
@click.option("-p", "--port", required=True, type=int)
@click.option("--host", default=None)
def remove_tunnel_deprecated(port, host):
    """(deprecated) Use `tunnel remove`."""
    _deprecation_warn("remove-tunnel", "tunnel remove")
    _do_tunnel_remove(port, host or _default_host())


@main.command("show-status", hidden=True)
@click.option("-p", "--port", type=int, default=None)
def show_status_deprecated(port):
    """(deprecated) Use `tunnel status`."""
    _deprecation_warn("show-status", "tunnel status")
    _do_tunnel_status(port)


# -----------------------------------------------------------------------
# Register top-level primitive + integration commands
# -----------------------------------------------------------------------

main.add_command(exec_cmd)
main.add_command(copy_cmd)
main.add_command(attach_cmd)
main.add_command(list_python_apis)
main.add_command(mcp)


# EOF
