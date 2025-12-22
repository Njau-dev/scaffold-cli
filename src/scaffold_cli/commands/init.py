"""
Scaffold init command - initialize existing projects
"""
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import questionary

from ..detectors.project_detector import ProjectDetector
from ..generators.env_generator import EnvGenerator
from ..generators.docker_generator import DockerGenerator
from ..validators.dependencies import DependencyValidator
from ..utils.command_runner import CommandRunner
from ..utils.git import GitManager

console = Console()


class InitCommand:
    """Handles project initialization"""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.detector = ProjectDetector(self.project_path)
        self.validator = DependencyValidator()
        self.runner = CommandRunner()
        self.git_manager = GitManager()

    def run(self):
        """Main initialization workflow"""
        # Welcome
        console.print()
        console.print(Panel.fit(
            "[bold cyan]🔍 Scaffold Init[/bold cyan]\n"
            "[dim]Analyze and set up your development environment[/dim]",
            border_style="cyan"
        ))

        # Step 1: Detect project
        console.print("\n[yellow]→ Analyzing project...[/yellow]")
        project = self.detector.detect()

        if project.type == 'unknown':
            console.print("[red]✗ Could not detect project type[/red]")
            console.print(
                "[dim]This directory doesn't appear to be a recognized project[/dim]")
            return False

        # Show detection results
        self._display_project_info(project)

        # Step 2: Validate dependencies
        console.print("\n[yellow]→ Checking system dependencies...[/yellow]")
        self._check_system_dependencies(project)

        # Step 3: Install project dependencies
        if not project.dependencies_installed:
            if questionary.confirm(
                "\n📦 Install project dependencies?",
                default=True
            ).ask():
                self._install_dependencies(project)

        # Step 4: Initialize git if needed
        if not project.has_git:
            if questionary.confirm(
                "\n🔧 Initialize git repository?",
                default=True
            ).ask():
                self.git_manager.init_repository(
                    self.project_path,
                    f"Initial commit - {project.type} project"
                )

        # Step 5: Environment setup
        if questionary.confirm(
            "\n🔧 Set up environment configuration?",
            default=True
        ).ask():
            self._setup_environment(project)

        # Step 6: Docker setup
        if questionary.confirm(
            "\n🐳 Set up Docker?",
            default=True
        ).ask():
            self._setup_docker(project)

        # Step 7: Show summary
        self._show_summary(project)

        return True

    def _display_project_info(self, project):
        """Display detected project information"""
        console.print("\n[green]✓ Project detected[/green]\n")

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("📁 Name", project.name)
        table.add_row("🏷️  Type", project.type.upper())

        if project.frameworks:
            table.add_row("🛠️  Frameworks", ", ".join(project.frameworks))

        if project.package_manager:
            table.add_row("📦 Package Manager", project.package_manager)

        # Status indicators
        table.add_row("", "")  # Spacer
        table.add_row(
            "Git",
            "[green]✓ Initialized[/green]" if project.has_git else "[yellow]✗ Not initialized[/yellow]"
        )
        table.add_row(
            "Dependencies",
            "[green]✓ Installed[/green]" if project.dependencies_installed else "[yellow]✗ Not installed[/yellow]"
        )
        table.add_row(
            "Environment",
            "[green]✓ Configured[/green]" if project.has_env else "[yellow]✗ Not configured[/yellow]"
        )
        table.add_row(
            "Docker",
            "[green]✓ Configured[/green]" if project.has_docker else "[yellow]✗ Not configured[/yellow]"
        )

        console.print(table)

    def _check_system_dependencies(self, project):
        """Check required system dependencies"""
        required_tools = []

        # Determine required tools
        if project.package_manager in ['npm', 'yarn', 'pnpm']:
            required_tools.extend(['node', 'npm'])
        elif project.package_manager == 'pip':
            required_tools.extend(['python3', 'pip'])

        if not project.has_git:
            required_tools.append('git')

        # Validate
        all_valid, results = self.validator.validate(required_tools)
        self.validator.display_results(results, show_all=True)

        if not all_valid:
            console.print("\n[yellow]⚠ Some dependencies are missing[/yellow]")
            self.validator.show_installation_hints(results)

            if not questionary.confirm("Continue anyway?", default=False).ask():
                raise SystemExit(1)

    def _install_dependencies(self, project):
        """Install project dependencies"""
        console.print("\n[cyan]→ Installing dependencies...[/cyan]")

        success = False
        pm = project.package_manager

        # Runtime fallback: if detector didn't pick a package manager but package.json exists, assume npm
        if pm is None and (self.project_path / "package.json").exists():
            pm = "npm"

        if pm == 'npm':
            success = self.runner.run(
                "npm install",
                cwd=self.project_path,
                description="Installing npm packages",
                show_output=False
            )
        elif pm == 'yarn':
            success = self.runner.run(
                "yarn install",
                cwd=self.project_path,
                description="Installing yarn packages",
                show_output=False
            )
        elif pm == 'pip':
            # Create venv first
            venv_path = self.project_path / "venv"
            if not venv_path.exists():
                self.runner.run(
                    "python3 -m venv venv",
                    cwd=self.project_path,
                    description="Creating virtual environment"
                )

            # Install requirements
            success = self.runner.run(
                "./venv/bin/pip install -r requirements.txt",
                cwd=self.project_path,
                description="Installing Python packages",
                show_output=False
            )
        else:
            console.print(
                f"[yellow]⚠ Unknown package manager: {project.package_manager}[/yellow]")
            success = False

        if success:
            console.print(
                "[green]✓ Dependencies installed successfully[/green]")
        else:
            console.print(
                "[yellow]⚠ Some dependencies failed to install[/yellow]")

    def _setup_environment(self, project):
        """Interactive environment setup"""
        env_gen = EnvGenerator(
            self.project_path,
            project.type,
            project.name
        )

        if env_gen.interactive_setup():
            env_gen.generate_files()

            summary = env_gen.get_summary()
            console.print(f"\n[green]✓ Environment configured[/green]")
            console.print(
                f"[dim]  → {summary['total_vars']} variables configured[/dim]")
            if summary['categories']:
                console.print(
                    f"[dim]  → Services: {', '.join(summary['categories'])}[/dim]")

    def _setup_docker(self, project):
        """Set up Docker configuration"""
        docker_gen = DockerGenerator(
            self.project_path,
            project.type,
            project.name
        )

        # Ask about docker-compose vs just Dockerfile
        try:
            setup_type = questionary.select(
                "What would you like to set up?",
                choices=[
                    "Dockerfile only",
                    "Docker Compose (recommended)",
                    "Both"
                ]
            ).ask()
        except Exception:
            setup_type = None

        # If running non-interactively, default to recommended compose setup
        if setup_type is None:
            setup_type = "Dockerfile only"

        if setup_type in ["Dockerfile only", "Both"]:
            docker_gen.generate_dockerfile()
            if project.type in ['react', 'vue']:
                docker_gen.generate_nginx_config()

        if setup_type in ["Docker Compose (recommended)", "Both"]:
            with_db = questionary.confirm(
                "Include database in docker-compose?",
                default=False
            ).ask()
            docker_gen.generate_docker_compose(with_database=with_db)

    def _show_summary(self, project):
        """Show initialization summary and next steps"""
        console.print("\n" + "=" * 70)
        console.print("[bold green]✨ Initialization Complete![/bold green]")
        console.print("=" * 70)

        # What was set up
        console.print("\n[bold]🎉 What was set up:[/bold]")

        if not project.dependencies_installed:
            console.print("  [green]✓[/green] Project dependencies installed")

        if not project.has_git:
            console.print("  [green]✓[/green] Git repository initialized")

        if (self.project_path / ".env.example").exists():
            console.print(
                "  [green]✓[/green] Environment configuration created")

        if (self.project_path / "Dockerfile").exists():
            console.print("  [green]✓[/green] Docker configuration added")

        # Next steps
        console.print("\n[bold]🚀 Next Steps:[/bold]")

        step = 1

        # Environment setup
        if (self.project_path / ".env.example").exists():
            console.print(
                f"\n  [bold cyan]{step}. Configure environment:[/bold cyan]")
            console.print("     cp .env.example .env")
            console.print("     # Edit .env with your actual values")
            step += 1

        # Start development
        console.print(f"\n  [bold cyan]{step}. Start development:[/bold cyan]")
        if project.package_manager == 'npm':
            console.print("     npm run dev")
        elif project.package_manager == 'pip':
            if project.type == 'django':
                console.print("     source venv/bin/activate")
                console.print("     python manage.py runserver")
            elif project.type == 'fastapi':
                console.print("     source venv/bin/activate")
                console.print("     uvicorn main:app --reload")
        step += 1

        # Docker instructions
        if (self.project_path / "Dockerfile").exists():
            console.print(f"\n  [bold cyan]{step}. Or use Docker:[/bold cyan]")

            if (self.project_path / "docker-compose.yml").exists():
                console.print("     docker-compose up")
            else:
                console.print("     docker build -t {} .".format(project.name))
                console.print(
                    "     docker run -p 8000:8000 {}".format(project.name))

        # Resources
        console.print("\n[bold]📚 Resources:[/bold]")
        console.print("  [cyan]scaffold --help[/cyan]     Show all commands")
        console.print(
            "  [cyan]scaffold list[/cyan]      View available templates")

        console.print("\n[dim]Happy coding! 🎉[/dim]\n")
