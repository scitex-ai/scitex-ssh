#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._introspect — `list-python-apis` command."""

import json

from click.testing import CliRunner

from scitex_ssh._cli._introspect import list_python_apis


class TestListPythonApis:
    def test_default_lists_function_names_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, [])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_default_lists_function_names_all_name_in_result_output_for_name_in_setup_remove_status_ge(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, [])
        # Act
        # Assert
        # Assert
        assert all(name in result.output for name in ('setup', 'remove', 'status', 'get_version'))


    def test_verbose_includes_constants_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-v"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_verbose_includes_constants_available_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-v"])
        # Act
        # Assert
        # Assert
        assert "AVAILABLE" in result.output

    def test_verbose_includes_constants_version_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-v"])
        # Act
        # Assert
        # Assert
        assert "__version__" in result.output


    def test_very_verbose_pulls_docstring_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-vv"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_very_verbose_pulls_docstring_set_up_a_persistent_ssh_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["-vv"])
        # Act
        # Assert
        # Assert
        assert "Set up a persistent SSH" in result.output


    def test_json_emits_structured_payload_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_emits_structured_payload_payload_module_scitex_ssh_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_emits_structured_payload_payload_module_scitex_ssh_payload_module_scitex_ssh(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        # Act
        # Assert
        assert payload["module"] == "scitex_ssh"


    def test_json_emits_structured_payload_setup_remove_status_get_version_issubset_api_names_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_emits_structured_payload_setup_remove_status_get_version_issubset_api_names_payload_module_scitex_ssh(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        # Act
        # Assert
        assert payload["module"] == "scitex_ssh"

    def test_json_emits_structured_payload_setup_remove_status_get_version_issubset_api_names_setup_remove_status_get_version_issubset_api_names(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["module"] == "scitex_ssh"
        api_names = {item["name"] for item in payload["apis"]}
        # Act
        # Assert
        assert {"setup", "remove", "status", "get_version"}.issubset(api_names)


    def test_json_emits_structured_payload_available_version_issubset_const_names_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_emits_structured_payload_available_version_issubset_const_names_payload_module_scitex_ssh(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        # Act
        # Assert
        assert payload["module"] == "scitex_ssh"

    def test_json_emits_structured_payload_available_version_issubset_const_names_setup_remove_status_get_version_issubset_api_names(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["module"] == "scitex_ssh"
        api_names = {item["name"] for item in payload["apis"]}
        # Act
        # Assert
        assert {"setup", "remove", "status", "get_version"}.issubset(api_names)

    def test_json_emits_structured_payload_available_version_issubset_const_names_available_version_issubset_const_names(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(list_python_apis, ["--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["module"] == "scitex_ssh"
        api_names = {item["name"] for item in payload["apis"]}
        assert {"setup", "remove", "status", "get_version"}.issubset(api_names)
        const_names = {item["name"] for item in payload["constants"]}
        # Act
        # Assert
        assert {"AVAILABLE", "__version__"}.issubset(const_names)




# EOF
