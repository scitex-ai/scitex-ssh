"""Basic SSH primitives — exec/copy/attach. No allowlist (always allowed)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Sequence


@dataclass
class SSHResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0


def exec_remote(
    host: str,
    command: str,
    *,
    ssh_opts: Sequence[str] = (),
    check: bool = False,
    timeout: float | None = None,
) -> SSHResult:
    """Run a command on `host` via ssh.

    `ssh_opts` is a list of raw ssh flags (e.g. ['-A', '-o', 'StrictHostKeyChecking=no'])
    passed through verbatim. Users opt into agent forwarding by passing '-A' themselves.
    """
    cmd = ["ssh", *ssh_opts, host, command]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    result = SSHResult(proc.returncode, proc.stdout, proc.stderr)
    if check and not result.success:
        raise RuntimeError(
            f"ssh {host!r} failed (rc={proc.returncode}): {proc.stderr.strip()}"
        )
    return result


def copy_to(
    host: str,
    src: str,
    dest: str,
    *,
    recursive: bool = False,
    ssh_opts: Sequence[str] = (),
) -> SSHResult:
    """scp local `src` to `host:dest`. ssh_opts forwarded via -o."""
    cmd = [
        "scp",
        *(["-r"] if recursive else []),
        *_ssh_opts_to_scp(ssh_opts),
        src,
        f"{host}:{dest}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return SSHResult(proc.returncode, proc.stdout, proc.stderr)


def copy_from(
    host: str,
    src: str,
    dest: str,
    *,
    recursive: bool = False,
    ssh_opts: Sequence[str] = (),
) -> SSHResult:
    """scp `host:src` to local `dest`."""
    cmd = [
        "scp",
        *(["-r"] if recursive else []),
        *_ssh_opts_to_scp(ssh_opts),
        f"{host}:{src}",
        dest,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return SSHResult(proc.returncode, proc.stdout, proc.stderr)


def attach(
    host: str,
    command: str | None = None,
    *,
    ssh_opts: Sequence[str] = (),
) -> int:
    """Interactive ssh -t. Replaces current process via os.execvp; returns rc only on failure-to-launch."""
    import os

    cmd = ["ssh", "-t", *ssh_opts, host]
    if command:
        cmd.append(command)
    os.execvp(cmd[0], cmd)
    return 1  # unreachable on success


def _ssh_opts_to_scp(opts: Sequence[str]) -> list[str]:
    """scp shares ssh's `-o KEY=VAL` syntax but rejects `-A` etc.

    Pass through `-o` pairs and `-i identity`; drop the rest with no warning
    (basic flags like -A are tunnel-related and not relevant for scp).
    """
    out: list[str] = []
    i = 0
    while i < len(opts):
        if opts[i] in ("-o", "-i", "-P", "-F"):
            if i + 1 < len(opts):
                out.extend([opts[i], opts[i + 1]])
            i += 2
        else:
            i += 1
    return out


# EOF
