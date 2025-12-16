# Copyright (C) 2025 Embedl AB

from __future__ import annotations

from pathlib import Path

from embedl_hub.tracking.rest_api import ApiError, ErrorCode


class DomainError(Exception):
    """Base class for domain-specific exceptions."""


class StorageQuotaExceededError(DomainError):
    """Raised when storage quota is exceeded."""

    def __init__(self, file_path: Path, message: str | None = None) -> None:
        self.file_path = file_path
        if message is None:
            message = "Storage quota exceeded. Please delete some artifacts or contact support."
        super().__init__(message)


class FileTooLargeError(DomainError):
    """Raised when the file for an artifact is too large to upload."""

    def __init__(self, file_path: Path, message: str | None = None) -> None:
        self.file_path = file_path
        if message is None:
            message = "File too large to upload. Please try a smaller file."
        super().__init__(message)


class ArtifactUploadError(DomainError):
    """Raised when the file upload for an artifact fails."""

    def __init__(self, file_path: Path, message: str | None = None) -> None:
        self.file_path = file_path
        if message is None:
            message = "File upload failed. Please try again."
        super().__init__(message)


class UnsupportedDeviceError(DomainError):
    """Raised when an unsupported device is specified."""

    def __init__(self, device: str, message: str | None = None) -> None:
        self.device = device
        if message is None:
            message = f"The device '{device}' is not supported."
        super().__init__(message)


class JobQuotaExceededError(DomainError):
    """Raised when the job quota is exceeded."""

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Job quota exceeded. Please try again later or contact support."
        super().__init__(message)


def raise_if_artifact_error(api_error: ApiError, *, file_path: Path):
    """Re-raise a domain-specific exception if the API error is related to artifacts."""

    for error in api_error.errors:
        if error.code == ErrorCode.FILE_TOO_LARGE.value:
            raise FileTooLargeError(
                file_path, message=error.detail
            ) from api_error

        if error.code == ErrorCode.STORAGE_QUOTA_EXCEEDED.value:
            raise StorageQuotaExceededError(
                file_path, message=error.detail
            ) from api_error


def raise_if_job_error(api_error: ApiError):
    """Re-raise a domain-specific exception if the API error is related to jobs."""

    for error in api_error.errors:
        if error.code == ErrorCode.JOB_QUOTA_EXCEEDED.value:
            raise JobQuotaExceededError(message=error.detail) from api_error
