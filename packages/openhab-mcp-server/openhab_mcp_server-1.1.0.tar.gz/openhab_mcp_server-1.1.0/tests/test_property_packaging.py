"""
Property-based tests for packaging functionality.

**Feature: openhab-mcp-server, Property 20: Package installation completeness**
**Validates: Requirements 9.2, 9.5**

**Feature: openhab-mcp-server, Property 21: Package metadata accuracy**
**Validates: Requirements 9.3**

**Feature: openhab-mcp-server, Property 22: Distribution file completeness**
**Validates: Requirements 9.4**
"""

import subprocess
import sys
import tempfile
import venv
import zipfile
import tarfile
from pathlib import Path
from typing import List, Dict, Any, Set
import importlib.metadata
import tomllib

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck


class TestPackageInstallationProperties:
    """Property-based tests for package installation completeness."""

    def test_package_installation_completeness_property(self):
        """
        **Feature: openhab-mcp-server, Property 20: Package installation completeness**
        **Validates: Requirements 9.2, 9.5**
        
        For any pip installation of the package, all required modules should be 
        importable and the command-line entry point should be executable.
        """
        # This is a concrete test since we need to test actual installation
        # Property: Package installation should make all modules importable
        
        # Check if wheel file exists
        dist_dir = Path("dist")
        wheel_files = list(dist_dir.glob("*.whl")) if dist_dir.exists() else []
        
        if not wheel_files:
            pytest.skip("No wheel file found. Run build script first.")
        
        wheel_file = wheel_files[0]
        
        # Test installation in temporary virtual environment
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            venv_path = temp_path / "test_venv"
            
            # Create virtual environment
            venv.create(venv_path, with_pip=True)
            
            # Determine python executable path
            if sys.platform == "win32":
                python_exe = venv_path / "Scripts" / "python.exe"
            else:
                python_exe = venv_path / "bin" / "python"
            
            # Install the package
            install_result = subprocess.run([
                str(python_exe), "-m", "pip", "install", str(wheel_file.absolute())
            ], capture_output=True, text=True)
            
            assert install_result.returncode == 0, f"Installation failed: {install_result.stderr}"
            
            # Property: All required modules should be importable
            required_modules = [
                "openhab_mcp_server",
                "openhab_mcp_server.server",
                "openhab_mcp_server.cli",
                "openhab_mcp_server.models",
                "openhab_mcp_server.tools",
                "openhab_mcp_server.resources",
                "openhab_mcp_server.utils"
            ]
            
            for module in required_modules:
                import_result = subprocess.run([
                    str(python_exe), "-c", f"import {module}; print('OK')"
                ], capture_output=True, text=True)
                
                assert import_result.returncode == 0, f"Module {module} not importable: {import_result.stderr}"
                assert "OK" in import_result.stdout, f"Module {module} import failed silently"
            
            # Property: CLI entry point should be executable
            cli_help_result = subprocess.run([
                str(python_exe), "-m", "openhab_mcp_server.cli", "--help"
            ], capture_output=True, text=True)
            
            assert cli_help_result.returncode == 0, f"CLI entry point failed: {cli_help_result.stderr}"
            assert "usage:" in cli_help_result.stdout.lower(), "CLI help output malformed"
            
            # Property: MCP server entry point should be accessible
            server_import_result = subprocess.run([
                str(python_exe), "-c", 
                "from openhab_mcp_server.server import main; print('Server entry point OK')"
            ], capture_output=True, text=True)
            
            assert server_import_result.returncode == 0, f"Server entry point not accessible: {server_import_result.stderr}"
            assert "Server entry point OK" in server_import_result.stdout

    @given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5))
    @settings(max_examples=10, deadline=60000)  # Longer deadline for installation tests
    def test_module_import_consistency_property(self, module_suffixes: List[str]):
        """
        Property: Module import paths should be consistent and predictable.
        
        For any valid module suffix, attempting to import non-existent modules
        should fail predictably, while valid modules should import successfully.
        """
        # Check if package is installed in current environment
        try:
            import openhab_mcp_server
        except ImportError:
            pytest.skip("Package not installed in current environment")
        
        # Test that valid base modules import successfully
        valid_modules = [
            "openhab_mcp_server",
            "openhab_mcp_server.server", 
            "openhab_mcp_server.cli"
        ]
        
        for module in valid_modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Valid module {module} should be importable: {e}")
        
        # Test that invalid module combinations fail predictably
        for suffix in module_suffixes:
            # Create potentially invalid module name
            invalid_module = f"openhab_mcp_server.{suffix}"
            
            # Skip if this happens to be a valid module
            if invalid_module in [
                "openhab_mcp_server.server",
                "openhab_mcp_server.cli", 
                "openhab_mcp_server.models",
                "openhab_mcp_server.tools",
                "openhab_mcp_server.resources", 
                "openhab_mcp_server.utils"
            ]:
                continue
            
            # Invalid modules should raise ImportError
            with pytest.raises(ImportError):
                __import__(invalid_module)

    def test_entry_point_consistency_property(self):
        """
        Property: Entry points should be consistently accessible.
        
        All defined entry points should be accessible and functional.
        """
        # Check if package is installed
        try:
            import openhab_mcp_server
        except ImportError:
            pytest.skip("Package not installed in current environment")
        
        # Test CLI entry point consistency
        cli_result = subprocess.run([
            sys.executable, "-m", "openhab_mcp_server.cli", "--help"
        ], capture_output=True, text=True)
        
        # Property: CLI should always provide help and return success
        assert cli_result.returncode == 0, "CLI entry point should return success for --help"
        assert "usage:" in cli_result.stdout.lower(), "CLI should provide usage information"
        
        # Test server entry point accessibility
        try:
            from openhab_mcp_server.server import main
            # Property: Server main function should be callable
            assert callable(main), "Server main should be a callable function"
        except ImportError as e:
            pytest.fail(f"Server entry point should be importable: {e}")


class TestPackageMetadataProperties:
    """Property-based tests for package metadata accuracy."""

    def test_package_metadata_accuracy_property(self):
        """
        **Feature: openhab-mcp-server, Property 21: Package metadata accuracy**
        **Validates: Requirements 9.3**
        
        For any package metadata query, the returned information should include 
        complete project details including version, description, and dependencies.
        """
        # Load expected metadata from pyproject.toml
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            pytest.skip("pyproject.toml not found")
        
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        
        expected_project = pyproject_data.get("project", {})
        
        # Check if package is installed
        try:
            metadata = importlib.metadata.metadata("openhab-mcp-server")
        except importlib.metadata.PackageNotFoundError:
            pytest.skip("Package not installed in current environment")
        
        # Property: Package name should match pyproject.toml
        assert metadata["Name"] == expected_project.get("name", "openhab-mcp-server")
        
        # Property: Version should be present and match
        assert "Version" in metadata
        expected_version = expected_project.get("version")
        if expected_version:
            assert metadata["Version"] == expected_version
        
        # Property: Description should be present and match
        assert "Summary" in metadata
        expected_description = expected_project.get("description")
        if expected_description:
            assert metadata["Summary"] == expected_description
        
        # Property: Author information should be present
        expected_authors = expected_project.get("authors", [])
        if expected_authors:
            # At least one author should be present in metadata (either Author or Author-email)
            author_found = False
            for author in expected_authors:
                author_name = author.get("name", "")
                author_email = author.get("email", "")
                
                # Check both Author and Author-email fields
                if author_name and (
                    author_name in metadata.get("Author", "") or 
                    author_name in metadata.get("Author-email", "")
                ):
                    author_found = True
                    break
                elif author_email and author_email in metadata.get("Author-email", ""):
                    author_found = True
                    break
            assert author_found, "Author information should be present in metadata"
        
        # Property: License should be present
        expected_license = expected_project.get("license", {}).get("text")
        if expected_license:
            assert "License" in metadata
            # License might be in different formats, check if it contains expected text
            assert expected_license.lower() in metadata["License"].lower()
        
        # Property: Keywords should be present
        expected_keywords = expected_project.get("keywords", [])
        if expected_keywords:
            metadata_keywords = metadata.get("Keywords", "").lower()
            # At least some keywords should be present
            keywords_found = any(keyword.lower() in metadata_keywords for keyword in expected_keywords)
            assert keywords_found, "Some keywords should be present in metadata"
        
        # Property: Classifiers should be present
        expected_classifiers = expected_project.get("classifiers", [])
        if expected_classifiers:
            metadata_classifiers = metadata.get_all("Classifier") or []
            # At least some classifiers should match
            classifiers_found = any(classifier in metadata_classifiers for classifier in expected_classifiers)
            assert classifiers_found, "Some classifiers should be present in metadata"

    @given(st.lists(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8), min_size=1, max_size=2))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
    def test_metadata_field_consistency_property(self, field_names: List[str]):
        """
        Property: Metadata fields should be consistently accessible.
        
        For any valid metadata field access, the result should be predictable.
        """
        try:
            metadata = importlib.metadata.metadata("openhab-mcp-server")
        except importlib.metadata.PackageNotFoundError:
            pytest.skip("Package not installed in current environment")
        
        # Property: Standard metadata fields should always be accessible
        standard_fields = ["Name", "Version", "Summary"]
        
        for field in standard_fields:
            # Standard fields should always be present
            assert field in metadata, f"Standard field {field} should be present"
            # And should have non-empty values
            assert metadata[field].strip(), f"Standard field {field} should have non-empty value"
        
        # Property: Non-existent fields should behave consistently
        for field_name in field_names:
            # Create a field name that's unlikely to exist
            fake_field = f"NonExistent{field_name.title()}"
            
            # Accessing non-existent fields should either return None or raise KeyError
            try:
                value = metadata.get(fake_field)
                # If get() succeeds, it should return None for non-existent fields
                assert value is None, f"Non-existent field {fake_field} should return None"
            except KeyError:
                # KeyError is also acceptable for non-existent fields
                pass

    def test_dependency_metadata_property(self):
        """
        Property: Dependency metadata should be complete and accurate.
        
        All declared dependencies should be present in package metadata.
        """
        # Load expected dependencies from pyproject.toml
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            pytest.skip("pyproject.toml not found")
        
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        
        expected_deps = pyproject_data.get("project", {}).get("dependencies", [])
        
        try:
            metadata = importlib.metadata.metadata("openhab-mcp-server")
        except importlib.metadata.PackageNotFoundError:
            pytest.skip("Package not installed in current environment")
        
        # Get actual dependencies from metadata
        requires_dist = metadata.get_all("Requires-Dist") or []
        
        # Property: All core dependencies should be present in metadata
        for expected_dep in expected_deps:
            # Extract package name from dependency specification (e.g., "mcp>=1.0.0" -> "mcp")
            dep_name = expected_dep.split(">=")[0].split("==")[0].split("<")[0].split(">")[0].strip()
            
            # Check if this dependency is present in requires_dist
            dep_found = any(dep_name.lower() in req.lower() for req in requires_dist)
            assert dep_found, f"Dependency {dep_name} should be present in package metadata"

    def test_entry_points_metadata_property(self):
        """
        Property: Entry points should be correctly defined in metadata.
        
        All entry points should be accessible through metadata.
        """
        try:
            # Get entry points from metadata
            entry_points = importlib.metadata.entry_points()
        except importlib.metadata.PackageNotFoundError:
            pytest.skip("Package not installed in current environment")
        
        # Property: Console scripts entry point should be present
        console_scripts = entry_points.select(group="console_scripts")
        openhab_scripts = [ep for ep in console_scripts if ep.name == "openhab-mcp-server"]
        
        assert len(openhab_scripts) > 0, "openhab-mcp-server console script should be defined"
        
        # Property: Entry point should point to correct module
        script_ep = openhab_scripts[0]
        assert "openhab_mcp_server.cli" in script_ep.value, "Console script should point to CLI module"
        
        # Property: MCP servers entry point should be present if defined
        mcp_servers = entry_points.select(group="mcp.servers")
        openhab_mcp_servers = [ep for ep in mcp_servers if ep.name == "openhab"]
        
        if openhab_mcp_servers:
            # If MCP server entry point is defined, it should point to correct module
            mcp_ep = openhab_mcp_servers[0]
            assert "openhab_mcp_server.server" in mcp_ep.value, "MCP server entry point should point to server module"


class TestDistributionCompletenessProperties:
    """Property-based tests for distribution file completeness."""

    def test_distribution_file_completeness_property(self):
        """
        **Feature: openhab-mcp-server, Property 22: Distribution file completeness**
        **Validates: Requirements 9.4**
        
        For any built package distribution, all necessary runtime files should be 
        included while development-only files are excluded.
        """
        # Check if distribution files exist
        dist_dir = Path("dist")
        if not dist_dir.exists():
            pytest.skip("No dist/ directory found. Run build script first.")
        
        wheel_files = list(dist_dir.glob("*.whl"))
        sdist_files = list(dist_dir.glob("*.tar.gz"))
        
        if not wheel_files and not sdist_files:
            pytest.skip("No distribution files found. Run build script first.")
        
        # Test wheel distribution if available
        if wheel_files:
            self._test_wheel_completeness(wheel_files[0])
        
        # Test source distribution if available
        if sdist_files:
            self._test_sdist_completeness(sdist_files[0])

    def _test_wheel_completeness(self, wheel_path: Path):
        """Test wheel distribution completeness."""
        with zipfile.ZipFile(wheel_path, 'r') as wheel:
            file_list = wheel.namelist()
            file_set = set(file_list)
            
            # Property: All necessary runtime files should be included
            required_files = [
                "openhab_mcp_server/__init__.py",
                "openhab_mcp_server/server.py",
                "openhab_mcp_server/cli.py",
                "openhab_mcp_server/models.py",
            ]
            
            for required_file in required_files:
                assert any(required_file in f for f in file_list), f"Required file {required_file} should be in wheel"
            
            # Property: Package directories should be included
            required_dirs = [
                "openhab_mcp_server/tools/",
                "openhab_mcp_server/resources/",
                "openhab_mcp_server/utils/"
            ]
            
            for required_dir in required_dirs:
                assert any(f.startswith(required_dir) for f in file_list), f"Required directory {required_dir} should be in wheel"
            
            # Property: Development-only files should be excluded
            excluded_patterns = [
                "__pycache__",
                ".hypothesis",
                ".pytest_cache",
                "tests/",
                ".git",
                ".mypy_cache"
            ]
            
            for pattern in excluded_patterns:
                assert not any(pattern in f for f in file_list), f"Development file pattern {pattern} should not be in wheel"
            
            # Property: Metadata files should be present
            metadata_files = [f for f in file_list if f.endswith(".dist-info/METADATA")]
            assert len(metadata_files) > 0, "METADATA file should be present in wheel"
            
            # Property: Entry points should be defined
            entry_points_files = [f for f in file_list if f.endswith(".dist-info/entry_points.txt")]
            assert len(entry_points_files) > 0, "entry_points.txt should be present in wheel"

    def _test_sdist_completeness(self, sdist_path: Path):
        """Test source distribution completeness."""
        with tarfile.open(sdist_path, 'r:gz') as sdist:
            file_list = sdist.getnames()
            file_set = set(file_list)
            
            # Property: Source files should be included
            required_source_patterns = [
                "src/openhab_mcp_server/",
                "pyproject.toml",
                "README.md"
            ]
            
            for pattern in required_source_patterns:
                assert any(pattern in f for f in file_list), f"Required source pattern {pattern} should be in sdist"
            
            # Property: Core project files should be included
            # Note: requirements.txt may not be included if dependencies are in pyproject.toml
            
            # Property: Test files should be included in source distribution
            test_files = [f for f in file_list if "tests/" in f and f.endswith(".py")]
            assert len(test_files) > 0, "Test files should be included in source distribution"
            
            # Property: Development artifacts should be excluded
            excluded_patterns = [
                "__pycache__",
                ".hypothesis/",
                ".pytest_cache/",
                "dist/",
                "build/",
                ".git/",
                ".mypy_cache/"
            ]
            
            for pattern in excluded_patterns:
                assert not any(pattern in f for f in file_list), f"Development artifact {pattern} should not be in sdist"
            
            # Property: MANIFEST.in should be respected
            manifest_path = Path("MANIFEST.in")
            if manifest_path.exists():
                # Check that MANIFEST.in rules are followed
                # This is a basic check - a full implementation would parse MANIFEST.in
                
                # License should be included if it exists
                license_files = [f for f in file_list if "LICENSE" in f.upper()]
                if Path("LICENSE").exists():
                    assert len(license_files) > 0, "LICENSE file should be included when it exists"

    @given(st.lists(st.sampled_from([".py", ".txt", ".md", ".toml", ".json"]), min_size=1, max_size=2))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.too_slow])
    def test_file_extension_consistency_property(self, extensions: List[str]):
        """
        Property: Distribution should include files with expected extensions.
        
        For any common file extension, the distribution should handle it appropriately.
        """
        dist_dir = Path("dist")
        if not dist_dir.exists():
            pytest.skip("No dist/ directory found")
        
        wheel_files = list(dist_dir.glob("*.whl"))
        if not wheel_files:
            pytest.skip("No wheel files found")
        
        wheel_path = wheel_files[0]
        
        with zipfile.ZipFile(wheel_path, 'r') as wheel:
            file_list = wheel.namelist()
            
            # Property: Python files should be present
            python_files = [f for f in file_list if f.endswith(".py")]
            assert len(python_files) > 0, "Python files should be present in distribution"
            
            # Property: No temporary or cache files should be included
            temp_extensions = [".pyc", ".pyo", ".pyd", ".swp", ".tmp"]
            for ext in temp_extensions:
                temp_files = [f for f in file_list if f.endswith(ext)]
                assert len(temp_files) == 0, f"Temporary files with extension {ext} should not be in distribution"

    def test_distribution_size_property(self):
        """
        Property: Distribution files should have reasonable sizes.
        
        Distribution files should not be empty and should not be excessively large.
        """
        dist_dir = Path("dist")
        if not dist_dir.exists():
            pytest.skip("No dist/ directory found")
        
        distribution_files = list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))
        if not distribution_files:
            pytest.skip("No distribution files found")
        
        for dist_file in distribution_files:
            file_size = dist_file.stat().st_size
            
            # Property: Distribution files should not be empty
            assert file_size > 0, f"Distribution file {dist_file.name} should not be empty"
            
            # Property: Distribution files should not be excessively large (> 100MB is suspicious)
            max_size = 100 * 1024 * 1024  # 100MB
            assert file_size < max_size, f"Distribution file {dist_file.name} is suspiciously large ({file_size} bytes)"
            
            # Property: Wheel files should be smaller than source distributions (generally)
            if dist_file.suffix == ".whl":
                # Wheels should be reasonably sized (not empty, not huge)
                min_wheel_size = 1024  # 1KB minimum
                max_wheel_size = 10 * 1024 * 1024  # 10MB maximum for this project
                assert min_wheel_size <= file_size <= max_wheel_size, f"Wheel file size {file_size} is outside expected range"

    def test_distribution_integrity_property(self):
        """
        Property: Distribution files should be valid and not corrupted.
        
        All distribution files should be readable and have valid structure.
        """
        dist_dir = Path("dist")
        if not dist_dir.exists():
            pytest.skip("No dist/ directory found")
        
        wheel_files = list(dist_dir.glob("*.whl"))
        sdist_files = list(dist_dir.glob("*.tar.gz"))
        
        # Property: Wheel files should be valid ZIP archives
        for wheel_file in wheel_files:
            try:
                with zipfile.ZipFile(wheel_file, 'r') as wheel:
                    # Test that we can read the file list
                    file_list = wheel.namelist()
                    assert len(file_list) > 0, f"Wheel {wheel_file.name} should contain files"
                    
                    # Test that we can read a sample file
                    python_files = [f for f in file_list if f.endswith(".py") and not f.endswith("/__init__.py")]
                    if python_files:
                        sample_file = python_files[0]
                        content = wheel.read(sample_file)
                        assert len(content) > 0, f"Sample file {sample_file} should have content"
            except (zipfile.BadZipFile, zipfile.LargeZipFile) as e:
                pytest.fail(f"Wheel file {wheel_file.name} is corrupted: {e}")
        
        # Property: Source distributions should be valid tar.gz archives
        for sdist_file in sdist_files:
            try:
                with tarfile.open(sdist_file, 'r:gz') as sdist:
                    # Test that we can read the file list
                    file_list = sdist.getnames()
                    assert len(file_list) > 0, f"Source distribution {sdist_file.name} should contain files"
                    
                    # Test that pyproject.toml is readable
                    pyproject_files = [f for f in file_list if f.endswith("pyproject.toml")]
                    if pyproject_files:
                        pyproject_file = pyproject_files[0]
                        member = sdist.getmember(pyproject_file)
                        content = sdist.extractfile(member).read()
                        assert len(content) > 0, f"pyproject.toml should have content"
            except (tarfile.TarError, tarfile.ReadError) as e:
                pytest.fail(f"Source distribution {sdist_file.name} is corrupted: {e}")