"""
Configuration management for Konigle CLI.
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional

import click


class ConfigManager:
    """Manages CLI configuration for multiple projects."""

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self.config_dir = Path.home() / ".konigle"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True)

    def _validate_project_name(self, name: str) -> None:
        """Validate project name format.

        Args:
            name: Project name to validate.

        Raises:
            click.ClickException: If name format is invalid.
        """
        if not re.match(r"^[a-z][a-z0-9-]*$", name):
            raise click.ClickException(
                "Project name must start with a lowercase letter and "
                "contain only lowercase letters, numbers, and hyphens"
            )

    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {"projects": {}, "active_project": None}

        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"projects": {}, "active_project": None}

    def _save_config(self, config: Dict) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except OSError as e:
            raise click.ClickException(f"Failed to save config: {e}")

    def add_project(
        self, name: str, api_key: str, base_url: Optional[str] = None
    ) -> None:
        """Add a new project configuration.

        Args:
            name: Project name.
            api_key: API key for the project.
            base_url: Optional base URL for the project.
        """
        self._validate_project_name(name)
        config = self._load_config()

        config["projects"][name] = {
            "api_key": api_key,
            "base_url": base_url or "https://tim.konigle.com",
        }

        # Set as active if it's the first project
        if not config["active_project"]:
            config["active_project"] = name

        self._save_config(config)

    def remove_project(self, name: str) -> None:
        """Remove a project configuration.

        Args:
            name: Project name to remove.
        """
        config = self._load_config()

        if name not in config["projects"]:
            raise click.ClickException(f"Project '{name}' not found")

        del config["projects"][name]

        # If this was the active project, clear it
        if config["active_project"] == name:
            config["active_project"] = None

        self._save_config(config)

    def set_active_project(self, name: str) -> None:
        """Set the active project.

        Args:
            name: Project name to activate.
        """
        config = self._load_config()

        if name not in config["projects"]:
            raise click.ClickException(f"Project '{name}' not found")

        config["active_project"] = name
        self._save_config(config)

    def get_active_project(self) -> Optional[Dict[str, str]]:
        """Get the active project configuration.

        Returns:
            Dictionary with api_key and base_url, or None if no active
            project.
        """
        config = self._load_config()
        active_name = config["active_project"]

        if not active_name or active_name not in config["projects"]:
            return None

        return config["projects"][active_name]

    def list_projects(self) -> Dict[str, Dict[str, str]]:
        """List all configured projects.

        Returns:
            Dictionary mapping project names to their configurations.
        """
        config = self._load_config()
        return config["projects"]

    def get_active_project_name(self) -> Optional[str]:
        """Get the name of the active project.

        Returns:
            Name of active project or None.
        """
        config = self._load_config()
        return config["active_project"]
