"""
Tests for CLI commands
"""
from typer.testing import CliRunner
from scaffold_cli.cli import app

runner = CliRunner()


def test_info_command():
    """Test the info command"""
    result = runner.invoke(app, ["info"])

    assert result.exit_code == 0
    assert "Scaffold CLI" in result.stdout
    assert "v0.1.0" in result.stdout


def test_help_command():
    """Test the help command"""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "scaffold" in result.stdout.lower()
    assert "new" in result.stdout


def test_new_command_help():
    """Test help for new command"""
    result = runner.invoke(app, ["new", "--help"])

    assert result.exit_code == 0
    assert "Create a new project" in result.stdout
    assert "--monorepo" in result.stdout
