#!/usr/bin/env python3
"""MCP CLI subcommands for scitex-tunnel."""

import click


@click.group()
def mcp():
    """MCP server management."""


@mcp.command()
def start():
    """Start the MCP server."""
    try:
        from scitex_tunnel._mcp._server import create_server

        server = create_server()
        server.run()
    except ImportError:
        click.secho(
            "ERROR: fastmcp is not installed. Install with: pip install scitex-tunnel[mcp]",
            fg="red",
            err=True,
        )
        raise SystemExit(1)


@mcp.command("list-tools")
@click.option("-v", "--verbose", count=True, help="Verbosity (-v, -vv, -vvv).")
def list_tools(verbose):
    """List available MCP tools."""
    tools = [
        ("tunnel_setup", "Set up a persistent SSH reverse tunnel", "port, bastion_server, secret_key_path"),
        ("tunnel_status", "Check status of SSH reverse tunnels", "port (optional)"),
        ("tunnel_remove", "Remove a persistent SSH reverse tunnel", "port"),
    ]

    click.echo("scitex-tunnel MCP tools:")
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
