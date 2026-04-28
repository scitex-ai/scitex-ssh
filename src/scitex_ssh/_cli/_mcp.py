#!/usr/bin/env python3
"""MCP CLI subcommands for scitex-ssh."""

import click


@click.group()
def mcp():
    """MCP server management."""


@mcp.command()
def start():
    """Start the MCP server."""
    try:
        from scitex_ssh._mcp._server import create_server

        server = create_server()
        server.run()
    except ImportError:
        click.secho(
            "ERROR: fastmcp is not installed. Install with: pip install scitex-ssh[mcp]",
            fg="red",
            err=True,
        )
        raise SystemExit(1)


@mcp.command()
def doctor():
    """Check MCP server dependencies and configuration."""
    issues = []

    try:
        import fastmcp  # noqa: F401

        click.secho("  fastmcp: installed", fg="green")
    except ImportError:
        click.secho("  fastmcp: NOT installed", fg="red")
        issues.append("pip install scitex-ssh[mcp]")

    import shutil

    if shutil.which("autossh"):
        click.secho("  autossh: installed", fg="green")
    else:
        click.secho("  autossh: NOT installed", fg="red")
        issues.append("sudo apt install autossh")

    if issues:
        click.echo()
        click.echo("Fix with:")
        for fix in issues:
            click.echo(f"  {fix}")
        raise SystemExit(1)
    else:
        click.secho("\nAll checks passed.", fg="green")


@mcp.command(
    "installation", hidden=True, context_settings={"ignore_unknown_options": True}
)
@click.pass_context
def installation_deprecated(ctx):
    """(deprecated) Renamed to `show-installation`."""
    click.echo(
        "error: `scitex-ssh mcp installation` was renamed to "
        "`scitex-ssh mcp show-installation`.\n"
        "Re-run with: scitex-ssh mcp show-installation",
        err=True,
    )
    ctx.exit(2)


@mcp.command("show-installation")
def show_installation():
    """Show MCP server installation instructions."""
    click.echo("Install scitex-ssh with MCP support:")
    click.echo()
    click.echo("  pip install scitex-ssh[mcp]")
    click.echo()
    click.echo("Add to your Claude Code MCP config:")
    click.echo()
    click.echo("  {")
    click.echo('    "mcpServers": {')
    click.echo('      "scitex-ssh": {')
    click.echo('        "command": "scitex-ssh",')
    click.echo('        "args": ["mcp", "start"]')
    click.echo("      }")
    click.echo("    }")
    click.echo("  }")


@mcp.command("list-tools")
@click.option("-v", "--verbose", count=True, help="Verbosity (-v, -vv, -vvv).")
def list_tools(verbose):
    """List available MCP tools."""
    tools = [
        (
            "tunnel_setup",
            "Set up a persistent SSH reverse tunnel",
            "port, bastion_server, secret_key_path",
        ),
        ("tunnel_status", "Check status of SSH reverse tunnels", "port (optional)"),
        ("tunnel_remove", "Remove a persistent SSH reverse tunnel", "port"),
    ]

    click.echo("scitex-ssh MCP tools:")
    click.echo()
    for name, desc, params in tools:
        if verbose >= 2:
            click.echo(f"  {name:20s} {desc}")
            click.echo(f"  {' ':20s} params: {params}")
        elif verbose >= 1:
            click.echo(f"  {name:20s} {desc}")
        else:
            click.echo(f"  {name}")


# EOF
