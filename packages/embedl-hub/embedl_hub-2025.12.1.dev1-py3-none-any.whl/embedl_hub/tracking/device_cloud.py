# Copyright (C) 2025 Embedl AB

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LiteRtFiles:
    """Paths to LiteRT output files."""

    log_file: Path
    profile_pb: Path


def get_litert_output_files(artifacts_dir: Path) -> LiteRtFiles:
    """Return paths to the LiteRT output files in the artifacts directory.

    Raises FileNotFoundError if any expected files are not found.
    """

    def find_required(name: str) -> Path:
        path = next(artifacts_dir.rglob(name), None)
        if path is None:
            raise FileNotFoundError(
                f"Could not find {name} in {artifacts_dir}"
            )
        return path

    return LiteRtFiles(
        log_file=find_required("tflite-logs.txt"),
        profile_pb=find_required("tflite-op-profile.pb"),
    )
