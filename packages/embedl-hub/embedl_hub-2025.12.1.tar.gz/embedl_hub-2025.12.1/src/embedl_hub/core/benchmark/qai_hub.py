# Copyright (C) 2025 Embedl AB
"""
On-device profiling of models via Qualcomm AI Hub.
This module provides functionality to profile model latency and memory usage
on a target device, returning detailed execution statistics.
"""

import json
from datetime import datetime
from numbers import Number
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import qai_hub as hub

from embedl_hub.core.benchmark.abc import Benchmarker, BenchmarkResult
from embedl_hub.core.hardware.qualcomm_ai_hub import create_device
from embedl_hub.core.utils.onnx_utils import maybe_package_onnx_folder_to_file
from embedl_hub.core.utils.qai_hub_utils import (
    get_global_qai_hub_client,
    get_job_result,
    parse_runtime_info,
)
from embedl_hub.core.utils.tracking_utils import (
    log_execution_detail,
    log_model_summary,
)
from embedl_hub.tracking import log_param


class ProfileError(RuntimeError):
    """Raised when Qualcomm AI Hub profile job fails or times out."""


class QAIHubBenchmarker(Benchmarker):
    """Benchmarker using Qualcomm AI Hub for on-device profiling."""

    supported_input_model_formats = {".onnx", ".tflite", ".bin"}
    supports_input_model_folders = True

    def __init__(self, device: str):
        self._device = self._validate_device(device)

    def _validate_device(self, device: str) -> hub.Device:
        """Validate that the specified device is supported by Qualcomm AI Hub."""
        return create_device(device)

    def _benchmark(self, model_path: Path) -> BenchmarkResult:
        """Run the benchmark and return a result."""
        summary, full_profile = benchmark_model(
            model=model_path, device=self._device
        )
        return BenchmarkResult(
            device=self._device.name, summary=summary, raw=full_profile
        )


def _to_ms(val: Number):
    "Always return milliseconds as float, or None if not available."
    return float(val) / 1000.0 if val is not None else None


def _count_layers_by_unit(execution_detail: list[dict]) -> dict[str, int]:
    """Count layers by compute unit (CPU, GPU, NPU) from execution detail."""
    counts = {"CPU": 0, "GPU": 0, "NPU": 0}
    for layer in execution_detail:
        unit = layer.get("compute_unit")
        if unit in counts:
            counts[unit] += 1
    return counts


def _to_megabytes(val: Number):
    "Convert bytes to megabytes as float, or None if not available."
    return float(val) / (1024 * 1024) if val is not None else None


def _collect_top_n_layer_times(
    execution_detail, num: int
) -> list[tuple[float, str, str]]:
    """
    Collect layer execution times for the top n slowest layers from the profile detail.

    Returns a list of tuples (time_ms, layer_name, layer_type) in descending order of time.
    """
    all_layer_times = [
        (_to_ms(layer["execution_time"]), layer["name"], layer["type"])
        for layer in execution_detail
    ]
    return sorted(all_layer_times, reverse=True)[:num]


def _make_layer_names_unique(execution_detail: list[dict]) -> None:
    """Modify execution_detail in-place to ensure all layer names are unique."""

    class LayerNamer:
        """Helper class to generate unique layer names."""

        def __init__(self, layer_details: dict):
            self.all_names_unique = True
            self.seen_names = set()
            for layer in layer_details:
                name = layer.get("name")
                if name in self.seen_names or name == "":
                    self.all_names_unique = False
                    break
                self.seen_names.add(name)

            self.counts: dict[str, int] = {}

        def __call__(self, layer_name: str, layer_type: str) -> str:
            if self.all_names_unique and layer_name:
                return layer_name
            count = self.counts.get(layer_type, 0)
            new_layer_name = f"{layer_type.lower()}_{count}"
            self.counts[layer_type] = count + 1
            return new_layer_name

    layer_namer = LayerNamer(execution_detail)

    for layer in execution_detail:
        layer["name"] = layer_namer(layer["name"], layer["type"])


def _parse_qai_hub_profile(profile: Any) -> tuple[dict, list[dict]]:
    """Parse QAI Hub profile and return a summary dict and execution detail."""
    summary = profile.get("execution_summary", {})
    execution_detail = profile.get("execution_detail", [])
    _make_layer_names_unique(execution_detail)
    layer_counts = _count_layers_by_unit(execution_detail)
    layer_times = _collect_top_n_layer_times(execution_detail, 5)
    summary_dict = {
        "mean_ms": _to_ms(summary.get("estimated_inference_time")),
        "peak_memory_usage_mb": _to_megabytes(
            summary.get("estimated_inference_peak_memory")
        ),
        "layer_times": layer_times,
        "layers": profile.get("layers", []),
        "layers_by_unit": layer_counts,
    }
    return summary_dict, execution_detail


def benchmark_model(model: Path, device: hub.Device) -> tuple[dict, dict]:
    """
    Profile model latency on a target device using Qualcomm AI Hub.
    Returns (summary_dict, full_profile_dict).
    Raises ProfileError on failure.
    """

    log_param("$device", device.name)

    with TemporaryDirectory() as tmpdir:
        model = maybe_package_onnx_folder_to_file(model, tmpdir)
        try:
            job = hub.submit_profile_job(
                model=model,
                device=device,
            )
        except Exception as exc:
            raise ProfileError("Failed to submit profile job.") from exc

    log_param("$qai_hub_job_id", job.job_id)

    try:
        prof = job.download_profile()
    except Exception as exc:
        raise ProfileError("Failed to download profile.") from exc

    try:
        job_result = get_job_result(
            job.job_id, get_global_qai_hub_client().config
        )
        runtime = parse_runtime_info(job_result)
    except RuntimeError as exc:
        raise ProfileError("Failed to extract runtime info from job.") from exc
    log_param("$runtime", runtime)

    summary_dict, execution_detail = _parse_qai_hub_profile(prof)
    log_model_summary(summary_dict)
    log_execution_detail(execution_detail)

    return summary_dict, prof


def write_benchmark_files(
    model, output_dir, summary, full
) -> tuple[Path, Path]:
    """Write benchmark summary and full profile to JSON files."""
    if output_dir is None:
        outdir = Path("benchmarks")
    else:
        outdir = Path(output_dir)
    outdir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = outdir / f"{model.stem}_{ts}.json"
    full_path = outdir / f"{model.stem}_{ts}.full.json"

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(full, f, indent=2)

    return summary_path, full_path
