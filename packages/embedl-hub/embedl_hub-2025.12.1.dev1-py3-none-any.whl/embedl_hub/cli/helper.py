# Copyright (C) 2025 Embedl AB

"""
Module containing a unified set of helper texts for CLI commands.
"""

# To avoid slowing down the CLI, avoid imports in this file.

CONFIG_HELPER = (
    "Path to an optional YAML configuration file for advanced settings."
)
DEVICE_HELPER = (
    "Target device name for deployment. "
    "Use command `list-devices` to view all available options."
)
OUTPUT_FILE_HELPER = "Path to the output file or directory where the resulting model will be saved."
SIZE_HELPER = "Input size of the model (e.g., 1,3,224,224)."

### Qualcomm AI Hub specific helpers
QUALCOMM_COMPILE_MODEL_HELPER = (
    "Path to the TorchScript model file, ONNX model file, or to a directory "
    "containing the ONNX model and any associated data files, to be compiled."
)
QUALCOMM_QUANTIZE_MODEL_HELPER = (
    "Path to ONNX model file, or to a directory "
    "containing the ONNX model and any associated data files, to be quantized."
)

## Embedl cloud specific helpers
EMBEDL_CLOUD_COMPILE_MODEL_HELPER = (
    "Path to an ONNX model file, or to a directory "
    "containing the ONNX model and any associated data files, to be compiled."
)
EMBEDL_CLOUD_QUANTIZE_MODEL_HELPER = (
    "Path to a TFLite model file to be quantized."
)
