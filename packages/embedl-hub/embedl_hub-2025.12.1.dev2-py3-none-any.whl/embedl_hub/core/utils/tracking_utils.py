# Copyright (C) 2025 Embedl AB

"""Utility functions for tracking experiments and runs."""

import logging
from contextlib import contextmanager
from pathlib import Path

from embedl_hub import tracking
from embedl_hub.core.hub_logging import console
from embedl_hub.tracking import (
    Metric,
    Parameter,
    RunType,
    set_experiment,
    set_project,
    start_run,
    update_run,
)
from embedl_hub.tracking.errors import (
    ArtifactUploadError,
    FileTooLargeError,
    StorageQuotaExceededError,
)
from embedl_hub.tracking.utils import timestamp_id, to_run_url

logger = logging.getLogger()


def set_new_project(ctx_obj: dict, project: str | None = None) -> None:
    """Set a new project in the context dict, using the given name or a generated one."""
    project_name = project or timestamp_id("project")
    project = set_project(project_name)
    ctx_obj["state"]["project_id"] = project.id
    ctx_obj["config"]["project_name"] = project.name


def set_new_experiment(ctx_obj: dict, experiment: str | None = None) -> None:
    """Set a new experiment in the context object, using the given name or a generated one."""
    experiment_name = experiment or timestamp_id("experiment")
    experiment = set_experiment(experiment_name)
    ctx_obj["state"]["experiment_id"] = experiment.id
    ctx_obj["config"]["experiment_name"] = experiment.name


def log_model_summary(summary: dict) -> None:
    """Log model runtime info to the web app."""

    metrics: list[Metric] = []
    tot_latency = Metric(name="$latency", value=summary.get("mean_ms", 0.0))
    peak_mem = Metric(
        name="$peak_memory_usage",
        value=summary.get("peak_memory_usage_mb", 0.0),
    )
    metrics.extend([tot_latency, peak_mem])
    for unit, count in summary.get("layers_by_unit", {}).items():
        metrics.append(
            Metric(
                name=f"$num_layers_{unit.lower()}",
                value=count,
            )
        )
    update_run(metrics=metrics)


def log_execution_detail(execution_detail: list[dict]) -> None:
    """Log profiling data to the web app."""

    metrics: list[Metric] = []
    params: list[Parameter] = []
    for idx, layer in enumerate(execution_detail):
        layer_name = Parameter(name=f"$layer_name_{idx}", value=layer["name"])
        layer_type = Parameter(name=f"$layer_type_{idx}", value=layer["type"])
        layer_unit_count = Parameter(
            name=f"$layer_compute_unit_{idx}", value=layer["compute_unit"]
        )
        params.extend([layer_name, layer_type, layer_unit_count])
        layer_latency = Metric(
            name="$latency_per_layer", value=layer["execution_time"], step=idx
        )
        layer_cycles = Metric(
            name="$cycles_per_layer", value=layer["execution_cycles"], step=idx
        )
        metrics.extend([layer_latency, layer_cycles])
    update_run(metrics=metrics, params=params)


def log_artifact(
    file_path: Path | str,
    file_name: str | None = None,
    run_id: str | None = None,
) -> None:
    """Log an artifact and handle all errors.

    Any exceptions raised during logging are caught and printed to the console.

    Use this function if you want to log artifacts, but not let exceptions
    propagate, for example in a CLI command.
    """

    try:
        tracking.log_artifact(file_path, file_name, run_id)
    except (
        StorageQuotaExceededError,
        FileTooLargeError,
        ArtifactUploadError,
    ) as exc:
        console.print(
            f"[yellow]Warning:[/] Skipping upload of artifact {exc.file_path.name}: {exc}"
        )
        logger.debug(exc, exc_info=True)
    except Exception as exc:
        console.print(
            f"[yellow]Warning:[/] Failed to upload artifact {Path(file_path).name}"
        )
        logger.debug(exc, exc_info=True)


def _embed_run_hyperlink(run_url: str, text: str) -> str:
    """Return a hyperlink string if the terminal supports it."""
    return (
        f"[blue][link={run_url}]{text}[/link][/]"
        if console.is_terminal
        else run_url
    )


@contextmanager
def experiment_context(
    project_name: str,
    experiment_name: str,
    run_type: RunType,
    run_name: str | None = None,
):
    """
    Context manager for managing the current experiment context.
    """
    try:
        project = set_project(project_name)
        experiment = set_experiment(experiment_name)

        console.log(f"Running command with project name: {project_name}")
        console.log(f"Running command with experiment name: {experiment_name}")
        with start_run(type=run_type, name=run_name) as run:
            run_url = to_run_url(
                project_id=project.id,
                experiment_id=experiment.id,
                run_id=run.id,
            )
            console.log(
                f"Track your progress {_embed_run_hyperlink(run_url, 'here')}."
            )
            yield
            console.log(
                f"View results {_embed_run_hyperlink(run_url, 'here')}"
            )
    finally:
        pass
