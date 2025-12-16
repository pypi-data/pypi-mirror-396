# Copyright (C) 2025 Embedl AB

"""Context manager for managing the current experiment context."""

from pathlib import Path

import platformdirs
import typer
import yaml

from embedl_hub.core.hub_logging import console

APP_NAME = "embedl-hub"
CONFIG_FILE = platformdirs.user_config_path(APP_NAME) / "config.yaml"
STATE_FILE = platformdirs.user_data_path(APP_NAME) / "state.yaml"


def _write_to_file(path: Path, content: dict[str, str]) -> None:
    """Write dict to YAML, creating parent directories if needed."""
    if not path.exists():
        console.print(f"File not found. Creating: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(content, sort_keys=False), encoding="utf-8")


def _read_from_file(path: Path) -> dict[str, str]:
    """Read dict from YAML, and return empty if file does not exist."""
    return (
        yaml.safe_load(path.read_text(encoding="utf-8"))
        if path.exists()
        else {}
    )


def write_ctx_config(config: dict[str, str]) -> None:
    """Persist the current `ctx.config` object to file."""
    _write_to_file(CONFIG_FILE, config)


def write_ctx_state(state: dict[str, str]) -> None:
    """Persist the current `ctx.state` object to file."""
    _write_to_file(STATE_FILE, state)


def load_ctx_config() -> dict[str, str]:
    """Read persisted `ctx.config` from file."""
    return _read_from_file(CONFIG_FILE)


def load_ctx_state() -> dict[str, str]:
    """Read persisted `ctx.state` from file."""
    return _read_from_file(STATE_FILE)


def require_initialized_ctx(config: dict[str, str]) -> None:
    """Throw error if `project_name` and `experiment_name` are not in config."""
    if not config.get("project_name") or not config.get("experiment_name"):
        console.print(
            "[red]Failed to find context: No project or experiment is initialized.[/]\n",
            "[red]Run 'embedl-hub init' to set up a project and experiment.[/]\n",
            "[red]Run 'embedl-hub auth' to set up an api key.[/]",
        )
        raise typer.Exit(1)
