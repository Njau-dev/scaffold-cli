"""
Project type definitions and registry
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ProjectConfig:
    """Configuration for a project type"""

    name: str
    display_name: str
    category: str
    command: str
    requires: List[str]
    interactive: bool = True  # Use tool's native prompts?
    post_install: Optional[List[str]] = None  # Commands to run after creation

    def __post_init__(self):
        if self.post_install is None:
            self.post_install = []


# Registry of all supported project types
PROJECTS = {
    "frontend": [
        ProjectConfig(
            name="react-vite",
            display_name="React (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template react",
            requires=["node", "npm"],
            interactive=True,
            post_install=["npm install"],
        ),
        ProjectConfig(
            name="react-vite-ts",
            display_name="React + TypeScript (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template react-ts",
            requires=["node", "npm"],
            interactive=False,  # We specify the template
            post_install=["npm install"],
        ),
        ProjectConfig(
            name="nextjs",
            display_name="Next.js",
            category="frontend",
            command="npx create-next-app@latest {name}",
            requires=["node", "npm"],
            # Next.js will ask about TypeScript, Tailwind, etc.
            interactive=True,
        ),
        ProjectConfig(
            name="vue-vite",
            display_name="Vue (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template vue",
            requires=["node", "npm"],
            interactive=True,
            post_install=["npm install"],
        ),
    ],
    "api": [
        ProjectConfig(
            name="express",
            display_name="Express.js",
            category="api",
            command="npx express-generator {name}",
            requires=["node", "npm"],
            interactive=False,
            post_install=["npm install"],
        ),
        ProjectConfig(
            name="fastapi",
            display_name="FastAPI",
            category="api",
            command="custom:fastapi",  # Custom handler for minimal setup
            requires=["python3"],
            interactive=False,
        ),
    ],
    "framework": [
        ProjectConfig(
            name="django",
            display_name="Django",
            category="framework",
            command="django-admin startproject {name}",
            requires=["python3", "django-admin"],
            interactive=False,
        ),
    ],
}


def get_project_categories() -> List[str]:
    """Get all available project categories"""
    return list(PROJECTS.keys())


def get_projects_by_category(category: str) -> List[ProjectConfig]:
    """Get all projects in a category"""
    return PROJECTS.get(category, [])


def get_project_by_name(name: str) -> Optional[ProjectConfig]:
    """Find a project config by its name"""
    for projects in PROJECTS.values():
        for project in projects:
            if project.name == name:
                return project
    return None
