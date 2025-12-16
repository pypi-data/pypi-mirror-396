# Copyright (C) 2025 Embedl AB

"""Module for quantizing ONNX models using Qualcomm AI Hub."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import qai_hub as hub

from embedl_hub.core.quantize.abc import (
    QuantizationError,
    QuantizationResult,
    Quantizer,
)
from embedl_hub.core.quantize.calibration_data import (
    load_onnx_calibration_data,
)
from embedl_hub.core.quantize.psnr import (
    log_psnr_results,
    measure_psnr_between_onnx_models,
    print_psnr_results,
)
from embedl_hub.core.utils.onnx_utils import load_onnx_model
from embedl_hub.core.utils.qai_hub_utils import save_qai_hub_model
from embedl_hub.tracking import log_param


def get_input_shapes(model_path: Path) -> dict[str, tuple[int, ...]]:
    """
    Get the input shape of the ONNX model.

    Args:
        model_path: Path to the ONNX model.

    Returns:
        Dictionary with input names and their shapes.
    """

    onnx_model = load_onnx_model(model_path)
    input_shapes = {}
    for model_input in onnx_model.graph.input:
        shape = []
        for dim in model_input.type.tensor_type.shape.dim:
            if dim.dim_value > 0:
                shape.append(dim.dim_value)
            else:
                shape.append(1)  # Use 1 for dynamic dimensions
        input_shapes[model_input.name] = tuple(shape)
    return input_shapes


def _generate_random_data(
    model_path: Path,
) -> dict[str, list[np.ndarray]]:
    """
    Generate random calibration data for quantization.

    Args:
        model_path: Path to the ONNX model.

    Returns:
        Dataset with random calibration data.
    """

    def _make_random_sample(shape: tuple[int, ...]) -> np.ndarray:
        """Generate a random sample with the given shape."""
        return np.random.rand(*shape).astype(np.float32)

    inputs_and_shapes = get_input_shapes(model_path=model_path)

    return {
        input_name: [_make_random_sample(shape)]
        for input_name, shape in inputs_and_shapes.items()
    }


def _load_calibration_data(
    model_path: Path, data_path: Path, num_samples: int
) -> tuple[int, dict[str, list[np.ndarray]]]:
    """
    Load calibration data from the specified path.

    Args:
        model_path: Path to the ONNX model.
        data_path: Path to the calibration data.
        num_samples: Number of samples to load.

    Returns:
        Tuple of number of samples and dictionary with calibration data.
    """

    dataset = load_onnx_calibration_data(
        model_path=model_path, data_path=data_path
    )
    for input_name, input_samples in dataset.items():
        dataset[input_name] = input_samples[:num_samples]
        num_samples = min(num_samples, len(dataset[input_name]))
    return num_samples, dataset


def collect_calibration_data(
    model_path: Path,
    data_path: Path | None,
    num_samples: int,
) -> tuple[int, dict[str, list[np.ndarray]]]:
    """
    Collect calibration data for quantization.

    Args:
        model_path: Path to the ONNX model.
        data_path: Path to the calibration data.
        num_samples: Number of samples to use.

    Returns:
        Tuple of number of samples and dictionary with calibration data.
    """
    if data_path is None:
        return 1, _generate_random_data(model_path=model_path)
    return _load_calibration_data(
        model_path=model_path, data_path=data_path, num_samples=num_samples
    )


def log_quantization_params(model_path: Path, num_samples: int) -> None:
    """Log the quantization parameters for tracking."""

    def _format_img_size(value: int | list[int]) -> str:
        """Format image size for logging."""
        return str(value).strip("[]").replace(", ", "x").strip()

    log_param("num samples", str(num_samples))

    def _find_input_sizes(
        model_path: Path,
    ) -> list[tuple[str, list[int]]]:
        """Find input sizes from the model."""
        onnx_model = load_onnx_model(model_path)
        input_sizes = []
        for model_input in onnx_model.graph.input:
            shape = []
            for dim in model_input.type.tensor_type.shape.dim:
                if dim.dim_value > 0:
                    shape.append(dim.dim_value)
                else:
                    shape.append(1)  # Use 1 for dynamic dimensions
            input_sizes.append((model_input.name, shape))
        return input_sizes

    for input_name, shape in _find_input_sizes(model_path=model_path):
        log_param(f"{input_name} input shape", _format_img_size(shape))


class QAIHubQuantizer(Quantizer):
    """Quantizer that uses Qualcomm AI Hub for quantization."""

    supported_input_model_formats = {".onnx"}
    supports_input_model_folders = True

    def __init__(
        self,
        num_samples: int,
        data_path: Path | None = None,
    ):
        self.num_samples = num_samples
        self.data_path = data_path

    def _quantize(self, model_path, output_path):
        return quantize_model(
            model_path=model_path,
            output_file=output_path,
            num_samples=self.num_samples,
            data_path=self.data_path,
        )


def quantize_model(
    model_path: Path,
    output_file: Path,
    num_samples: int,
    data_path: Path | None = None,
) -> QuantizationResult:
    """
    Submit an ONNX model to Qualcomm AI Hub and retrieve the compiled artifact.

    Args:

    Returns:
        QuantizationResult with local path to compiled model.

    """

    if not model_path.exists():
        raise ValueError(f"Model not found: {model_path}")

    num_samples, calibration_data = collect_calibration_data(
        model_path=model_path, data_path=data_path, num_samples=num_samples
    )
    log_quantization_params(model_path=model_path, num_samples=num_samples)

    try:
        job = hub.submit_quantize_job(
            model=model_path.as_posix(),
            weights_dtype=hub.QuantizeDtype.INT8,
            activations_dtype=hub.QuantizeDtype.INT8,
            calibration_data=calibration_data,
        )
    except Exception as error:
        raise QuantizationError(
            "Failed to submit quantization job."
        ) from error

    log_param("$qai_hub_job_id", job.job_id)

    try:
        quantized = job.get_target_model()
    except Exception as error:
        raise QuantizationError(
            "Failed to download quantized model from Qualcomm AI Hub."
        ) from error
    if quantized is None:
        raise QuantizationError(
            "Quantized model returned by Qualcomm AI Hub is None."
        )

    local_path = save_qai_hub_model(quantized, output_file)

    try:
        layer_psnr, output_psnr = measure_psnr_between_onnx_models(
            model_path,
            local_path,
            calibration_data,
        )
        print_psnr_results(layer_psnr, output_psnr)
        log_psnr_results(layer_psnr, output_psnr)
    except Exception as error:
        # Log PSNR measurement failure but do not fail the quantization.
        print(f"Warning: Failed to measure PSNR: {error}")
    return QuantizationResult(model_path=local_path, job_id=job.job_id)
