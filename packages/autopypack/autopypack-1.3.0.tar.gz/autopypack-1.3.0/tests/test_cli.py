"""Tests for the CLI module of AutoPyPack."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from AutoPyPack.autopypack.cli import (
    STDLIB_MODULES,
    collect_all_imports,
    find_python_files,
    is_local_module,
    is_stdlib_module,
    list_project_modules,
    main,
)


class TestFindPythonFiles:
    """Tests for the find_python_files function."""

    def test_find_python_files_in_empty_dir(self) -> None:
        """Test finding Python files in an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = find_python_files(tmpdir)
            assert files == []

    def test_find_python_files_single_file(self) -> None:
        """Test finding a single Python file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text("# test")

            files = find_python_files(tmpdir)
            assert len(files) == 1
            assert files[0].endswith("test.py")

    def test_find_python_files_nested(self) -> None:
        """Test finding Python files in nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()

            (Path(tmpdir) / "root.py").write_text("# root")
            (subdir / "nested.py").write_text("# nested")
            (Path(tmpdir) / "not_python.txt").write_text("not python")

            files = find_python_files(tmpdir)
            assert len(files) == 2
            assert any(f.endswith("root.py") for f in files)
            assert any(f.endswith("nested.py") for f in files)


class TestIsStdlibModule:
    """Tests for the is_stdlib_module function."""

    def test_common_stdlib_modules(self) -> None:
        """Test that common stdlib modules are detected."""
        stdlib_names = [
            "os", "sys", "json", "pathlib", "collections",
            "typing", "argparse", "logging", "unittest",
        ]
        for name in stdlib_names:
            assert is_stdlib_module(name) is True, f"{name} should be stdlib"

    def test_third_party_modules(self) -> None:
        """Test that third-party modules are not detected as stdlib."""
        third_party = ["numpy", "pandas", "requests", "flask", "django"]
        for name in third_party:
            assert is_stdlib_module(name) is False, f"{name} should not be stdlib"

    def test_builtin_modules(self) -> None:
        """Test that builtin modules are detected."""
        import sys

        for name in list(sys.builtin_module_names)[:5]:
            assert is_stdlib_module(name) is True, f"{name} should be stdlib (builtin)"

    def test_stdlib_modules_set_is_comprehensive(self) -> None:
        """Test that STDLIB_MODULES contains essential modules."""
        essential = {"os", "sys", "json", "re", "math", "datetime", "pathlib"}
        assert essential.issubset(STDLIB_MODULES)


class TestIsLocalModule:
    """Tests for the is_local_module function."""

    def test_local_py_file(self) -> None:
        """Test detecting a local .py file as a local module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "mymodule.py").write_text("# local module")

            assert is_local_module("mymodule", tmpdir) is True
            assert is_local_module("nonexistent", tmpdir) is False

    def test_local_package(self) -> None:
        """Test detecting a local package as a local module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_dir = Path(tmpdir) / "mypackage"
            pkg_dir.mkdir()
            (pkg_dir / "__init__.py").write_text("# package init")

            assert is_local_module("mypackage", tmpdir) is True

    def test_local_package_without_init(self) -> None:
        """Test detecting a directory with Python files but no __init__.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_dir = Path(tmpdir) / "mypackage"
            pkg_dir.mkdir()
            (pkg_dir / "module.py").write_text("# module")

            assert is_local_module("mypackage", tmpdir) is True


class TestCollectAllImports:
    """Tests for the collect_all_imports function."""

    def test_collect_imports_from_multiple_files(self) -> None:
        """Test collecting imports from multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file1.py").write_text("import os\nimport json\n")
            (Path(tmpdir) / "file2.py").write_text("import sys\nimport os\n")

            imports = collect_all_imports(tmpdir, quiet=True)

            assert "os" in imports
            assert "sys" in imports
            assert "json" in imports

    def test_collect_imports_empty_directory(self) -> None:
        """Test collecting imports from an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            imports = collect_all_imports(tmpdir, quiet=True)
            assert imports == set()


class TestListProjectModules:
    """Tests for the list_project_modules function."""

    def test_list_excludes_stdlib(self) -> None:
        """Test that stdlib modules are excluded from the list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text(
                "import os\nimport sys\nimport json\n"
            )

            packages = list_project_modules(tmpdir, quiet=True)

            # All imports are stdlib, so the list should be empty
            assert packages == []

    @mock.patch("AutoPyPack.autopypack.cli.is_module_available")
    def test_list_includes_third_party(
        self, mock_is_available: mock.Mock
    ) -> None:
        """Test that third-party modules are included in the list."""
        # Simulate that numpy and pandas are not installed
        mock_is_available.return_value = False

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text(
                "import numpy\nimport pandas\n"
            )

            packages = list_project_modules(tmpdir, quiet=True)

            assert "numpy" in packages
            assert "pandas" in packages


class TestMain:
    """Tests for the main CLI function."""

    def test_main_no_args_shows_help(self, capsys: pytest.CaptureFixture) -> None:
        """Test that running with no args shows help."""
        main([])

        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower() or "autopypack" in captured.out.lower()

    def test_main_list_command(self, capsys: pytest.CaptureFixture) -> None:
        """Test the list command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("import os\n")

            main(["list", "--dir", tmpdir])

            captured = capsys.readouterr()
            assert "AutoPyPack" in captured.out or "Scanning" in captured.out

    def test_main_install_command_no_missing(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test the install command when no packages are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Only stdlib imports, nothing to install
            (Path(tmpdir) / "test.py").write_text("import os\nimport sys\n")

            main(["install", "--dir", tmpdir])

            captured = capsys.readouterr()
            # Should indicate all packages are installed or no external packages
            assert "AutoPyPack" in captured.out

    def test_main_quiet_mode(self, capsys: pytest.CaptureFixture) -> None:
        """Test quiet mode suppresses output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("import os\n")

            main(["list", "--dir", tmpdir, "--quiet"])

            captured = capsys.readouterr()
            # In quiet mode with only stdlib imports, there should be minimal output
            # (no packages to list)
            assert "[AutoPyPack]" not in captured.out or captured.out.strip() == ""
