"""
Project type detection - analyzes existing projects
"""
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
import json
from rich.console import Console

console = Console()


@dataclass
class DetectedProject:
    """Information about a detected project"""
    type: str  # 'react', 'nextjs', 'django', 'fastapi', 'express', 'unknown'
    name: str
    path: Path
    package_manager: Optional[str] = None  # 'npm', 'yarn', 'pnpm', 'pip'
    has_git: bool = False
    has_env: bool = False
    has_docker: bool = False
    dependencies_installed: bool = False
    python_version: Optional[str] = None
    node_version: Optional[str] = None
    frameworks: List[str] = None

    def __post_init__(self):
        if self.frameworks is None:
            self.frameworks = []


class ProjectDetector:
    """Detects project type and configuration"""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()

    def detect(self) -> DetectedProject:
        """Analyze the project and detect its type"""
        project_name = self.project_path.name

        # Check for common markers
        has_git = (self.project_path / ".git").exists()
        has_env = (self.project_path / ".env").exists()
        has_docker = (self.project_path / "Dockerfile").exists()

        # Detect project type
        project_type = self._detect_type()
        package_manager = self._detect_package_manager()
        frameworks = self._detect_frameworks()
        deps_installed = self._check_dependencies_installed()

        # Debug detected information
        console.print(f"Detected project type: {project_type}")
        console.print(f"Detected package manager: {package_manager}")
        console.print(f"Detected frameworks: {frameworks}")
        console.print(f"Dependencies installed: {deps_installed}")

        return DetectedProject(
            type=project_type,
            name=project_name,
            path=self.project_path,
            package_manager=package_manager,
            has_git=has_git,
            has_env=has_env,
            has_docker=has_docker,
            dependencies_installed=deps_installed,
            frameworks=frameworks
        )

    def _detect_type(self) -> str:
        """Detect the primary project type"""
        # Check for Node.js projects
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}),
                            **data.get('devDependencies', {})}

                    # Check for specific frameworks
                    if 'next' in deps:
                        return 'nextjs'
                    elif 'react' in deps or 'react-dom' in deps:
                        return 'react'
                    elif 'vue' in deps:
                        return 'vue'
                    elif 'express' in deps:
                        return 'express'
                    else:
                        return 'nodejs'
            except:
                return 'nodejs'

        # Check for Python projects
        if (self.project_path / "manage.py").exists():
            return 'django'

        if (self.project_path / "main.py").exists():
            # Check if it's FastAPI
            req_file = self.project_path / "requirements.txt"
            if req_file.exists():
                content = req_file.read_text()
                if 'fastapi' in content.lower():
                    return 'fastapi'
                elif 'flask' in content.lower():
                    return 'flask'
            return 'python'

        if (self.project_path / "requirements.txt").exists():
            return 'python'

        if (self.project_path / "pyproject.toml").exists():
            return 'python'

        # Check for monorepo
        web_dir = self.project_path / "web"
        api_dir = self.project_path / "api"
        if web_dir.exists() and api_dir.exists():
            return 'monorepo'

        return 'unknown'

    def _detect_package_manager(self) -> Optional[str]:
        """Detect which package manager is used"""
        # lockfile checks (keep existing order)
        if (self.project_path / "package-lock.json").exists():
            return 'npm'
        elif (self.project_path / "yarn.lock").exists():
            return 'yarn'
        elif (self.project_path / "pnpm-lock.yaml").exists():
            return 'pnpm'
        # python checks (existing)
        elif (self.project_path / "requirements.txt").exists() or \
             (self.project_path / "pyproject.toml").exists():
            return 'pip'

        # Fallback: if package.json exists, default to npm (or detect packageManager field)
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                pkg_mgr_field = data.get("packageManager")
                if isinstance(pkg_mgr_field, str):
                    # common format: "pnpm@8.0.0" or "yarn@1.22.0"
                    for key in ("pnpm", "yarn", "npm"):
                        if key in pkg_mgr_field:
                            return key
            except Exception:
                pass
            return 'npm'

        return None

    def _detect_frameworks(self) -> List[str]:
        """Detect all frameworks and libraries used"""
        frameworks = []

        # Check package.json
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}),
                            **data.get('devDependencies', {})}

                    # Common frameworks
                    framework_map = {
                        'react': 'React',
                        'next': 'Next.js',
                        'vue': 'Vue',
                        'express': 'Express.js',
                        'tailwindcss': 'Tailwind CSS',
                        'typescript': 'TypeScript',
                        'vite': 'Vite'
                    }

                    for key, name in framework_map.items():
                        if key in deps:
                            frameworks.append(name)
            except:
                pass

        # Check requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text().lower()
            if 'django' in content:
                frameworks.append('Django')
            if 'fastapi' in content:
                frameworks.append('FastAPI')
            if 'flask' in content:
                frameworks.append('Flask')

        return frameworks

    def _check_dependencies_installed(self) -> bool:
        """Check if dependencies are installed"""
        # Check node_modules
        if (self.project_path / "package.json").exists():
            return (self.project_path / "node_modules").exists()

        # Check venv for Python
        if (self.project_path / "requirements.txt").exists():
            return (self.project_path / "venv").exists() or \
                   (self.project_path / ".venv").exists()

        return True  # Assume installed if we can't determine

    def get_missing_files(self) -> List[str]:
        """Get list of recommended files that are missing"""
        missing = []

        if not (self.project_path / ".gitignore").exists():
            missing.append(".gitignore")

        if not (self.project_path / ".env.example").exists():
            missing.append(".env.example")

        if not (self.project_path / "README.md").exists():
            missing.append("README.md")

        if not (self.project_path / "Dockerfile").exists():
            missing.append("Dockerfile")

        # Check for CI/CD
        github_dir = self.project_path / ".github" / "workflows"
        if not github_dir.exists():
            missing.append(".github/workflows/")

        return missing
