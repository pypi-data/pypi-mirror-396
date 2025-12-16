# Copyright (C) 2025 Embedl AB

"""
Functions for quantizing TensorFlow Lite models.
"""

from pathlib import Path

import numpy as np
from ai_edge_litert.interpreter import Interpreter
from ai_edge_quantizer import recipe
from ai_edge_quantizer.quantizer import Quantizer as AIEdgeQuantizer
from ai_edge_quantizer.recipe_manager import ModelQuantizationRecipe
from tensorflow.lite.python import schema_py_generated as schema_fb

from embedl_hub.core.quantize.abc import QuantizationResult, Quantizer
from embedl_hub.core.quantize.calibration_data import (
    load_tflite_calibration_data,
)
from embedl_hub.core.quantize.psnr import (
    log_psnr_results,
    measure_psnr_between_tflite_models,
    print_psnr_results,
)
from embedl_hub.core.utils.tflite_utils import instantiate_tflite_interpreter
from embedl_hub.tracking import log_param


def _quantize_input(float_input, detail):
    """Quantize a float input tensor based on tensor details."""
    qp = detail.get('quantization_parameters', {})
    scales = np.asarray(qp.get('scales', []), dtype=np.float32)
    zps = np.asarray(qp.get('zero_points', []), dtype=np.int32)

    if scales.size == 0:
        # No quantization info, return original input
        return float_input

    # Perform quantization: (float / scale) + zero_point
    quantized = float_input / scales + zps

    # Clip to the dtype's min/max values
    dtype_info = np.iinfo(detail['dtype'])
    quantized = np.clip(quantized, dtype_info.min, dtype_info.max)

    return quantized.astype(detail['dtype'])


def _forward_tflite(
    interpreter: Interpreter,
    input_data: dict[str, np.ndarray],
):
    """Run inference with TFLite model."""

    input_details = interpreter.get_input_details()

    for name, input_sample in input_data.items():
        inp = next((d for d in input_details if name in d['name']), None)
        if not inp:
            raise ValueError(f"Input tensor {name} not found in model.")
        input_sample = _quantize_input(input_sample, inp)
        interpreter.set_tensor(inp['index'], input_sample)

    interpreter.invoke()


def _dequantize(arr, detail):
    """Dequantize an int8/uint8 tensor based on tensor details."""
    qp = detail.get('quantization_parameters', {})
    scales = np.asarray(qp.get('scales', []), dtype=np.float32)
    zps = np.asarray(qp.get('zero_points', []), dtype=np.float32)

    # No quantization info -> just cast
    if scales.size == 0:
        return arr.astype(np.float32)

    x = arr.astype(np.float32)

    # Per-tensor case
    if scales.size == 1:
        scale = scales.item()
        zp = zps.item() if zps.size else 0.0
        return scale * (x - zp)

    # Per-channel case
    axis = qp.get('quantized_dimension', x.ndim - 1)
    if axis < 0:
        axis += x.ndim

    # Reshape scales to broadcast along 'axis'
    shape = [1] * x.ndim
    shape[axis] = scales.size
    scales = scales.reshape(shape)

    # zero_points:
    #  - if 0 or 1 value -> broadcast scalar
    #  - if same length as scales -> reshape like scales
    #  - otherwise, fall back to scalar (common in TFLite: per-channel scales with zp==0)
    if zps.size in (0, 1):
        zp = zps.item() if zps.size else 0.0
        return scales * (x - zp)
    if zps.size == scales.size:
        zps = zps.reshape(shape)
        return scales * (x - zps)
    # Unusual mismatch: warn and treat as scalar
    zp = zps.flat[0]
    return scales * (x - zp)


def _get_builtin_op_name(builtin_code: int) -> str:
    """Get the operation name from builtin code using TFLite schema."""
    # Use the BuiltinOperator enum from the TFLite schema
    try:
        # Get all attributes that start with uppercase (enum values)
        builtin_ops = [
            attr
            for attr in dir(schema_fb.BuiltinOperator)
            if attr.isupper() and not attr.startswith('_')
        ]

        # Create a mapping from enum values to names
        builtin_op_map = {}
        for name in builtin_ops:
            value = getattr(schema_fb.BuiltinOperator, name)
            builtin_op_map[value] = name

        return builtin_op_map.get(builtin_code, f"BUILTIN_{builtin_code}")
    except Exception:
        # Fallback if schema access fails
        return f"BUILTIN_{builtin_code}"


def parse_tflite_model(model_path: str) -> dict:
    """Parse TFLite model to extract operation types for each tensor."""
    # Read the model file
    with open(model_path, 'rb') as f:
        buf = f.read()

    # Parse the model
    model = schema_fb.Model.GetRootAs(buf, 0)

    # Get the subgraph (assuming single subgraph)
    subgraph = model.Subgraphs(0)

    # Create mapping from tensor index to operation type
    tensor_to_op_type = {}

    # Initialize all tensors as unknown
    for i in range(subgraph.TensorsLength()):
        tensor_to_op_type[i] = "Unknown"

    # Process each operator
    for op_idx in range(subgraph.OperatorsLength()):
        operator = subgraph.Operators(op_idx)

        # Get operator code
        opcode_idx = operator.OpcodeIndex()
        opcode = model.OperatorCodes(opcode_idx)

        # Get builtin code
        builtin_code = opcode.BuiltinCode()

        # Get operation name using TFLite schema
        op_name = _get_builtin_op_name(builtin_code)

        # Map output tensors to this operation type
        for j in range(operator.OutputsLength()):
            output_tensor_idx = operator.Outputs(j)
            tensor_to_op_type[output_tensor_idx] = op_name

        # For input tensors, if they don't have an op type yet, mark as input
        for j in range(operator.InputsLength()):
            input_tensor_idx = operator.Inputs(j)
            if tensor_to_op_type.get(input_tensor_idx, "Unknown") == "Unknown":
                # Check if this is actually a model input
                is_model_input = False
                for k in range(subgraph.InputsLength()):
                    if subgraph.Inputs(k) == input_tensor_idx:
                        is_model_input = True
                        break

                if is_model_input:
                    tensor_to_op_type[input_tensor_idx] = "INPUT"
                else:
                    # This is an intermediate tensor without a producing op (constant)
                    tensor_to_op_type[input_tensor_idx] = "CONSTANT"

    return tensor_to_op_type


def _make_random_calibration_data(
    input_names: list[str],
    input_details: list[dict],
) -> list[dict[str, np.ndarray]]:
    """Generate random calibration data for a TFLite model.

    Args:
        input_names: List of input tensor names.
        input_details: List of input tensor details from the interpreter.
    """

    calibration_data = {}
    for name in input_names:
        detail = next((d for d in input_details if name in d['name']), None)
        if detail is None:
            raise ValueError(f"Input tensor {name} not found in model.")
        shape = detail['shape']
        dtype = detail['dtype']
        # Use random data in the valid range for the dtype
        if np.issubdtype(dtype, np.integer):
            info = np.iinfo(dtype)
            data = np.random.randint(
                info.min, info.max + 1, size=shape, dtype=dtype
            )
        else:
            data = np.random.randn(*shape).astype(dtype)
        calibration_data[name] = data

    # Generate a few calibration samples
    return [calibration_data]


def _load_calibration_data(
    interpreter: Interpreter,
    data_path: Path | None,
    num_samples: int,
) -> tuple[int, list[dict[str, np.ndarray]]]:
    """Load calibration data from the specified path.

    Args:
        interpreter: TFLite interpreter for the model.
        data_path: Path to the calibration data directory.
        num_samples: Number of samples to load.
    Returns:
        A tuple of (num_samples, calibration_data) where calibration_data is a list
        of dictionaries mapping input names to numpy arrays.
    """

    signatures: dict[str, dict[str, list[str]]] = (
        interpreter.get_signature_list()
    )
    signature_key = list(signatures.keys())[0]
    input_names = signatures[signature_key]['inputs']

    if data_path is None:
        return 1, _make_random_calibration_data(
            input_names=input_names,
            input_details=interpreter.get_input_details(),
        )

    calibration_data = load_tflite_calibration_data(
        interpreter=interpreter, data_path=data_path
    )
    calibration_data = calibration_data[:num_samples]

    return len(calibration_data), calibration_data


class TFLiteQuantizer(Quantizer):
    """Quantizer for TensorFlow Lite models using AI Edge Quantizer."""

    supported_input_model_formats = {".tflite"}

    def __init__(
        self,
        num_samples: int,
        data_path: Path | None = None,
    ):
        """Initialize the TFLite quantizer.

        Args:
            num_samples: Number of calibration samples to use.
            data_path: Path to the calibration data directory.
        """
        self.num_samples = num_samples
        self.data_path = data_path

    def _quantize(
        self,
        model_path: Path,
        output_path: Path | None,
    ) -> QuantizationResult:
        """Quantize the TFLite model.

        Args:
            model_path: Path to the input float TFLite model.
            output_path: Path to save the quantized int8 TFLite model.

        Returns:
            QuantizationResult with path to quantized model.
        """
        if output_path is None:
            output_path = model_path.with_name(
                model_path.stem + "_int8.tflite"
            )

        quantize_tflite_model(
            float_model_path=model_path,
            int8_model_path=output_path,
            num_samples=self.num_samples,
            data_path=self.data_path,
            report_psnr=True,
        )

        return QuantizationResult(model_path=output_path)


def _log_quantization_params(
    model_interpreter: Interpreter,
    num_samples: int,
):
    """Log number of samples and input sizes used for quantization."""
    log_param("num samples", str(num_samples))

    signatures: dict[str, dict[str, list[str]]] = (
        model_interpreter.get_signature_list()
    )
    signature_key = list(signatures.keys())[0]
    input_names = signatures[signature_key]['inputs']
    input_details = model_interpreter.get_input_details()

    def _format_img_size(value: np.ndarray) -> str:
        """Format image size for logging."""
        return "x".join(str(x) for x in value)

    for name in input_names:
        detail = next((d for d in input_details if name in d['name']), None)
        if detail is None:
            raise ValueError(f"Input tensor {name} not found in model.")
        shape = detail['shape']
        log_param(f"{name} input shape", _format_img_size(shape))


def quantize_tflite_model(
    float_model_path: Path,
    int8_model_path: Path,
    num_samples: int,
    data_path: Path | None = None,
    quantization_recipe: ModelQuantizationRecipe | None = None,
    report_psnr: bool = True,
):
    """Quantize a TFLite model to int8 using AI Edge Quantizer.

    Args:
        float_model_path: Path to the input float TFLite model.
        int8_model_path: Path to save the quantized int8 TFLite model.
        calibration_data: Optional dictionary of input data for calibration.
        quantization_recipe: The quantization recipe to use.
        compute_psnr: Whether to compute and print PSNR between float and int8 models.
    """
    if quantization_recipe is None:
        quantization_recipe = recipe.static_wi8_ai8()

    float_interpreter = instantiate_tflite_interpreter(
        str(float_model_path), experimental_preserve_all_tensors=True
    )

    signatures: dict[str, dict[str, list[str]]] = (
        float_interpreter.get_signature_list()
    )
    signature_key = list(signatures.keys())[0]

    tflite_quantizer = AIEdgeQuantizer(
        str(float_model_path), quantization_recipe=quantization_recipe
    )

    num_samples, calibration_data = _load_calibration_data(
        float_interpreter, data_path, num_samples
    )
    _log_quantization_params(float_interpreter, num_samples)

    calibration_result = tflite_quantizer.calibrate(
        {signature_key: calibration_data}
    )
    quantization_result = tflite_quantizer.quantize(calibration_result)
    quantization_result.export_model(int8_model_path)

    if not report_psnr:
        # No need to compute PSNR
        return

    quant_interpreter = instantiate_tflite_interpreter(
        str(int8_model_path), experimental_preserve_all_tensors=True
    )

    _forward_tflite(
        float_interpreter,
        input_data=calibration_data[0],
    )
    _forward_tflite(
        quant_interpreter,
        input_data=calibration_data[0],
    )

    layer_psnr, output_psnr = measure_psnr_between_tflite_models(
        float_interpreter=float_interpreter,
        int8_interpreter=quant_interpreter,
        float_tensor_to_op_type=parse_tflite_model(str(float_model_path)),
    )
    print_psnr_results(layer_psnr, output_psnr)
    log_psnr_results(layer_psnr, output_psnr)
