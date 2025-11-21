"""
Tests for project_types module
"""
import pytest
from scaffold_cli.core.project_types import (
    ProjectConfig,
    PROJECTS,
    get_project_categories,
    get_projects_by_category,
    get_project_by_name
)


def test_project_config_creation():
    """Test creating a ProjectConfig"""
    config = ProjectConfig(
        name='test-react',
        display_name='Test React',
        category='frontend',
        command='npm create vite@latest {name}',
        requires=['node', 'npm']
    )

    assert config.name == 'test-react'
    assert config.display_name == 'Test React'
    assert config.category == 'frontend'
    assert config.interactive is True
    assert config.post_install == []


def test_projects_registry_structure():
    """Test that PROJECTS registry has expected structure"""
    assert 'frontend' in PROJECTS
    assert 'api' in PROJECTS
    assert 'framework' in PROJECTS

    assert len(PROJECTS['frontend']) > 0
    assert len(PROJECTS['api']) > 0
    assert len(PROJECTS['framework']) > 0


def test_get_project_categories():
    """Test getting all categories"""
    categories = get_project_categories()

    assert 'frontend' in categories
    assert 'api' in categories
    assert 'framework' in categories


def test_get_projects_by_category():
    """Test getting projects by category"""
    frontend_projects = get_projects_by_category('frontend')

    assert len(frontend_projects) > 0
    assert all(isinstance(p, ProjectConfig) for p in frontend_projects)
    assert all(p.category == 'frontend' for p in frontend_projects)


def test_get_projects_by_invalid_category():
    """Test getting projects from non-existent category"""
    projects = get_projects_by_category('invalid')
    assert projects == []


def test_get_project_by_name():
    """Test finding a project by name"""
    react_project = get_project_by_name('react-vite')

    assert react_project is not None
    assert react_project.name == 'react-vite'
    assert react_project.display_name == 'React (Vite)'


def test_get_project_by_invalid_name():
    """Test finding a non-existent project"""
    project = get_project_by_name('non-existent')
    assert project is None


def test_all_projects_have_required_fields():
    """Test that all projects have required fields"""
    for category, projects in PROJECTS.items():
        for project in projects:
            assert project.name
            assert project.display_name
            assert project.category == category
            assert project.command
            assert project.requires
            assert isinstance(project.requires, list)


def test_command_has_name_placeholder():
    """Test that all commands have {name} placeholder"""
    for projects in PROJECTS.values():
        for project in projects:
            # Custom handlers might not need {name}
            if not project.command.startswith('custom:'):
                assert '{name}' in project.command, \
                    f"{project.name} command missing {{name}} placeholder"


def test_requires_are_valid_tools():
    """Test that required tools are recognized"""
    valid_tools = {'node', 'npm', 'python3', 'django-admin', 'composer', 'pip'}

    for projects in PROJECTS.values():
        for project in projects:
            for tool in project.requires:
                assert tool in valid_tools, \
                    f"Unknown tool '{tool}' in {project.name}"
