# Copyright (C) 2025 Embedl AB

"""
Abstract base classes for model compilers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from embedl_hub.core.utils.tracking_utils import experiment_context
from embedl_hub.tracking import RunType


class CompileError(RuntimeError):
    """Raised when a compile job fails or times out."""


@dataclass
class CompileResult:
    """Result of a successful compile job."""

    model_path: Path  # local .tflite, .bin, or .onnx after compile
    job_id: str | None = None
    device: str | None = None


class Compiler(ABC):
    """Abstract base class for model compilers."""

    supported_input_model_formats: ClassVar[set[str]] = set()
    supports_input_model_folders: ClassVar[bool] = False

    @classmethod
    def validate_core_args(
        cls, model_path: Path, output_path: Path | None
    ) -> None:
        """
        Validate that the model format and output path are accepted by compiler.

        Args:
            model_path: Path to the input model file.
            output_path: Path to the output compiled model file.
        Raises:
            ValueError: If the model format is not supported.
        """
        # TODO: Add output_path validation if needed

        if not model_path.exists():
            raise ValueError(f"Model path does not exist: {model_path}")
        if model_path.is_dir() and not cls.supports_input_model_folders:
            raise ValueError(
                f"Model path is a directory, but {cls.__name__} does not support "
                "input model folders."
            )
        if model_path.suffix.lower() not in cls.supported_input_model_formats:
            raise ValueError(
                f"Model format '{model_path.suffix}' is not supported by {cls.__name__}. "
                f"Supported formats: {sorted(cls.supported_input_model_formats)}"
            )

    @abstractmethod
    def _compile(
        self,
        model_path: Path,
        output_path: Path | None,
    ) -> CompileResult:
        """
        Compile the model.

        A compiler is responsible for taking a model and compiling it for a specific device
        and/or runtime. The specifics of the compilation process will depend on the
        implementation.

        Args:
            model_path: Path to the input model file.
            output_path: Path to save the compiled model.

        Returns:
            CompileResult: The result of the compilation.

        Raises:
            CompileError: If the compilation fails.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def compile(
        self,
        project_name: str,
        experiment_name: str,
        model_path: Path,
        output_path: Path | None,
    ) -> CompileResult:
        """
        Compile the model.

        A compiler is responsible for taking a model and compiling it for a specific device
        and/or runtime. The specifics of the compilation process will depend on the
        implementation.

        Args:
            project_name: Name of the project.
            experiment_name: Name of the experiment.
            model_path: Path to the input model file.
            output_path: Path to save the compiled model.

        Returns:
            CompileResult: The result of the compilation.

        Raises:
            CompileError: If the compilation fails.
        """

        with experiment_context(
            project_name, experiment_name, RunType.COMPILE
        ):
            return self._compile(model_path, output_path)
