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


def test_no_config_fails_closed_not_cfg_path_exists(cfg_path):
    # Arrange
    # Act
    # Assert
    # Arrange
    # Act
    # Assert
    assert not cfg_path.exists()


def test_no_config_fails_closed_is_allowed_anyhost_tunnels_is_false(cfg_path):
    # Arrange
    # Act
    # Assert
    # Arrange
    # Act
    # Assert
    assert is_allowed("anyhost", "tunnels") is False


def test_no_config_fails_closed_raises_policyerror(cfg_path):
    # Arrange
    # Act
    # Assert
    # Arrange
    # Act
    # Assert
    with pytest.raises(PolicyError):
        require("anyhost", "tunnels")




def test_host_explicitly_allowed(cfg_path: Path):
    # Arrange
    # Act
    # Arrange
    # Act
    cfg_path.write_text("default: {tunnels: deny}\nhosts:\n  mba: {tunnels: allow}\n")
    # Assert
    # Assert
    assert is_allowed("mba", "tunnels") is True
    require("mba", "tunnels")  # no raise


def test_host_explicitly_denied_is_allowed_spartan_tunnels_is_false(cfg_path: Path):
    # Arrange
    # Arrange
    # Act
    cfg_path.write_text(
        "default: {tunnels: allow}\nhosts:\n  spartan: {tunnels: deny}\n"
    )
    # Act
    # Assert
    # Assert
    assert is_allowed("spartan", "tunnels") is False


def test_host_explicitly_denied_raises_policyerror(cfg_path: Path):
    # Arrange
    # Arrange
    # Act
    cfg_path.write_text(
        "default: {tunnels: allow}\nhosts:\n  spartan: {tunnels: deny}\n"
    )
    # Act
    # Assert
    # Assert
    with pytest.raises(PolicyError):
        require("spartan", "tunnels")




def test_default_allow_unlisted(cfg_path: Path):
    # Arrange
    # Act
    # Arrange
    # Act
    cfg_path.write_text("default: {tunnels: allow}\n")
    # Assert
    # Assert
    assert is_allowed("randomhost", "tunnels") is True


def test_default_deny_unlisted_is_allowed_randomhost_tunnels_is_false(cfg_path: Path):
    # Arrange
    # Arrange
    # Act
    cfg_path.write_text("default: {tunnels: deny}\n")
    # Act
    # Assert
    # Assert
    assert is_allowed("randomhost", "tunnels") is False


def test_default_deny_unlisted_raises_policyerror(cfg_path: Path):
    # Arrange
    # Arrange
    # Act
    cfg_path.write_text("default: {tunnels: deny}\n")
    # Act
    # Assert
    # Assert
    with pytest.raises(PolicyError):
        require("randomhost", "tunnels")




# EOF
