# Copyright (C) 2025 Embedl AB

"""Benchmarking of models using the Embedl device cloud."""

import tempfile
import time
from pathlib import Path

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from embedl_hub.core.benchmark.abc import Benchmarker, BenchmarkResult
from embedl_hub.core.utils.tracking_utils import (
    log_artifact,
    log_execution_detail,
    log_model_summary,
)
from embedl_hub.tracking import (
    BenchmarkJob,
    log_param,
    submit_benchmark_job,
    validate_device,
)

RUNTIME = "TensorFlow Lite"


class EmbedlBenchmarker(Benchmarker):
    """Benchmarker that uses the Embedl device cloud."""

    supported_input_model_formats = {".tflite"}

    def __init__(self, device: str, artifacts_dir: Path | None = None):
        self._device = device
        self._artifacts_dir = artifacts_dir

        self._validate_device()

    def _validate_device(self) -> None:
        """Validate that the specified device is supported."""
        return validate_device(self._device)

    def _benchmark(self, model_path: Path) -> BenchmarkResult:
        """Benchmark a model on the Embedl device cloud and track results.

        Return a tuple of (summary_dict, execution_detail).
        """
        summary, _ = benchmark_model(
            model_path=model_path,
            device=self._device,
            artifacts_dir=self._artifacts_dir,
        )
        return BenchmarkResult(device=self._device, summary=summary)


def _display_progress_bar(job: BenchmarkJob, device: str) -> None:
    """Display a progress bar for the benchmark job."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(f"Benchmarking on {device}...", total=None)

        while True:
            status = job.get_status()
            progress.update(
                task,
                description=f"Benchmarking on {device}... {status.value}",
            )

            if status.is_final():
                break

            time.sleep(job.poll_interval_seconds)


def _submit_benchmark_job_with_progress_bar(
    model_path: Path, device: str
) -> BenchmarkJob:
    """Submit a benchmark job and display a progress bar."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
    ) as progress:
        progress.add_task("Uploading model...", total=None)
        job = submit_benchmark_job(model_path=model_path, device=device)

    _display_progress_bar(job, device)
    return job


def benchmark_model(
    model_path: Path, device: str, artifacts_dir: Path | None = None
) -> tuple[dict, list[dict]]:
    """Benchmark a model on the Embedl device cloud and track results.

    Return a tuple of (summary_dict, execution_detail).
    """

    log_param("$device", device)
    log_param("$runtime", RUNTIME)

    job = _submit_benchmark_job_with_progress_bar(
        model_path=model_path, device=device
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        artifacts_dir = artifacts_dir or Path(temp_dir)

        result = job.download_results(artifacts_dir=artifacts_dir)

        summary = result.summary
        execution_detail = result.execution_detail

        log_model_summary(summary)
        log_execution_detail(execution_detail)

        if result.artifacts is not None:
            for file_path in result.artifacts:
                log_artifact(file_path)

    return summary, execution_detail
