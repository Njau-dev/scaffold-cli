import subprocess
from pathlib import Path
from typing import Optional
from rich.console import Console

from .project_types import ProjectConfig
from scaffold_cli.utils.command_runner import CommandRunner

console = Console()


class Installer:
    """Handles actual project creation"""

    def __init__(self):
        self.console = console
        self.runner = CommandRunner()

    def install(
        self,
        config: ProjectConfig,
        project_name: str,
        parent_dir: Optional[Path] = None
    ) -> bool:
        """
        Install a project based on its configuration

        Args:
            config: Project configuration
            project_name: Name of the project to create
            parent_dir: Parent directory (defaults to current directory)

        Returns:
            True if installation succeeded
        """
        if parent_dir is None:
            parent_dir = Path.cwd()

        project_path = parent_dir / project_name

        # Handle custom installers
        if config.command.startswith('custom:'):
            return self._handle_custom_install(config, project_path)

        # Run the main installation command
        console.print(
            f"\n[bold cyan]📦 Creating {config.display_name} project...[/bold cyan]")

        # Format the command with project name
        command = config.command.format(name=project_name)

        # For interactive tools, show output. Otherwise use spinner.
        success = self.runner.run(
            command=command,
            cwd=parent_dir,
            description=f"Installing {config.display_name}",
            show_output=config.interactive
        )

        if not success:
            console.print(f"[red]✗ Failed to create project[/red]")
            return False

        # Run post-install commands
        if config.post_install:
            return self._run_post_install(config, project_path)

        return True

    def _run_post_install(self, config: ProjectConfig, project_path: Path) -> bool:
        """Run post-installation commands"""
        console.print(f"\n[yellow]⚙️  Running post-install steps...[/yellow]")

        for cmd in config.post_install:
            # Change to project directory for post-install commands
            success = self.runner.run(
                command=cmd,
                cwd=project_path,
                description=f"Running: {cmd}",
                show_output=False
            )

            if not success:
                console.print(
                    f"[yellow]⚠ Post-install step failed: {cmd}[/yellow]")
                console.print("[dim]You may need to run this manually[/dim]")
                # Don't fail the whole installation for post-install failures

        return True

    def _handle_custom_install(self, config: ProjectConfig, project_path: Path) -> bool:
        """Handle custom installation types"""
        custom_type = config.command.split(':')[1]

        if custom_type == 'fastapi':
            return self._create_fastapi_project(project_path)

        console.print(f"[red]Unknown custom installer: {custom_type}[/red]")
        return False

    def _create_fastapi_project(self, project_path: Path) -> bool:
        """Create a minimal FastAPI project"""
        console.print(
            f"\n[bold cyan]📦 Creating FastAPI project...[/bold cyan]")

        try:
            # Create project structure
            project_path.mkdir(parents=True, exist_ok=True)

            # Create main.py
            main_py = project_path / "main.py"
            main_py.write_text('''"""
FastAPI application
"""
from fastapi import FastAPI

app = FastAPI(title="My API")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello World", "status": "ok"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
''')

            # Create requirements.txt
            requirements = project_path / "requirements.txt"
            requirements.write_text('''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
''')

            # Create README.md
            readme = project_path / "README.md"
            readme.write_text(f'''# {project_path.name}

FastAPI project created with Scaffold CLI.

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Visit: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
''')

            # Create .gitignore
            gitignore = project_path / ".gitignore"
            gitignore.write_text('''__pycache__/
*.py[cod]
*$py.class
venv/
.env
.venv
.pytest_cache/
.coverage
*.log
''')

            console.print(
                f"[green]✓ FastAPI project created successfully[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ Error creating FastAPI project: {e}[/red]")
            return False
