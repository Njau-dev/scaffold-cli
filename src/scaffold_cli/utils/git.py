"""
Git operations and repository initialization
"""

import subprocess
from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()


class GitManager:
    """Handles Git repository operations"""

    def __init__(self):
        self.console = console

    def is_git_available(self) -> bool:
        """Check if git is installed"""
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def init_repository(
        self,
        project_path: Path,
        initial_message: str = "Initial commit from Scaffold CLI",
    ) -> bool:
        """
        Initialize a git repository with an initial commit

        Args:
            project_path: Path to the project
            initial_message: Commit message

        Returns:
            True if successful
        """
        if not self.is_git_available():
            self.console.print(
                "\n[yellow]⚠  Git not installed - skipping repository initialization[/yellow]"
            )
            self.console.print("[dim]   Install git from: https://git-scm.com/[/dim]")
            return False

        try:
            # Check if already a git repo
            git_dir = project_path / ".git"
            if git_dir.exists():
                self.console.print("\n[dim]Git repository already initialized[/dim]")
                return True

            self.console.print("\n[cyan]→ Initializing git repository...[/cyan]")

            # Initialize repo
            result = subprocess.run(
                ["git", "init"],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Create/update .gitignore if needed
            self._ensure_gitignore(project_path)

            # Configure git to avoid warnings about line endings
            subprocess.run(
                ["git", "config", "core.autocrlf", "input"],
                cwd=project_path,
                capture_output=True,
            )

            # Stage all files
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Check if there are files to commit
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True,
            )

            if status_result.stdout.strip():
                # Initial commit
                result = subprocess.run(
                    ["git", "commit", "-m", initial_message],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                # Set default branch to master
                subprocess.run(
                    ["git", "branch", "-M", "master"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                self.console.print(
                    "[green]✓ Git repository initialized successfully[/green]"
                )
                self.console.print("[dim]  → Branch: master[/dim]")
                self.console.print("[dim]  → Initial commit created[/dim]")
            else:
                self.console.print("[yellow]⚠  No files to commit[/yellow]")

            return True

        except subprocess.CalledProcessError as e:
            self.console.print(f"[yellow]⚠  Git initialization failed[/yellow]")
            if e.stderr:
                self.console.print(f"[dim]   Error: {e.stderr.strip()}[/dim]")
            return False
        except Exception as e:
            self.console.print(f"[yellow]⚠  Unexpected error: {str(e)}[/yellow]")
            return False

    def _ensure_gitignore(self, project_path: Path):
        """Ensure a basic .gitignore exists"""
        gitignore_path = project_path / ".gitignore"

        # Don't overwrite existing .gitignore
        if gitignore_path.exists():
            return

        # Create a minimal .gitignore
        basic_gitignore = """# Dependencies
node_modules/
venv/
__pycache__/
*.pyc

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build outputs
dist/
build/
*.egg-info/
"""
        gitignore_path.write_text(basic_gitignore)

    def get_remote_instructions(self, project_name: str) -> str:
        """Get instructions for adding a remote"""
        return f"""
[bold]To push to a remote repository:[/bold]

  # Create a new repository on GitHub/GitLab/etc., then:
  git remote add origin <your-repo-url>
  git push -u origin master

[dim]Example with GitHub:[/dim]
  git remote add origin git@github.com:username/{project_name}.git
  git push -u origin master
"""
