"""Utility functions for working with dbt project files."""

from pathlib import Path
from typing import Optional
import yaml


def get_project_profile_name(project_dir: Path) -> Optional[str]:
    """
    Read profile name from dbt_project.yml in the given directory.

    Args:
        project_dir: Path to the project directory

    Returns:
        Profile name if found, None otherwise
    """
    try:
        project_yml_path = project_dir / "dbt_project.yml"
        if not project_yml_path.exists():
            return None

        with open(project_yml_path) as f:
            project = yaml.safe_load(f)
            return project.get("profile")
    except Exception:
        # Silently handle any YAML parsing or file read errors
        return None
