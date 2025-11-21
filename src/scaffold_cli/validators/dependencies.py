import shutil
import subprocess
import re
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.table import Table

console = Console()


class DependencyValidator:
    """Validates system dependencies"""

    # Tool configurations
    TOOLS = {
        'node': {
            'check': 'node --version',
            'install_hint': 'https://nodejs.org/',
            'min_version': '18.0.0',
            'description': 'Node.js runtime'
        },
        'npm': {
            'check': 'npm --version',
            'install_hint': 'https://nodejs.org/ (comes with Node.js)',
            'min_version': '9.0.0',
            'description': 'Node package manager'
        },
        'python3': {
            'check': 'python3 --version',
            'install_hint': 'https://python.org/',
            'min_version': '3.10.0',
            'description': 'Python 3 runtime'
        },
        'pip': {
            'check': 'pip --version',
            'install_hint': 'python3 -m ensurepip',
            'min_version': '20.0.0',
            'description': 'Python package manager'
        },
        'django-admin': {
            'check': 'django-admin --version',
            'install_hint': 'pip install django',
            'min_version': None,
            'description': 'Django CLI'
        },
        'composer': {
            'check': 'composer --version',
            'install_hint': 'https://getcomposer.org/',
            'min_version': None,
            'description': 'PHP dependency manager'
        }
    }

    def validate(self, required: List[str]) -> Tuple[bool, Dict[str, Dict]]:
        """
        Validate all required tools are available

        Args:
            required: List of required tool names

        Returns:
            Tuple of (all_valid, results_dict)
        """
        results = {}
        all_valid = True

        for tool in required:
            if tool not in self.TOOLS:
                console.print(f"[yellow]⚠ Unknown tool: {tool}[/yellow]")
                continue

            is_available, version = self._check_tool(tool)
            results[tool] = {
                'available': is_available,
                'version': version,
                'config': self.TOOLS[tool]
            }

            if not is_available:
                all_valid = False

        return all_valid, results

    def _check_tool(self, tool: str) -> Tuple[bool, Optional[str]]:
        """Check if a single tool is available"""
        # First check if command exists
        tool_cmd = tool.split()[0]
        if not shutil.which(tool_cmd):
            return False, None

        # Get version
        try:
            check_cmd = self.TOOLS[tool]['check']
            result = subprocess.run(
                check_cmd.split(),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False, None

            # Extract version from output
            version = self._extract_version(result.stdout + result.stderr)
            return True, version

        except (subprocess.TimeoutExpired, Exception) as e:
            console.print(f"[dim]Error checking {tool}: {e}[/dim]")
            return False, None

    def _extract_version(self, output: str) -> str:
        """Extract version number from command output"""
        # Common version patterns
        patterns = [
            r'v?(\d+\.\d+\.\d+)',  # 1.2.3 or v1.2.3
            r'version\s+(\d+\.\d+\.\d+)',  # version 1.2.3
            r'(\d+\.\d+)',  # 1.2
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)

        return 'unknown'

    def display_results(self, results: Dict[str, Dict], show_all: bool = False):
        """Display validation results in a nice table"""
        table = Table(title="Dependency Check")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Version", style="dim")
        table.add_column("Description", style="dim")

        for tool, info in results.items():
            if info['available']:
                status = "[green]✓ Installed[/green]"
                version = info['version']
            else:
                status = "[red]✗ Missing[/red]"
                version = "-"

            if show_all or not info['available']:
                table.add_row(
                    tool,
                    status,
                    version,
                    info['config']['description']
                )

        console.print(table)

    def show_installation_hints(self, results: Dict[str, Dict]):
        """Show how to install missing dependencies"""
        missing = [
            (tool, info) for tool, info in results.items()
            if not info['available']
        ]

        if not missing:
            return

        console.print("\n[bold red]Missing Dependencies:[/bold red]")
        for tool, info in missing:
            console.print(
                f"\n[bold]{tool}[/bold] - {info['config']['description']}")
            console.print(
                f"  Install: [blue]{info['config']['install_hint']}[/blue]")

    def validate_and_report(self, required: List[str]) -> bool:
        """Validate dependencies and show detailed report"""
        console.print("\n[yellow]⚙️  Checking dependencies...[/yellow]")

        all_valid, results = self.validate(required)

        # Show results
        self.display_results(results, show_all=False)

        if all_valid:
            console.print("\n[green]✓ All dependencies are installed![/green]")
            return True
        else:
            self.show_installation_hints(results)
            console.print(
                "\n[red]✗ Please install missing dependencies and try again[/red]")
            return False
