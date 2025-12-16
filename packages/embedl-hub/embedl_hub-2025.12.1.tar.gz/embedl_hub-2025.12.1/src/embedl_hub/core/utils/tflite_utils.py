# Copyright (C) 2025 Embedl AB

"""
Utility functions for working with TFLite models.
"""

import re
from pathlib import Path

from google.protobuf import json_format


def instantiate_tflite_interpreter(
    model_path: str, experimental_preserve_all_tensors: bool = False
) -> 'Interpreter':
    """Instantiate a TFLite interpreter and allocate tensors."""

    # pylint: disable=import-outside-toplevel
    # TF logging showed up in cli output without this.
    from ai_edge_litert.interpreter import Interpreter
    # pylint: enable=import-outside-toplevel

    interpreter = Interpreter(
        model_path=model_path,
        experimental_preserve_all_tensors=experimental_preserve_all_tensors,
    )
    interpreter.allocate_tensors()
    return interpreter


def get_tflite_model_input_names(model_path: str) -> list[str]:
    """Get the input tensor names of a TFLite model.

    Args:
        model_path: Path to the TFLite model file.

    Returns:
        A list of input tensor names.
    """
    interpreter = instantiate_tflite_interpreter(model_path)

    signatures: dict[str, dict[str, list[str]]] = (
        interpreter.get_signature_list()
    )
    signature_key = list(signatures.keys())[0]
    return signatures[signature_key]['inputs']


def _count_layers_by_unit(execution_detail: dict) -> dict[str, int]:
    """Count layers by compute unit (CPU, GPU, NPU) from execution detail."""

    num_layers = sum(
        len(subgraph.get('perOpProfiles', []))
        for subgraph in execution_detail['runtimeProfile']['subgraphProfiles']
    )
    # TODO: Add proper compute unit parsing when available in TFLite profiling
    counts = {"CPU": num_layers, "GPU": 0, "NPU": 0}
    return counts


def _parse_memory_from_log_file(log_file: Path) -> float | None:
    """
    Parse memory usage (in MB) from a tflite benchmark log string.
    """

    log_text = log_file.read_text(encoding="utf-8", errors="ignore")

    MEMORY_LINE_RE = re.compile(
        r"Memory footprint delta from the start of the tool \(MB\):\s*"
        r"init=(?P<init>\d+(?:\.\d+)?)\s+overall=(?P<overall>\d+(?:\.\d+)?)"
    )

    for line in log_text.splitlines():
        print(line)
        match = MEMORY_LINE_RE.search(line)
        if match:
            return float(match.group("overall"))
    return None


def parse_tflite_profiling_artifacts(
    proto_path: Path,
    log_path: Path,
) -> tuple[dict, list[dict]]:
    """Parse TFLite profiling proto and return a summary dictionary and execution details."""

    # pylint: disable=import-outside-toplevel
    # TF logging showed up in cli output without this.
    from tensorflow.lite.profiling.proto import profiling_info_pb2
    # pylint: enable=import-outside-toplevel

    proto = profiling_info_pb2.BenchmarkProfilingData()
    with proto_path.open("rb") as f:
        proto.ParseFromString(f.read())
        profile_info = json_format.MessageToDict(proto)

    layer_times = []
    execution_detail = []

    for subgraph in profile_info['runtimeProfile']['subgraphProfiles']:
        for layer in subgraph['perOpProfiles']:
            name = layer['name']
            latency_us = float(layer['inferenceMicroseconds']['avg'])
            node_type = layer['nodeType']
            layer_times.append((latency_us, name, node_type))
            layer_record = {
                "name": name,
                "type": node_type,
                "compute_unit": "CPU",
                "execution_time": latency_us,
                "execution_cycles": 0,
            }
            execution_detail.append(layer_record)

    total_latency_ms = (
        sum(layer_time_us[0] for layer_time_us in layer_times) / 1000.0
    )

    # Top 5 slowest layers
    top_5_layers = sorted(layer_times, reverse=True)[:5]

    summary_dict = {
        "mean_ms": total_latency_ms,
        "peak_memory_usage_mb": _parse_memory_from_log_file(log_path) or 0.0,
        "layer_times": top_5_layers,
        "layers": execution_detail,
        "layers_by_unit": _count_layers_by_unit(profile_info),
    }

    return summary_dict, execution_detail
