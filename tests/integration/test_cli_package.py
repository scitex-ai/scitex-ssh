#!/usr/bin/env python3
"""Integration test: backward-compatible CLI entry point.

Asserts that the legacy `scitex_ssh.cli` shim and the new `scitex_ssh._cli`
package both resolve to the same Click group object — guards against shim
drift after the 0.x → 1.x layout refactor.
"""

from scitex_ssh._cli import main as _cli_main


def test_main_re_exported_from_subpackage_cli_main_is_click_group():
    # Arrange
    # Arrange
    # Act
    import click
    # Act
    # Assert
    # Assert
    assert isinstance(_cli_main, click.Group)


def test_main_re_exported_from_subpackage_cli_main_name_equals_main():
    # Arrange
    # Arrange
    # Act
    import click
    # Act
    # Assert
    # Assert
    assert _cli_main.name == "main"




def test_compat_shim_at_top_level():
    """`scitex_ssh.cli.main` (legacy import path) still works."""
    # Arrange
    # Act
    from scitex_ssh.cli import main as legacy_main

    # Assert
    assert legacy_main is _cli_main


# EOF
