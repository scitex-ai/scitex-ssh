#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._introspect — `list-python-apis` command.

All tests run real Click invocations against a live CliRunner — no
mocks. Multi-assert variants from the prior file are collapsed via a
shared ``json_payload`` fixture so each test stays single-assert
(TQ007).
"""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from scitex_ssh._cli._introspect import list_python_apis


@pytest.fixture
def json_payload() -> dict:
    """Parsed JSON payload from `list-python-apis --json`."""
    runner = CliRunner()
    result = runner.invoke(list_python_apis, ["--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


# ---------------------------------------------------------------------
# Default (text) output
# ---------------------------------------------------------------------


class TestListPythonApisDefault:
    def test_default_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, [])
        # Assert
        assert result.exit_code == 0

    def test_default_output_lists_all_expected_public_function_names(self) -> None:
        # Arrange
        runner = CliRunner()
        expected = ("setup", "remove", "status", "get_version")
        # Act
        result = runner.invoke(list_python_apis, [])
        # Assert
        assert all(name in result.output for name in expected)


# ---------------------------------------------------------------------
# Verbose (-v) output — includes module constants
# ---------------------------------------------------------------------


class TestListPythonApisVerbose:
    def test_verbose_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-v"])
        # Assert
        assert result.exit_code == 0

    def test_verbose_output_lists_available_constant_name(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-v"])
        # Assert
        assert "AVAILABLE" in result.output

    def test_verbose_output_lists_version_dunder_constant_name(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-v"])
        # Assert
        assert "__version__" in result.output


# ---------------------------------------------------------------------
# Very-verbose (-vv) output — pulls docstrings
# ---------------------------------------------------------------------


class TestListPythonApisVeryVerbose:
    def test_very_verbose_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-vv"])
        # Assert
        assert result.exit_code == 0

    def test_very_verbose_output_includes_setup_docstring_lead(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-vv"])
        # Assert
        assert "Set up a persistent SSH" in result.output


# ---------------------------------------------------------------------
# --json output — structured payload (uses json_payload fixture)
# ---------------------------------------------------------------------


class TestListPythonApisJson:
    def test_json_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Assert
        assert result.exit_code == 0

    def test_json_payload_module_field_matches_canonical_import_name(
        self, json_payload: dict
    ) -> None:
        # Arrange
        # Act
        module = json_payload["module"]
        # Assert
        assert module == "scitex_ssh"

    def test_json_payload_apis_includes_all_expected_public_function_names(
        self, json_payload: dict
    ) -> None:
        # Arrange
        expected = {"setup", "remove", "status", "get_version"}
        # Act
        api_names = {item["name"] for item in json_payload["apis"]}
        # Assert
        assert expected.issubset(api_names)

    def test_json_payload_constants_includes_available_and_version(
        self, json_payload: dict
    ) -> None:
        # Arrange
        expected = {"AVAILABLE", "__version__"}
        # Act
        const_names = {item["name"] for item in json_payload["constants"]}
        # Assert
        assert expected.issubset(const_names)


# EOF
