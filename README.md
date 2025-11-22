# 🚀 Scaffold CLI

A modern, interactive CLI tool for quickly scaffolding development projects with best practices built-in.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎨 **Interactive project setup** with arrow-key navigation
- 📦 **Multiple tech stacks** - React, Next.js, Vue, Django, FastAPI, Express
- 🗂️ **Monorepo support** - Create full-stack projects with frontend + backend
- ✅ **Dependency validation** - Checks for required tools before installation
- 🔧 **Git integration** - Automatic repository initialization with first commit
- 🎯 **Zero configuration** - Just pick your stack and go!

## 📋 Requirements

- Python 3.12 or higher
- Git (optional, but recommended)

**For specific projects:**
- Node.js 18+ and npm (for JavaScript/TypeScript projects)
- Python 3.10+ (for Python projects)

## 🔧 Installation

### Using pipx (Recommended)

```bash
pipx install scaffold-cli
```

### Using pip

```bash
pip install scaffold-cli
```

### From source

```bash
git clone https://github.com/Njau-dev/scaffold-cli.git
cd scaffold-cli
poetry install
poetry run scaffold --help
```

## 🚀 Quick Start

### Create a single project

```bash
scaffold new my-awesome-app
```

Follow the interactive prompts to select your tech stack!

### Create a monorepo

```bash
scaffold new my-fullstack-app --monorepo
```

This creates a project with both frontend (`web/`) and backend (`api/`) in one repository.

### List available templates

```bash
scaffold list
```

## 📚 Usage Examples

### React + Vite Project

```bash
$ scaffold new my-react-app
? Select project type: Frontend
? Select frontend: React (Vite)

✨ Success! Created my-react-app

Next steps:
  cd my-react-app
  npm install
  npm run dev
```

### Django API

```bash
$ scaffold new my-api
? Select project type: Framework
? Select framework: Django

✨ Success! Created my-api

Next steps:
  cd my-api
  python3 -m venv venv
  source venv/bin/activate
  python manage.py migrate
  python manage.py runserver
```

### Full-Stack Monorepo

```bash
$ scaffold new my-fullstack --monorepo
? Select frontend: Next.js
? Select backend: FastAPI

✨ Success! Created monorepo: my-fullstack

Structure:
  my-fullstack/
  ├── web/     (Next.js)
  ├── api/     (FastAPI)
  └── README.md
```

## 📦 Supported Technologies

### Frontend
- **React (Vite)** - Fast, modern React development
- **React + TypeScript (Vite)** - Type-safe React
- **Next.js** - Full-featured React framework
- **Vue (Vite)** - Progressive JavaScript framework

### Backend APIs
- **Express.js** - Fast, minimalist Node.js framework
- **FastAPI** - Modern Python API framework

### Full-Stack Frameworks
- **Django** - Batteries-included Python framework

## 🛠️ Commands

| Command | Description |
|---------|-------------|
| `scaffold new <name>` | Create a new project |
| `scaffold new <name> --monorepo` | Create a monorepo |
| `scaffold list` | List all available templates |
| `scaffold info` | Show CLI information |
| `scaffold version` | Show version |
| `scaffold --help` | Show help message |

## 🎯 Roadmap

- [ ] More templates (Laravel, Ruby on Rails, Go)
- [ ] Custom template support
- [ ] Remote templates from GitHub
- [ ] Docker setup automation
- [ ] CI/CD template generation
- [ ] Database setup integration
- [ ] Environment variable management

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Njau-dev/scaffold-cli.git
cd scaffold-cli

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run the CLI locally
poetry run scaffold new test-project

# Format code
poetry run black src/
```

## 🐛 Bug Reports

Found a bug? Please [open an issue](https://github.com/Njau-dev/scaffold-cli/issues) with:
- Your OS and Python version
- Steps to reproduce
- Expected vs actual behavior

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI framework
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Interactive prompts powered by [Questionary](https://questionary.readthedocs.io/)

## 📬 Contact

Jeff Njau - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/Njau-dev/scaffold-cli](https://github.com/Njau-dev/scaffold-cli)

---

Made with ❤️ by [Jeff Njau](https://github.com/Njau-dev)