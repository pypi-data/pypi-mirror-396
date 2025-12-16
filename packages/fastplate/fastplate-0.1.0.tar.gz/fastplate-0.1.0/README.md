# 🚀 Fastplate

[![PyPI version](https://badge.fury.io/py/fastplate.svg)](https://badge.fury.io/py/fastplate)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Fastplate** is a CLI tool that scaffolds production-ready FastAPI projects with Tailwind CSS, DaisyUI, and Jinja2 templates in seconds.

## ✨ Features

- 🏗️ **FastAPI** backend with async support and automatic OpenAPI docs
- 🎨 **Tailwind CSS v4** + **DaisyUI** for beautiful, responsive UIs
- 📄 **Jinja2** server-side templating with component-based structure
- 📦 **uv** for fast Python dependency management
- 🐳 **Docker** & **docker-compose** ready for deployment
- ⚡ **Hot reload** for both backend and CSS during development
- 🔧 **Makefile** with common development commands

## 📦 Installation

### With uv (recommended)

```bash
uv add fastplate
```

### With pip

```bash
pip install fastplate
```

### With pipx (global install)

```bash
pipx install fastplate
```

## 🚀 Quick Start

### Using uv (recommended)

```bash
# Create a new project directory and add fastplate
mkdir my-app && cd my-app
uv init
uv add fastplate

# Initialize the project
uv run fastplate init --name "My App"

# Start development
make dev          # FastAPI server at http://localhost:8000
make npm-watch    # Tailwind CSS watcher (in another terminal)
```

### Using pip/pipx

```bash
# Create in a new directory
fastplate init ./my-app --name "My App"
cd my-app

# Start development
make dev
make npm-watch
```

## 📖 CLI Reference

Fastplate uses a command-based CLI structure.

### Commands

| Command | Description                                     |
| ------- | ----------------------------------------------- |
| `init`  | Initialize a new FastAPI + Tailwind CSS project |

### `fastplate init`

Scaffolds a new project with the full FastAPI + Tailwind CSS stack.

```bash
fastplate init [OPTIONS] [PATH]
# or with uv
uv run fastplate init [OPTIONS] [PATH]
```

#### Arguments

| Argument | Description                        | Default                 |
| -------- | ---------------------------------- | ----------------------- |
| `PATH`   | Directory to create the project in | `.` (current directory) |

#### Options

| Option           | Short | Description                            |
| ---------------- | ----- | -------------------------------------- |
| `--name TEXT`    | `-n`  | Project name (prompts if not provided) |
| `--skip-install` |       | Skip automatic dependency installation |
| `--force`        | `-f`  | Overwrite existing project files       |
| `--help`         |       | Show help message and exit             |

#### Examples

```bash
# Interactive mode - prompts for project name
uv run fastplate init

# Specify project name directly
uv run fastplate init --name "My Awesome App"

# Create in a specific directory
uv run fastplate init ./projects/my-app --name my-app

# Skip automatic dependency installation
uv run fastplate init --skip-install

# Overwrite existing project files
uv run fastplate init --force

# Short flags
uv run fastplate init -n "My App" -f
```

#### What it does

1. **Copies template** - Scaffolds the full project structure into the target directory
2. **Replaces placeholders** - Injects your project name into config files (`pyproject.toml`, templates, etc.)
3. **Installs Python deps** - Runs `uv sync` to install FastAPI and dependencies
4. **Installs npm deps** - Runs `npm install` in `frontend/` for Tailwind CSS

Use `--skip-install` if you want to handle dependency installation manually.

## 📁 Generated Project Structure

```
my-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/                  # API routes (REST endpoints)
│   ├── core/
│   │   ├── config.py        # Settings & configuration
│   │   └── middleware.py    # Custom middleware
│   ├── models/              # Database models (SQLAlchemy, etc.)
│   ├── schemas/             # Pydantic schemas for validation
│   ├── services/            # Business logic layer
│   └── views/               # HTML view routes (Jinja2)
│       └── index.py
├── frontend/
│   ├── package.json         # npm dependencies (Tailwind)
│   ├── static/
│   │   └── css/
│   │       ├── input.css    # Tailwind source
│   │       └── output.css   # Compiled CSS
│   └── templates/
│       ├── base.html        # Base template with layout
│       ├── components/      # Reusable Jinja2 components
│       │   ├── card.html
│       │   └── navbar.html
│       └── pages/           # Page templates
│           └── index.html
├── Dockerfile
├── docker-compose.yml
├── Makefile                 # Development commands
├── pyproject.toml           # Python project config
└── README.md                # Project-specific docs
```

## 🛠️ Development Commands

The generated project includes a `Makefile` with these commands:

```bash
make dev          # Start FastAPI dev server with hot reload
make run          # Start production server
make npm-watch    # Watch & compile Tailwind CSS
make npm-build    # Build minified CSS for production
make docker-up    # Start with Docker Compose
make docker-down  # Stop Docker containers
make clean        # Remove generated files
```

## 🎨 Styling with Tailwind & DaisyUI

The template uses [Tailwind CSS v4](https://tailwindcss.com/) with [DaisyUI](https://daisyui.com/) components.

Edit `frontend/static/css/input.css` to customize your styles:

```css
@import "tailwindcss";
@plugin "daisyui";

/* Your custom styles here */
```

Run `make npm-watch` during development to auto-compile CSS changes.

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
make docker-up

# Or manually
docker build -t my-app .
docker run -p 8000:8000 my-app
```

## 📋 Requirements

- **Python 3.12+**
- **Node.js 18+** (for Tailwind CSS)
- **uv** (recommended) or pip

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
