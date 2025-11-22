# Contributing to Scaffold CLI

First off, thank you for considering contributing to Scaffold CLI! 🎉

## Code of Conduct

This project and everyone participating in it is governed by our commitment to fostering an open and welcoming environment.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Logs or error messages** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear description** of the feature
- **Use cases** - why would this be useful?
- **Possible implementation** - if you have ideas

### Adding New Templates

Want to add support for a new framework? Great! Here's how:

1. **Add to `project_types.py`**:
```python
ProjectConfig(
    name='your-framework',
    display_name='Your Framework',
    category='frontend',  # or 'api', 'framework'
    command='npx create-your-framework {name}',
    requires=['node', 'npm'],
    interactive=True,
    post_install=[]
)
```

2. **Test it thoroughly**:
```bash
poetry run scaffold new test-project
# Select your new template
# Verify it works correctly
```

3. **Update documentation**:
- Add to README.md supported technologies
- Update tests if needed

### Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `master`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**:
   - Write clear, documented code
   - Follow existing code style
   - Add tests for new features

4. **Test your changes**:
   ```bash
   # Run tests
   poetry run pytest
   
   # Format code
   poetry run black src/
   
   # Test the CLI
   poetry run scaffold new test-project
   ```

5. **Commit** with clear messages:
   ```bash
   git commit -m "feat: add Laravel template support"
   ```

6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots/demos if applicable

## Development Setup

### Prerequisites

- Python 3.12+
- Poetry
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/scaffold-cli.git
cd scaffold-cli

# Install dependencies
poetry install

# Run in development mode
poetry run scaffold --help
```

### Project Structure

```
scaffold-cli/
├── src/scaffold_cli/
│   ├── core/              # Core logic
│   │   ├── project_types.py   # Template definitions
│   │   ├── orchestrator.py    # Main workflow
│   │   └── installer.py       # Installation logic
│   ├── validators/        # Dependency validation
│   ├── utils/             # Helper utilities
│   └── cli.py             # CLI entry point
├── tests/                 # Test suite
└── README.md
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=scaffold_cli

# Run specific test file
poetry run pytest tests/test_project_types.py
```

### Code Style

We use **Black** for formatting:

```bash
# Format all code
poetry run black src/

# Check formatting
poetry run black --check src/
```

**Guidelines:**
- Use type hints where possible
- Write docstrings for public functions
- Keep functions small and focused
- Use Rich for all console output

## Adding Custom Installers

For frameworks without official CLI tools, you can add custom installers:

```python
# In installer.py
def _create_your_framework_project(self, project_path: Path) -> bool:
    """Create a minimal project structure"""
    try:
        # Create directories
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create files
        (project_path / "main.py").write_text("# Your framework code")
        
        # Create README
        readme = project_path / "README.md"
        readme.write_text("# Project documentation")
        
        console.print("[green]✓ Project created[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a git tag: `git tag v0.2.0`
4. Push: `git push origin v0.2.0`
5. Build: `poetry build`
6. Publish: `poetry publish`

## Questions?

Feel free to open an issue with the `question` label!

---

Thank you for contributing! 🙏
