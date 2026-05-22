#!/usr/bin/env python3
"""Tests for scitex_ssh._allowlist — fail-closed per-host policy.

Uses the production ``config_path`` injection kwarg + ``tmp_path`` so
each test exercises the real YAML loader against a real file (no
``monkeypatch.setattr`` on module globals).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scitex_ssh._allowlist import PolicyError, is_allowed, require


@pytest.fixture
def cfg_path(tmp_path: Path) -> Path:
    """Return the on-disk config path for the test (file not yet written)."""
    return tmp_path / "config.yaml"


def test_missing_config_returns_false_for_any_host(cfg_path: Path) -> None:
    # Arrange
    assert not cfg_path.exists()
    # Act
    allowed = is_allowed("anyhost", "tunnels", config_path=cfg_path)
    # Assert
    assert allowed is False


def test_missing_config_raises_policyerror_on_require(cfg_path: Path) -> None:
    # Arrange
    assert not cfg_path.exists()
    # Act
    ctx = pytest.raises(PolicyError)
    # Assert
    with ctx:
        require("anyhost", "tunnels", config_path=cfg_path)


def test_host_explicitly_allowed_returns_true(cfg_path: Path) -> None:
    # Arrange
    cfg_path.write_text(
        "default: {tunnels: deny}\nhosts:\n  mba: {tunnels: allow}\n"
    )
    # Act
    allowed = is_allowed("mba", "tunnels", config_path=cfg_path)
    # Assert
    assert allowed is True


def test_host_explicitly_allowed_does_not_raise_on_require(cfg_path: Path) -> None:
    # Arrange
    cfg_path.write_text(
        "default: {tunnels: deny}\nhosts:\n  mba: {tunnels: allow}\n"
    )
    # Act
    require("mba", "tunnels", config_path=cfg_path)
    # Assert
    # If require() had raised, we'd never reach this line — the absence
    # of a raised exception IS the assertion. Materialise it explicitly
    # for TQ001.
    assert is_allowed("mba", "tunnels", config_path=cfg_path) is True


def test_host_explicitly_denied_returns_false(cfg_path: Path) -> None:
    # Arrange
    cfg_path.write_text(
        "default: {tunnels: allow}\nhosts:\n  spartan: {tunnels: deny}\n"
    )
    # Act
    allowed = is_allowed("spartan", "tunnels", config_path=cfg_path)
    # Assert
    assert allowed is False


def test_host_explicitly_denied_raises_policyerror_on_require(cfg_path: Path) -> None:
    # Arrange
    cfg_path.write_text(
        "default: {tunnels: allow}\nhosts:\n  spartan: {tunnels: deny}\n"
    )
    # Act
    ctx = pytest.raises(PolicyError)
    # Assert
    with ctx:
        require("spartan", "tunnels", config_path=cfg_path)


def test_default_allow_grants_unlisted_host(cfg_path: Path) -> None:
    # Arrange
    cfg_path.write_text("default: {tunnels: allow}\n")
    # Act
    allowed = is_allowed("randomhost", "tunnels", config_path=cfg_path)
    # Assert
    assert allowed is True


def test_default_deny_blocks_unlisted_host(cfg_path: Path) -> None:
    # Arrange
    cfg_path.write_text("default: {tunnels: deny}\n")
    # Act
    allowed = is_allowed("randomhost", "tunnels", config_path=cfg_path)
    # Assert
    assert allowed is False


def test_default_deny_raises_policyerror_for_unlisted_host(cfg_path: Path) -> None:
    # Arrange
    cfg_path.write_text("default: {tunnels: deny}\n")
    # Act
    ctx = pytest.raises(PolicyError)
    # Assert
    with ctx:
        require("randomhost", "tunnels", config_path=cfg_path)


# EOF
