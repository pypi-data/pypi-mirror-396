#!/usr/bin/env python3
"""
System Check Module
Validates system requirements before installation
"""

import sys
import platform
import shutil
import subprocess
from pathlib import Path

import psutil
import distro
from rich.console import Console

console = Console()


class SystemCheck:
    """Perform system requirement checks"""

    MIN_RAM_GB = 4
    RECOMMENDED_RAM_GB = 8
    MIN_STORAGE_GB = 5
    RECOMMENDED_STORAGE_GB = 10

    def __init__(self):
        self.results = {}

    def check_os(self) -> bool:
        """Check if running on supported OS"""
        console.print("[bold]Checking Operating System...[/bold]")

        os_name = platform.system()
        if os_name != "Linux":
            console.print(f"[red]✗ Unsupported OS: {os_name}[/red]")
            console.print(
                "[yellow]  Currently only Debian-based Linux is supported[/yellow]"
            )
            self.results["os"] = False
            return False

        # Check if Debian-based
        dist_id = distro.id()
        dist_name = distro.name()
        dist_version = distro.version()

        debian_based = dist_id.lower() in [
            "debian",
            "ubuntu",
            "linuxmint",
            "pop",
            "elementary",
        ]

        if debian_based:
            console.print(f"[green]✓ Detected: {dist_name} {dist_version}[/green]")
            self.results["os"] = True
            return True
        else:
            console.print(f"[yellow]⚠ Non-Debian system detected: {dist_name}[/yellow]")
            console.print(
                "[yellow]  Installation may work but is not officially supported[/yellow]"
            )
            self.results["os"] = True  # Allow to proceed with warning
            return True

    def check_ram(self) -> bool:
        """Check available RAM"""
        console.print("[bold]Checking RAM...[/bold]")

        ram_bytes = psutil.virtual_memory().total
        ram_gb = ram_bytes / (1024**3)

        self.results["ram_gb"] = ram_gb

        if ram_gb < self.MIN_RAM_GB:
            console.print(
                f"[red]✗ Insufficient RAM: {ram_gb:.1f}GB (minimum {self.MIN_RAM_GB}GB)[/red]"
            )
            self.results["ram"] = False
            return False
        elif ram_gb < self.RECOMMENDED_RAM_GB:
            console.print(
                f"[yellow]⚠ Low RAM: {ram_gb:.1f}GB (recommended {self.RECOMMENDED_RAM_GB}GB+)[/yellow]"
            )
            console.print(
                "[yellow]  Only small models (3B-7B) will be available[/yellow]"
            )
            self.results["ram"] = True
            return True
        else:
            console.print(f"[green]✓ RAM: {ram_gb:.1f}GB (excellent!)[/green]")
            self.results["ram"] = True
            return True

    def check_storage(self) -> bool:
        """Check available storage space"""
        console.print("[bold]Checking Storage...[/bold]")

        home = Path.home()
        usage = shutil.disk_usage(home)
        free_gb = usage.free / (1024**3)

        self.results["storage_gb"] = free_gb

        if free_gb < self.MIN_STORAGE_GB:
            console.print(
                f"[red]✗ Insufficient storage: {free_gb:.1f}GB free (minimum {self.MIN_STORAGE_GB}GB)[/red]"
            )
            self.results["storage"] = False
            return False
        elif free_gb < self.RECOMMENDED_STORAGE_GB:
            console.print(
                f"[yellow]⚠ Low storage: {free_gb:.1f}GB free (recommended {self.RECOMMENDED_STORAGE_GB}GB+)[/yellow]"
            )
            self.results["storage"] = True
            return True
        else:
            console.print(f"[green]✓ Storage: {free_gb:.1f}GB free[/green]")
            self.results["storage"] = True
            return True

    def check_python(self) -> bool:
        """Check Python version"""
        console.print("[bold]Checking Python...[/bold]")

        version = platform.python_version()
        major, minor = sys.version_info[:2]

        if major >= 3 and minor >= 8:
            console.print(f"[green]✓ Python {version}[/green]")
            self.results["python"] = True
            return True
        else:
            console.print(f"[red]✗ Python {version} (minimum 3.8 required)[/red]")
            self.results["python"] = False
            return False

    def check_command(self, command: str) -> bool:
        """Check if a command exists"""
        return shutil.which(command) is not None

    def check_tools(self) -> bool:
        """Check for required system tools"""
        console.print("[bold]Checking System Tools...[/bold]")

        required = ["curl", "wget", "git"]
        optional = ["bash", "apt-get"]

        all_good = True
        for tool in required:
            if self.check_command(tool):
                console.print(f"[green]✓ {tool} found[/green]")
            else:
                console.print(f"[red]✗ {tool} not found (required)[/red]")
                all_good = False

        for tool in optional:
            if self.check_command(tool):
                console.print(f"[green]✓ {tool} found[/green]")
            else:
                console.print(f"[yellow]⚠ {tool} not found (optional)[/yellow]")

        self.results["tools"] = all_good
        return all_good

    def check_internet(self) -> bool:
        """Check internet connectivity"""
        console.print("[bold]Checking Internet Connection...[/bold]")

        try:
            # Try to reach a common endpoint
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                capture_output=True,
                timeout=3,
            )
            if result.returncode == 0:
                console.print("[green]✓ Internet connection available[/green]")
                self.results["internet"] = True
                return True
            else:
                console.print("[yellow]⚠ No internet connection detected[/yellow]")
                console.print(
                    "[yellow]  Internet required for initial model download[/yellow]"
                )
                self.results["internet"] = False
                return False
        except Exception:
            console.print("[yellow]⚠ Could not verify internet connection[/yellow]")
            self.results["internet"] = False
            return False

    def run_all_checks(self) -> bool:
        """Run all system checks"""
        console.print("\n[bold cyan]Running System Checks...[/bold cyan]\n")

        checks = [
            self.check_os(),
            self.check_ram(),
            self.check_storage(),
            self.check_python(),
            self.check_tools(),
            self.check_internet(),
        ]

        all_passed = all(checks)

        # Summary
        console.print("\n[bold]Summary:[/bold]")
        if all_passed:
            console.print("[green]All checks passed! Ready to proceed.[/green]")
        else:
            console.print("[red]Some checks failed. Please review above.[/red]")

        return all_passed

    def get_recommended_model_size(self) -> str:
        """Get recommended model size based on RAM"""
        ram_gb = self.results.get("ram_gb", 0)

        if ram_gb < 4:
            return "tiny"  # <3B parameters
        elif ram_gb < 8:
            return "small"  # 3B-7B parameters
        elif ram_gb < 16:
            return "medium"  # 7B-13B parameters
        else:
            return "large"  # 13B+ parameters


if __name__ == "__main__":
    import sys as sys_module

    checker = SystemCheck()
    success = checker.run_all_checks()
    sys_module.exit(0 if success else 1)
