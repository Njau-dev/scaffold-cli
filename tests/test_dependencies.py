"""
Tests for dependency validation
"""
import pytest
from scaffold_cli.validators.dependencies import DependencyValidator


def test_validator_initialization():
    """Test that validator initializes correctly"""
    validator = DependencyValidator()
    assert validator.TOOLS is not None
    assert 'node' in validator.TOOLS
    assert 'python3' in validator.TOOLS


def test_validate_empty_list():
    """Test validation with no requirements"""
    validator = DependencyValidator()
    all_valid, results = validator.validate([])

    assert all_valid is True
    assert results == {}


def test_validate_unknown_tool():
    """Test validation with unknown tool"""
    validator = DependencyValidator()
    all_valid, results = validator.validate(['totally-fake-tool'])

    # Should not crash, just skip unknown tools
    assert 'totally-fake-tool' not in results


def test_version_extraction():
    """Test version number extraction"""
    validator = DependencyValidator()

    # Test various version formats
    assert validator._extract_version("v18.2.0") == "18.2.0"
    assert validator._extract_version("Node.js v20.0.0") == "20.0.0"
    assert validator._extract_version("version 3.10.5") == "3.10.5"
    assert validator._extract_version("9.5") == "9.5"


@pytest.mark.skipif(True, reason="Requires actual system tools")
def test_check_node():
    """Test checking if node is installed (integration test)"""
    validator = DependencyValidator()
    all_valid, results = validator.validate(['node'])

    # This will depend on whether node is actually installed
    assert 'node' in results
    assert 'available' in results['node']
