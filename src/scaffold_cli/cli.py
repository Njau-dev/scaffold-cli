"""
Main CLI entry point
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from rich.panel import Panel
import sys
import platform
from pathlib import Path

from .core.orchestrator import ProjectOrchestrator
from .core.project_types import PROJECTS
from .validators.dependencies import DependencyValidator
from .commands.init import InitCommand

app = typer.Typer(
    name="scaffold",
    help="""
    🚀 Scaffold CLI - Modern Project Generator
    
    Quickly create production-ready projects with best practices built-in.
    Supports React, Vue, Next.js, Django, FastAPI, Express, and more!
    
    Examples:
    
      $ scaffold new my-app
      $ scaffold new my-fullstack --monorepo
      $ scaffold list
      $ scaffold info
    
    Documentation: https://github.com/Njau-dev/scaffold-cli#readme
    """,
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()

# Version
__version__ = "0.1.0"


@app.command()
def new(
    name: Optional[str] = typer.Argument(None, help="Project name"),
    monorepo: bool = typer.Option(
        False, "--monorepo", "-m", help="Create as monorepo")
):
    """
    Create a new project
    
    Examples:
    
        scaffold new myapp
        
        scaffold new my-fullstack --monorepo
    """
    orchestrator = ProjectOrchestrator()
    success = orchestrator.create_project(name=name, monorepo=monorepo)

    if not success:
        raise typer.Exit(1)

    console.print("\n[green]✨ Ready to build something awesome![/green]")


@app.command()
def init(
    path: Optional[str] = typer.Argument(
        None, help="Project directory (defaults to current)")
):
    """
    Initialize an existing project
    
    Analyzes your project, installs dependencies, and sets up:
    - Environment variables
    - Docker configuration
    - Git repository
    
    Works with scaffold-generated projects or any existing codebase!
    
    Examples:
    
        scaffold init                    # Initialize current directory
        
        scaffold init ./my-project       # Initialize specific project
    """
    project_path = Path(path) if path else Path.cwd()

    if not project_path.exists():
        console.print(f"[red]✗ Directory not found: {project_path}[/red]")
        raise typer.Exit(1)

    init_cmd = InitCommand(project_path)
    success = init_cmd.run()

    if not success:
        raise typer.Exit(1)

@app.command()
def info():
    """Show detailed CLI information"""

    # Header
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Scaffold CLI[/bold cyan] [dim]v{__version__}[/dim]\n"
        "[dim]A modern project scaffolding tool for developers[/dim]",
        border_style="cyan"
    ))

    # Features
    console.print("\n[bold]✨ Features:[/bold]")
    console.print("  • 🎨 Interactive project setup with arrow-key navigation")
    console.print(
        "  • 📦 Multiple tech stacks (React, Vue, Next.js, Django, FastAPI, Express)")
    console.print("  • 🗂️  Full-stack monorepo support")
    console.print("  • ✅ Automatic dependency validation")
    console.print("  • 🔧 Git repository initialization")
    console.print("  • 🚀 Zero configuration required")

    # Supported Technologies
    console.print("\n[bold]🛠️  Supported Technologies:[/bold]")

    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Technologies", style="white")

    table.add_row("Frontend", "React (Vite), React + TypeScript, Next.js, Vue")
    table.add_row("Backend APIs", "Express.js, FastAPI")
    table.add_row("Frameworks", "Django")
    table.add_row("Monorepo", "Any frontend + backend combination")

    console.print(table)

    # Quick Start
    console.print("\n[bold]🚀 Quick Start:[/bold]")
    console.print(
        "  [cyan]scaffold new[/cyan] [dim]<project-name>[/dim]          Create a new project")
    console.print(
        "  [cyan]scaffold new[/cyan] [dim]<project-name>[/dim] [yellow]--monorepo[/yellow]  Create a monorepo")
    console.print(
        "  [cyan]scaffold list[/cyan]                        List all templates")

    # More Commands
    console.print("\n[bold]📚 More Commands:[/bold]")
    console.print("  [cyan]scaffold --help[/cyan]     Show detailed help")
    console.print("  [cyan]scaffold version[/cyan]    Show version")

    # Links
    console.print("\n[bold]🔗 Links:[/bold]")
    console.print(
        "  GitHub: [blue]https://github.com/Njau-dev/scaffold-cli[/blue]")
    console.print(
        "  Issues: [blue]https://github.com/Njau-dev/scaffold-cli/issues[/blue]")

    console.print()


@app.command()
def list():
    """List all available project templates"""

    console.print()
    console.print(Panel.fit(
        "[bold cyan]📋 Available Project Templates[/bold cyan]\n"
        "[dim]Use 'scaffold new' to create a project with any template[/dim]",
        border_style="cyan"
    ))

    total_templates = 0

    for category, projects in PROJECTS.items():
        console.print(f"\n[bold cyan]{'─' * 60}[/bold cyan]")
        console.print(f"[bold white]{category.upper()}[/bold white]\n")

        table = Table(show_header=True, header_style="bold",
                      box=None, padding=(0, 2))
        table.add_column("Template", style="cyan", no_wrap=True)
        table.add_column("Name", style="white")
        table.add_column("Requirements", style="dim")

        for project in projects:
            table.add_row(
                f"→ {project.name}",
                project.display_name,
                ", ".join(project.requires)
            )
            total_templates += 1

        console.print(table)

    console.print(f"\n[dim]Total: {total_templates} templates available[/dim]")
    console.print("\n[bold]Examples:[/bold]")
    console.print(
        "  [cyan]scaffold new my-app[/cyan]              [dim]# Create a single project[/dim]")
    console.print(
        "  [cyan]scaffold new my-app --monorepo[/cyan]   [dim]# Create a monorepo[/dim]")
    console.print()


@app.command()
def version():
    """Show version and system information"""

    # Version info
    version_info = f"[bold cyan]Scaffold CLI[/bold cyan] [white]v{__version__}[/white]"

    # System info
    system_info = f"""[dim]Python: {sys.version.split()[0]}
Platform: {platform.system()} {platform.release()}
Architecture: {platform.machine()}[/dim]"""

    console.print()
    console.print(Panel(
        f"{version_info}\n\n{system_info}",
        border_style="cyan",
        padding=(1, 2)
    ))

    # Check for dependencies
    console.print("\n[bold]Available Tools:[/bold]")
    validator = DependencyValidator()

    tools_to_check = ['node', 'npm', 'python3', 'git']
    all_valid, results = validator.validate(tools_to_check)

    for tool in tools_to_check:
        if tool in results and results[tool]['available']:
            version = results[tool]['version']
            console.print(f"  [green]✓[/green] {tool:12} [dim]{version}[/dim]")
        else:
            console.print(f"  [red]✗[/red] {tool:12} [dim]not found[/dim]")

    console.print()


@app.command()
def test():
    """Test command"""
    console.print("Test command")

@app.callback()
def main():
    """
    Scaffold CLI - Generate modern development projects with ease

    Run 'scaffold --help' for more information.
    """
    pass


if __name__ == "__main__":
    app()
