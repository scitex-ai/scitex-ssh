"""Importing the MCP adapter must not require the optional transport library."""

import subprocess
import sys
from pathlib import Path


def test_stdlib_only_mcp_adapter_import_gives_actionable_error_on_creation(tmp_path):
    # Arrange
    server = Path(__file__).resolve().parents[2] / "src/scitex_ssh/_mcp/_server.py"
    driver = (
        "import importlib.util,sys\n"
        "spec=importlib.util.spec_from_file_location('owned_mcp',sys.argv[1])\n"
        "module=importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        "try:\n"
        " module.create_server()\n"
        "except ImportError as error:\n"
        " print(repr(str(error)))\n"
    )
    # Act
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", driver, str(server)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    # Assert
    assert (result.returncode, "scitex-ssh[mcp]" in result.stdout) == (0, True)
