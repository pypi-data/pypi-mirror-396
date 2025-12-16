"""
Tests for Code Refactoring Plugin.

Tests the plugin's ability to:
- Analyze code for issues
- Suggest name improvements
- Calculate complexity
- Find duplicate patterns
"""

import pytest

from lmapp.plugins.example_code_refactoring import (
    CodeRefactoringPlugin,
    RefactoringIssue,
)


class TestCodeRefactoringPlugin:
    """Tests for CodeRefactoringPlugin."""

    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return CodeRefactoringPlugin()

    def test_metadata(self, plugin):
        """Verify plugin metadata."""
        metadata = plugin.metadata
        assert metadata.name == "code-refactoring"
        assert metadata.version == "0.1.0"
        assert metadata.author == "community"
        assert "refactoring" in metadata.tags
        assert metadata.license == "MIT"

    def test_analyze_valid_code(self, plugin):
        """Test analyzing valid code."""
        code = """
def hello(name):
    message = "Hello"
    print(f"{message}, {name}")
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        assert "metrics" in result
        assert result["metrics"]["functions"] == 1

    def test_analyze_syntax_error(self, plugin):
        """Test analyzing code with syntax error."""
        code = "def hello(:\n    pass"
        result = plugin.execute("analyze", code=code)
        assert result["success"] is False
        assert "error" in result

    def test_detect_unused_variables(self, plugin):
        """Test detection of unused variables."""
        code = """
def example():
    unused_var = 42
    used_var = 100
    print(used_var)
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        unused_issues = [
            i for i in result["issues"] if i["type"] == "unused_variable"
        ]
        assert len(unused_issues) > 0

    def test_detect_bare_except(self, plugin):
        """Test detection of bare except clauses."""
        code = """
try:
    risky_operation()
except:
    pass
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        bare_except = [i for i in result["issues"] if i["type"] == "bare_except"]
        assert len(bare_except) > 0
        assert bare_except[0]["severity"] == "high"

    def test_detect_naming_issues(self, plugin):
        """Test detection of naming convention issues."""
        code = """
def MyFunction():
    return 42

class my_class:
    pass
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        naming_issues = [i for i in result["issues"] if i["type"] == "naming"]
        assert len(naming_issues) >= 2  # MyFunction should be my_function, my_class should be MyClass

    def test_detect_high_complexity(self, plugin):
        """Test detection of high cyclomatic complexity."""
        code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        if x > 50:
                            return "very high"
    return "low"
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        complexity_issues = [
            i for i in result["issues"] if i["type"] == "complexity"
        ]
        assert len(complexity_issues) > 0

    def test_suggest_names(self, plugin):
        """Test name suggestions."""
        code = """
def process(d):
    x = d.get('key')
    y = d.get('other')
    return x + y
"""
        result = plugin.execute("suggest_names", code=code)
        assert result["success"] is True
        assert "suggestions" in result

    def test_analyze_complexity(self, plugin):
        """Test complexity analysis."""
        code = """
def simple():
    return 42

def complex():
    if True:
        if True:
            if True:
                return 1
    return 0
"""
        result = plugin.execute("complexity", code=code)
        assert result["success"] is True
        assert "functions" in result
        assert "simple" in result["functions"]
        assert result["functions"]["simple"] == 1
        assert result["functions"]["complex"] > result["functions"]["simple"]

    def test_find_duplicates(self, plugin):
        """Test finding duplicate lines."""
        code = """
print("hello")
x = 1
print("hello")
y = 2
"""
        result = plugin.execute("duplicates", code=code)
        assert result["success"] is True
        assert "duplicates" in result
        assert result["duplicate_count"] > 0

    def test_unknown_action(self, plugin):
        """Test unknown action."""
        result = plugin.execute("unknown_action", code="x = 1")
        assert result["success"] is False
        assert "error" in result

    def test_empty_code(self, plugin):
        """Test with empty code."""
        result = plugin.execute("analyze", code="")
        assert result["success"] is True
        assert "metrics" in result

    def test_metrics_calculation(self, plugin):
        """Test metrics calculation."""
        code = """
class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        assert result["metrics"]["classes"] == 1
        assert result["metrics"]["functions"] == 2

    def test_issue_structure(self, plugin):
        """Test that issues have correct structure."""
        code = """
try:
    pass
except:
    pass
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        if result["issues"]:
            issue = result["issues"][0]
            assert "type" in issue
            assert "severity" in issue
            assert "description" in issue
            assert "suggestion" in issue

    def test_severity_levels(self, plugin):
        """Test that severity levels are correctly assigned."""
        code = """
try:
    pass
except:
    pass
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        bare_except = [i for i in result["issues"] if i["type"] == "bare_except"]
        assert len(bare_except) > 0
        assert bare_except[0]["severity"] in ["low", "medium", "high", "critical"]

    def test_multiple_issues(self, plugin):
        """Test that multiple issues are detected."""
        code = """
def BadFunctionName():
    unused = 42
    try:
        risky()
    except:
        pass
    return None
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        assert len(result["issues"]) >= 2  # naming + bare except

    def test_line_numbers(self, plugin):
        """Test that line numbers are included in issues."""
        code = """
def bad_name():
    pass
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        for issue in result["issues"]:
            if issue["type"] == "naming":
                assert issue["line"] is not None

    def test_class_and_function_detection(self, plugin):
        """Test that classes and functions are correctly counted."""
        code = """
class FirstClass:
    def method(self):
        pass

class SecondClass:
    def method1(self):
        pass
    
    def method2(self):
        pass

def standalone_function():
    pass
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        assert result["metrics"]["classes"] == 2
        assert result["metrics"]["functions"] == 4  # 2 + 2 + 1

    def test_complexity_severity(self, plugin):
        """Test that complexity severity is appropriate."""
        # High complexity code
        code = """
def very_complex(x):
    if x > 0:
        if x > 1:
            if x > 2:
                if x > 3:
                    if x > 4:
                        if x > 5:
                            if x > 6:
                                if x > 7:
                                    if x > 8:
                                        return 10
    return 0
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        complexity_issues = [
            i for i in result["issues"] if i["type"] == "complexity"
        ]
        if complexity_issues:
            assert complexity_issues[0]["severity"] in ["high", "critical"]

    def test_issue_count_metrics(self, plugin):
        """Test that issue count metrics are accurate."""
        code = """
try:
    pass
except:
    pass
"""
        result = plugin.execute("analyze", code=code)
        assert result["success"] is True
        total = result["metrics"]["total_issues"]
        by_severity = (
            result["metrics"]["critical"]
            + result["metrics"]["high"]
            + result["metrics"]["medium"]
            + result["metrics"]["low"]
        )
        assert total == by_severity

    def test_complex_duplicate_detection(self, plugin):
        """Test duplicate detection with variations."""
        code = """
x = calculate()
y = process()
x = calculate()
"""
        result = plugin.execute("duplicates", code=code)
        assert result["success"] is True
        assert result["duplicate_count"] >= 1

    def test_refactoring_issue_dataclass(self):
        """Test RefactoringIssue dataclass creation."""
        issue = RefactoringIssue(
            issue_type="test",
            severity="low",
            line_number=1,
            description="Test issue",
            suggestion="Test suggestion",
        )
        assert issue.issue_type == "test"
        assert issue.severity == "low"
        assert issue.line_number == 1
