import os
import shutil
import subprocess
import sys

import click


@click.group()
def cli():
    """Fastplate - FastAPI + Tailwind CSS project generator."""
    pass


@cli.command()
@click.argument("path", default=".", type=click.Path(file_okay=False, dir_okay=True))
@click.option("--name", "-n", help="Project name (defaults to directory name)")
@click.option("--skip-install", is_flag=True, help="Skip dependency installation")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
def init(path: str, name: str | None, skip_install: bool, force: bool):
    """Initialize a new FastAPI + Tailwind CSS project.

    PATH is the directory to create the project in (defaults to current directory).
    """
    import re

    abs_path = os.path.abspath(path)

    # Determine project name
    if name:
        project_name = name
    else:
        default_name = os.path.basename(abs_path) or "my-fastapi-app"
        project_name = click.prompt("Project name", default=default_name)

    # Create sanitized name for pyproject.toml (PEP 508 compliant)
    sanitized_name = re.sub(r"[^a-zA-Z0-9._-]", "-", project_name).lower()
    sanitized_name = re.sub(r"-+", "-", sanitized_name).strip("-")

    click.echo(f"\n🚀 Creating project '{project_name}' in {abs_path}")
    click.echo(f"   Package name: {sanitized_name}\n")

    # Check for conflicting directories that would indicate an existing project
    conflicting = ["app", "frontend"]
    if os.path.exists(path):
        existing_conflicts = [
            d for d in conflicting if os.path.isdir(os.path.join(path, d))
        ]
        if existing_conflicts and not force:
            click.echo(
                f"❌ Error: Directory contains existing project folders: {', '.join(existing_conflicts)}",
                err=True,
            )
            click.echo("   Use --force to overwrite.", err=True)
            sys.exit(1)

    # Copy template (merge with existing directory)
    template_dir = os.path.join(os.path.dirname(__file__), "template")
    try:
        shutil.copytree(template_dir, path, dirs_exist_ok=True)
        click.echo("📁 Copied project template")
    except Exception as e:
        click.echo(f"❌ Error copying template: {e}", err=True)
        sys.exit(1)

    # Replace placeholders in copied files
    replacements = {
        "{{project_name}}": project_name,
        "{{project_name_sanitized}}": sanitized_name,
        "{{project_name_snake}}": sanitized_name.replace("-", "_"),
    }

    for root, _, files in os.walk(path):
        # Skip node_modules if it exists
        if "node_modules" in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                modified = False
                for placeholder, value in replacements.items():
                    if placeholder in content:
                        content = content.replace(placeholder, value)
                        modified = True

                if modified:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
            except (UnicodeDecodeError, PermissionError):
                # Skip binary files and permission errors
                pass

    click.echo("✏️  Replaced template placeholders")

    if skip_install:
        click.echo("\n⏭️  Skipping dependency installation (--skip-install)")
        _print_next_steps(path, skipped=True)
        return

    # Install Python dependencies with uv
    click.echo("\n📦 Installing Python dependencies...")
    try:
        result = subprocess.run(
            ["uv", "sync"],
            cwd=path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            click.echo(f"⚠️  Warning: uv sync failed:\n{result.stderr}", err=True)
        else:
            click.echo("✅ Python dependencies installed")
    except FileNotFoundError:
        click.echo(
            "⚠️  Warning: 'uv' not found. Run 'uv sync' manually to install Python dependencies.",
            err=True,
        )

    # Install npm dependencies
    frontend_dir = os.path.join(path, "frontend")
    if os.path.isdir(frontend_dir):
        click.echo("\n📦 Installing npm dependencies...")
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                click.echo(
                    f"⚠️  Warning: npm install failed:\n{result.stderr}", err=True
                )
            else:
                click.echo("✅ npm dependencies installed")
        except FileNotFoundError:
            click.echo(
                "⚠️  Warning: 'npm' not found. Run 'npm install' in frontend/ manually.",
                err=True,
            )

    _print_next_steps(path, skipped=False)


def _print_next_steps(path: str, skipped: bool):
    """Print next steps for the user."""
    click.echo("\n" + "=" * 50)
    click.echo("🎉 Project created successfully!")
    click.echo("=" * 50)

    if path != ".":
        click.echo(f"\n📂 cd {path}")

    if skipped:
        click.echo("\n📦 Install dependencies:")
        click.echo("   uv sync                    # Python deps")
        click.echo("   cd frontend && npm install # npm deps")

    click.echo("\n🚀 Start development:")
    click.echo("   make dev        # Start FastAPI server")
    click.echo("   make npm-watch  # Start Tailwind watcher (in another terminal)")

    click.echo("\n📖 Other commands:")
    click.echo("   make run        # Production server")
    click.echo("   make docker-up  # Run with Docker")
    click.echo("")


if __name__ == "__main__":
    cli()
