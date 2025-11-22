"""
Command execution utilities
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class CommandRunner:
    """Handles running shell commands with nice output"""

    def __init__(self):
        self.console = console

    def run(
        self,
        command: str,
        cwd: Optional[Path] = None,
        description: str = "Running command",
        show_output: bool = False,
    ) -> bool:
        """
        Run a shell command with progress indication

        Args:
            command: Command to run
            cwd: Working directory
            description: Description to show user
            show_output: Whether to show command output in real-time

        Returns:
            True if command succeeded
        """
        if show_output:
            return self._run_interactive(command, cwd, description)
        else:
            return self._run_with_spinner(command, cwd, description)

    def _run_interactive(
        self, command: str, cwd: Optional[Path], description: str
    ) -> bool:
        """Run command and show output in real-time with proper TTY"""
        console.print(f"\n[cyan]→ {description}...[/cyan]")
        console.print(f"[dim]$ {command}[/dim]\n")

        try:
            # Run with shell and inherit stdin/stdout/stderr for full interactivity
            process = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )

            if process.returncode == 0:
                console.print(f"\n[green]✓ {description} completed[/green]")
                return True
            else:
                console.print(
                    f"\n[red]✗ {description} failed (exit code: {process.returncode})[/red]"
                )
                return False

        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def _run_with_spinner(
        self, command: str, cwd: Optional[Path], description: str
    ) -> bool:
        """Run command with a spinner (hides output)"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(description, total=None)

            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                if result.returncode == 0:
                    console.print(f"[green]✓ {description}[/green]")
                    return True
                else:
                    console.print(f"[red]✗ {description} failed[/red]")
                    if result.stderr:
                        console.print(f"[dim]{result.stderr[:500]}[/dim]")
                    return False

            except subprocess.TimeoutExpired:
                console.print(f"[red]✗ {description} timed out[/red]")
                return False
            except Exception as e:
                console.print(f"[red]✗ Error: {e}[/red]")
                return False

    def run_multiple(
        self,
        commands: List[str],
        cwd: Optional[Path] = None,
        descriptions: Optional[List[str]] = None,
        show_output: bool = False,
    ) -> bool:
        """
        Run multiple commands in sequence

        Returns True only if all commands succeed
        """
        if descriptions is None:
            descriptions = [f"Command {i+1}" for i in range(len(commands))]

        for cmd, desc in zip(commands, descriptions):
            if not self.run(cmd, cwd, desc, show_output):
                return False

        return True
