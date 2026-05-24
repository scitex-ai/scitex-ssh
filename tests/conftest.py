"""Pytest fixtures and rootdir marker for this package.

An empty conftest.py at tests/ is the canonical SciTeX
convention (audit-project PS208) — it pins the pytest
rootdir and gives downstream fixtures a home.

Also wires subprocess coverage: see
05_development_06_subprocess-coverage.md. `os.environ.setdefault`
would be a no-op because pytest-cov has already set
COVERAGE_FILE by the time conftest is loaded.
"""

from __future__ import annotations

import json
import os
import stat
import sysconfig
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

os.environ["COVERAGE_PROCESS_START"] = str(_PROJECT_ROOT / "pyproject.toml")
os.environ["COVERAGE_FILE"] = str(_PROJECT_ROOT / ".coverage")


def _ensure_subprocess_coverage_shim() -> None:
    """Drop an idempotent `.pth` file in site-packages that auto-starts
    coverage in every child Python interpreter via
    `coverage.process_startup()`.
    """
    purelib = Path(sysconfig.get_paths()["purelib"])
    pth = purelib / "_scitex_ssh_subprocess_coverage.pth"
    shim = (
        "import os, coverage\n"
        "if os.environ.get('COVERAGE_PROCESS_START'):\n"
        "    coverage.process_startup()\n"
    )
    try:
        if not pth.exists() or pth.read_text() != shim:
            pth.write_text(shim)
    except OSError:
        # site-packages may be read-only (e.g. system Python); silently
        # skip — local dev venvs are writable and that's where this matters.
        pass


_ensure_subprocess_coverage_shim()


# ---------------------------------------------------------------------------
# Real-collaborator fixtures (no-mocks discipline — see 02_package_12_no-mocks.md)
# ---------------------------------------------------------------------------


class _Shim:
    """Handle to a directory of fake binaries that log their argv.

    Each installed binary appends one JSON line per invocation to a
    per-binary log file, so a test can assert on the *real* argv that
    `subprocess.run` constructed — exercising the production codepath
    end to end instead of patching `subprocess.run`.
    """

    def __init__(self, bin_dir: Path):
        self.bin_dir = bin_dir

    def install(
        self, name: str, *, rc: int = 0, stdout: str = "", stderr: str = ""
    ) -> None:
        """Create an executable fake `name` that records argv and exits `rc`."""
        log = self.bin_dir / f"{name}.log"
        log.write_text("")
        script = (
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            f"log = {str(log)!r}\n"
            "with open(log, 'a') as fh:\n"
            "    fh.write(json.dumps(sys.argv[1:]) + '\\n')\n"
            f"sys.stdout.write({stdout!r})\n"
            f"sys.stderr.write({stderr!r})\n"
            f"sys.exit({int(rc)})\n"
        )
        path = self.bin_dir / name
        path.write_text(script)
        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    def argv(self, name: str) -> list[str]:
        """Return argv (excluding binary name) of the last call to `name`."""
        log = self.bin_dir / f"{name}.log"
        lines = [ln for ln in log.read_text().splitlines() if ln.strip()]
        if not lines:
            raise AssertionError(f"shim {name!r} was never invoked")
        return json.loads(lines[-1])

    def call_count(self, name: str) -> int:
        log = self.bin_dir / f"{name}.log"
        if not log.exists():
            return 0
        return len([ln for ln in log.read_text().splitlines() if ln.strip()])


@pytest.fixture
def subprocess_shim(tmp_path):
    """Yield a `_Shim` whose `bin/` is prepended to `$PATH`.

    Tests call `shim.install("ssh", stdout="hi")` then exercise the
    production function; the real `subprocess.run(["ssh", ...])` resolves
    to the fake, which logs argv. Assert via `shim.argv("ssh")`.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    saved_path = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{bin_dir}{os.pathsep}{saved_path}"
    try:
        yield _Shim(bin_dir)
    finally:
        os.environ["PATH"] = saved_path


@pytest.fixture
def allow_tunnels(tmp_path, env_save_restore):
    """Write an allowlist config that permits tunnels for every host.

    Points the allowlist at it via $SCITEX_SSH_CONFIG (the documented
    override) so allowlist-gated CLI commands (setup/remove) pass the
    `_require_allowed(...)` check against a real config file.
    """
    cfg = tmp_path / "allow_config.yaml"
    cfg.write_text("default: {tunnels: allow}\n")
    env_save_restore("SCITEX_SSH_CONFIG", str(cfg))
    return cfg


@pytest.fixture
def deny_tunnels(tmp_path, env_save_restore):
    """Write an allowlist config that denies tunnels for every host.

    Used to exercise the real PolicyError path through the CLI without a
    forced mock side effect.
    """
    cfg = tmp_path / "deny_config.yaml"
    cfg.write_text("default: {tunnels: deny}\n")
    env_save_restore("SCITEX_SSH_CONFIG", str(cfg))
    return cfg


@pytest.fixture
def env_save_restore():
    """Yield a setter that mutates os.environ and restores it on teardown.

    Replaces `monkeypatch.setenv(...)`: call `set("HOME", "/tmp")` inside
    a test; the original value (or absence) is restored at teardown.
    """
    saved: dict[str, str | None] = {}

    def _set(key: str, value: str) -> None:
        if key not in saved:
            saved[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        yield _set
    finally:
        for key, old in saved.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old
