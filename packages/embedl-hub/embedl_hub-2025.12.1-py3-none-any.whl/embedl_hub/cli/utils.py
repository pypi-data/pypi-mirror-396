# Copyright (C) 2025 Embedl AB

"""Utility functions for the Embedl Hub CLI."""

from pathlib import Path
from typing import Any

import tabulate
import typer

from embedl_hub.core.hub_logging import console
from embedl_hub.core.utils.onnx_utils import maybe_package_onnx_folder_to_file
from embedl_hub.tracking import global_client


def remove_none_values(input_dict: dict[str, Any]) -> dict[str, Any]:
    """Remove keys with None values from a dictionary."""
    return {key: val for key, val in input_dict.items() if val is not None}


def assert_api_config():
    """Assert that the API configuration can be accessed without error."""
    try:
        _ = global_client.api_config
    except RuntimeError as e:
        console.print(f"[red]✗[/] API configuration error: {e}")
        raise typer.Exit(1)


def prepare_input_size(size: str | None) -> tuple[int, ...] | None:
    """Prepare the input size from a string in comma separated format."""
    if not size:
        return None
    try:
        sizes = tuple(map(int, size.split(",")))
    except ValueError as error:
        raise ValueError(
            "Invalid size format. Use dim0, dim1,..., e.g. 1,3,224,224"
        ) from error
    console.print(f"[yellow]Using input size: {size}[/]")
    return sizes


def _make_layer_times_table(layer_times: list) -> str:
    """Create a pretty-printed table of layer execution times as a string, with a title."""
    headers = ["Name", "Type", "Time (ms)"]
    rows = [
        [name, layer_type, f"{time:.2f}" if time is not None else "—"]
        for time, name, layer_type in layer_times
    ]
    title = f"Layer execution times (Top {len(layer_times)})"
    table = tabulate.tabulate(rows, headers=headers, tablefmt="github")
    return f"\n{title}\n{table}\n"


def print_profile_summary(summary: dict) -> None:
    """Print latency summary to the user in a consistent way."""
    if summary.get("mean_ms") is not None:
        console.print(f"[green]✓ Mean latency:[/] {summary['mean_ms']:.2f} ms")
    if summary.get("peak_memory_usage_mb") is not None:
        console.print(
            f"[green]✓ Peak memory usage:[/] {summary['peak_memory_usage_mb']:.2f} MB"
        )
    if summary.get("layers_by_unit"):
        units = summary["layers_by_unit"]
        console.print(
            f"[green]✓ Layers by compute unit:[/] NPU={units['NPU']}, "
            f"GPU={units['GPU']}, CPU={units['CPU']}"
        )
    if summary.get("layer_times"):
        table = _make_layer_times_table(summary["layer_times"])
        console.print(table)


def prepare_compile_kwargs(
    model: Path,
    device: str,
    runtime: str,
    size: str,
    tmpdir: Path | str,
    quantize_io: bool = False,
    output_file: Path | str | None = None,
) -> dict:
    """Prepare keyword arguments for the compile_model function."""

    if not model.exists():
        raise ValueError(f"Model not found: {model}")
    if not size:
        raise ValueError(
            "Please specify input size using --size, e.g. 1,3,224,224"
        )

    if not output_file:
        output_file = model.with_suffix(f".{runtime}").as_posix()
        console.print(
            f"[yellow]No output file specified, using {output_file}[/]"
        )
    input_size = prepare_input_size(size)
    model_path = maybe_package_onnx_folder_to_file(model, tmpdir)
    return {
        "model_path": model_path,
        "device": device,
        "runtime": runtime,
        "quantize_io": quantize_io,
        "output_file": output_file,
        "input_size": input_size,
    }
