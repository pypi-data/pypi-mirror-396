# Copyright (C) 2025 Embedl AB

"""
Convert ONNX models to TensorFlow/TFLite format."""

from pathlib import Path
from tempfile import TemporaryDirectory

# TODO: Remove this try-except when `onnx2tf` and/or `tf-keras` has updated
#       requirements to require a compatible TensorFlow version.
try:
    # pylint: disable-next=unused-import
    import tf_keras
except ImportError as e:
    raise ImportError(
        "tf-keras is required for ONNX to TFLite conversion. "
        "Please install it via 'pip install tf-keras --no-deps'."
    ) from e

import onnx2tf
import tensorflow as tf

from embedl_hub.core.compile.abc import Compiler, CompileResult
from embedl_hub.core.utils.onnx_utils import maybe_package_onnx_folder_to_file
from embedl_hub.core.utils.tracking_utils import log_artifact


# pylint: disable-next=too-few-public-methods
class ONNXToTFCompiler(Compiler):
    """Compiler that converts ONNX models to TensorFlow/TFLite format."""

    supported_input_model_formats = {".onnx"}
    supports_input_model_folders = True

    def __init__(self, fp16: bool) -> None:
        self.fp16 = fp16

    def _compile(
        self,
        model_path: Path,
        output_path: Path | None = None,
    ) -> CompileResult:
        """
        Compile an ONNX model to TensorFlow/TFLite format.

        Args:
            project_name: Name of the project.
            experiment_name: Name of the experiment.
            model_path: Path to the input ONNX model file.
        """

        with TemporaryDirectory() as tmpdir:
            model_path = maybe_package_onnx_folder_to_file(model_path, tmpdir)
            return compile_onnx_to_tflite(
                onnx_model_path=model_path,
                output_model_path=output_path,
                fp16=self.fp16,
            )


def compile_onnx_to_tflite(
    onnx_model_path: Path,
    output_model_path: Path | None = None,
    fp16: bool = True,
) -> CompileResult:
    """Convert an ONNX model to TFLite format.

    Args:
        onnx_model_path: Path to the input ONNX model file.
        output_model_path: Path to save the converted TFLite model.
        fp16: Whether to use float16 quantization.
    """

    if output_model_path is None:
        new_suffix = ".fp16.tflite" if fp16 else ".tflite"
        output_model_path = onnx_model_path.with_suffix(new_suffix)
    with TemporaryDirectory() as tmpdir:
        # Onnx -> TF SavedModel
        # (Onnx2tf is not able to provide correct signatures during TFLite conversion)
        try:
            onnx2tf.convert(
                input_onnx_file_path=onnx_model_path,
                output_folder_path=tmpdir,
                output_signaturedefs=True,
            )
        except ValueError as e:
            if "axes don't match array" in str(e):
                raise RuntimeError(
                    "The ONNX model might be missing the 'kernel_shape' attribute in convolution layers. "
                    "This is a known issue when exporting with `dynamo=True` in PyTorch. "
                    "See https://github.com/pytorch/pytorch/issues/169824 for more details."
                ) from e
            raise e

        # TF SavedModel -> TFLite (With correct signatures)
        converter = tf.lite.TFLiteConverter.from_saved_model(str(tmpdir))
        if fp16:
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS
            ]
            converter.target_spec.supported_types = [tf.float16]
        tflite_model = converter.convert()
        with open(output_model_path, "wb") as f:
            f.write(tflite_model)

    log_artifact(output_model_path)

    return CompileResult(model_path=output_model_path)
