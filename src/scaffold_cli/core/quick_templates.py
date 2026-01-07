"""
Quick template definitions - pre-configured project setups
"""

from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass
class QuickTemplate:
    """Pre-configured template with specific settings"""

    key: str  # unique identifier
    name: str  # display name
    description: str
    category: str  # 'frontend', 'backend', 'fullstack'
    base_project: str  # project type name from project_types.py
    emoji: str = "📦"

    # Optional configurations
    setup_env: bool = False
    setup_docker: bool = False
    recommended_services: List[str] = None  # ['database', 'email', etc]

    def __post_init__(self):
        if self.recommended_services is None:
            self.recommended_services = []


# Quick template registry
QUICK_TEMPLATES = {
    # ============================================
    # FRONTEND TEMPLATES
    # ============================================
    "react-ts-tailwind": QuickTemplate(
        key="react-ts-tailwind",
        name="React + TypeScript + Tailwind",
        description="Modern React with TypeScript and Tailwind CSS",
        category="frontend",
        base_project="react-vite-ts",
        emoji="⚛️",
        setup_env=True,
        setup_docker=False,
    ),
    "nextjs-full": QuickTemplate(
        key="nextjs-full",
        name="Next.js Full Stack",
        description="Next.js with TypeScript and modern features",
        category="frontend",
        base_project="nextjs",
        emoji="▲",
        setup_env=True,
        setup_docker=False,
    ),
    "vue-ts": QuickTemplate(
        key="vue-ts",
        name="Vue + TypeScript",
        description="Vue 3 with TypeScript and Composition API",
        category="frontend",
        base_project="vue-vite-ts",
        emoji="🟢",
        setup_env=True,
        setup_docker=False,
    ),
    "svelte-kit": QuickTemplate(
        key="svelte-kit",
        name="SvelteKit",
        description="Full-featured Svelte framework",
        category="frontend",
        base_project="sveltekit",
        emoji="🔥",
        setup_env=True,
        setup_docker=False,
    ),
    # ============================================
    # BACKEND TEMPLATES
    # ============================================
    "fastapi-postgres": QuickTemplate(
        key="fastapi-postgres",
        name="FastAPI + PostgreSQL",
        description="FastAPI with PostgreSQL and async support",
        category="backend",
        base_project="fastapi",
        emoji="⚡",
        setup_env=True,
        setup_docker=True,
        recommended_services=["database"],
    ),
    "django-rest": QuickTemplate(
        key="django-rest",
        name="Django REST API",
        description="Django with REST Framework",
        category="backend",
        base_project="django-drf",
        emoji="🎸",
        setup_env=True,
        setup_docker=True,
        recommended_services=["database"],
    ),
    "express-ts": QuickTemplate(
        key="express-ts",
        name="Express + TypeScript",
        description="Express.js API with TypeScript",
        category="backend",
        base_project="express-ts",
        emoji="🚂",
        setup_env=True,
        setup_docker=False,
    ),
    "go-gin-api": QuickTemplate(
        key="go-gin-api",
        name="Go (Gin) API",
        description="High-performance Go API with Gin",
        category="backend",
        base_project="go-gin",
        emoji="🐹",
        setup_env=True,
        setup_docker=True,
    ),
    "flask-api": QuickTemplate(
        key="flask-api",
        name="Flask API",
        description="Lightweight Python API with Flask",
        category="backend",
        base_project="flask",
        emoji="🌶️",
        setup_env=True,
        setup_docker=False,
        recommended_services=["database"],
    ),
    # ============================================
    # FULL-STACK TEMPLATES (for monorepo)
    # ============================================
    "mern-stack": QuickTemplate(
        key="mern-stack",
        name="MERN Stack",
        description="React + Express + MongoDB monorepo",
        category="fullstack",
        base_project="monorepo",  # special handling
        emoji="🔥",
        setup_env=True,
        setup_docker=True,
        recommended_services=["database"],
    ),
    "pern-stack": QuickTemplate(
        key="pern-stack",
        name="PERN Stack",
        description="React + Express + PostgreSQL monorepo",
        category="fullstack",
        base_project="monorepo",
        emoji="🐘",
        setup_env=True,
        setup_docker=True,
        recommended_services=["database"],
    ),
    "nextjs-fastapi": QuickTemplate(
        key="nextjs-fastapi",
        name="Next.js + FastAPI",
        description="Next.js frontend with FastAPI backend",
        category="fullstack",
        base_project="monorepo",
        emoji="⚡",
        setup_env=True,
        setup_docker=True,
        recommended_services=["database"],
    ),
}


def get_quick_template(key: str) -> Optional[QuickTemplate]:
    """Get a quick template by key"""
    return QUICK_TEMPLATES.get(key)


def get_templates_by_category() -> Dict[str, List[QuickTemplate]]:
    """Group templates by category"""
    categories = {"frontend": [], "backend": [], "fullstack": []}

    for template in QUICK_TEMPLATES.values():
        if template.category in categories:
            categories[template.category].append(template)

    return categories


def list_all_templates() -> List[QuickTemplate]:
    """Get all quick templates as a list"""
    return list(QUICK_TEMPLATES.values())


def get_template_choices() -> List[str]:
    """Get formatted template choices for interactive prompts"""
    templates = list_all_templates()
    choices = []

    current_category = None
    for template in sorted(templates, key=lambda t: (t.category, t.name)):
        # Add category header
        if template.category != current_category:
            category_name = template.category.capitalize()
            choices.append(f"───── {category_name} ─────")
            current_category = template.category

        # Add template choice
        choice = f"{template.emoji} {template.name}"
        choices.append(choice)

    return choices


def get_template_from_choice(choice: str) -> Optional[QuickTemplate]:
    """Get template from a formatted choice string"""
    # Skip category headers
    if "─────" in choice:
        return None

    # Extract template name from "emoji name" format
    for template in QUICK_TEMPLATES.values():
        if template.name in choice:
            return template

    return None
