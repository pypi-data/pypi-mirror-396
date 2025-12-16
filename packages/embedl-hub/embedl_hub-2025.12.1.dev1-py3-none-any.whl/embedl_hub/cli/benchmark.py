# Copyright (C) 2025 Embedl AB

"""
CLI command to benchmark a model's performance on a device.

This command profiles the latency of a compiled model on a specified device.
"""

from pathlib import Path

import typer

# All other embedl_hub imports should be done inside the function.
from embedl_hub.cli.helper import DEVICE_HELPER
from embedl_hub.tracking.errors import JobQuotaExceededError

benchmark_cli = typer.Typer(
    name="benchmark",
    help="Benchmark commands (default subcommand: 'embedl').",
    invoke_without_command=True,
)


@benchmark_cli.callback(invoke_without_command=True)
def benchmark_command(
    ctx: typer.Context,
    model: Path | None = typer.Option(
        None,
        "-m",
        "--model",
        help="Path to a compiled model file (.tflite).",
        show_default=False,
    ),
    device: str | None = typer.Option(
        None, "-d", "--device", help=DEVICE_HELPER, show_default=False
    ),
    output_dir: Path | None = typer.Option(
        None, "--output-dir", "-o", help="Output folder for artifacts."
    ),
):
    """Benchmark a model on the specified device."""

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import assert_api_config
    from embedl_hub.core.context import require_initialized_ctx
    # pylint: enable=import-outside-toplevel

    assert_api_config()
    require_initialized_ctx(ctx.obj["config"])
    if ctx.invoked_subcommand is None:
        if not model:
            raise typer.BadParameter(
                "Please specify a model to compile using --model"
            )
        if not device:
            raise typer.BadParameter(
                "Please specify a device to benchmark on using --device"
            )
        ctx.invoke(
            embedl_benchmark_command,
            ctx=ctx,
            model=model,
            device=device,
            output_dir=output_dir,
        )


@benchmark_cli.command("embedl", no_args_is_help=True)
def embedl_benchmark_command(
    ctx: typer.Context,
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help="Path to a .tflite model file.",
        show_default=False,
    ),
    device: str = typer.Option(
        ..., "-d", "--device", help=DEVICE_HELPER, show_default=False
    ),
    output_dir: Path | None = typer.Option(
        None, "--output-dir", "-o", help="Output folder for artifacts."
    ),
):
    """Benchmark compiled model using the Embedl device cloud.

    Examples:
    ---------
    Benchmark a .tflite model on Samsung Galaxy S25 and upload artifacts to the web app:

        $ embedl-hub benchmark embedl -m my_model.tflite -d "Samsung Galaxy S25"

    Benchmark a .tflite model on Samsung Galaxy 8 Elite QRD and save
    artifacts to a custom output directory:

        $ embedl-hub benchmark embedl -m my_model.tflite -d "Samsung Galaxy 8 Elite QRD" -o results/

    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import print_profile_summary
    from embedl_hub.core.benchmark.embedl import EmbedlBenchmarker
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    console.log(f"Profiling {model.name} on {device}")
    try:
        benchmarker = EmbedlBenchmarker(device, artifacts_dir=output_dir)
        result = benchmarker.benchmark(
            project_name=ctx.obj["config"]["project_name"],
            experiment_name=ctx.obj["config"]["experiment_name"],
            model_path=model,
        )
    except JobQuotaExceededError as exc:
        console.print(f"[red]Job quota exceeded:[/] {exc}")
        raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[red]✗ profiling failed:[/] {exc}")
        raise typer.Exit(1)

    print_profile_summary(result.summary)

    if output_dir is not None:
        console.print(
            f"[green]✓ Saved benchmark artifacts to:[/] {output_dir.absolute()}"
        )


@benchmark_cli.command("qai-hub", no_args_is_help=True)
def qai_hub_benchmark_command(
    ctx: typer.Context,
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help="Path to a compiled model file (.tflite, .onnx, or .bin), or "
        "to a directory containing an ONNX model and its data files.",
        show_default=False,
    ),
    device: str = typer.Option(
        ..., "-d", "--device", help=DEVICE_HELPER, show_default=False
    ),
    output_dir: Path = typer.Option(
        None, "--output-dir", "-o", help="Output folder for artifacts."
    ),
):
    """Benchmark compiled model using Qualcomm AI Hub.

    Examples:
    ---------
    Benchmark a .tflite model on Samsung Galaxy S25 and save artifacts to
    the default benchmarks folder:

        $ embedl-hub benchmark qai-hub -m my_model.tflite -d "Samsung Galaxy S25"

    Benchmark an .onnx model on Samsung Galaxy 8 Elite QRD and save
    artifacts to a custom output directory:

        $ embedl-hub benchmark qai-hub -m my_model.onnx -d "Samsung Galaxy 8 Elite QRD" -o results/

    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import print_profile_summary
    from embedl_hub.core.benchmark.qai_hub import (
        ProfileError,
        QAIHubBenchmarker,
        write_benchmark_files,
    )
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    console.log(f"Profiling {model.name} on {device} using Qualcomm AI Hub")
    try:
        benchmarker = QAIHubBenchmarker(device)
        result = benchmarker.benchmark(
            project_name=ctx.obj["config"]["project_name"],
            experiment_name=ctx.obj["config"]["experiment_name"],
            model_path=model,
        )
    except (ValueError, ProfileError) as e:
        console.print(f"[red]✗ profiling failed:[/] {e}")
        raise typer.Exit(1)

    summary = result.summary
    full_profile = result.raw

    print_profile_summary(summary)

    summary_path, full_path = write_benchmark_files(
        model, output_dir, summary, full_profile
    )
    console.print(f"[green]✓ Saved benchmark summary to:[/] {summary_path}")
    console.print(
        f"[green]✓ Saved full Qualcomm AI Hub benchmark to:[/] {full_path}"
    )
