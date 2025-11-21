"""
Tests for orchestrator module
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from scaffold_cli.core.orchestrator import ProjectOrchestrator


def test_orchestrator_initialization():
    """Test that orchestrator initializes correctly"""
    orchestrator = ProjectOrchestrator()
    assert orchestrator.console is not None


@patch('scaffold_cli.core.orchestrator.questionary.text')
@patch('scaffold_cli.core.orchestrator.questionary.confirm')
@patch('scaffold_cli.core.orchestrator.questionary.select')
@patch('scaffold_cli.core.orchestrator.Path')
def test_create_single_project_flow(mock_path, mock_select, mock_confirm, mock_text):
    """Test the single project creation flow"""
    # Setup mocks
    mock_path.return_value.exists.return_value = False
    mock_text.return_value.ask.return_value = "test-project"
    mock_confirm.return_value.ask.return_value = False  # Not a monorepo
    mock_select.return_value.ask.side_effect = ["Frontend", "React (Vite)"]

    orchestrator = ProjectOrchestrator()
    result = orchestrator.create_project()

    assert result is True
    assert mock_text.called
    assert mock_select.called


@patch('scaffold_cli.core.orchestrator.questionary.text')
@patch('scaffold_cli.core.orchestrator.questionary.confirm')
@patch('scaffold_cli.core.orchestrator.questionary.select')
@patch('scaffold_cli.core.orchestrator.Path')
def test_create_monorepo_flow(mock_path, mock_select, mock_confirm, mock_text):
    """Test the monorepo creation flow"""
    # Setup mocks
    mock_path.return_value.exists.return_value = False
    mock_text.return_value.ask.return_value = "test-monorepo"
    mock_confirm.return_value.ask.return_value = True  # Is a monorepo
    mock_select.return_value.ask.side_effect = ["React (Vite)", "Express.js"]

    orchestrator = ProjectOrchestrator()
    result = orchestrator.create_project()

    assert result is True
    assert mock_select.call_count == 2  # Frontend + Backend selection


@patch('scaffold_cli.core.orchestrator.questionary.text')
@patch('scaffold_cli.core.orchestrator.Path')
def test_cancel_on_ctrl_c(mock_path, mock_text):
    """Test that Ctrl+C is handled gracefully"""
    mock_path.return_value.exists.return_value = False
    mock_text.return_value.ask.return_value = None  # Simulates Ctrl+C

    orchestrator = ProjectOrchestrator()
    result = orchestrator.create_project()

    assert result is False


@patch('scaffold_cli.core.orchestrator.questionary.text')
@patch('scaffold_cli.core.orchestrator.questionary.confirm')
@patch('scaffold_cli.core.orchestrator.Path')
def test_existing_directory_overwrite_declined(mock_path, mock_confirm, mock_text):
    """Test declining to overwrite existing directory"""
    mock_path.return_value.exists.return_value = True
    mock_text.return_value.ask.return_value = "existing-project"
    mock_confirm.return_value.ask.return_value = False  # Don't overwrite

    orchestrator = ProjectOrchestrator()
    result = orchestrator.create_project(name="existing-project")

    assert result is False
