# Copyright (C) 2025 Embedl AB
"""
Project and experiment context management for embedl-hub CLI.

This module provides CLI commands to initialize and display the current project
and experiment context. The selected context determines under which project and
experiment all data, results, and metadata are stored in the user's account on
https://hub.embedl.com.

Users can create new projects and experiments, switch between them, and view the
active context. Context information is stored locally in a YAML file.
"""

from __future__ import annotations

import typer
from rich.table import Table

init_cli = typer.Typer(help="Initialise / show project & experiment context")


@init_cli.command("init")
def init_command(
    ctx: typer.Context,
    project: str | None = typer.Option(
        None, "-p", "--project", help="Project name or id", show_default=False
    ),
    experiment: str | None = typer.Option(
        None,
        "-e",
        "--experiment",
        help="Experiment name or id",
        show_default=False,
    ),
):
    """
    Configure persistent CLI context.

    This command stores values used by other commands in a local context file
    in your home directory. The context file can contain:

    - Active project (created automatically if name does not exist)
    - Active experiment (created automatically if name does not exist)

    Examples
    --------
    Create a new project and experiment with random names:
        $ embedl-hub init

    Create or set named project:
        $ embedl-hub init -p "My Flower Detector App"

    Create or load named experiment inside current project:
        $ embedl-hub init -e "MobileNet Flower Detector"

    Set both project and experiment explicitly:
        $ embedl-hub init -p "My Flower Detector App" -e "MobileNet Flower Detector"
    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import assert_api_config
    from embedl_hub.core.context import write_ctx_config, write_ctx_state
    from embedl_hub.core.hub_logging import console
    from embedl_hub.core.utils.tracking_utils import (
        set_new_experiment,
        set_new_project,
    )
    from embedl_hub.tracking.utils import (
        to_experiment_url,
    )
    # pylint: enable=import-outside-toplevel

    assert_api_config()

    current_project = ctx.obj["config"].get("project_name")
    current_experiment = ctx.obj["config"].get("experiment_name")
    force_new_experiment = project is not None and project != current_project

    # Decide which project to use
    project_to_use: str | None
    if project:
        console.print(f"Setting project to '{project}'")
        project_to_use = project
    elif not current_project:
        console.print("No active project, creating a new one")
        project_to_use = project
    else:
        console.print(f"Keeping current project '{current_project}'")
        project_to_use = current_project
    set_new_project(ctx.obj, project_to_use)

    # Decide which experiment to use
    experiment_to_use: str | None
    if experiment:
        console.print(f"Setting experiment to '{experiment}'")
        experiment_to_use = experiment
    elif not current_experiment or force_new_experiment:
        console.print("No active experiment, creating a new one")
        experiment_to_use = experiment
    else:
        console.print(f"Keeping current experiment '{current_experiment}'")
        experiment_to_use = current_experiment
    set_new_experiment(ctx.obj, experiment_to_use)

    write_ctx_config(ctx.obj["config"])
    write_ctx_state(ctx.obj["state"])

    console.print(f"[green]✓ Project:[/] {ctx.obj['config']['project_name']}")
    console.print(
        f"[green]✓ Experiment:[/] {ctx.obj['config']['experiment_name']}"
    )
    console.print(
        f"See your results: {to_experiment_url(ctx.obj['state']['project_id'], ctx.obj['state']['experiment_id'])}"
    )


@init_cli.command("show")
def show_command(
    ctx: typer.Context,
):
    """Print active project/experiment IDs and names."""

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import assert_api_config
    from embedl_hub.core.context import require_initialized_ctx
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    assert_api_config()
    require_initialized_ctx(ctx.obj["config"])

    table = Table(title="Configuration", show_lines=True, show_header=False)
    for k in (
        "project_name",
        "experiment_name",
    ):
        table.add_row(k, ctx.obj["config"].get(k, "—"))
    console.print(table)
