#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._introspect — `list-python-apis` command.

No mocks. Each test runs the real Click command and asserts one thing.
Shared invocations are lifted into fixtures so every test stays
single-assertion.
"""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from scitex_ssh._cli._introspect import list_python_apis


@pytest.fixture
def json_payload():
    """Invoke `list-python-apis --json` once and return the parsed payload."""
    result = CliRunner().invoke(list_python_apis, ["--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


class TestListPythonApis:
    def test_default_invocation_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, [])
        # Assert
        assert result.exit_code == 0

    def test_default_lists_public_function_names(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, [])
        # Assert
        assert all(
            name in result.output
            for name in ("setup", "remove", "status", "get_version")
        )

    def test_verbose_invocation_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-v"])
        # Assert
        assert result.exit_code == 0

    def test_verbose_includes_available_constant(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-v"])
        # Assert
        assert "AVAILABLE" in result.output

    def test_verbose_includes_version_constant(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-v"])
        # Assert
        assert "__version__" in result.output

    def test_very_verbose_invocation_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-vv"])
        # Assert
        assert result.exit_code == 0

    def test_very_verbose_pulls_function_docstring(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-vv"])
        # Assert
        assert "Set up a persistent SSH" in result.output

    def test_json_payload_names_the_module(self, json_payload):
        # Arrange
        payload = json_payload
        # Act
        module = payload["module"]
        # Assert
        assert module == "scitex_ssh"

    def test_json_payload_lists_public_apis(self, json_payload):
        # Arrange
        payload = json_payload
        # Act
        api_names = {item["name"] for item in payload["apis"]}
        # Assert
        assert {"setup", "remove", "status", "get_version"}.issubset(api_names)

    def test_json_payload_lists_constants(self, json_payload):
        # Arrange
        payload = json_payload
        # Act
        const_names = {item["name"] for item in payload["constants"]}
        # Assert
        assert {"AVAILABLE", "__version__"}.issubset(const_names)


# EOF
