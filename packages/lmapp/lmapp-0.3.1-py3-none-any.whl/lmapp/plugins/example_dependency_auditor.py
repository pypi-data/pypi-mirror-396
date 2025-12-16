#!/usr/bin/env python3
"""
Dependency Auditor Plugin
Scans project dependencies for vulnerabilities and license compliance
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from .plugin_manager import BasePlugin, PluginMetadata


@dataclass
class DependencyVulnerability:
    """Vulnerability information"""
    package: str
    version: str
    vulnerability_id: str
    severity: str  # critical, high, medium, low
    description: str
    fix_version: Optional[str] = None


@dataclass
class DependencyLicense:
    """License information"""
    package: str
    version: str
    license: str
    is_permissive: bool  # True for MIT, BSD, Apache; False for GPL, AGPL


@dataclass
class AuditResult:
    """Complete audit report"""
    project_type: str  # python, node, mixed
    total_dependencies: int
    vulnerabilities: List[DependencyVulnerability]
    license_issues: List[DependencyLicense]
    summary: Dict[str, Any]


class DependencyAuditorPlugin(BasePlugin):
    """
    Audits project dependencies for vulnerabilities and license compliance.
    
    Supports Python and Node.js projects without external API calls (offline).
    """

    _METADATA = PluginMetadata(
        name="dependency_auditor",
        version="1.0.0",
        author="lmapp-dev",
        description="Scan project dependencies for vulnerabilities and license compliance",
        license="MIT",
        dependencies=[],
        tags=["security", "audit", "dependencies"],
    )

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return self._METADATA
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the plugin."""
        pass

    # Known vulnerable packages (curated, offline database)
    KNOWN_VULNERABILITIES = {
        # Python packages
        "cryptography": {"<42.0.0": "CVE-2024-XXXX: Integer overflow in crypto"},
        "pillow": {"<10.0.0": "CVE-2023-XXXX: Buffer overflow in image processing"},
        "requests": {"<2.31.0": "CVE-2023-XXXX: Connection pooling issue"},
        "django": {"<4.2": "CVE-2023-XXXX: SQL injection vulnerability"},
        # Node packages
        "lodash": {"<4.17.21": "CVE-2021-23337: Prototype pollution"},
        "express": {"<4.18.0": "CVE-2022-XXXX: Denial of service"},
    }

    # Permissive licenses
    PERMISSIVE_LICENSES = {
        "MIT", "Apache-2.0", "Apache 2.0", "BSD", "BSD-2-Clause",
        "BSD-3-Clause", "ISC", "MPL-2.0", "LGPL-2.1+", "LGPL-3.0+"
    }

    def __init__(self):
        """Initialize auditor"""
        super().__init__()
        self.vulnerabilities: List[DependencyVulnerability] = []
        self.license_issues: List[DependencyLicense] = []

    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Audit project dependencies.
        
        Args:
            path: Project root path (default: current directory)
            severity_filter: Minimum severity to report (default: 'low')
            
        Returns:
            Dictionary with audit results
        """
        project_path = kwargs.get("path", ".")
        severity_filter = kwargs.get("severity_filter", "low")

        result = self._run_audit(project_path, severity_filter)

        return {
            "status": "success",
            "audit_result": asdict(result),
            "message": f"Scanned {result.total_dependencies} dependencies, "
                      f"found {len(result.vulnerabilities)} vulnerabilities, "
                      f"{len(result.license_issues)} license concerns",
        }

    def _run_audit(self, project_path: str, severity_filter: str) -> AuditResult:
        """Run comprehensive audit"""
        project_path_obj = Path(project_path).resolve()

        # Detect project type
        project_type = self._detect_project_type(project_path_obj)

        # Get dependencies
        python_deps = self._get_python_dependencies(project_path_obj)
        node_deps = self._get_node_dependencies(project_path_obj)

        all_deps = {**python_deps, **node_deps}
        total_deps = len(all_deps)

        # Audit each dependency
        for package, version in all_deps.items():
            self._check_vulnerabilities(package, version)
            self._check_license(package, version)

        # Filter by severity
        filtered_vulns = [
            v for v in self.vulnerabilities
            if self._severity_rank(v.severity) >= self._severity_rank(severity_filter)
        ]

        return AuditResult(
            project_type=project_type,
            total_dependencies=total_deps,
            vulnerabilities=filtered_vulns,
            license_issues=self.license_issues,
            summary={
                "critical": len([v for v in filtered_vulns if v.severity == "critical"]),
                "high": len([v for v in filtered_vulns if v.severity == "high"]),
                "medium": len([v for v in filtered_vulns if v.severity == "medium"]),
                "low": len([v for v in filtered_vulns if v.severity == "low"]),
                "license_violations": len(self.license_issues),
            },
        )

    def _detect_project_type(self, project_path: Path) -> str:
        """Detect if project is Python, Node, or mixed"""
        has_python = (project_path / "requirements.txt").exists() or (project_path / "setup.py").exists()
        has_node = (project_path / "package.json").exists()

        if has_python and has_node:
            return "mixed"
        elif has_python:
            return "python"
        elif has_node:
            return "node"
        return "unknown"

    def _get_python_dependencies(self, project_path: Path) -> Dict[str, str]:
        """Extract Python dependencies"""
        deps = {}

        # From requirements.txt
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            for line in req_file.read_text().split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Parse "package==version"
                    parts = line.replace(">=", "==").replace(">", "==").split("==")
                    if len(parts) >= 2:
                        deps[parts[0].strip()] = parts[1].strip()
                    else:
                        deps[parts[0].strip()] = "unknown"

        # From setup.py (simplified parsing)
        setup_file = project_path / "setup.py"
        if setup_file.exists():
            content = setup_file.read_text()
            # Very simple heuristic - real parsing would use ast module
            if "install_requires" in content:
                # Would need proper parsing here
                pass

        return deps

    def _get_node_dependencies(self, project_path: Path) -> Dict[str, str]:
        """Extract Node.js dependencies"""
        deps = {}

        package_file = project_path / "package.json"
        if package_file.exists():
            try:
                package_json = json.loads(package_file.read_text())
                for section in ["dependencies", "devDependencies", "peerDependencies"]:
                    if section in package_json:
                        for package, version in package_json[section].items():
                            # Normalize version (remove ^, ~, etc.)
                            version_normalized = version.lstrip("^~><=").split()[0]
                            deps[package] = version_normalized
            except (json.JSONDecodeError, KeyError):
                pass

        return deps

    def _check_vulnerabilities(self, package: str, version: str) -> None:
        """Check if package version has known vulnerabilities"""
        if package not in self.KNOWN_VULNERABILITIES:
            return

        vulns = self.KNOWN_VULNERABILITIES[package]
        for constraint, description in vulns.items():
            # Simple version comparison
            if self._version_satisfies(version, constraint):
                vuln = DependencyVulnerability(
                    package=package,
                    version=version,
                    vulnerability_id=description.split(":")[0],
                    severity=self._extract_severity(description),
                    description=description,
                    fix_version=self._extract_fix_version(constraint),
                )
                self.vulnerabilities.append(vuln)

    def _check_license(self, package: str, version: str) -> None:
        """Check package license (simplified - would use real metadata)"""
        # Placeholder: in production, would query PyPI/NPM for real licenses
        # For now, we'll assume common packages have known good licenses
        known_good = {
            "requests", "flask", "django", "pytest", "black", "cryptography",
            "express", "react", "lodash", "axios", "webpack"
        }

        if package in known_good:
            return

        # Mark as potential concern if license unknown
        concern = DependencyLicense(
            package=package,
            version=version,
            license="unknown",
            is_permissive=False,
        )
        self.license_issues.append(concern)

    def _version_satisfies(self, version: str, constraint: str) -> bool:
        """Simple version constraint checking"""
        # Very simplified - would use packaging.version for real
        try:
            # Parse versions as tuples of ints for comparison
            def parse_version(v_str):
                parts = v_str.replace("<", "").replace(">", "").replace("=", "").strip().split(".")
                return tuple(int(p) for p in parts)
            
            v = parse_version(version)
            c = parse_version(constraint)

            if constraint.startswith("<"):
                return v < c
            elif constraint.startswith(">"):
                return v > c
            return v == c
        except (ValueError, IndexError, AttributeError):
            return False

    def _severity_rank(self, severity: str) -> int:
        """Get numeric rank for severity comparison"""
        ranks = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return ranks.get(severity, 0)

    def _extract_severity(self, description: str) -> str:
        """Extract severity from description"""
        for severity in ["critical", "high", "medium", "low"]:
            if severity.lower() in description.lower():
                return severity
        return "medium"

    def _extract_fix_version(self, constraint: str) -> Optional[str]:
        """Extract suggested fix version from constraint"""
        # constraint is like "<42.0.0", extract "42.0.0"
        version = constraint.replace("<", "").replace(">", "").replace("=", "").strip()
        return version if version else None
