#!/usr/bin/env python3
"""CLI commands for SSH primitives (exec/copy/attach)."""

from __future__ import annotations

import shlex

import click


def _split_opts(s: str | None) -> list[str]:
    return shlex.split(s) if s else []


@click.command("exec")
@click.argument("host")
@click.argument("command")
@click.option(
    "--ssh-opts",
    default=None,
    help='Extra ssh flags as a single shell-quoted string (e.g. "-A -o StrictHostKeyChecking=no").',
)
@click.option("--timeout", type=float, default=None, help="Timeout in seconds.")
def exec_cmd(host, command, ssh_opts, timeout):
    """Run a command on HOST via ssh."""
    from scitex_ssh import exec_remote

    result = exec_remote(host, command, ssh_opts=_split_opts(ssh_opts), timeout=timeout)
    if result.stdout:
        click.echo(result.stdout, nl=False)
    if result.stderr:
        click.echo(result.stderr, err=True, nl=False)
    raise SystemExit(result.returncode)


def _split_host_path(arg: str) -> tuple[str | None, str]:
    """Return (host, path) for HOST:PATH; (None, path) for local."""
    # Be tolerant of Windows-style or absolute paths without colon.
    if ":" in arg and not arg.startswith("/") and not arg.startswith("./"):
        host, _, path = arg.partition(":")
        if host and "/" not in host:
            return host, path
    return None, arg


@click.command("copy")
@click.argument("src")
@click.argument("dest")
@click.option("-r", "--recursive", is_flag=True, help="Recursive copy.")
@click.option(
    "--ssh-opts",
    default=None,
    help="Extra ssh flags as a single shell-quoted string.",
)
def copy_cmd(src, dest, recursive, ssh_opts):
    """Copy files between local and a remote HOST:PATH."""
    from scitex_ssh import copy_from, copy_to

    src_host, src_path = _split_host_path(src)
    dest_host, dest_path = _split_host_path(dest)
    opts = _split_opts(ssh_opts)

    if src_host and not dest_host:
        result = copy_from(
            src_host, src_path, dest_path, recursive=recursive, ssh_opts=opts
        )
    elif dest_host and not src_host:
        result = copy_to(
            dest_host, src_path, dest_path, recursive=recursive, ssh_opts=opts
        )
    elif src_host and dest_host:
        click.secho(
            "ERROR: remote-to-remote copy is not supported.", fg="red", err=True
        )
        raise SystemExit(2)
    else:
        click.secho(
            "ERROR: at least one of SRC or DEST must be HOST:PATH.", fg="red", err=True
        )
        raise SystemExit(2)

    if result.stdout:
        click.echo(result.stdout, nl=False)
    if result.stderr:
        click.echo(result.stderr, err=True, nl=False)
    raise SystemExit(result.returncode)


@click.command("attach")
@click.argument("host")
@click.option("--command", "-c", default=None, help="Command to run after attaching.")
@click.option(
    "--ssh-opts",
    default=None,
    help="Extra ssh flags as a single shell-quoted string.",
)
def attach_cmd(host, command, ssh_opts):
    """Open an interactive ssh -t session to HOST."""
    from scitex_ssh import attach

    rc = attach(host, command, ssh_opts=_split_opts(ssh_opts))
    raise SystemExit(rc)


# EOF
