"""
Unit tests for packaging functionality.

Tests CLI entry point functionality, package importability after installation,
and distribution file contents.

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""

import subprocess
import sys
import tempfile
import venv
import zipfile
import tarfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import importlib.util

import pytest


class TestCLIEntryPoint:
    """Unit tests for CLI entry point functionality."""

    def test_cli_module_importable(self):
        """Test that CLI module can be imported."""
        try:
            from openhab_mcp_server.cli import main
            assert callable(main), "CLI main function should be callable"
        except ImportError as e:
            pytest.fail(f"CLI module should be importable: {e}")

    def test_cli_help_command(self):
        """Test CLI help command functionality."""
        result = subprocess.run([
            sys.executable, "-m", "openhab_mcp_server.cli", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, "CLI help should return success"
        assert "usage:" in result.stdout.lower(), "Help should show usage information"
        assert "openhab-mcp-server" in result.stdout.lower(), "Help should mention the program name"

    def test_cli_version_handling(self):
        """Test CLI version information."""
        # Test that CLI doesn't crash with common version flags
        version_flags = ["--version", "-V"]
        
        for flag in version_flags:
            result = subprocess.run([
                sys.executable, "-m", "openhab_mcp_server.cli", flag
            ], capture_output=True, text=True)
            
            # Either succeeds with version info or fails gracefully
            if result.returncode == 0:
                # If version flag is supported, output should contain version info
                assert len(result.stdout.strip()) > 0, f"Version output should not be empty for {flag}"
            else:
                # If not supported, should show help or error message
                assert len(result.stderr.strip()) > 0 or len(result.stdout.strip()) > 0, f"Should provide feedback for {flag}"

    @patch('openhab_mcp_server.cli.asyncio.run')
    def test_cli_main_function_structure(self, mock_asyncio_run):
        """Test CLI main function structure without actually running server."""
        from openhab_mcp_server.cli import main
        
        # Mock sys.argv to provide test arguments
        test_args = ["openhab-mcp-server", "--help"]
        
        with patch('sys.argv', test_args):
            try:
                # This should not crash, even if it exits early due to --help
                main()
            except SystemExit:
                # SystemExit is expected for --help
                pass
            except Exception as e:
                # Other exceptions indicate structural problems
                pytest.fail(f"CLI main function has structural issues: {e}")


class TestPackageImportability:
    """Unit tests for package importability after installation."""

    def test_main_package_import(self):
        """Test that main package can be imported."""
        try:
            import openhab_mcp_server
            assert hasattr(openhab_mcp_server, '__version__'), "Package should have version attribute"
        except ImportError as e:
            pytest.fail(f"Main package should be importable: {e}")

    def test_submodule_imports(self):
        """Test that all main submodules can be imported."""
        submodules = [
            "openhab_mcp_server.server",
            "openhab_mcp_server.cli", 
            "openhab_mcp_server.models",
            "openhab_mcp_server.tools",
            "openhab_mcp_server.resources",
            "openhab_mcp_server.utils"
        ]
        
        for module_name in submodules:
            try:
                module = __import__(module_name, fromlist=[''])
                assert module is not None, f"Module {module_name} should not be None"
            except ImportError as e:
                pytest.fail(f"Submodule {module_name} should be importable: {e}")

    def test_package_structure_consistency(self):
        """Test that package structure is consistent."""
        import openhab_mcp_server
        
        # Check that package has expected attributes
        expected_attributes = ['__version__', '__name__']
        for attr in expected_attributes:
            assert hasattr(openhab_mcp_server, attr), f"Package should have {attr} attribute"
        
        # Check that version is a string
        assert isinstance(openhab_mcp_server.__version__, str), "Version should be a string"
        assert len(openhab_mcp_server.__version__) > 0, "Version should not be empty"

    def test_entry_points_accessibility(self):
        """Test that entry points are accessible."""
        # Test server entry point
        try:
            from openhab_mcp_server.server import main as server_main
            assert callable(server_main), "Server main should be callable"
        except ImportError as e:
            pytest.fail(f"Server entry point should be accessible: {e}")
        
        # Test CLI entry point
        try:
            from openhab_mcp_server.cli import main as cli_main
            assert callable(cli_main), "CLI main should be callable"
        except ImportError as e:
            pytest.fail(f"CLI entry point should be accessible: {e}")


class TestDistributionFileContents:
    """Unit tests for distribution file contents."""

    def test_wheel_file_structure(self):
        """Test wheel file structure and contents."""
        dist_dir = Path("dist")
        if not dist_dir.exists():
            pytest.skip("No dist/ directory found")
        
        wheel_files = list(dist_dir.glob("*.whl"))
        if not wheel_files:
            pytest.skip("No wheel files found")
        
        wheel_path = wheel_files[0]
        
        with zipfile.ZipFile(wheel_path, 'r') as wheel:
            file_list = wheel.namelist()
            
            # Test that essential files are present
            essential_files = [
                "openhab_mcp_server/__init__.py",
                "openhab_mcp_server/server.py",
                "openhab_mcp_server/cli.py"
            ]
            
            for essential_file in essential_files:
                assert any(essential_file in f for f in file_list), f"Essential file {essential_file} should be in wheel"
            
            # Test that metadata is present
            metadata_files = [f for f in file_list if f.endswith(".dist-info/METADATA")]
            assert len(metadata_files) == 1, "Exactly one METADATA file should be present"
            
            # Test metadata content
            metadata_content = wheel.read(metadata_files[0]).decode('utf-8')
            assert "Name: openhab-mcp-server" in metadata_content, "Metadata should contain package name"
            assert "Version:" in metadata_content, "Metadata should contain version"

    def test_source_distribution_structure(self):
        """Test source distribution structure and contents."""
        dist_dir = Path("dist")
        if not dist_dir.exists():
            pytest.skip("No dist/ directory found")
        
        sdist_files = list(dist_dir.glob("*.tar.gz"))
        if not sdist_files:
            pytest.skip("No source distribution files found")
        
        sdist_path = sdist_files[0]
        
        with tarfile.open(sdist_path, 'r:gz') as sdist:
            file_list = sdist.getnames()
            
            # Test that source files are present
            source_patterns = [
                "pyproject.toml",
                "README.md",
                "src/openhab_mcp_server/"
            ]
            
            for pattern in source_patterns:
                assert any(pattern in f for f in file_list), f"Source pattern {pattern} should be in sdist"
            
            # Test that PKG-INFO is present
            pkg_info_files = [f for f in file_list if f.endswith("PKG-INFO")]
            assert len(pkg_info_files) >= 1, "PKG-INFO should be present in source distribution"

    def test_distribution_file_sizes(self):
        """Test that distribution files have reasonable sizes."""
        dist_dir = Path("dist")
        if not dist_dir.exists():
            pytest.skip("No dist/ directory found")
        
        distribution_files = list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))
        if not distribution_files:
            pytest.skip("No distribution files found")
        
        for dist_file in distribution_files:
            file_size = dist_file.stat().st_size
            
            # Files should not be empty
            assert file_size > 0, f"Distribution file {dist_file.name} should not be empty"
            
            # Files should not be suspiciously large (> 50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            assert file_size < max_size, f"Distribution file {dist_file.name} is suspiciously large"
            
            # Files should have minimum reasonable size (> 1KB)
            min_size = 1024  # 1KB
            assert file_size > min_size, f"Distribution file {dist_file.name} is suspiciously small"

    def test_no_development_files_in_distribution(self):
        """Test that development files are excluded from distributions."""
        dist_dir = Path("dist")
        if not dist_dir.exists():
            pytest.skip("No dist/ directory found")
        
        wheel_files = list(dist_dir.glob("*.whl"))
        
        for wheel_file in wheel_files:
            with zipfile.ZipFile(wheel_file, 'r') as wheel:
                file_list = wheel.namelist()
                
                # Development patterns that should not be present
                dev_patterns = [
                    "__pycache__",
                    ".pytest_cache",
                    ".hypothesis",
                    "tests/",
                    ".git",
                    ".mypy_cache",
                    ".pyc",
                    ".pyo"
                ]
                
                for pattern in dev_patterns:
                    dev_files = [f for f in file_list if pattern in f]
                    assert len(dev_files) == 0, f"Development files with pattern {pattern} should not be in wheel"


class TestBuildScripts:
    """Unit tests for build and installation scripts."""

    def test_build_script_exists(self):
        """Test that build script exists and is readable."""
        build_script = Path("scripts/build.py")
        assert build_script.exists(), "Build script should exist"
        assert build_script.is_file(), "Build script should be a file"
        
        # Test that script is valid Python
        with open(build_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic syntax check
        try:
            compile(content, str(build_script), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Build script has syntax errors: {e}")

    def test_install_verify_script_exists(self):
        """Test that installation verification script exists."""
        verify_script = Path("scripts/install_verify.py")
        assert verify_script.exists(), "Installation verification script should exist"
        assert verify_script.is_file(), "Installation verification script should be a file"
        
        # Test that script is valid Python
        with open(verify_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            compile(content, str(verify_script), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Installation verification script has syntax errors: {e}")

    def test_dev_install_script_exists(self):
        """Test that development installation script exists."""
        dev_script = Path("scripts/dev_install.py")
        assert dev_script.exists(), "Development installation script should exist"
        assert dev_script.is_file(), "Development installation script should be a file"
        
        # Test that script is valid Python
        with open(dev_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            compile(content, str(dev_script), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Development installation script has syntax errors: {e}")

    def test_scripts_have_main_functions(self):
        """Test that scripts have main functions."""
        scripts = [
            "scripts/build.py",
            "scripts/install_verify.py", 
            "scripts/dev_install.py"
        ]
        
        for script_path in scripts:
            script = Path(script_path)
            if not script.exists():
                continue
            
            with open(script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for main function definition
            assert "def main(" in content, f"Script {script_path} should have a main function"
            
            # Check for main execution guard
            assert 'if __name__ == "__main__":' in content, f"Script {script_path} should have main execution guard"


class TestManifestFile:
    """Unit tests for MANIFEST.in file."""

    def test_manifest_file_exists(self):
        """Test that MANIFEST.in file exists."""
        manifest_file = Path("MANIFEST.in")
        assert manifest_file.exists(), "MANIFEST.in should exist"
        assert manifest_file.is_file(), "MANIFEST.in should be a file"

    def test_manifest_file_content(self):
        """Test MANIFEST.in file content."""
        manifest_file = Path("MANIFEST.in")
        if not manifest_file.exists():
            pytest.skip("MANIFEST.in not found")
        
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for essential include directives
        essential_includes = [
            "include README.md",
            "include pyproject.toml",
            "recursive-include src *.py"
        ]
        
        for include_directive in essential_includes:
            assert include_directive in content, f"MANIFEST.in should contain: {include_directive}"
        
        # Check for essential exclude directives
        essential_excludes = [
            "prune __pycache__",
            "prune .hypothesis",
            "prune .pytest_cache"
        ]
        
        for exclude_directive in essential_excludes:
            assert exclude_directive in content, f"MANIFEST.in should contain: {exclude_directive}"

    def test_manifest_syntax(self):
        """Test MANIFEST.in syntax validity."""
        manifest_file = Path("MANIFEST.in")
        if not manifest_file.exists():
            pytest.skip("MANIFEST.in not found")
        
        with open(manifest_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        valid_commands = [
            'include', 'exclude', 'recursive-include', 'recursive-exclude',
            'global-include', 'global-exclude', 'prune', 'graft'
        ]
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check that line starts with valid command
            first_word = line.split()[0]
            assert first_word in valid_commands, f"Line {line_num}: '{first_word}' is not a valid MANIFEST.in command"