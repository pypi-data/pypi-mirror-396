"""
Code Analyzer Plugin for LMAPP v0.2.5.

Provides static code analysis capabilities for common programming languages.
Uses pattern matching and heuristics for bug detection, style issues, and performance hints.

Features:
- Multi-language support (Python, JavaScript, Java, C++)
- Bug detection (null checks, type issues, logic errors)
- Style analysis (naming conventions, code structure)
- Performance hints (inefficient patterns, memory issues)
- Complexity metrics (cyclomatic complexity estimation)
- Severity levels (critical, high, medium, low, info)

Usage:
    plugin = CodeAnalyzerPlugin()
    plugin.initialize({"language": "python", "strict": True})
    result = plugin.execute(code="def foo():\\n  x = None\\n  print(x.strip())")
    # Returns: {"issues": [...], "summary": {...}, "language": "python"}

Supported Languages:
- Python (.py)
- JavaScript (.js, .ts)
- Java (.java)
- C++ (.cpp, .h)
- Generic patterns for any language
"""

from typing import Dict, Optional, Any, Callable, List, Tuple
from dataclasses import dataclass, field
import re

from .plugin_manager import BasePlugin, PluginMetadata


@dataclass
class CodeIssue:
    """Represents a code issue found during analysis."""
    
    severity: str  # critical, high, medium, low, info
    issue_type: str  # bug, style, performance, complexity
    line: int
    column: int
    message: str
    suggestion: Optional[str] = None
    pattern: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "severity": self.severity,
            "type": self.issue_type,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "suggestion": self.suggestion,
            "pattern": self.pattern,
        }


@dataclass
class AnalysisResult:
    """Result of code analysis."""
    
    language: str
    issues: List[CodeIssue] = field(default_factory=list)
    lines_analyzed: int = 0
    complexity_estimate: int = 0
    
    @property
    def summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        critical = sum(1 for i in self.issues if i.severity == "critical")
        high = sum(1 for i in self.issues if i.severity == "high")
        medium = sum(1 for i in self.issues if i.severity == "medium")
        low = sum(1 for i in self.issues if i.severity == "low")
        info = sum(1 for i in self.issues if i.severity == "info")
        
        return {
            "total_issues": len(self.issues),
            "by_severity": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "info": info,
            },
            "by_type": self._count_by_type(),
            "lines_analyzed": self.lines_analyzed,
            "complexity_estimate": self.complexity_estimate,
            "pass": critical == 0 and high == 0,
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count issues by type."""
        counts = {}
        for issue in self.issues:
            counts[issue.issue_type] = counts.get(issue.issue_type, 0) + 1
        return counts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "language": self.language,
            "issues": [i.to_dict() for i in self.issues],
            "summary": self.summary,
        }


class CodeAnalyzerPlugin(BasePlugin):
    """
    Code Analyzer plugin for static code analysis.
    
    Detects bugs, style issues, performance problems, and complexity issues
    across multiple programming languages.
    """
    
    # Pattern definitions for different issue types
    CRITICAL_PATTERNS = {
        "null_deref": {
            "patterns": [
                r"\.(?:strip|split|replace)\s*\(\s*\)",  # Missing guard for potential None
                r"(?:null|None|nil)\s*\..*?\(",  # Direct null dereference
            ],
            "message": "Potential null pointer dereference",
            "suggestion": "Add null check before accessing property or method",
        },
        "logic_error": {
            "patterns": [
                r"(?:if|while)\s+\(.*?==.*?==.*?\)",  # Double equals in condition
                r"(?:if|while)\s+\(.*?\s+and\s+.*?\s+or\s+",  # Mixed and/or without parens
            ],
            "message": "Potential logic error in condition",
            "suggestion": "Verify operator precedence and logical intent",
        },
    }
    
    HIGH_PATTERNS = {
        "uncaught_exception": {
            "patterns": [
                r"(?:open|read|write|delete)\s*\([^)]*\)(?!\s*except)",  # File ops without exception handling
                r"(?:json\.parse|JSON\.parse)\s*\([^)]*\)(?!\s*catch)",  # JSON parse without error handling
            ],
            "message": "Unhandled exception risk",
            "suggestion": "Add try-except/try-catch block",
        },
        "resource_leak": {
            "patterns": [
                r"(?:open|socket|connect)\s*\([^)]*\)(?!.*with|.*using)",  # Resource without cleanup
            ],
            "message": "Potential resource leak",
            "suggestion": "Use context manager (with/using) for resource management",
        },
    }
    
    MEDIUM_PATTERNS = {
        "performance": {
            "patterns": [
                r"for\s+.*\s+in\s+.*:\s*.*\.append\(",  # List append in loop (consider list comprehension)
                r"str\s*\+\s*=\s*(?!f['\"])",  # String concatenation in loop
                r"(?:.*\s+)?=\s*\[\s*\].*for",  # List comprehension opportunity
            ],
            "message": "Performance optimization opportunity",
            "suggestion": "Consider using list comprehension or more efficient method",
        },
    }
    
    STYLE_PATTERNS = {
        "naming": {
            "patterns": [
                r"def\s+[a-z]+[A-Z][a-zA-Z]*\s*\(",  # Mixed case in snake_case language
                r"(?:let|var|const)\s+[A-Z][a-z_]*\s*=",  # PascalCase for variable
            ],
            "message": "Naming convention violation",
            "suggestion": "Follow language naming conventions (snake_case for Python, camelCase for JS)",
        },
        "unused_variable": {
            "patterns": [
                r"(?:def|function)\s+\w+\s*\([^)]*\).*?:.*?(?:pass|return)",  # Function that doesn't use params
            ],
            "message": "Potentially unused variable",
            "suggestion": "Remove or use the declared variable",
        },
    }
    
    def __init__(self):
        """Initialize code analyzer plugin."""
        self._metadata = PluginMetadata(
            name="code-analyzer",
            version="0.1.0",
            description="Static code analysis for bugs, style, and performance issues",
            author="LMAPP Team",
            license="MIT",
            dependencies=[],
            entry_point="example_code_analyzer:CodeAnalyzerPlugin",
            tags=["code-analysis", "static-analysis", "linting", "quality"],
        )
        self.language = "python"
        self.strict_mode = False
        self.analysis_stats = {
            "analyses_run": 0,
            "total_issues_found": 0,
            "average_complexity": 0.0,
        }
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return self._metadata
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the code analyzer plugin.
        
        Args:
            config: Configuration dict with keys:
                - language: Programming language (python, javascript, java, cpp)
                - strict: Strict mode (report more issues)
        """
        if config:
            self.language = config.get("language", "python")
            self.strict_mode = config.get("strict", False)
    
    def _estimate_complexity(self, code: str) -> int:
        """
        Estimate cyclomatic complexity based on control structures.
        
        Returns:
            Estimated complexity (1-10+)
        """
        complexity = 1
        
        # Count decision points
        control_keywords = [
            r"\b(?:if|elif|else|switch|case)\b",
            r"\b(?:for|while|do)\b",
            r"\b(?:try|except|catch|finally)\b",
            r"\b(?:and|or)\b",
        ]
        
        for pattern in control_keywords:
            matches = len(re.findall(pattern, code, re.IGNORECASE))
            complexity += matches
        
        return min(complexity, 10)  # Cap at 10
    
    def _detect_issues(self, code: str, language: str) -> List[CodeIssue]:
        """
        Detect issues in code.
        
        Args:
            code: Source code to analyze
            language: Programming language
        
        Returns:
            List of CodeIssue objects
        """
        issues = []
        lines = code.split("\n")
        
        # Detect critical issues
        for issue_name, issue_def in self.CRITICAL_PATTERNS.items():
            for line_no, line in enumerate(lines, 1):
                for pattern in issue_def["patterns"]:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(CodeIssue(
                            severity="critical",
                            issue_type="bug",
                            line=line_no,
                            column=len(line) - len(line.lstrip()),
                            message=issue_def["message"],
                            suggestion=issue_def["suggestion"],
                            pattern=issue_name,
                        ))
        
        # Detect high severity issues
        for issue_name, issue_def in self.HIGH_PATTERNS.items():
            for line_no, line in enumerate(lines, 1):
                for pattern in issue_def["patterns"]:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(CodeIssue(
                            severity="high",
                            issue_type="bug",
                            line=line_no,
                            column=len(line) - len(line.lstrip()),
                            message=issue_def["message"],
                            suggestion=issue_def["suggestion"],
                            pattern=issue_name,
                        ))
        
        # Detect medium severity issues (performance)
        if not self.strict_mode or True:  # Always check performance
            for issue_name, issue_def in self.MEDIUM_PATTERNS.items():
                for line_no, line in enumerate(lines, 1):
                    for pattern in issue_def["patterns"]:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append(CodeIssue(
                                severity="medium",
                                issue_type="performance",
                                line=line_no,
                                column=len(line) - len(line.lstrip()),
                                message=issue_def["message"],
                                suggestion=issue_def["suggestion"],
                                pattern=issue_name,
                            ))
        
        # Detect style issues (only in strict mode)
        if self.strict_mode:
            for issue_name, issue_def in self.STYLE_PATTERNS.items():
                for line_no, line in enumerate(lines, 1):
                    for pattern in issue_def["patterns"]:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append(CodeIssue(
                                severity="low",
                                issue_type="style",
                                line=line_no,
                                column=len(line) - len(line.lstrip()),
                                message=issue_def["message"],
                                suggestion=issue_def["suggestion"],
                                pattern=issue_name,
                            ))
        
        return issues
    
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute code analysis.
        
        Args:
            code: Source code to analyze
            language: Programming language (optional, uses config default)
        
        Returns:
            Dict with analysis results
        """
        code = kwargs.get("code", "")
        if not code and args:
            code = args[0]
        
        language = kwargs.get("language", self.language)
        
        # Create result object
        result = AnalysisResult(
            language=language,
            lines_analyzed=len(code.split("\n")),
        )
        
        # Estimate complexity
        result.complexity_estimate = self._estimate_complexity(code)
        
        # Detect issues
        result.issues = self._detect_issues(code, language)
        
        # Update stats
        self.analysis_stats["analyses_run"] += 1
        self.analysis_stats["total_issues_found"] += len(result.issues)
        
        return result.to_dict()
    
    def cleanup(self) -> None:
        """Cleanup when plugin is unloaded."""
        self.analysis_stats = {
            "analyses_run": 0,
            "total_issues_found": 0,
            "average_complexity": 0.0,
        }
    
    def get_commands(self) -> Dict[str, Callable]:
        """Get CLI commands provided by this plugin."""
        return {
            "analyze": self._analyze_command,
            "analyze-file": self._analyze_file_command,
            "set-language": self._set_language_command,
            "analysis-stats": self._stats_command,
        }
    
    def _analyze_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: analyze code snippet."""
        return self.execute(*args, **kwargs)
    
    def _analyze_file_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: analyze file."""
        filepath = kwargs.get("filepath")
        if not filepath:
            return {"error": "filepath required"}
        
        try:
            with open(filepath, "r") as f:
                code = f.read()
            return self.execute(code=code, **kwargs)
        except Exception as e:
            return {"error": str(e)}
    
    def _set_language_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: set language."""
        language = kwargs.get("language")
        if language:
            self.language = language
        
        return {
            "status": "success",
            "language": self.language,
            "strict": self.strict_mode,
        }
    
    def _stats_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: show analysis statistics."""
        return {
            "stats": self.analysis_stats.copy(),
        }


# Export for marketplace registration
__all__ = ["CodeAnalyzerPlugin", "CodeIssue", "AnalysisResult"]


# Marketplace registration metadata
PLUGIN_MANIFEST = {
    "name": "code-analyzer",
    "version": "0.1.0",
    "author": "LMAPP Team",
    "description": "Static code analysis for bugs, style, and performance issues",
    "repository": "https://github.com/nabaznyl/lmapp/tree/mother/src/lmapp/plugins",
    "install_url": "https://github.com/nabaznyl/lmapp/raw/mother/src/lmapp/plugins/example_code_analyzer.py",
    "tags": ["code-analysis", "static-analysis", "linting", "quality"],
    "dependencies": [],
    "license": "MIT",
}
