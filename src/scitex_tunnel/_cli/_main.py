#!/usr/bin/env python3
"""Main CLI entry point for scitex-tunnel."""

import click

from ._introspect import list_python_apis
from ._mcp import mcp

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

COMMAND_CATEGORIES = [
    ("Tunnel Management", ["setup", "remove", "status"]),
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
    from scitex_tunnel import __version__

    return __version__


@click.group(
    cls=CategorizedGroup,
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.option("--version", "-V", is_flag=True, help="Show version and exit.")
@click.option("--help-recursive", is_flag=True, help="Show help for all commands.")
@click.pass_context
def main(ctx, version, help_recursive):
    """scitex-tunnel - Persistent SSH reverse tunnel for NAT traversal."""
    if version:
        click.echo(f"scitex-tunnel {_get_version()}")
        ctx.exit(0)

    if help_recursive:
        _show_recursive_help(ctx)
        ctx.exit(0)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# -----------------------------------------------------------------------
# Subcommands: setup, remove, status
# -----------------------------------------------------------------------


@main.command("setup", hidden=True, context_settings={"ignore_unknown_options": True})
@click.pass_context
def setup_deprecated(ctx):
    """(deprecated) Renamed to `setup-tunnel`."""
    click.echo(
        "error: `scitex-tunnel setup` was renamed to `scitex-tunnel setup-tunnel`.\n"
        "Re-run with: scitex-tunnel setup-tunnel",
        err=True,
    )
    ctx.exit(2)


@main.command("setup-tunnel")
@click.option("-p", "--port", required=True, type=int, help="Remote port to forward.")
@click.option(
    "-b",
    "--bastion",
    default=None,
    help="Bastion server hostname or IP. [env: SCITEX_TUNNEL_BASTION_SERVER]",
)
@click.option(
    "-s",
    "--secret-key",
    default=None,
    help="Path to SSH private key. [env: SCITEX_TUNNEL_SECRET_KEY_PATH]",
)
def setup_tunnel(port, bastion, secret_key):
    """Set up a persistent SSH reverse tunnel."""
    import scitex_tunnel

    try:
        result = scitex_tunnel.setup(port, bastion, secret_key)
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


@main.command("remove", hidden=True, context_settings={"ignore_unknown_options": True})
@click.pass_context
def remove_deprecated(ctx):
    """(deprecated) Renamed to `remove-tunnel`."""
    click.echo(
        "error: `scitex-tunnel remove` was renamed to `scitex-tunnel remove-tunnel`.\n"
        "Re-run with: scitex-tunnel remove-tunnel",
        err=True,
    )
    ctx.exit(2)


@main.command("remove-tunnel")
@click.option("-p", "--port", required=True, type=int, help="Port of tunnel to remove.")
def remove_tunnel(port):
    """Remove a persistent SSH reverse tunnel."""
    import scitex_tunnel

    result = scitex_tunnel.remove(port)
    if result["success"]:
        click.secho(f"Tunnel on port {port} removed.", fg="green")
        if result["stdout"]:
            click.echo(result["stdout"])
    else:
        click.secho(f"Failed to remove tunnel on port {port}.", fg="red", err=True)
        if result["stderr"]:
            click.echo(result["stderr"], err=True)
        raise SystemExit(1)


@main.command("status", hidden=True, context_settings={"ignore_unknown_options": True})
@click.pass_context
def status_deprecated(ctx):
    """(deprecated) Renamed to `show-status`."""
    click.echo(
        "error: `scitex-tunnel status` was renamed to `scitex-tunnel show-status`.\n"
        "Re-run with: scitex-tunnel show-status",
        err=True,
    )
    ctx.exit(2)


@main.command("show-status")
@click.option(
    "-p",
    "--port",
    type=int,
    default=None,
    help="Specific port to check (default: all).",
)
def show_status(port):
    """Check status of SSH reverse tunnels."""
    import scitex_tunnel

    result = scitex_tunnel.status(port)
    click.echo(result["stdout"])
    if result["stderr"]:
        click.echo(result["stderr"], err=True)


# -----------------------------------------------------------------------
# Register integration commands
# -----------------------------------------------------------------------

main.add_command(list_python_apis)
main.add_command(mcp)


# EOF
