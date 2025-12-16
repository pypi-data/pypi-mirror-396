# Copyright (C) 2025 Embedl AB

"""
Abstract base classes for model quantizers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from embedl_hub.core.utils.tracking_utils import experiment_context
from embedl_hub.tracking import RunType


# TODO: Change wording when other quantizers than Qualcomm AI Hub are added
class QuantizationError(RuntimeError):
    """Raised when Qualcomm AI Hub quantization job fails or times out."""


@dataclass
class QuantizationResult:
    """Result of a successful quantization job."""

    model_path: Path
    job_id: str | None = None


# pylint: disable-next=too-few-public-methods
class Quantizer(ABC):
    """Abstract base class for model quantizers."""

    supported_input_model_formats: ClassVar[set[str]] = set()
    supports_input_model_folders: ClassVar[bool] = False

    @classmethod
    def validate_core_args(
        cls, model_path: Path, output_path: Path | None
    ) -> None:
        """
        Validate that the model format and output path are accepted by the quantizer.

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

    def quantize(
        self,
        project_name: str,
        experiment_name: str,
        model_path: Path,
        output_path: Path | None,
        run_name: str | None = None,
    ) -> QuantizationResult:
        """
        Quantize the model.

        A quantizer is responsible for taking a model and preparing the model
        for inference with a lower precision compute type. The specifics of the
        quantization process will depend on the implementation.

        Args:
            project_name: Name of the project.
            experiment_name: Name of the experiment.
            model_path: Path to the input model file.
            output_path: Path to save the quantized model.
            run_name: Optional name for the quantization run.

        Returns:
            QuantizationResult: The result of the quantization.

        Raises:
            QuantizationError: If the quantization fails.
        """

        with experiment_context(
            project_name, experiment_name, RunType.QUANTIZE, run_name
        ):
            return self._quantize(model_path, output_path)

    @abstractmethod
    def _quantize(
        self,
        model_path: Path,
        output_path: Path | None,
    ) -> QuantizationResult:
        """
        Quantize the model.

        A quantizer is responsible for taking a model and preparing the model
        for inference with a lower precision compute type. The specifics of the
        quantization process will depend on the implementation.

        Args:
            model_path: Path to the input model file.
            output_path: Path to save the quantized model.

        Returns:
            QuantizationResult: The result of the quantization.

        Raises:
            QuantizationError: If the quantization fails.
        """
        raise NotImplementedError("Subclasses must implement this method.")
