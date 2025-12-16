#!/usr/bin/env python3
"""
Tests for Dependency Auditor Plugin
"""

import pytest
from pathlib import Path
import tempfile
import json

from lmapp.plugins.example_dependency_auditor import (
    DependencyAuditorPlugin,
    DependencyVulnerability,
    DependencyLicense,
    AuditResult,
)


class TestDependencyVulnerability:
    """Test vulnerability data class"""

    def test_vulnerability_creation(self):
        """Test vulnerability can be created"""
        vuln = DependencyVulnerability(
            package="requests",
            version="2.28.0",
            vulnerability_id="CVE-2023-XXXX",
            severity="high",
            description="Connection pooling issue",
            fix_version="2.31.0",
        )
        assert vuln.package == "requests"
        assert vuln.severity == "high"
        assert vuln.fix_version == "2.31.0"

    def test_vulnerability_without_fix(self):
        """Test vulnerability without fix version"""
        vuln = DependencyVulnerability(
            package="package",
            version="1.0.0",
            vulnerability_id="CVE-2024-XXXX",
            severity="critical",
            description="Test vulnerability",
        )
        assert vuln.fix_version is None


class TestDependencyLicense:
    """Test license data class"""

    def test_license_creation(self):
        """Test license can be created"""
        lic = DependencyLicense(
            package="requests",
            version="2.31.0",
            license="Apache-2.0",
            is_permissive=True,
        )
        assert lic.package == "requests"
        assert lic.is_permissive is True

    def test_restrictive_license(self):
        """Test restrictive license marking"""
        lic = DependencyLicense(
            package="package",
            version="1.0.0",
            license="GPL-3.0",
            is_permissive=False,
        )
        assert lic.is_permissive is False


class TestAuditResult:
    """Test audit result data class"""

    def test_audit_result_creation(self):
        """Test audit result can be created"""
        result = AuditResult(
            project_type="python",
            total_dependencies=10,
            vulnerabilities=[],
            license_issues=[],
            summary={"critical": 0, "high": 0, "medium": 0, "low": 0, "license_violations": 0},
        )
        assert result.project_type == "python"
        assert result.total_dependencies == 10


class TestDependencyAuditorPlugin:
    """Test dependency auditor plugin"""

    def test_plugin_initialization(self):
        """Test plugin can be instantiated"""
        plugin = DependencyAuditorPlugin()
        assert plugin.metadata.name == "dependency_auditor"

    def test_plugin_metadata(self):
        """Test plugin metadata is correct"""
        plugin = DependencyAuditorPlugin()
        assert "auditor" in plugin.metadata.name
        assert plugin.metadata.version == "1.0.0"

    def test_detect_python_project(self):
        """Test Python project detection"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements.txt
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0\nflask==2.0.0\n")

            project_type = plugin._detect_project_type(Path(tmpdir))
            assert project_type == "python"

    def test_detect_node_project(self):
        """Test Node project detection"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package.json
            package_json = {
                "name": "test-app",
                "dependencies": {"express": "^4.18.0"},
            }
            Path(tmpdir, "package.json").write_text(json.dumps(package_json))

            project_type = plugin._detect_project_type(Path(tmpdir))
            assert project_type == "node"

    def test_detect_mixed_project(self):
        """Test mixed Python/Node project detection"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0\n")
            Path(tmpdir, "package.json").write_text(json.dumps({"name": "app"}))

            project_type = plugin._detect_project_type(Path(tmpdir))
            assert project_type == "mixed"

    def test_parse_python_dependencies(self):
        """Test Python dependency parsing"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            requirements = "requests==2.28.0\nflask>=2.0.0\ndjango\n"
            Path(tmpdir, "requirements.txt").write_text(requirements)

            deps = plugin._get_python_dependencies(Path(tmpdir))
            assert "requests" in deps
            assert deps["requests"] == "2.28.0"
            assert "flask" in deps
            assert "django" in deps

    def test_parse_node_dependencies(self):
        """Test Node dependency parsing"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            package_json = {
                "name": "test",
                "dependencies": {"express": "^4.18.0", "lodash": "4.17.20"},
                "devDependencies": {"jest": "^28.0.0"},
            }
            Path(tmpdir, "package.json").write_text(json.dumps(package_json))

            deps = plugin._get_node_dependencies(Path(tmpdir))
            assert "express" in deps
            assert "lodash" in deps
            assert "jest" in deps

    def test_version_constraint_checking(self):
        """Test version constraint matching"""
        plugin = DependencyAuditorPlugin()

        # Test less than constraint
        assert plugin._version_satisfies("2.28.0", "<2.31.0") is True
        assert plugin._version_satisfies("3.0.0", "<2.31.0") is False
        assert plugin._version_satisfies("2.32.0", "<2.31.0") is False

    def test_severity_ranking(self):
        """Test severity ranking"""
        plugin = DependencyAuditorPlugin()

        assert plugin._severity_rank("critical") == 4
        assert plugin._severity_rank("high") == 3
        assert plugin._severity_rank("medium") == 2
        assert plugin._severity_rank("low") == 1

    def test_severity_filtering(self):
        """Test severity-based filtering"""
        plugin = DependencyAuditorPlugin()

        # Add test vulnerabilities
        plugin.vulnerabilities = [
            DependencyVulnerability("pkg1", "1.0", "CVE-1", "critical", "desc"),
            DependencyVulnerability("pkg2", "1.0", "CVE-2", "high", "desc"),
            DependencyVulnerability("pkg3", "1.0", "CVE-3", "low", "desc"),
        ]

        # Filter for high and above
        filtered = [v for v in plugin.vulnerabilities if plugin._severity_rank(v.severity) >= plugin._severity_rank("high")]
        assert len(filtered) == 2

    def test_execute_returns_dict(self):
        """Test execute returns properly structured result"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0\n")

            result = plugin.execute(path=tmpdir, severity_filter="low")
            assert "status" in result
            assert result["status"] == "success"
            assert "audit_result" in result
            assert "message" in result

    def test_known_vulnerability_detection(self):
        """Test detection of known vulnerabilities"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a requirements file with vulnerable package
            Path(tmpdir, "requirements.txt").write_text("pillow==9.5.0\n")

            result = plugin.execute(path=tmpdir)
            assert result["status"] == "success"
            # Should detect pillow as vulnerable

    def test_license_issues_detection(self):
        """Test license issue detection"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements with unknown packages
            Path(tmpdir, "requirements.txt").write_text("obscure-package==1.0.0\n")

            result = plugin.execute(path=tmpdir)
            assert result["status"] == "success"

    def test_empty_project(self):
        """Test handling of project with no dependencies"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = plugin.execute(path=tmpdir)
            assert result["status"] == "success"
            assert result["audit_result"]["total_dependencies"] == 0

    def test_extract_fix_version(self):
        """Test fix version extraction"""
        plugin = DependencyAuditorPlugin()

        assert plugin._extract_fix_version("<42.0.0") == "42.0.0"
        assert plugin._extract_fix_version(">3.5.0") == "3.5.0"
        assert plugin._extract_fix_version("==1.2.3") == "1.2.3"

    def test_extract_severity_from_description(self):
        """Test severity extraction from CVE description"""
        plugin = DependencyAuditorPlugin()

        assert plugin._extract_severity("CRITICAL: Buffer overflow") == "critical"
        assert plugin._extract_severity("HIGH: SQL injection") == "high"
        assert plugin._extract_severity("Unknown issue") == "medium"

    def test_permissive_licenses(self):
        """Test permissive license identification"""
        plugin = DependencyAuditorPlugin()

        assert "MIT" in plugin.PERMISSIVE_LICENSES
        assert "Apache-2.0" in plugin.PERMISSIVE_LICENSES
        assert "GPL-3.0" not in plugin.PERMISSIVE_LICENSES

    def test_plugin_has_execute_method(self):
        """Test plugin implements execute method"""
        plugin = DependencyAuditorPlugin()
        assert hasattr(plugin, "execute")
        assert callable(plugin.execute)

    def test_audit_summary_counts(self):
        """Test audit summary correctly counts vulnerabilities"""
        plugin = DependencyAuditorPlugin()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0\n")

            result = plugin.execute(path=tmpdir)
            summary = result["audit_result"]["summary"]

            assert "critical" in summary
            assert "high" in summary
            assert "medium" in summary
            assert "low" in summary
            assert "license_violations" in summary
