"""
Main CLI entry point
"""

import typer
from rich.console import Console
from typing import Optional

from .core.orchestrator import ProjectOrchestrator

app = typer.Typer(
    name="scaffold",
    help="🚀 Scaffold CLI - Quickly generate modern development projects",
    add_completion=False,
)
console = Console()


@app.command()
def new(
    name: Optional[str] = typer.Argument(None, help="Project name"),
    monorepo: bool = typer.Option(False, "--monorepo", "-m", help="Create as monorepo"),
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
def info():
    """Show CLI information and version"""
    console.print("\n[bold cyan]📦 Scaffold CLI v0.1.0[/bold cyan]")
    console.print("[dim]A modern project scaffolding tool[/dim]\n")

    console.print("[bold]Supported Technologies:[/bold]")
    console.print("  • Frontend: React, Next.js, Vue")
    console.print("  • APIs: Express, FastAPI")
    console.print("  • Frameworks: Django")
    console.print("  • Monorepo support\n")

    console.print("[bold]Usage:[/bold]")
    console.print("  scaffold new <project-name>")
    console.print("  scaffold new <project-name> --monorepo")
    console.print("  scaffold info")
    console.print("  scaffold --help\n")


@app.callback()
def main():
    """
    Scaffold CLI - Generate modern development projects with ease
    """
    pass


if __name__ == "__main__":
    app()
