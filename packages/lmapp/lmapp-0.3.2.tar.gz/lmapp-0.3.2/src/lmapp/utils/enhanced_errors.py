"""
Enhanced error messages for LMAPP v0.2.3.

Provides helpful, user-friendly error messages with troubleshooting suggestions.
Integrates with error recovery to give users clear guidance on resolving issues.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import re


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"              # Informational, no action needed
    WARNING = "warning"        # Warning, might need attention
    ERROR = "error"            # Error, action required
    CRITICAL = "critical"      # Critical, immediate action required


class HelpfulError:
    """Represents an error with helpful context and solutions."""
    
    def __init__(
        self,
        title: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        suggestions: Optional[List[str]] = None,
        reference: Optional[str] = None,
    ):
        """
        Initialize a HelpfulError.
        
        Args:
            title: Short error title
            message: Detailed error message
            severity: Error severity level
            suggestions: List of suggested fixes
            reference: Link to documentation or issue tracker
        """
        self.title = title
        self.message = message
        self.severity = severity
        self.suggestions = suggestions or []
        self.reference = reference
    
    def format_for_display(self, verbose: bool = False) -> str:
        """Format error for display to user."""
        lines = [
            f"{'❌' if self.severity == ErrorSeverity.CRITICAL else '⚠️'} {self.title}",
            "",
            self.message,
        ]
        
        if self.suggestions and (verbose or self.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.ERROR]):
            lines.append("")
            lines.append("💡 Try these solutions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"   {i}. {suggestion}")
        
        if self.reference:
            lines.append("")
            lines.append(f"📖 Learn more: {self.reference}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "suggestions": self.suggestions,
            "reference": self.reference,
        }


class ErrorMessageLibrary:
    """Library of common errors and helpful messages."""
    
    @staticmethod
    def model_not_found(model_name: str, backend: str, available_models: Optional[List[str]] = None) -> HelpfulError:
        """Error when model is not available."""
        suggestions = [
            f"Download the model: lmapp download {model_name}",
            f"List available models: lmapp models --available",
        ]
        
        if available_models:
            suggestions.append(
                f"Available models: {', '.join(available_models[:3])}"
                f"{' ...' if len(available_models) > 3 else ''}"
            )
        
        return HelpfulError(
            title=f"Model '{model_name}' not found",
            message=f"The model '{model_name}' is not available in your {backend} installation.",
            severity=ErrorSeverity.ERROR,
            suggestions=suggestions,
            reference="https://lmapp.dev/guides/models",
        )
    
    @staticmethod
    def backend_not_running(backend: str) -> HelpfulError:
        """Error when backend is not running."""
        start_cmd = f"lmapp start {backend}"
        
        return HelpfulError(
            title=f"{backend.capitalize()} is not running",
            message=f"LMAPP could not connect to {backend}. It may not be installed or running.",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                f"Start {backend}: {start_cmd}",
                f"Install {backend}: lmapp setup {backend}",
                f"Check status: lmapp status",
                f"View logs: lmapp logs {backend}",
            ],
            reference=f"https://lmapp.dev/backends/{backend}",
        )
    
    @staticmethod
    def out_of_memory() -> HelpfulError:
        """Error when system runs out of memory."""
        return HelpfulError(
            title="Out of memory",
            message="The model requires more memory than is currently available on your system.",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Use a smaller model: lmapp models --size small",
                "Close other applications to free memory",
                "Check system memory: free -h (Linux) or Task Manager (Windows)",
                "Enable GPU offloading if available",
                "Increase swap space if possible",
            ],
            reference="https://lmapp.dev/guides/memory-optimization",
        )
    
    @staticmethod
    def configuration_error(detail: str) -> HelpfulError:
        """Error in configuration."""
        return HelpfulError(
            title="Configuration error",
            message=f"There's a problem with your LMAPP configuration: {detail}",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Reset configuration: lmapp config --reset",
                "View current config: lmapp config --show",
                "Check config file: ~/.lmapp/config.json",
                "View documentation: lmapp config --help",
            ],
            reference="https://lmapp.dev/guides/configuration",
        )
    
    @staticmethod
    def network_error(detail: str = "Connection failed") -> HelpfulError:
        """Error connecting to backend or network."""
        return HelpfulError(
            title="Network connection error",
            message=f"Could not connect to the backend: {detail}",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Check if backend is running: lmapp status",
                "Check network connection: ping 127.0.0.1",
                "Check firewall settings",
                "Restart the backend: lmapp restart",
                "Check backend logs: lmapp logs",
            ],
            reference="https://lmapp.dev/guides/troubleshooting",
        )
    
    @staticmethod
    def request_timeout(operation: str = "request", timeout_seconds: int = 30) -> HelpfulError:
        """Error when request times out."""
        return HelpfulError(
            title="Request timeout",
            message=f"The {operation} took longer than {timeout_seconds} seconds and was cancelled.",
            severity=ErrorSeverity.WARNING,
            suggestions=[
                "Increase timeout: lmapp config --timeout 60",
                "Use a faster model: lmapp models --speed fast",
                "Check system load: top (Linux) or Task Manager (Windows)",
                "Try again with shorter input",
                "Check backend performance: lmapp status --detailed",
            ],
            reference="https://lmapp.dev/guides/performance",
        )
    
    @staticmethod
    def gpu_error(detail: str = "GPU unavailable") -> HelpfulError:
        """Error with GPU."""
        return HelpfulError(
            title="GPU error",
            message=f"There's a problem with your GPU: {detail}",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Check GPU driver: nvidia-smi (NVIDIA) or amd-smi (AMD)",
                "Disable GPU: lmapp config --gpu false",
                "Update drivers to latest version",
                "Check CUDA/ROCm installation",
                "Restart your system",
            ],
            reference="https://lmapp.dev/guides/gpu-setup",
        )
    
    @staticmethod
    def permission_error(resource: str) -> HelpfulError:
        """Error with file/resource permissions."""
        return HelpfulError(
            title="Permission denied",
            message=f"LMAPP doesn't have permission to access: {resource}",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                f"Check file permissions: ls -la {resource}",
                f"Fix permissions: chmod u+rw {resource}",
                "Run with appropriate privileges",
                "Check SELinux/AppArmor settings",
                "Ensure ~/.lmapp/ directory is writable",
            ],
            reference="https://lmapp.dev/guides/permissions",
        )
    
    @staticmethod
    def version_mismatch(current: str, required: str, component: str = "Backend") -> HelpfulError:
        """Error when version is incompatible."""
        return HelpfulError(
            title=f"{component} version mismatch",
            message=f"Your {component} version ({current}) is incompatible. Required: {required}",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                f"Update {component}: lmapp update {component.lower()}",
                f"Check version: {component.lower()} --version",
                "Run diagnostics: lmapp doctor",
                "Check release notes for breaking changes",
            ],
            reference="https://lmapp.dev/releases",
        )


class ErrorMessageFormatter:
    """Format errors for different output contexts."""
    
    @staticmethod
    def format_for_cli(error: HelpfulError, verbose: bool = False) -> str:
        """Format for CLI output."""
        return error.format_for_display(verbose)
    
    @staticmethod
    def format_for_log(error: HelpfulError) -> str:
        """Format for logging."""
        return f"[{error.severity.value.upper()}] {error.title}\n{error.message}"
    
    @staticmethod
    def format_for_api(error: HelpfulError) -> Dict:
        """Format for API responses."""
        return error.to_dict()


# Error context extraction utilities
class ErrorContextExtractor:
    """Extract context from error messages and stack traces."""
    
    @staticmethod
    def extract_model_name_from_error(error_text: str) -> Optional[str]:
        """Try to extract model name from error message."""
        patterns = [
            r"model['\"]?\s*[:=]\s*['\"]?([a-z0-9\-:.]+)",
            r"['\"]([a-z0-9\-:.]+)['\"]?\s+not found",
            r"model\s+['\"]?([a-z0-9\-:.]+)['\"]?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def extract_backend_name_from_error(error_text: str) -> Optional[str]:
        """Try to extract backend name from error message."""
        backends = ["ollama", "llamafile", "openai"]
        for backend in backends:
            if backend.lower() in error_text.lower():
                return backend
        return None
    
    @staticmethod
    def suggest_common_fixes(error_text: str) -> List[str]:
        """Suggest common fixes based on error text."""
        fixes = []
        
        if any(word in error_text.lower() for word in ["connection", "refused", "timeout"]):
            fixes.append("Ensure the backend is running: lmapp status")
        
        if any(word in error_text.lower() for word in ["memory", "out of", "exceeded"]):
            fixes.append("Try a smaller model: lmapp models --size small")
        
        if any(word in error_text.lower() for word in ["gpu", "cuda", "rocm"]):
            fixes.append("Check GPU setup: lmapp doctor --gpu")
        
        if any(word in error_text.lower() for word in ["permission", "denied", "access"]):
            fixes.append("Check file permissions: chmod u+rw ~/.lmapp")
        
        if any(word in error_text.lower() for word in ["not found", "not available"]):
            fixes.append("Download required model: lmapp download")
        
        return fixes if fixes else ["Check logs: lmapp logs", "Run diagnostics: lmapp doctor"]
