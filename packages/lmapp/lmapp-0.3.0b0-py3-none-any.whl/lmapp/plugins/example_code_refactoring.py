"""
Code Refactoring Plugin - Analyze and suggest code improvements.

Provides pattern detection, refactoring suggestions, and safety checks
for Python code without external dependencies.

Author: LMAPP Community
License: MIT
"""

import ast
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from lmapp.plugins.plugin_manager import BasePlugin, PluginMetadata


@dataclass
class RefactoringIssue:
    """Represents a code issue or refactoring opportunity."""

    issue_type: str  # "dead_code", "naming", "complexity", "duplication", etc.
    severity: str  # "low", "medium", "high", "critical"
    line_number: Optional[int]
    description: str
    suggestion: str
    code_snippet: str = ""


@dataclass
class RefactoringResult:
    """Result of code analysis or refactoring."""

    success: bool
    issues: List[RefactoringIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    refactored_code: Optional[str] = None
    error: Optional[str] = None


class CodeRefactoringPlugin(BasePlugin):
    """Analyze Python code and suggest refactorings."""

    @property
    def metadata(self) -> PluginMetadata:
        """Plugin metadata."""
        return PluginMetadata(
            name="code-refactoring",
            version="0.1.0",
            author="community",
            description="Analyze and suggest code improvements with pattern detection",
            license="MIT",
            dependencies=[],
            tags=["analysis", "refactoring", "quality"],
        )

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize plugin with optional configuration."""
        # No initialization needed for this plugin
        pass

    def execute(self, action: str, code: str = "", **kwargs) -> Dict[str, Any]:
        """Execute refactoring action.

        Actions:
            - "analyze": Detect issues in code
            - "suggest_names": Suggest better variable/function names
            - "complexity": Analyze cyclomatic complexity
            - "duplicates": Find duplicate code patterns
        """
        if action == "analyze":
            return self._analyze_code(code)
        elif action == "suggest_names":
            return self._suggest_names(code)
        elif action == "complexity":
            return self._analyze_complexity(code)
        elif action == "duplicates":
            return self._find_duplicates(code)
        return {
            "success": False,
            "error": f"Unknown action: {action}",
        }

    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for issues and improvements."""
        result = RefactoringResult(success=True)

        # Try to parse the code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error: {str(e)}",
            }

        # Run all checks
        result.issues.extend(self._check_dead_code(tree, code))
        result.issues.extend(self._check_naming(tree))
        result.issues.extend(self._check_complexity(tree))
        result.issues.extend(self._check_imports(tree))
        result.issues.extend(self._check_except_clauses(tree))

        # Calculate metrics
        result.metrics = {
            "total_issues": len(result.issues),
            "critical": sum(1 for i in result.issues if i.severity == "critical"),
            "high": sum(1 for i in result.issues if i.severity == "high"),
            "medium": sum(1 for i in result.issues if i.severity == "medium"),
            "low": sum(1 for i in result.issues if i.severity == "low"),
            "lines_of_code": len(code.split("\n")),
            "functions": sum(
                1
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ),
            "classes": sum(
                1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ),
        }

        return {
            "success": True,
            "issues": [
                {
                    "type": i.issue_type,
                    "severity": i.severity,
                    "line": i.line_number,
                    "description": i.description,
                    "suggestion": i.suggestion,
                }
                for i in result.issues
            ],
            "metrics": result.metrics,
        }

    def _check_dead_code(self, tree: ast.AST, code: str) -> List[RefactoringIssue]:
        """Detect dead code patterns."""
        issues = []
        lines = code.split("\n")

        # Check for unused variables
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get all assigned variables
                assigned = set()
                used = set()

                for child in ast.walk(node):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                assigned.add(target.id)
                    elif isinstance(child, ast.Name):
                        if isinstance(child.ctx, ast.Load):
                            used.add(child.id)

                # Find unused
                unused = assigned - used - {"self", "cls"}
                for var in unused:
                    issues.append(
                        RefactoringIssue(
                            issue_type="unused_variable",
                            severity="medium",
                            line_number=node.lineno,
                            description=f"Variable '{var}' is assigned but never used",
                            suggestion=f"Remove variable '{var}' or use it in the code",
                        )
                    )

        return issues

    def _check_naming(self, tree: ast.AST) -> List[RefactoringIssue]:
        """Check for poor naming conventions."""
        issues = []

        for node in ast.walk(tree):
            # Check function names
            if isinstance(node, ast.FunctionDef):
                if not self._is_valid_snake_case(node.name):
                    issues.append(
                        RefactoringIssue(
                            issue_type="naming",
                            severity="low",
                            line_number=node.lineno,
                            description=f"Function name '{node.name}' should be snake_case",
                            suggestion=f"Rename to: {self._to_snake_case(node.name)}",
                        )
                    )

            # Check class names
            elif isinstance(node, ast.ClassDef):
                if not self._is_valid_class_case(node.name):
                    issues.append(
                        RefactoringIssue(
                            issue_type="naming",
                            severity="low",
                            line_number=node.lineno,
                            description=f"Class name '{node.name}' should be PascalCase",
                            suggestion=f"Rename to: {self._to_pascal_case(node.name)}",
                        )
                    )

        return issues

    def _check_complexity(self, tree: ast.AST) -> List[RefactoringIssue]:
        """Check for high cyclomatic complexity."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                severity = "low"
                if complexity >= 10:
                    severity = "high"
                elif complexity >= 8:
                    severity = "medium"

                if complexity > 5:
                    issues.append(
                        RefactoringIssue(
                            issue_type="complexity",
                            severity=severity,
                            line_number=node.lineno,
                            description=f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                            suggestion="Consider breaking down this function into smaller, more focused functions",
                        )
                    )

        return issues

    def _check_imports(self, tree: ast.AST) -> List[RefactoringIssue]:
        """Check for unused or problematic imports."""
        issues = []
        imports = set()
        used = set()

        # Collect all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports.add(name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports.add(name)

        # Collect all used names
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    used.add(node.id)

        # Find unused imports
        unused_imports = imports - used
        for imp in unused_imports:
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    issues.append(
                        RefactoringIssue(
                            issue_type="unused_import",
                            severity="medium",
                            line_number=node.lineno,
                            description=f"Import '{imp}' is never used",
                            suggestion=f"Remove the unused import '{imp}'",
                        )
                    )
                    break

        return issues

    def _check_except_clauses(self, tree: ast.AST) -> List[RefactoringIssue]:
        """Check for bare except clauses."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:  # Bare except
                    issues.append(
                        RefactoringIssue(
                            issue_type="bare_except",
                            severity="high",
                            line_number=node.lineno,
                            description="Bare except clause catches all exceptions",
                            suggestion="Specify the exception type to catch (e.g., except ValueError:)",
                        )
                    )

        return issues

    def _suggest_names(self, code: str) -> Dict[str, Any]:
        """Suggest better variable and function names."""
        suggestions = {}

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"success": False, "error": "Invalid Python code"}

        # Collect short variable names
        short_vars = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if len(node.id) == 1 and node.id.islower():
                    if node.id not in {"_", "i", "j", "k", "x", "y", "z"}:
                        short_vars[node.id] = (
                            f"Use a more descriptive name instead of '{node.id}'"
                        )

        suggestions["short_variable_names"] = short_vars

        return {
            "success": True,
            "suggestions": suggestions,
        }

    def _analyze_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze cyclomatic complexity."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"success": False, "error": "Invalid Python code"}

        complexity_map = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                complexity_map[node.name] = complexity

        avg_complexity = (
            sum(complexity_map.values()) / len(complexity_map)
            if complexity_map
            else 0
        )

        return {
            "success": True,
            "functions": complexity_map,
            "average_complexity": avg_complexity,
            "status": (
                "Good"
                if avg_complexity < 5
                else "Moderate"
                if avg_complexity < 10
                else "High"
            ),
        }

    def _find_duplicates(self, code: str) -> Dict[str, Any]:
        """Find duplicate code patterns."""
        lines = code.split("\n")
        duplicates = []

        # Look for repeated lines
        seen_lines = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                if stripped in seen_lines:
                    duplicates.append(
                        {
                            "line": i + 1,
                            "previous_line": seen_lines[stripped] + 1,
                            "code": stripped,
                        }
                    )
                else:
                    seen_lines[stripped] = i

        return {
            "success": True,
            "duplicates": duplicates,
            "duplicate_count": len(duplicates),
        }

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(
                child,
                (
                    ast.If,
                    ast.While,
                    ast.For,
                    ast.ExceptHandler,
                    ast.BoolOp,
                ),
            ):
                complexity += 1

        return complexity

    @staticmethod
    def _is_valid_snake_case(name: str) -> bool:
        """Check if name is valid snake_case."""
        return bool(re.match(r"^[a-z_][a-z0-9_]*$", name))

    @staticmethod
    def _is_valid_class_case(name: str) -> bool:
        """Check if name is valid PascalCase."""
        return bool(re.match(r"^[A-Z][a-zA-Z0-9]*$", name))

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert name to snake_case."""
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        """Convert name to PascalCase."""
        return "".join(word.capitalize() for word in name.split("_"))
