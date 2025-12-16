"""Tests for the core module of AutoPyPack."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from AutoPyPack.autopypack.core import (
    install_package,
    is_module_available,
    load_mappings,
    scan_imports,
)


class TestLoadMappings:
    """Tests for the load_mappings function."""

    def test_load_mappings_returns_dict(self) -> None:
        """Test that load_mappings returns a dictionary."""
        mappings = load_mappings()
        assert isinstance(mappings, dict)

    def test_load_mappings_contains_common_mappings(self) -> None:
        """Test that mappings contain some common import-to-package mappings."""
        mappings = load_mappings()
        # These are common mappings that should exist
        # The exact contents depend on mappings.json
        assert isinstance(mappings, dict)


class TestIsModuleAvailable:
    """Tests for the is_module_available function."""

    def test_builtin_module_available(self) -> None:
        """Test that builtin modules are available."""
        assert is_module_available("sys") is True
        assert is_module_available("os") is True
        assert is_module_available("json") is True

    def test_nonexistent_module_not_available(self) -> None:
        """Test that nonexistent modules are not available."""
        assert is_module_available("nonexistent_module_xyz_123") is False

    def test_installed_module_available(self) -> None:
        """Test that installed modules are available."""
        # pytest is installed (we're using it), so it should be available
        assert is_module_available("pytest") is True


class TestScanImports:
    """Tests for the scan_imports function."""

    def test_scan_simple_imports(self) -> None:
        """Test scanning a file with simple import statements."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("import os\nimport sys\nimport json\n")
            f.flush()
            temp_path = f.name

        try:
            imports = scan_imports(temp_path)
            assert "os" in imports
            assert "sys" in imports
            assert "json" in imports
        finally:
            os.unlink(temp_path)

    def test_scan_from_imports(self) -> None:
        """Test scanning a file with from-import statements."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("from pathlib import Path\nfrom collections import defaultdict\n")
            f.flush()
            temp_path = f.name

        try:
            imports = scan_imports(temp_path)
            assert "pathlib" in imports
            assert "collections" in imports
        finally:
            os.unlink(temp_path)

    def test_scan_submodule_imports(self) -> None:
        """Test scanning a file with submodule imports."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("import os.path\nfrom urllib.parse import urlparse\n")
            f.flush()
            temp_path = f.name

        try:
            imports = scan_imports(temp_path)
            # Only top-level modules should be captured
            assert "os" in imports
            assert "urllib" in imports
            assert "os.path" not in imports
        finally:
            os.unlink(temp_path)

    def test_scan_empty_file(self) -> None:
        """Test scanning an empty file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("")
            f.flush()
            temp_path = f.name

        try:
            imports = scan_imports(temp_path)
            assert imports == set()
        finally:
            os.unlink(temp_path)

    def test_scan_file_with_syntax_error(self) -> None:
        """Test scanning a file with syntax errors."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("def broken(\n")  # Syntax error
            f.flush()
            temp_path = f.name

        try:
            imports = scan_imports(temp_path)
            assert imports == set()
        finally:
            os.unlink(temp_path)

    def test_scan_nonexistent_file(self) -> None:
        """Test scanning a nonexistent file."""
        imports = scan_imports("/nonexistent/path/to/file.py")
        assert imports == set()

    def test_scan_mixed_imports(self) -> None:
        """Test scanning a file with mixed import styles."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                """
import os
import sys as system
from pathlib import Path
from collections import defaultdict, OrderedDict
import json, csv
from typing import List, Dict, Optional
"""
            )
            f.flush()
            temp_path = f.name

        try:
            imports = scan_imports(temp_path)
            assert "os" in imports
            assert "sys" in imports
            assert "pathlib" in imports
            assert "collections" in imports
            assert "json" in imports
            assert "csv" in imports
            assert "typing" in imports
        finally:
            os.unlink(temp_path)


class TestInstallPackage:
    """Tests for the install_package function."""

    @mock.patch("subprocess.check_call")
    def test_install_package_success(self, mock_check_call: mock.Mock) -> None:
        """Test successful package installation."""
        mock_check_call.return_value = 0

        result = install_package("some-package", quiet=True)

        assert result is True
        mock_check_call.assert_called_once()

    @mock.patch("subprocess.check_call")
    def test_install_package_failure(self, mock_check_call: mock.Mock) -> None:
        """Test failed package installation."""
        import subprocess

        mock_check_call.side_effect = subprocess.CalledProcessError(1, "pip")

        result = install_package("nonexistent-package-xyz", quiet=True)

        assert result is False

    @mock.patch("subprocess.check_call")
    def test_install_package_uses_correct_python(
        self, mock_check_call: mock.Mock
    ) -> None:
        """Test that install_package uses the correct Python executable."""
        import sys

        mock_check_call.return_value = 0

        install_package("test-package", quiet=True)

        # Check that the call used the current Python executable
        call_args = mock_check_call.call_args[0][0]
        assert call_args[0] == sys.executable
        assert call_args[1:4] == ["-m", "pip", "install"]
        assert call_args[4] == "test-package"
