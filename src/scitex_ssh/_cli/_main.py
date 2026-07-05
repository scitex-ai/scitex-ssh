#!/usr/bin/env python3
"""Main CLI entry point for scitex-ssh (root group + command registration)."""

import click

from ._introspect import list_python_apis
from ._mcp import mcp
from ._primitives import attach_cmd, copy_cmd, exec_cmd, sync_cmd
from ._tunnel import (
    _default_host,
    _deprecation_warn,
    _do_tunnel_remove,
    _do_tunnel_setup,
    _do_tunnel_status,
    tunnel,
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

COMMAND_CATEGORIES = [
    ("SSH Primitives", ["exec", "copy", "sync", "attach"]),
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


@click.group(
    cls=CategorizedGroup,
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.option("--version", "-V", is_flag=True, help="Show version and exit.")
@click.option("--help-recursive", is_flag=True, help="Show help for all commands.")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit structured JSON output (propagates to subcommands that honour it).",
)
@click.pass_context
def main(ctx, version, help_recursive, as_json):
    """scitex-ssh - SSH primitives (exec/copy/attach) and gated reverse tunnels.

    \b
    Config is loaded with the SciTeX precedence chain:
      config.yaml -> $SCITEX_SSH_CONFIG -> ~/.scitex/ssh/config.yaml -> defaults
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    if version:
        click.echo(f"scitex-ssh {_get_version()}")
        ctx.exit(0)

    if help_recursive:
        _show_recursive_help(ctx)
        ctx.exit(0)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# -----------------------------------------------------------------------
# Deprecated top-level aliases (hidden) — thin wrappers over `tunnel *`
# -----------------------------------------------------------------------
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
    """(deprecated) Use `tunnel check-status`."""
    _deprecation_warn("show-status", "tunnel check-status")
    _do_tunnel_status(port)


# -----------------------------------------------------------------------
# Register command groups (tunnel) + top-level primitives + integration
# -----------------------------------------------------------------------
main.add_command(tunnel)
main.add_command(exec_cmd)
main.add_command(copy_cmd)
main.add_command(sync_cmd)
main.add_command(attach_cmd)
main.add_command(list_python_apis)
main.add_command(mcp)

try:
    from scitex_dev._cli._completion import attach_shell_completion

    attach_shell_completion(main, prog_name="scitex-ssh")
except Exception:
    pass


# EOF
