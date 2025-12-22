"""
Main orchestration logic for project creation
"""

from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
import questionary

from .project_types import (
    ProjectConfig,
    get_project_categories,
    get_projects_by_category,
)
from .installer import Installer
from ..validators.dependencies import DependencyValidator
from ..utils.git import GitManager

console = Console()


class ProjectOrchestrator:
    """Handles the project creation workflow"""

    def __init__(self):
        self.console = console
        self.validator = DependencyValidator()
        self.installer = Installer()
        self.git_manager = GitManager()

    def create_project(self, name: Optional[str] = None, monorepo: bool = False):
        """Main entry point for project creation"""

        # Welcome message
        self.console.print(
            Panel.fit(
                "🚀 [bold blue]Scaffold CLI[/bold blue] - Project Generator\n"
                "[dim]Quickly scaffold modern development projects with a single command[/dim]",
                border_style="blue",
            )
        )

        # Get project name
        if not name:
            name = questionary.text(
                "📦 Project name:",
                validate=lambda text: len(text) > 0 or "Project name cannot be empty",
            ).ask()

            if name is None:  # User pressed Ctrl+C
                self.console.print("\n[yellow]Cancelled[/yellow]")
                return False

        # Check if directory already exists
        if Path(name).exists():
            self.console.print(f"[red]✗ Directory '{name}' already exists![/red]")
            overwrite = questionary.confirm("Overwrite?", default=False).ask()

            if not overwrite:
                self.console.print("[yellow]Cancelled[/yellow]")
                return False

        # Ask about monorepo
        if not monorepo:
            monorepo = questionary.confirm(
                "🗂️  Create as monorepo?", default=False
            ).ask()

            if monorepo is None:  # User pressed Ctrl+C
                self.console.print("\n[yellow]Cancelled[/yellow]")
                return False

        if monorepo:
            return self._create_monorepo(name)
        else:
            return self._create_single_project(name)

    def _create_single_project(self, name: str) -> bool:
        """Create a single project"""

        self.console.print("\n[bold cyan]→ Single Project Setup[/bold cyan]")

        # Step 1: Choose category with arrow keys
        categories = get_project_categories()
        category = questionary.select(
            "📂 Select project type:",
            choices=[cat.capitalize() for cat in categories],
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if category is None:  # User pressed Ctrl+C
            self.console.print("\n[yellow]Cancelled[/yellow]")
            return False

        category = category.lower()

        # Step 2: Choose specific stack with arrow keys
        projects = get_projects_by_category(category)
        project_choices = [project.display_name for project in projects]

        selected_display_name = questionary.select(
            f"Select {category}:",
            choices=project_choices,
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if selected_display_name is None:  # User pressed Ctrl+C
            self.console.print("\n[yellow]Cancelled[/yellow]")
            return False

        # Find the project config
        project_config = next(
            p for p in projects if p.display_name == selected_display_name
        )

        # Step 3: Validate dependencies
        if not self.validator.validate_and_report(project_config.requires):
            return False

        # Step 4: Install project
        success = self.installer.install(project_config, name)

        if not success:
            return False

        # Step 5: Initialize git
        project_path = Path.cwd() / name
        self.git_manager.init_repository(
            project_path, f"Initial commit - {project_config.display_name} project"
        )

        # Step 6: Show success message
        self._show_success_message(name, project_config)

        return True

    def _create_monorepo(self, name: str) -> bool:
        """Create a monorepo project"""

        self.console.print("\n[bold cyan]→ Monorepo Setup[/bold cyan]")
        self.console.print("[dim]Select frontend and backend technologies[/dim]")

        # Choose frontend with arrow keys
        frontend_projects = get_projects_by_category("frontend")
        frontend_choices = [project.display_name for project in frontend_projects]

        selected_frontend = questionary.select(
            "🎨 Select frontend:",
            choices=frontend_choices,
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if selected_frontend is None:  # User pressed Ctrl+C
            self.console.print("\n[yellow]Cancelled[/yellow]")
            return False

        frontend_config = next(
            p for p in frontend_projects if p.display_name == selected_frontend
        )

        # Choose backend with arrow keys
        api_projects = get_projects_by_category("api")
        api_choices = [project.display_name for project in api_projects]

        selected_api = questionary.select(
            "⚙️  Select backend API:",
            choices=api_choices,
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if selected_api is None:  # User pressed Ctrl+C
            self.console.print("\n[yellow]Cancelled[/yellow]")
            return False

        api_config = next(p for p in api_projects if p.display_name == selected_api)

        # Validate all dependencies
        all_deps = list(set(frontend_config.requires + api_config.requires))
        if not self.validator.validate_and_report(all_deps):
            return False

        # Create monorepo structure
        self.console.print(f"\n[bold yellow]📦 Creating monorepo: {name}[/bold yellow]")

        project_root = Path.cwd() / name
        project_root.mkdir(parents=True, exist_ok=True)

        # Install frontend
        self.console.print("\n[cyan]→ Setting up frontend (web/)...[/cyan]")
        frontend_success = self.installer.install(
            frontend_config,
            "web",
            parent_dir=project_root,
            skip_post_install=True,  # Skip npm install in monorepo
        )

        if not frontend_success:
            self.console.print("[red]✗ Frontend installation failed[/red]")
            return False

        # Install backend
        self.console.print("\n[cyan]→ Setting up backend (api/)...[/cyan]")
        api_success = self.installer.install(
            api_config,
            "api",
            parent_dir=project_root,
            skip_post_install=True,  # Skip post-install in monorepo
        )

        if not api_success:
            self.console.print("[red]✗ Backend installation failed[/red]")
            return False

        # Create root README
        self._create_monorepo_readme(project_root, frontend_config, api_config)

        # Initialize git for the monorepo
        self.git_manager.init_repository(
            project_root, "Initial commit - Monorepo with frontend and backend"
        )

        # Show success
        self._show_monorepo_success(name, frontend_config, api_config)

        return True

    def _show_success_message(self, name: str, config: ProjectConfig):
        """Display success message for single project"""
        from rich.panel import Panel

        self.console.print("\n" + "=" * 70)
        self.console.print(
            f"[bold green]✨ Success![/bold green] Project created: [cyan]{name}[/cyan]"
        )
        self.console.print("=" * 70)

        self.console.print(f"\n[bold]📁 Project Structure:[/bold]")
        self.console.print(f"  {name}/")
        if "node" in config.requires:
            self.console.print("  ├── package.json")
            self.console.print("  ├── src/")
            self.console.print("  └── ...")
        elif "python3" in config.requires:
            if config.name == "django":
                self.console.print("  ├── manage.py")
                self.console.print("  ├── {name}/")
                self.console.print("  └── ...")
            else:
                self.console.print("  ├── main.py")
                self.console.print("  ├── requirements.txt")
                self.console.print("  └── ...")

        # Next steps
        self.console.print(f"\n[bold]🚀 Next Steps:[/bold]")
        self.console.print(f"\n  [bold cyan]1. Navigate to your project:[/bold cyan]")
        self.console.print(f"     cd {name}")

        # Project-specific instructions
        if "node" in config.requires:
            self.console.print(f"\n  [bold cyan]2. Install dependencies:[/bold cyan]")
            self.console.print(f"     npm install")
            self.console.print(
                f"\n  [bold cyan]3. Start development server:[/bold cyan]"
            )
            self.console.print(f"     npm run dev")

            if config.name == "nextjs":
                self.console.print(
                    f"\n  [dim]→ Your Next.js app will be at: http://localhost:3000[/dim]"
                )
            else:
                self.console.print(
                    f"\n  [dim]→ Your app will be at: http://localhost:5173[/dim]"
                )

        elif "python3" in config.requires:
            self.console.print(
                f"\n  [bold cyan]2. Set up virtual environment:[/bold cyan]"
            )
            self.console.print(f"     python3 -m venv venv")
            self.console.print(
                f"     source venv/bin/activate  [dim]# On Windows: venv\\Scripts\\activate[/dim]"
            )

            if config.name == "django":
                self.console.print(
                    f"\n  [bold cyan]3. Install dependencies & migrate:[/bold cyan]"
                )
                self.console.print(f"     pip install django")
                self.console.print(f"     python manage.py migrate")
                self.console.print(
                    f"\n  [bold cyan]4. Start development server:[/bold cyan]"
                )
                self.console.print(f"     python manage.py runserver")
                self.console.print(
                    f"\n  [dim]→ Your Django app will be at: http://127.0.0.1:8000[/dim]"
                )
            elif config.name == "fastapi":
                self.console.print(
                    f"\n  [bold cyan]3. Install dependencies:[/bold cyan]"
                )
                self.console.print(f"     pip install -r requirements.txt")
                self.console.print(
                    f"\n  [bold cyan]4. Start development server:[/bold cyan]"
                )
                self.console.print(f"     uvicorn main:app --reload")
                self.console.print(
                    f"\n  [dim]→ Your API will be at: http://127.0.0.1:8000[/dim]"
                )
                self.console.print(
                    f"  [dim]→ API docs at: http://127.0.0.1:8000/docs[/dim]"
                )

        # Git instructions
        self.console.print(f"\n[bold]🔧 Git Repository:[/bold]")
        self.console.print(
            f"  [green]✓[/green] Repository initialized with first commit"
        )
        self.console.print(
            f"  [green]✓[/green] Default branch set to 'master'")

        self.console.print(
            f"\n  [bold cyan]To push to a remote repository:[/bold cyan]"
        )
        self.console.print(f"     git remote add origin <repository-url>")
        self.console.print(f"     git push -u origin master")

        self.console.print(f"\n  [dim]Example with GitHub:[/dim]")
        self.console.print(
            f"     [dim]git remote add origin git@github.com:username/{name}.git[/dim]"
        )
        self.console.print(f"     [dim]git push -u origin master[/dim]")

        # Footer
        self.console.print(f"\n[bold]📚 Resources:[/bold]")
        self.console.print(
            f"  [cyan]scaffold --help[/cyan]           Show all commands"
        )
        self.console.print(
            f"  [cyan]scaffold list[/cyan]             View available templates"
        )
        self.console.print(f"\n[dim]Happy coding! 🎉[/dim]\n")

    def _show_monorepo_success(
        self, name: str, frontend: ProjectConfig, api: ProjectConfig
    ):
        """Display success message for monorepo"""
        self.console.print("\n" + "=" * 60)
        self.console.print(
            f"[bold green]✨ Success![/bold green] Created monorepo: {name}"
        )
        self.console.print("=" * 60)

        self.console.print(f"\n[bold]Structure:[/bold]")
        self.console.print(f"  {name}/")
        self.console.print(f"  ├── web/     ({frontend.display_name})")
        self.console.print(f"  ├── api/     ({api.display_name})")
        self.console.print(f"  └── README.md")

        self.console.print(f"\n[bold]Next steps:[/bold]")
        self.console.print(f"  cd {name}")

        self.console.print(
            f"\n  [bold cyan]# Install frontend dependencies[/bold cyan]"
        )
        self.console.print(f"  cd web && npm install")

        self.console.print(f"\n  [bold cyan]# Start frontend dev server[/bold cyan]")
        self.console.print(f"  npm run dev")

        self.console.print(
            f"\n  [bold cyan]# Setup backend (in another terminal)[/bold cyan]"
        )
        self.console.print(f"  cd ../api")
        if "python3" in api.requires:
            self.console.print(f"  python3 -m venv venv")
            self.console.print(f"  source venv/bin/activate")
            self.console.print(f"  pip install -r requirements.txt")
        elif "node" in api.requires:
            self.console.print(f"  npm install")

        self.console.print(f"\n[bold]Git:[/bold]")
        self.console.print(f"  ✓ Repository initialized")
        self.console.print(f"  ✓ Initial commit created")

        self.console.print(f"\n[dim]See README.md for detailed instructions[/dim]\n")

    def _create_monorepo_readme(
        self, project_root: Path, frontend: ProjectConfig, api: ProjectConfig
    ):
        """Create README for monorepo"""
        readme_content = f"""# {project_root.name}

Monorepo created with Scaffold CLI.

## Structure

```
{project_root.name}/
├── web/     # {frontend.display_name}
└── api/     # {api.display_name}
```

## Getting Started

### Frontend (web/)

```bash
cd web
npm install
npm run dev
```

### Backend (api/)

```bash
cd api
# Follow setup instructions in api/README.md
```

## Development

Run both services concurrently for full-stack development.

### Frontend
- Default port: 5173 (Vite) or 3000 (Next.js)

### Backend
- Configure API URL in frontend as needed

## Scripts

You can add npm scripts to the root `package.json` to manage both services:

```json
{{
  "scripts": {{
    "dev:web": "cd web && npm run dev",
    "dev:api": "cd api && <start command>",
    "install:all": "cd web && npm install && cd ../api && <install>"
  }}
}}
```
"""

        readme_path = project_root / "README.md"
        readme_path.write_text(readme_content)
