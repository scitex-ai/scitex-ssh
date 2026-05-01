#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._introspect — `list-python-apis` command."""

import json

from click.testing import CliRunner

from scitex_ssh._cli._introspect import list_python_apis


class TestListPythonApis:
    def test_default_lists_function_names(self):
        runner = CliRunner()
        result = runner.invoke(list_python_apis, [])
        assert result.exit_code == 0
        for name in ("setup", "remove", "status", "get_version"):
            assert name in result.output

    def test_verbose_includes_constants(self):
        runner = CliRunner()
        result = runner.invoke(list_python_apis, ["-v"])
        assert result.exit_code == 0
        assert "AVAILABLE" in result.output
        assert "__version__" in result.output

    def test_very_verbose_pulls_docstring(self):
        runner = CliRunner()
        result = runner.invoke(list_python_apis, ["-vv"])
        assert result.exit_code == 0
        # First line of `setup`'s docstring is "Set up a persistent SSH reverse tunnel."
        assert "Set up a persistent SSH" in result.output

    def test_json_emits_structured_payload(self):
        runner = CliRunner()
        result = runner.invoke(list_python_apis, ["--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["module"] == "scitex_ssh"
        api_names = {item["name"] for item in payload["apis"]}
        assert {"setup", "remove", "status", "get_version"}.issubset(api_names)
        const_names = {item["name"] for item in payload["constants"]}
        assert {"AVAILABLE", "__version__"}.issubset(const_names)


# EOF
