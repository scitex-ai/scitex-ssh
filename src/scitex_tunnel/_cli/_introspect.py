#!/usr/bin/env python3
"""Introspection CLI commands for scitex-tunnel."""

import click


@click.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity (-v, -vv, -vvv).")
def list_python_apis(verbose):
    """List public Python API functions."""
    import scitex_tunnel

    apis = [
        ("setup", "Set up a persistent SSH reverse tunnel"),
        ("remove", "Remove a persistent SSH reverse tunnel"),
        ("status", "Check status of SSH reverse tunnels"),
        ("get_version", "Get scitex-tunnel version"),
    ]

    constants = [
        ("AVAILABLE", "Whether scitex-tunnel is available"),
        ("__version__", "Package version string"),
    ]

    click.echo("scitex_tunnel Python API:")
    click.echo()
    for name, desc in apis:
        if verbose >= 2:
            func = getattr(scitex_tunnel, name, None)
            sig = ""
            if func and func.__doc__:
                sig = func.__doc__.strip().split("\n")[0]
            click.echo(f"  {name:20s} {sig}")
        elif verbose >= 1:
            click.echo(f"  {name:20s} {desc}")
        else:
            click.echo(f"  {name}")

    if verbose >= 1:
        click.echo()
        click.echo("Constants:")
        for name, desc in constants:
            click.echo(f"  {name:20s} {desc}")


# EOF
