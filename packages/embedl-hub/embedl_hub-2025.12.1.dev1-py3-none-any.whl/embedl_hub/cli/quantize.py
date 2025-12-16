# Copyright (C) 2025 Embedl AB

"""
embedl-hub quantize - send an onnx model to Qualcomm AI Hub and retrieve a
quantized onnx model.
"""

from pathlib import Path

import typer

# All other embedl_hub imports should be done inside the function.
from embedl_hub.cli.helper import (
    EMBEDL_CLOUD_QUANTIZE_MODEL_HELPER,
    OUTPUT_FILE_HELPER,
    QUALCOMM_QUANTIZE_MODEL_HELPER,
)

quantize_cli = typer.Typer(
    name="quantize",
    help="Quantize commands (default: 'embedl').",
    invoke_without_command=True,
)


@quantize_cli.callback(invoke_without_command=True)
def quantize_command(
    ctx: typer.Context,
    model: Path = typer.Option(
        None,
        "-m",
        "--model",
        help=EMBEDL_CLOUD_QUANTIZE_MODEL_HELPER,
        show_default=False,
    ),
    data_path: Path = typer.Option(
        None,
        "--data",
        "-d",
        help=(
            "Path to the dataset used for calibration. "
            "If not provided, random data will be used for calibration. "
            "If the model is a single-input model, the directory should contain "
            "numpy files (.npy) with the input data. "
            "If the model has multiple inputs, the directory should contain "
            "subdirectories named after the input names, each containing "
            "numpy files (.npy) with the corresponding input data."
        ),
        show_default=False,
    ),
    output_file: Path = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
    num_samples: int = typer.Option(
        500,
        "--num-samples",
        "-n",
        help="Number of data samples to use during quantization calibration.",
        show_default=True,
    ),
):
    """
    Quantize a model to make it more efficient on your edge platform.
    """
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
        ctx.invoke(
            tflite_quantize_command,
            ctx=ctx,
            model=model,
            data_path=data_path,
            output_file=output_file,
            num_samples=num_samples,
        )


@quantize_cli.command("embedl", no_args_is_help=True)
def tflite_quantize_command(
    ctx: typer.Context,
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help=EMBEDL_CLOUD_QUANTIZE_MODEL_HELPER,
        show_default=False,
    ),
    data_path: Path = typer.Option(
        None,
        "--data",
        "-d",
        help=(
            "Path to the dataset used for calibration. "
            "If not provided, random data will be used for calibration. "
            "If the model is a single-input model, the directory should contain "
            "numpy files (.npy) with the input data. "
            "If the model has multiple inputs, the directory should contain "
            "subdirectories named after the input names, each containing "
            "numpy files (.npy) with the corresponding input data."
        ),
        show_default=False,
    ),
    output_file: Path = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
    num_samples: int = typer.Option(
        500,
        "--num-samples",
        "-n",
        help="Number of data samples to use during quantization calibration.",
        show_default=True,
    ),
):
    """
    Quantize a TFLite model to int8 using post-training quantization.

    Examples
    --------
    Quantize the TFLite model `compiled_model.tflite` calibrating on data
    from `/path/to/dataset/` using 1000 samples from the dataset:

        $ embedl-hub quantize embedl -m compiled_model.tflite -d /path/to/dataset/ -n 1000

    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.core.hub_logging import console
    from embedl_hub.core.quantize import TFLiteQuantizer
    # pylint: enable=import-outside-toplevel

    if not output_file:
        output_file = Path(model).with_suffix(".quantized.tflite")
        console.print(
            f"[yellow]No output file specified, using default: {output_file}[/]"
        )
    if data_path is None:
        console.print(
            "[yellow]No data path specified, generating random calibration data.[/]"
        )

    TFLiteQuantizer.validate_core_args(model, output_file)
    quantizer = TFLiteQuantizer(num_samples=num_samples, data_path=data_path)
    res = quantizer.quantize(
        project_name=ctx.obj["config"]["project_name"],
        experiment_name=ctx.obj["config"]["experiment_name"],
        model_path=model,
        output_path=output_file,
    )
    console.print(f"[green]✓ Quantized model saved to {res.model_path}[/]")


@quantize_cli.command("qai-hub", no_args_is_help=True)
def qai_hub_quantize_command(
    ctx: typer.Context,
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help=QUALCOMM_QUANTIZE_MODEL_HELPER,
        show_default=False,
    ),
    data_path: Path = typer.Option(
        None,
        "--data",
        "-d",
        help=(
            "Path to the dataset used for calibration. "
            "If not provided, random data will be used for calibration. "
            "If the model is a single-input model, the directory should contain "
            "numpy files (.npy) with the input data. "
            "If the model has multiple inputs, the directory should contain "
            "subdirectories named after the input names, each containing "
            "numpy files (.npy) with the corresponding input data."
        ),
        show_default=False,
    ),
    output_file: Path = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
    num_samples: int = typer.Option(
        500,
        "--num-samples",
        "-n",
        help="Number of data samples to use during quantization calibration.",
        show_default=True,
    ),
):
    """
    Quantize an ONNX model using Qualcomm AI Hub.

    Examples
    --------
    Quantize the ONNX model `compiled_model.onnx` calibrating on data
    from `/path/to/dataset/` using 1000 samples from the dataset:

        $ embedl-hub quantize qai-hub -m compiled_model.onnx -d /path/to/dataset/ -n 1000

    """

    # pylint: disable=import-outside-toplevel
    from tempfile import TemporaryDirectory

    from embedl_hub.core.hub_logging import console
    from embedl_hub.core.quantize import QAIHubQuantizer
    from embedl_hub.core.utils.onnx_utils import (
        maybe_package_onnx_folder_to_file,
    )
    # pylint: enable=import-outside-toplevel

    if not output_file:
        output_file = Path(model).with_suffix(".quantized.onnx")
        console.print(
            f"[yellow]No output file specified, using default: {output_file}[/]"
        )
    if data_path is None:
        console.print(
            "[yellow]No data path specified, generating random calibration data.[/]"
        )

    QAIHubQuantizer.validate_core_args(model, output_file)
    with TemporaryDirectory() as tmpdir:
        model = maybe_package_onnx_folder_to_file(model, tmpdir)
        quantizer = QAIHubQuantizer(
            data_path=data_path, num_samples=num_samples
        )
        res = quantizer.quantize(
            project_name=ctx.obj["config"]["project_name"],
            experiment_name=ctx.obj["config"]["experiment_name"],
            model_path=model,
            output_path=output_file,
        )
    console.print(f"[green]✓ Quantized model saved to {res.model_path}[/]")
