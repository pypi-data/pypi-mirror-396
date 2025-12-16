# Copyright (C) 2025 Embedl AB

"""Abstract base classes for model benchmarkers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from embedl_hub.core.utils.tracking_utils import experiment_context
from embedl_hub.tracking import RunType


class BenchmarkError(RuntimeError):
    """Raised when a benchmark/profile job fails."""


@dataclass
class BenchmarkResult:
    """Result of a successful benchmark run."""

    device: str
    summary: dict
    raw: dict | None = None


class Benchmarker(ABC):
    """Abstract base class for model benchmarkers."""

    supported_input_model_formats: ClassVar[set[str]] = set()
    supports_input_model_folders: ClassVar[bool] = False

    @classmethod
    def validate_model_path(cls, model_path: Path) -> None:
        """Validate that the model format is accepted by benchmarker."""

        if not model_path.exists():
            raise ValueError(f"Model path does not exist: {model_path}")
        if model_path.is_dir() and not cls.supports_input_model_folders:
            raise ValueError(
                f"Model path is a directory, but {cls.__name__} does not support "
                "input model folders."
            )
        if (
            cls.supported_input_model_formats
            and model_path.suffix.lower()
            not in cls.supported_input_model_formats
        ):
            raise ValueError(
                f"Model format '{model_path.suffix}' is not supported by {cls.__name__}. "
                f"Supported formats: {sorted(cls.supported_input_model_formats)}"
            )

    @abstractmethod
    def _benchmark(self, model_path: Path) -> BenchmarkResult:
        """Run the benchmark and return a result."""
        raise NotImplementedError("Subclasses must implement this method.")

    def benchmark(
        self,
        project_name: str,
        experiment_name: str,
        model_path: Path,
        run_name: str | None = None,
    ) -> BenchmarkResult:
        """Benchmark a model within an experiment tracking context."""

        self.validate_model_path(model_path)

        with experiment_context(
            project_name, experiment_name, RunType.BENCHMARK, run_name
        ):
            return self._benchmark(model_path)
