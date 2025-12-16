# Copyright (C) 2025 Embedl AB

"""
embedl-hub compile - send an model to Qualcomm AI Hub, retrieve a
device-specific binary (.tflite for tflite, .bin for qnn, or .onnx for onnxruntime).
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import typer

# All other embedl_hub imports should be done inside the function.
from embedl_hub.cli.helper import (
    DEVICE_HELPER,
    EMBEDL_CLOUD_COMPILE_MODEL_HELPER,
    OUTPUT_FILE_HELPER,
    QUALCOMM_COMPILE_MODEL_HELPER,
    SIZE_HELPER,
)

compile_cli = typer.Typer(
    name="compile",
    help="Compilation commands (default subcommand: 'embedl').",
    invoke_without_command=True,
)


@compile_cli.callback(invoke_without_command=True)
def compile_command(
    ctx: typer.Context,
    model: Path | None = typer.Option(
        None,
        "-m",
        "--model",
        help=EMBEDL_CLOUD_COMPILE_MODEL_HELPER,
        show_default=False,
    ),
    output_file: Path = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
    fp16: bool = typer.Option(
        False,
        "--fp16",
        is_flag=True,
        help="Enable FP16 quantization for the TFLite model.",
        show_default=True,
    ),
):
    """
    Compile a model into a device ready binary using local compilation tools or cloud services.
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
            onnx_to_tflite_compile_command,
            ctx=ctx,
            model=model,
            output_file=output_file,
            fp16=fp16,
        )


@compile_cli.command("embedl", no_args_is_help=True)
def onnx_to_tflite_compile_command(
    ctx: typer.Context,
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help=EMBEDL_CLOUD_COMPILE_MODEL_HELPER,
        show_default=False,
    ),
    output_file: Path = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
    fp16: bool = typer.Option(
        False,
        "--fp16",
        is_flag=True,
        help="Enable FP16 quantization for the TFLite model.",
        show_default=True,
    ),
):
    """
    Compile an ONNX model into a TensorFlow Lite model.
    The result is a saved TensorFlow model and two TFLite (both float32 and float16)
    models in the specified output folder.

    Examples
    --------

    Compile the ONNX model `model.onnx` to TensorFlow Lite format:

        $ embedl-hub compile embedl -m model.onnx -o ./my_outputs/

    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.core.compile import ONNXToTFCompiler
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    ONNXToTFCompiler.validate_core_args(
        model_path=model, output_path=output_file
    )
    compiler = ONNXToTFCompiler(fp16=fp16)
    res = compiler.compile(
        project_name=ctx.obj["config"]["project_name"],
        experiment_name=ctx.obj["config"]["experiment_name"],
        model_path=model,
        output_path=output_file,
    )
    console.print(f"[green]✓ Compiled model to {res.model_path}[/]")


@compile_cli.command("qai-hub", no_args_is_help=True)
def qai_hub_compile_command(
    ctx: typer.Context,
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help=QUALCOMM_COMPILE_MODEL_HELPER,
        show_default=False,
    ),
    output_file: Path = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
    device: str = typer.Option(
        ...,
        "-d",
        "--device",
        help=DEVICE_HELPER,
        show_default=False,
    ),
    size: str = typer.Option(
        ...,
        "--size",
        "-s",
        help=SIZE_HELPER,
        show_default=False,
    ),
    runtime: str = typer.Option(
        ...,
        "-r",
        "--runtime",
        help="Runtime backend for compilation: tflite, qnn, or onnx.",
    ),
    quantize_io: bool = typer.Option(
        False,
        "--quantize-io",
        help="Quantize input and output tensors. "
        "Improves performance on platforms that support quantized I/O.",
        show_default=True,
    ),
):
    """
    Compile a model into a device ready binary using Qualcomm AI Hub.

    Examples
    --------

    Compile the ONNX model `fp32_model.onnx` with input size 1x3x224x224 for the Samsung Galaxy S24 using the tflite runtime:

        $ embedl-hub compile qai-hub -m fp32_model.onnx  --size 1,3,224,224 -d "Samsung Galaxy S24" -r tflite

    Compile the TorchScript model `model.pt` with input size 1x3x224x224
    for the Samsung Galaxy S24, and save it to `./my_outputs/model.onnx`:

        $ embedl-hub compile qai-hub -m model.pt -r onnx --size 1,3,224,224 --device "Samsung Galaxy S24" -o ./my_outputs/model.onnx
    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import (
        assert_api_config,
        prepare_compile_kwargs,
    )
    from embedl_hub.core.compile import (
        CompileError,
        CompileResult,
        QAIHubCompiler,
    )
    from embedl_hub.core.context import require_initialized_ctx
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    assert_api_config()
    require_initialized_ctx(ctx.obj["config"])

    with TemporaryDirectory() as tmpdir:
        compile_kwargs = prepare_compile_kwargs(
            model, device, runtime, size, tmpdir, quantize_io, output_file
        )
        QAIHubCompiler.validate_core_args(
            model_path=compile_kwargs["model_path"],
            output_path=compile_kwargs["output_file"],
        )
        compiler = QAIHubCompiler(
            device=compile_kwargs["device"],
            runtime=compile_kwargs["runtime"],
            quantize_io=compile_kwargs["quantize_io"],
            input_size=compile_kwargs["input_size"],
        )
        try:
            res: CompileResult = compiler.compile(
                project_name=ctx.obj["config"]["project_name"],
                experiment_name=ctx.obj["config"]["experiment_name"],
                model_path=compile_kwargs["model_path"],
                output_path=compile_kwargs["output_file"],
            )
            console.print(f"[green]✓ Compiled model for {res.device}[/]")

            # TODO: upload artifacts to web
        except (CompileError, ValueError) as error:
            console.print(f"[red]✗ {error}[/]")
            raise typer.Exit(1)
