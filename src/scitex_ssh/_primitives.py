"""Basic SSH primitives — exec/copy/attach. No allowlist (always allowed)."""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class SSHResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0


@dataclass
class ProbeResult:
    reachable: bool
    capabilities: dict = field(default_factory=dict)
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        """Reachable and every requested capability present (vacuously True if none requested)."""
        return self.reachable and all(self.capabilities.values())

    def has(self, name: str) -> bool:
        return self.capabilities.get(name, False)


def exec_remote(
    host: str,
    command: str,
    *,
    ssh_opts: Sequence[str] = (),
    check: bool = False,
    timeout: float | None = None,
    runner=None,
) -> SSHResult:
    """Run a command on `host` via ssh.

    `ssh_opts` is a list of raw ssh flags (e.g. ['-A', '-o', 'StrictHostKeyChecking=no'])
    passed through verbatim. Users opt into agent forwarding by passing '-A' themselves.

    Parameters
    ----------
    runner : callable, optional
        Subprocess invoker matching ``subprocess.run``'s signature. Defaults
        to ``subprocess.run``. Pass a hand-rolled fake from tests to observe
        and stub the call without mocks.
    """
    if runner is None:
        runner = subprocess.run
    cmd = ["ssh", *ssh_opts, host, command]
    proc = runner(cmd, capture_output=True, text=True, timeout=timeout)
    result = SSHResult(proc.returncode, proc.stdout, proc.stderr)
    if check and not result.success:
        raise RuntimeError(
            f"ssh {host!r} failed (rc={proc.returncode}): {proc.stderr.strip()}"
        )
    return result


def probe_remote(
    host: str,
    *,
    requires: Sequence[str] = (),
    ssh_opts: Sequence[str] = (),
    timeout: float | None = None,
    runner=None,
) -> ProbeResult:
    """Reachability + capability preflight over a single ssh round-trip.

    Confirms `host` answers, then checks each name in `requires` via
    `command -v <name>` on the remote (e.g. "apptainer", "rsync"). Policy-free
    like `sync_dir`: the caller decides which capabilities matter (what to
    require, what to do if missing); this only reports what is there.

    Capability names are matched to remote output by ORDER, not by echoing
    the name back through the remote shell — avoids any quoting hazard for
    unusual capability strings and tolerates login-banner/MOTD noise on
    stdout (the reachability marker is located by scanning, not by assuming
    it is line 0).

    Parameters
    ----------
    host : str
        Remote ssh host (an ``~/.ssh/config`` alias like ``spartan`` works).
    requires : sequence of str
        Executable names to probe for via ``command -v`` on the remote.
        Empty by default — a bare reachability check.
    ssh_opts : sequence of str
        Raw ssh flags forwarded verbatim, same convention as ``exec_remote``.
    timeout : float, optional
        Passed through to the underlying ``ssh`` subprocess call.
    runner : callable, optional
        ``subprocess.run``-shaped invoker; defaults to ``subprocess.run``.
        Pass a hand-rolled fake from tests to observe argv without mocks.

    Returns
    -------
    ProbeResult
        ``reachable`` is False if ssh itself failed (down, auth, timeout) —
        in that case ``capabilities`` is always empty rather than reporting
        every requirement as absent, since an unreachable host tells you
        nothing about what is installed there.
    """
    if runner is None:
        runner = subprocess.run
    marker = "__SCITEX_SSH_PROBE_REACHABLE__"
    parts = [f"echo {marker}"]
    for req in requires:
        q = shlex.quote(req)
        parts.append(f"command -v {q} >/dev/null 2>&1 && echo yes || echo no")
    remote_cmd = " ; ".join(parts)
    cmd = ["ssh", *ssh_opts, host, remote_cmd]
    proc = runner(cmd, capture_output=True, text=True, timeout=timeout)

    lines = proc.stdout.splitlines()
    reachable = proc.returncode == 0 and marker in lines
    capabilities: dict = {}
    if reachable:
        idx = lines.index(marker)
        cap_lines = lines[idx + 1 : idx + 1 + len(requires)]
        for name, line in zip(requires, cap_lines):
            capabilities[name] = line.strip() == "yes"

    return ProbeResult(
        reachable=reachable,
        capabilities=capabilities,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def copy_to(
    host: str,
    src: str,
    dest: str,
    *,
    recursive: bool = False,
    ssh_opts: Sequence[str] = (),
    runner=None,
) -> SSHResult:
    """scp local `src` to `host:dest`. ssh_opts forwarded via -o."""
    if runner is None:
        runner = subprocess.run
    cmd = [
        "scp",
        *(["-r"] if recursive else []),
        *_ssh_opts_to_scp(ssh_opts),
        src,
        f"{host}:{dest}",
    ]
    proc = runner(cmd, capture_output=True, text=True)
    return SSHResult(proc.returncode, proc.stdout, proc.stderr)


def copy_from(
    host: str,
    src: str,
    dest: str,
    *,
    recursive: bool = False,
    ssh_opts: Sequence[str] = (),
    runner=None,
) -> SSHResult:
    """scp `host:src` to local `dest`."""
    if runner is None:
        runner = subprocess.run
    cmd = [
        "scp",
        *(["-r"] if recursive else []),
        *_ssh_opts_to_scp(ssh_opts),
        f"{host}:{src}",
        dest,
    ]
    proc = runner(cmd, capture_output=True, text=True)
    return SSHResult(proc.returncode, proc.stdout, proc.stderr)


def sync_dir(
    host: str,
    local: str,
    remote: str,
    *,
    direction: str = "push",
    exclude: Sequence[str] = (),
    delete: bool = False,
    extra_opts: Sequence[str] = (),
    ssh_opts: Sequence[str] = (),
    runner=None,
) -> SSHResult:
    """rsync a directory one-way between local and ``host`` over ssh.

    A thin, policy-free wrapper over ``rsync -a`` for syncing a directory
    tree between the local machine and a remote host. Unlike ``copy_to`` /
    ``copy_from`` (single-shot scp, no delta/exclude), this does an
    incremental transfer with per-file excludes — the right tool for
    mirroring a per-user dir (e.g. ``~/.scitex/scholar/library``) between
    a WSL host and an HPC login node.

    The primitive is deliberately generic: it never decides *what* to
    exclude or *whether* to delete. Callers pass ``exclude`` globs and any
    ``extra_opts`` (``--checksum``, ``--mkpath``, ``--dry-run``, …); any
    post-sync step (e.g. rebuilding a derived index) is the caller's job
    via ``exec_remote``.

    Parameters
    ----------
    host : str
        Remote ssh host (an ``~/.ssh/config`` alias like ``spartan`` works).
    local : str
        Local directory path. Trailing-slash semantics are rsync's and are
        passed through verbatim: ``src/`` copies *contents*, ``src`` copies
        the dir itself. The caller controls this.
    remote : str
        Remote directory path on ``host``.
    direction : {"push", "pull"}
        ``push`` sends ``local`` → ``host:remote`` (default); ``pull`` pulls
        ``host:remote`` → ``local``.
    exclude : sequence of str
        Glob patterns passed as ``--exclude=<pat>`` (e.g. ``index.db``,
        ``*.db-wal``). Never ship a live sqlite/WAL file — exclude it and
        rebuild or snapshot it caller-side.
    delete : bool
        Add ``--delete`` (mirror deletions). Off by default: an additive
        merge library should not have receiver-side files deleted.
    extra_opts : sequence of str
        Raw rsync flags appended verbatim (escape hatch for
        ``--checksum``, ``--mkpath``, ``--dry-run``, ``--info=progress2``).
    ssh_opts : sequence of str
        ssh flags for the transport; wired via ``-e 'ssh <opts>'`` (e.g.
        ``['-o', 'BatchMode=yes']`` for non-interactive cron).
    runner : callable, optional
        ``subprocess.run``-shaped invoker; defaults to ``subprocess.run``.
        Pass a hand-rolled fake from tests to observe argv without mocks.
    """
    if direction not in ("push", "pull"):
        raise ValueError(f"direction must be 'push' or 'pull', got {direction!r}")
    if runner is None:
        runner = subprocess.run

    local_end = local
    remote_end = f"{host}:{remote}"
    src, dest = (
        (local_end, remote_end) if direction == "push" else (remote_end, local_end)
    )

    cmd = [
        "rsync",
        "-a",
        "--partial",
        *(["--delete"] if delete else []),
        *extra_opts,
        *[f"--exclude={pat}" for pat in exclude],
        *(["-e", "ssh " + " ".join(ssh_opts)] if ssh_opts else []),
        src,
        dest,
    ]
    proc = runner(cmd, capture_output=True, text=True)
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
