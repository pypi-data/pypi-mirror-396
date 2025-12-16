# Copyright (C) 2025 Embedl AB

"""Module for loading calibration data for quantization."""

from pathlib import Path

import numpy as np
from ai_edge_litert.interpreter import Interpreter

from embedl_hub.core.utils.onnx_utils import load_onnx_model


def load_calibration_dataset(
    data_path: Path,
    input_names: list[str],
) -> dict[str, list[np.ndarray]]:
    """
    Create a Dataset for calibration data.

    Args:
        model_path: Path to the ONNX model.
        data_path: Path to the calibration data.

    If single input, data path should contain numpy files (.npy).
    If multiple inputs, data path should contain subdirectories named after
    the input names, each containing numpy files (.npy).

    Returns:
        Dataset for calibration data.
    """
    if not data_path or not data_path.is_dir():
        raise ValueError(f"Invalid data path: {data_path}")

    if len(input_names) == 1:
        # Single input model
        input_name = input_names[0]
        npy_files = sorted(data_path.glob("*.npy"))
        if not npy_files:
            raise FileNotFoundError(f"No .npy files found in {data_path}")
        return {input_name: [np.load(f) for f in npy_files]}

    # Multiple input model
    datasets = {}
    num_input_samples = set()
    for input_name in input_names:
        input_dir = data_path / input_name
        if not input_dir.is_dir():
            raise FileNotFoundError(
                f"Input directory not found for input '{input_name}': {input_dir}"
            )
        npy_files = sorted(input_dir.glob("*.npy"))
        if not npy_files:
            raise FileNotFoundError(f"No .npy files found in {input_dir}")
        datasets[input_name] = [np.load(f) for f in npy_files]
        num_input_samples.add(len(datasets[input_name]))

    if len(num_input_samples) != 1:
        raise ValueError("All inputs must have the same number of samples.")
    return datasets


def load_onnx_calibration_data(
    model_path: Path,
    data_path: Path,
) -> dict[str, list[np.ndarray]]:
    """
    Load calibration data for an ONNX model.

    Args:
        model_path: Path to the ONNX model.
        data_path: Path to the calibration data.

    Returns:
        Dataset with random calibration data.
    """

    onnx_model = load_onnx_model(model_path=model_path)
    input_names = [i.name for i in onnx_model.graph.input]
    return load_calibration_dataset(
        data_path=data_path,
        input_names=input_names,
    )


def load_tflite_calibration_data(
    interpreter: Interpreter,
    data_path: Path,
) -> list[dict[str, np.ndarray]]:
    """
    Load calibration data for TFLite model.

    Args:
        interpreter: TFLite interpreter for the model.
        data_path: Path to the calibration data.
    Returns:
        Dataset with calibration data.
    """

    signatures: dict[str, dict[str, list[str]]] = (
        interpreter.get_signature_list()
    )
    signature_key = list(signatures.keys())[0]
    input_names = signatures[signature_key]['inputs']

    calibration_data = load_calibration_dataset(
        data_path=data_path,
        input_names=input_names,
    )
    return [
        {name: calibration_data[name][i] for name in input_names}
        for i in range(len(calibration_data[input_names[0]]))
    ]
