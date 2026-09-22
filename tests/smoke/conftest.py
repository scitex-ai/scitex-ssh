"""Smoke-test isolation: CLI subprocesses get a hermetic environment.

`scitex-ssh` resolves config via $SCITEX_SSH_CONFIG and credentials via
$SCITEX_SSH_BASTION_SERVER / $SCITEX_SSH_SECRET_KEY_PATH. The fixture
points config at a tmp allowlist and blanks the credential vars (blank,
not deleted: a deleted var can be repopulated from the developer's real
`.env` by dotenv-loading layers, while a blank one still reads as unset
after `strip()`).

No monkeypatch (PA-306): explicit save/restore with try/finally.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated_scitex_env(tmp_path: Path) -> Iterator[None]:
    allow_cfg = tmp_path / "allow_config.yaml"
    allow_cfg.write_text("default: {tunnels: allow}\n")
    names = (
        "SCITEX_SSH_CONFIG",
        "SCITEX_SSH_BASTION_SERVER",
        "SCITEX_SSH_SECRET_KEY_PATH",
    )
    previous = {name: os.environ.get(name) for name in names}
    os.environ["SCITEX_SSH_CONFIG"] = str(allow_cfg)
    os.environ["SCITEX_SSH_BASTION_SERVER"] = " "
    os.environ["SCITEX_SSH_SECRET_KEY_PATH"] = " "
    try:
        yield
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
