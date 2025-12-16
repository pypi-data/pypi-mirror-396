# Copyright (C) 2025 Embedl AB
"""
Core compile logic for the embedl-hub CLI.

Handles submitting models to Qualcomm AI Hub for compilation and saving the resulting artifacts.
"""

from __future__ import annotations

from pathlib import Path

import qai_hub as hub
from qai_hub.client import CompileJob

from embedl_hub.core.compile.abc import CompileError, Compiler, CompileResult
from embedl_hub.core.hardware.qai_hub import create_device
from embedl_hub.core.utils.qai_hub_utils import (
    get_global_qai_hub_client,
    get_job_result,
    parse_runtime_info,
    save_qai_hub_model,
)
from embedl_hub.core.utils.tracking_utils import log_artifact
from embedl_hub.tracking import log_param


# pylint: disable-next=too-few-public-methods
class QAIHubCompiler(Compiler):
    """Compiler that uses Qualcomm AI Hub to compile models."""

    supported_input_model_formats = {".onnx", ".pt", ".pth"}
    supports_input_model_folders = True

    def __init__(
        self,
        device: str,
        runtime: str,
        quantize_io: bool = False,
        input_size: tuple[int, ...] | None = None,
    ):
        """
        Initialize the QAIHubCompiler.

        Args:
            device: Device nickname, e.g. 'Samsung Galaxy S24'.
            runtime: 'tflite' | 'qnn' | 'onnx'
            quantize_io: Add --quantize_io to options.
            input_size: Input size as (dim0, dim1, ...) tuple, e.g. (1, 3, 224, 224).
        """

        self.device = self._validate_device(device)
        self.runtime = runtime
        self.quantize_io = quantize_io
        self.input_size = input_size

    def _validate_device(self, device: str) -> hub.Device:
        """Validate that the specified device is supported by Qualcomm AI Hub."""
        return create_device(device)

    def _compile(
        self,
        model_path: Path,
        output_path: Path | None = None,
    ) -> CompileResult:
        """
        Compile a model using Qualcomm AI Hub.

        Args:
            project_name: Name of the project.
            experiment_name: Name of the experiment.
            model_path: Path to TorchScript/ONNX (INT8 or FP32).

        Returns:
            CompileResult with local path to compiled model.
        """
        return compile_model(
            model_path=model_path,
            device=self.device,
            runtime=self.runtime,
            quantize_io=self.quantize_io,
            output_file=output_path,
            input_size=self.input_size,
        )


def compile_model(
    model_path: Path,
    device: hub.Device,
    runtime: str,
    quantize_io: bool = False,
    output_file: Path | str | None = None,
    input_size: tuple[int, ...] | None = None,
) -> CompileResult:
    """
    Submit an ONNX model to Qualcomm AI Hub and retrieve the compiled artifact.

    Args:
        model_path: Path to TorchScript/ONNX (INT8 or FP32).
        device: Device object, e.g. hub.Device(name='Samsung Galaxy S24').
        runtime: 'tflite' | 'qnn' | 'onnx'
        quantize_io: Add --quantize_io to options.
        output_file: Compiled model filename. File ending added automatically if not specified.
        input_size: Input size as (dim0, dim1, ...) tuple, e.g. (1, 3, 224, 224).

    Returns:
        CompileResult with local path to compiled model.
    """

    return _compile_model(
        model_file=model_path,
        device=device,
        runtime=runtime,
        quantize_io=quantize_io,
        output_file=output_file,
        input_size=input_size,
    )


def _compile_model(
    model_file: Path,
    device: hub.Device,
    runtime: str = "tflite",
    quantize_io: bool = False,
    output_file: Path | str | None = None,
    input_size: tuple[int, ...] | None = None,
) -> CompileResult:
    """
    Submit a model to Qualcomm AI Hub and retrieve the compiled artifact.

    Args:
        model_file: Path to the model.
        device: Device object, e.g. hub.Device(name='Samsung Galaxy S24').
        runtime: 'tflite' | 'qnn' | 'onnx'
        quantize_io: Add --quantize_io to options.
        output_file: Compiled model filename. File ending added automatically if not specified.
        input_size: Input size as tuple, e.g. (1, 3, 224, 224).

    Returns:
        CompileResult with local path to compiled model.

    """
    log_param("$device", device.name)

    opts = f"--target_runtime {runtime}"
    if quantize_io:
        opts += " --quantize_io"

    input_specs = {"image": input_size} if input_size else None

    try:
        job: CompileJob = hub.submit_compile_job(
            model=model_file.as_posix(),
            device=device,
            options=opts,
            input_specs=input_specs,
        )
    except Exception as error:
        raise CompileError("Failed to submit compile job.") from error

    log_param("$qai_hub_job_id", job.job_id)

    try:
        compiled_model = job.get_target_model()
    except Exception as error:
        raise CompileError(
            "Failed to download compiled model from Qualcomm AI Hub."
        ) from error
    compiled_model_path = save_qai_hub_model(compiled_model, output_file)

    if "qnn" in runtime:
        # Compile jobs with --target-runtime qnn_dlc, qnn_lib_aarch64_android or
        # qnn_context_binary don't expose runtime info in the job result
        logged_runtime = "QNN"
    else:
        try:
            job_result = get_job_result(
                job.job_id, get_global_qai_hub_client().config
            )
            logged_runtime = parse_runtime_info(job_result)
        except RuntimeError as error:
            raise CompileError("Failed to parse runtime info.") from error
    log_param("$runtime", logged_runtime)

    log_artifact(compiled_model_path)

    return CompileResult(
        model_path=compiled_model_path,
        job_id=job.job_id,
        device=device.name,
    )
