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
    interactive: bool = True
    post_install: Optional[List[str]] = None
    language: str = "javascript"

    def __post_init__(self):
        if self.post_install is None:
            self.post_install = []


# Registry of all supported project types
PROJECTS = {
    # ============================================
    # FRONTEND
    # ============================================
    "frontend": [
        ProjectConfig(
            name="react-vite",
            display_name="React (Vite)",
            category="frontend",
            command="npm create vite@latest {name}",
            requires=["node", "npm"],
            interactive=True,
            language="javascript",
        ),
        ProjectConfig(
            name="react-vite-ts",
            display_name="React + TypeScript (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template react-ts",
            requires=["node", "npm"],
            interactive=True,
            language="typescript",
        ),
        ProjectConfig(
            name="nextjs",
            display_name="Next.js",
            category="frontend",
            command="npx create-next-app@latest {name}",
            requires=["node", "npm"],
            interactive=True,
            language="javascript",
        ),
        ProjectConfig(
            name="vue-vite",
            display_name="Vue (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template vue",
            requires=["node", "npm"],
            interactive=True,
            language="javascript",
        ),
        ProjectConfig(
            name="vue-vite-ts",
            display_name="Vue + TypeScript (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template vue-ts",
            requires=["node", "npm"],
            interactive=True,
            language="typescript",
        ),
        ProjectConfig(
            name="svelte",
            display_name="Svelte (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template svelte",
            requires=["node", "npm"],
            interactive=True,
            language="javascript",
        ),
        ProjectConfig(
            name="svelte-ts",
            display_name="Svelte + TypeScript (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template svelte-ts",
            requires=["node", "npm"],
            interactive=True,
            language="typescript",
        ),
        ProjectConfig(
            name="solidjs",
            display_name="Solid.js (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template solid",
            requires=["node", "npm"],
            interactive=True,
            language="javascript",
        ),
        ProjectConfig(
            name="solidjs-ts",
            display_name="Solid.js + TypeScript (Vite)",
            category="frontend",
            command="npm create vite@latest {name} -- --template solid-ts",
            requires=["node", "npm"],
            interactive=True,
            language="typescript",
        ),
        ProjectConfig(
            name="astro",
            display_name="Astro",
            category="frontend",
            command="npm create astro@latest {name}",
            requires=["node", "npm"],
            interactive=True,
            language="javascript",
        ),
        ProjectConfig(
            name="angular",
            display_name="Angular",
            category="frontend",
            command="npx @angular/cli new {name}",
            requires=["node", "npm"],
            interactive=True,
            language="typescript",
        ),
    ],
    # ============================================
    # API / BACKEND
    # ============================================
    "api": [
        # Node.js
        ProjectConfig(
            name="express",
            display_name="Express.js",
            category="api",
            command="npx express-generator {name} --view=ejs --git",
            requires=["node", "npm"],
            interactive=False,
            language="javascript",
        ),
        ProjectConfig(
            name="express-ts",
            display_name="Express + TypeScript",
            category="api",
            command="custom:express-ts",
            requires=["node", "npm"],
            interactive=False,
            language="typescript",
        ),
        ProjectConfig(
            name="nestjs",
            display_name="NestJS",
            category="api",
            command="npx @nestjs/cli new {name}",
            requires=["node", "npm"],
            interactive=True,
            language="typescript",
        ),
        # Python
        ProjectConfig(
            name="fastapi",
            display_name="FastAPI",
            category="api",
            command="custom:fastapi",
            requires=["python3"],
            interactive=False,
            language="python",
        ),
        ProjectConfig(
            name="flask",
            display_name="Flask",
            category="api",
            command="custom:flask",
            requires=["python3"],
            interactive=False,
            language="python",
        ),
        # Go
        ProjectConfig(
            name="go-gin",
            display_name="Go (Gin)",
            category="api",
            command="custom:go-gin",
            requires=["go"],
            interactive=False,
            language="go",
        ),
        ProjectConfig(
            name="go-fiber",
            display_name="Go (Fiber)",
            category="api",
            command="custom:go-fiber",
            requires=["go"],
            interactive=False,
            language="go",
        ),
        ProjectConfig(
            name="go-echo",
            display_name="Go (Echo)",
            category="api",
            command="custom:go-echo",
            requires=["go"],
            interactive=False,
            language="go",
        ),
        # Rust
        ProjectConfig(
            name="rust-axum",
            display_name="Rust (Axum)",
            category="api",
            command="custom:rust-axum",
            requires=["cargo"],
            interactive=False,
            language="rust",
        ),
        ProjectConfig(
            name="rust-actix",
            display_name="Rust (Actix-web)",
            category="api",
            command="custom:rust-actix",
            requires=["cargo"],
            interactive=False,
            language="rust",
        ),
        # Django api
        ProjectConfig(
            name="django-drf",
            display_name="Django REST Framework",
            category="api",
            command="custom:django-drf",
            requires=["python3"],
            interactive=False,
            language="python",
        ),
        # ruby api
        ProjectConfig(
            name="rails-api",
            display_name="Ruby on Rails (API)",
            category="api",
            command="rails new {name} --api",
            requires=["ruby", "rails"],
            interactive=False,
            language="ruby",
        ),
    ],
    # ============================================
    # FULL-STACK FRAMEWORKS
    # ============================================
    "framework": [
        # Python
        ProjectConfig(
            name="django",
            display_name="Django",
            category="framework",
            command="django-admin startproject {name}",
            requires=["python3", "django-admin"],
            interactive=False,
            language="python",
        ),
        # PHP
        ProjectConfig(
            name="laravel",
            display_name="Laravel",
            category="framework",
            command="composer create-project laravel/laravel {name}",
            requires=["composer", "php"],
            interactive=False,
            language="php",
        ),
        # Ruby
        ProjectConfig(
            name="rails",
            display_name="Ruby on Rails",
            category="framework",
            command="rails new {name}",
            requires=["ruby", "rails"],
            interactive=False,
            language="ruby",
        ),
        ProjectConfig(
            name="sveltekit",
            display_name="SvelteKit",
            category="framework",
            command="npm create svelte@latest {name}",
            requires=["node", "npm"],
            interactive=True,
            language="javascript",
        ),
    ],
    # ============================================
    # MOBILE
    # ============================================
    "mobile": [
        ProjectConfig(
            name="react-native",
            display_name="React Native",
            category="mobile",
            command="npx react-native@latest init {name}",
            requires=["node", "npm"],
            interactive=False,
            language="javascript",
        ),
        ProjectConfig(
            name="expo",
            display_name="Expo (React Native)",
            category="mobile",
            command="npx create-expo-app@latest {name}",
            requires=["node", "npm"],
            interactive=True,
            language="javascript",
        ),
        ProjectConfig(
            name="flutter",
            display_name="Flutter",
            category="mobile",
            command="flutter create {name}",
            requires=["flutter"],
            interactive=False,
            language="dart",
        ),
    ],
    # ============================================
    # CLI APPS
    # ============================================
    "cli": [
        # Python
        ProjectConfig(
            name="python-cli-typer",
            display_name="Python CLI (Typer)",
            category="cli",
            command="custom:python-cli-typer",
            requires=["python3"],
            interactive=False,
            language="python",
        ),
        ProjectConfig(
            name="python-cli-click",
            display_name="Python CLI (Click)",
            category="cli",
            command="custom:python-cli-click",
            requires=["python3"],
            interactive=False,
            language="python",
        ),
        # Node.js
        ProjectConfig(
            name="node-cli",
            display_name="Node.js CLI",
            category="cli",
            command="custom:node-cli",
            requires=["node", "npm"],
            interactive=False,
            language="javascript",
        ),
        ProjectConfig(
            name="node-cli-ts",
            display_name="Node.js CLI (TypeScript)",
            category="cli",
            command="custom:node-cli-ts",
            requires=["node", "npm"],
            interactive=False,
            language="typescript",
        ),
        # Go
        ProjectConfig(
            name="go-cli-cobra",
            display_name="Go CLI (Cobra)",
            category="cli",
            command="custom:go-cli-cobra",
            requires=["go"],
            interactive=False,
            language="go",
        ),
        # Rust
        ProjectConfig(
            name="rust-cli-clap",
            display_name="Rust CLI (Clap)",
            category="cli",
            command="custom:rust-cli-clap",
            requires=["cargo"],
            interactive=False,
            language="rust",
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


def get_all_projects() -> List[ProjectConfig]:
    """Get all project configs"""
    all_projects = []
    for projects in PROJECTS.values():
        all_projects.extend(projects)
    return all_projects
