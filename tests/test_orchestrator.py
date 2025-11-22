"""
Updated tests for orchestrator module
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from scaffold_cli.core.orchestrator import ProjectOrchestrator
from scaffold_cli.core.project_types import ProjectConfig


# ---------------------------------------------------------------------------
# FIXTURES FOR COMMON MOCKS
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_single_project_config():
    return ProjectConfig(
        name="react",
        command="npm create vite@latest {name}",
        display_name="React (Vite)",
        category="frontend",
        requires=["node"]
    )


@pytest.fixture
def mock_backend_project_config():
    return ProjectConfig(
        name="express",
        command="npm create express@latest {name}",
        display_name="Express.js",
        category="api",
        requires=["node"]
    )


# ---------------------------------------------------------------------------
# BASIC INITIALIZATION TEST
# ---------------------------------------------------------------------------

def test_orchestrator_initialization():
    orchestrator = ProjectOrchestrator()
    assert orchestrator.console is not None


# ---------------------------------------------------------------------------
# SINGLE PROJECT CREATION FLOW
# ---------------------------------------------------------------------------

@patch("scaffold_cli.core.orchestrator.DependencyValidator")
@patch("scaffold_cli.core.orchestrator.Installer")
@patch("scaffold_cli.core.orchestrator.get_projects_by_category")
@patch("scaffold_cli.core.orchestrator.get_project_categories")
@patch("scaffold_cli.core.orchestrator.questionary")
@patch("scaffold_cli.core.orchestrator.Path")
def test_create_single_project_flow(
    mock_path,
    mock_questionary,
    mock_categories,
    mock_projects_by_cat,
    mock_installer,
    mock_validator,
    mock_single_project_config
):
    mock_path.return_value.exists.return_value = False

    # Questionary mocks
    mock_questionary.text.return_value.ask.return_value = "test-project"
    mock_questionary.confirm.return_value.ask.return_value = False  # not monorepo
    mock_questionary.select.return_value.ask.side_effect = [
        "Frontend",              # category selection
        "React (Vite)",          # actual project selection
    ]

    # Fake project types
    mock_categories.return_value = ["frontend"]
    mock_projects_by_cat.return_value = [mock_single_project_config]

    # Dependency validator
    mock_validator.return_value.validate_and_report.return_value = True

    # Installer mock
    mock_installer.return_value.install.return_value = True

    orchestrator = ProjectOrchestrator()
    result = orchestrator.create_project()

    assert result is True
    assert mock_questionary.text.called
    assert mock_questionary.select.called


# ---------------------------------------------------------------------------
# MONOREPO PROJECT CREATION FLOW
# ---------------------------------------------------------------------------

@patch("scaffold_cli.core.orchestrator.DependencyValidator")
@patch("scaffold_cli.core.orchestrator.Installer")
@patch("scaffold_cli.core.orchestrator.get_projects_by_category")
@patch("scaffold_cli.core.orchestrator.questionary")
@patch("scaffold_cli.core.orchestrator.Path")
def test_create_monorepo_flow(
    mock_path,
    mock_questionary,
    mock_projects_by_cat,
    mock_installer,
    mock_validator,
    mock_single_project_config,
    mock_backend_project_config
):
    mock_path.return_value.exists.return_value = False
    mock_path.return_value.mkdir.return_value = None

    # User input
    mock_questionary.text.return_value.ask.return_value = "test-monorepo"
    mock_questionary.confirm.return_value.ask.return_value = True  # monorepo mode
    mock_questionary.select.return_value.ask.side_effect = [
        "React (Vite)",   # frontend
        "Express.js"      # backend
    ]

    # Fake category lookups
    mock_projects_by_cat.side_effect = [
        [mock_single_project_config],  # frontend list
        [mock_backend_project_config],  # backend list
    ]

    # Mocks
    mock_validator.return_value.validate_and_report.return_value = True
    mock_installer.return_value.install.return_value = True

    orchestrator = ProjectOrchestrator()
    result = orchestrator.create_project()

    assert result is True
    assert mock_questionary.select.call_count == 2


# ---------------------------------------------------------------------------
# CANCEL HANDLING (CTRL+C)
# ---------------------------------------------------------------------------

@patch("scaffold_cli.core.orchestrator.questionary")
@patch("scaffold_cli.core.orchestrator.Path")
def test_cancel_on_ctrl_c(mock_path, mock_questionary):
    mock_path.return_value.exists.return_value = False
    mock_questionary.text.return_value.ask.return_value = None  # simulate cancel

    orchestrator = ProjectOrchestrator()
    result = orchestrator.create_project()

    assert result is False


# ---------------------------------------------------------------------------
# EXISTING DIRECTORY HANDLING
# ---------------------------------------------------------------------------

@patch("scaffold_cli.core.orchestrator.questionary")
@patch("scaffold_cli.core.orchestrator.Path")
def test_existing_directory_overwrite_declined(mock_path, mock_questionary):
    mock_path.return_value.exists.return_value = True
    mock_questionary.text.return_value.ask.return_value = "existing-project"
    mock_questionary.confirm.return_value.ask.return_value = False  # decline overwrite

    orchestrator = ProjectOrchestrator()
    result = orchestrator.create_project(name="existing-project")

    assert result is False
