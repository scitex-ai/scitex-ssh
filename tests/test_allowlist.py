#!/usr/bin/env python3
"""Tests for scitex_ssh._allowlist."""

from __future__ import annotations

from pathlib import Path

import pytest

from scitex_ssh import _allowlist
from scitex_ssh._allowlist import PolicyError, is_allowed, require


@pytest.fixture
def cfg_path(tmp_path, monkeypatch):
    p = tmp_path / "config.yaml"
    monkeypatch.setattr(_allowlist, "CONFIG_PATH", p)
    return p


def test_no_config_fails_closed(cfg_path):
    assert not cfg_path.exists()
    assert is_allowed("anyhost", "tunnels") is False
    with pytest.raises(PolicyError):
        require("anyhost", "tunnels")


def test_host_explicitly_allowed(cfg_path: Path):
    cfg_path.write_text("default: {tunnels: deny}\nhosts:\n  mba: {tunnels: allow}\n")
    assert is_allowed("mba", "tunnels") is True
    require("mba", "tunnels")  # no raise


def test_host_explicitly_denied(cfg_path: Path):
    cfg_path.write_text(
        "default: {tunnels: allow}\nhosts:\n  spartan: {tunnels: deny}\n"
    )
    assert is_allowed("spartan", "tunnels") is False
    with pytest.raises(PolicyError):
        require("spartan", "tunnels")


def test_default_allow_unlisted(cfg_path: Path):
    cfg_path.write_text("default: {tunnels: allow}\n")
    assert is_allowed("randomhost", "tunnels") is True


def test_default_deny_unlisted(cfg_path: Path):
    cfg_path.write_text("default: {tunnels: deny}\n")
    assert is_allowed("randomhost", "tunnels") is False
    with pytest.raises(PolicyError):
        require("randomhost", "tunnels")


# EOF
