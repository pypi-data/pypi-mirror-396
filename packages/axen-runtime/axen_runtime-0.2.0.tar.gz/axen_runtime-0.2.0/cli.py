#!/usr/bin/env python3
"""
Agent Platform CLI - Deploy and manage AI agents

Commands:
    agent init      Initialize a new agent project
    agent deploy    Deploy your agent to the platform
"""

import typer
import os
import shutil
import zipfile
import requests
from pathlib import Path
from typing import Optional
import yaml

app = typer.Typer(
    name="agent",
    help="Agent Platform CLI - Deploy and share your AI agents",
    add_completion=False,
)

# Configuration
DEFAULT_API_URL = os.getenv("AGENT_PLATFORM_URL", "http://localhost:8000")
TEMPLATE_DIR = Path(__file__).parent / "templates"

# Files/directories to exclude from deployment
EXCLUDE_PATTERNS = {
    "venv",
    ".venv",
    "env",
    ".env",
    ".git",
    ".gitignore",
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    ".mypy_cache",
    ".DS_Store",
    "node_modules",
    ".next",
    "uploads",
    "*.egg-info",
    "dist",
    "build",
}


@app.command()
def init(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Agent name"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """
    Initialize a new agent project in the current directory.

    Creates:
        - agent.yaml: Configuration file
        - main.py: Sample agent code
    """
    cwd = Path.cwd()

    # Check if files already exist
    agent_yaml_path = cwd / "agent.yaml"
    main_py_path = cwd / "main.py"

    if agent_yaml_path.exists() and not force:
        typer.secho(
            "❌ agent.yaml already exists. Use --force to overwrite.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    if main_py_path.exists() and not force:
        typer.secho(
            "❌ main.py already exists. Use --force to overwrite.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    # Copy template files
    try:
        typer.secho("🚀 Initializing agent project...", fg=typer.colors.BLUE)

        # Copy agent.yaml
        shutil.copy(TEMPLATE_DIR / "agent.yaml", agent_yaml_path)
        typer.secho(f"✅ Created agent.yaml", fg=typer.colors.GREEN)

        # Copy main.py
        shutil.copy(TEMPLATE_DIR / "main.py", main_py_path)
        typer.secho(f"✅ Created main.py", fg=typer.colors.GREEN)

        # Update agent name if provided
        if name:
            with open(agent_yaml_path, "r") as f:
                config = yaml.safe_load(f)
            config["name"] = name
            with open(agent_yaml_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            typer.secho(f"✅ Set agent name to: {name}", fg=typer.colors.GREEN)

        typer.secho("\n🎉 Agent project initialized successfully!", fg=typer.colors.GREEN, bold=True)
        typer.secho("\nNext steps:", fg=typer.colors.CYAN)
        typer.secho("  1. Edit main.py to implement your agent logic")
        typer.secho("  2. Update agent.yaml with your agent's metadata")
        typer.secho("  3. Run 'agent deploy' to deploy your agent\n")

    except Exception as e:
        typer.secho(f"❌ Error initializing project: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def deploy(
    api_url: str = typer.Option(DEFAULT_API_URL, "--api-url", help="API server URL"),
):
    """
    Deploy your agent to the Agent Platform.

    Requirements:
        - agent.yaml must exist in current directory
        - main.py must exist in current directory
    """
    cwd = Path.cwd()

    # Validate agent.yaml exists
    agent_yaml_path = cwd / "agent.yaml"
    if not agent_yaml_path.exists():
        typer.secho(
            "❌ agent.yaml not found. Run 'agent init' first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    # Validate main.py exists
    main_py_path = cwd / "main.py"
    if not main_py_path.exists():
        typer.secho(
            "❌ main.py not found. Run 'agent init' first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    # Load and validate agent.yaml
    try:
        with open(agent_yaml_path, "r") as f:
            config = yaml.safe_load(f)

        agent_name = config.get("name", "unnamed-agent")
        typer.secho(f"📦 Packaging agent: {agent_name}", fg=typer.colors.BLUE)

    except Exception as e:
        typer.secho(f"❌ Error reading agent.yaml: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Create deployment package
    try:
        zip_path = cwd / "project.zip"

        typer.secho("📦 Creating deployment package...", fg=typer.colors.BLUE)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for item in cwd.rglob("*"):
                # Skip excluded patterns
                if any(pattern in str(item) for pattern in EXCLUDE_PATTERNS):
                    continue

                # Skip the zip file itself
                if item == zip_path:
                    continue

                # Skip directories (they'll be created automatically)
                if item.is_file():
                    arcname = item.relative_to(cwd)
                    zipf.write(item, arcname)
                    typer.secho(f"  ✅ Added: {arcname}", fg=typer.colors.GREEN, dim=True)

        file_size_mb = zip_path.stat().st_size / (1024 * 1024)
        typer.secho(f"✅ Package created: {file_size_mb:.2f} MB", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"❌ Error creating package: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Upload to server
    try:
        typer.secho(f"🚀 Deploying to {api_url}...", fg=typer.colors.BLUE)

        with open(zip_path, "rb") as f:
            files = {"file": ("project.zip", f, "application/zip")}
            data = {"name": agent_name}

            response = requests.post(
                f"{api_url}/api/deploy",
                files=files,
                data=data,
                timeout=60,
            )

        if response.status_code == 200:
            result = response.json()
            deployment_id = result.get("deployment_id")
            agent_url = f"http://localhost:3000/chat/{deployment_id}"

            typer.secho("\n✅ Deployment successful!", fg=typer.colors.GREEN, bold=True)
            typer.secho(f"\n📋 Deployment ID: {deployment_id}", fg=typer.colors.CYAN)
            typer.secho(f"🔗 Access your agent here:", fg=typer.colors.CYAN)
            typer.secho(f"   {agent_url}\n", fg=typer.colors.BLUE, bold=True)

            # Clean up zip file
            zip_path.unlink()

        else:
            typer.secho(f"❌ Deployment failed: {response.status_code}", fg=typer.colors.RED)
            typer.secho(f"   {response.text}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    except requests.exceptions.ConnectionError:
        typer.secho(
            f"❌ Cannot connect to API server at {api_url}",
            fg=typer.colors.RED,
        )
        typer.secho("   Make sure the server is running.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"❌ Error deploying agent: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
