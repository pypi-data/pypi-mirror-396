# Copyright (C) 2025 Embedl AB

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Self, TypeAlias
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


@dataclass
class ApiConfig:
    """Configuration for interacting with the Embedl Hub REST API."""

    base_url: str
    api_key: str

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }


class Model(BaseModel):
    """Base model with camel case aliasing."""

    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True)


class Project(Model):
    id: str
    name: str


class Experiment(Model):
    id: str
    name: str


class RunType(Enum):
    QUANTIZE = "QUANTIZE"
    COMPILE = "COMPILE"
    BENCHMARK = "BENCHMARK"


class RunStatus(Enum):
    RUNNING = "RUNNING"
    SCHEDULED = "SCHEDULED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    KILLED = "KILLED"


class Run(Model):
    id: str
    name: str
    type: RunType
    status: RunStatus
    created_at: datetime
    started_at: datetime
    ended_at: datetime | None


class Parameter(Model):
    name: str
    value: str
    measured_at: datetime | None = None


class Metric(Model):
    name: str
    value: float
    step: int | None = None
    measured_at: datetime | None = None


class ArtifactStatus(Enum):
    PENDING = "PENDING"
    UPLOADED = "UPLOADED"
    FAILED = "FAILED"


class Artifact(Model):
    id: str
    run_id: str
    file_name: str
    file_size: str
    status: ArtifactStatus
    created_at: datetime
    updated_at: datetime


class ArtifactUploadResponse(Model):
    url: str
    expires_at: datetime
    max_size: str


class CpuSpec(Model):
    architecture: str
    frequency: str
    clock: float


class Device(Model):
    name: str
    os: str
    vendor: str
    platform: str
    type: str
    cpu: CpuSpec


class DeviceCloudUpload(Model):
    id: str
    url: str
    created_at: datetime


class DeviceCloudJobStatus(Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    PENDING_CONCURRENCY = "PENDING_CONCURRENCY"
    PENDING_DEVICE = "PENDING_DEVICE"
    PREPARING = "PREPARING"
    PROCESSING = "PROCESSING"
    RUNNING = "RUNNING"
    SCHEDULING = "SCHEDULING"
    STOPPING = "STOPPING"

    def is_final(self) -> bool:
        return self == DeviceCloudJobStatus.COMPLETED

    def is_active(self) -> bool:
        return self in (
            DeviceCloudJobStatus.PREPARING,
            DeviceCloudJobStatus.PROCESSING,
            DeviceCloudJobStatus.RUNNING,
            DeviceCloudJobStatus.STOPPING,
        )

    def is_waiting(self) -> bool:
        return self in (
            DeviceCloudJobStatus.PENDING,
            DeviceCloudJobStatus.PENDING_CONCURRENCY,
            DeviceCloudJobStatus.PENDING_DEVICE,
            DeviceCloudJobStatus.SCHEDULING,
        )


class DeviceCloudJob(Model):
    id: str
    status: DeviceCloudJobStatus
    created_at: datetime


class DeviceCloudJobArtifacts(Model):
    job_id: str
    url: str
    extension: str | None = None


CompletedRunStatus: TypeAlias = Literal[
    RunStatus.FINISHED, RunStatus.KILLED, RunStatus.FAILED
]


JSONObj: TypeAlias = dict[str, Any]
JSONItems: TypeAlias = list[JSONObj]
JSONData: TypeAlias = JSONObj | JSONItems


def create_project(config: ApiConfig, name: str) -> Project:
    """Create a new project."""

    data = _request(config, "POST", "/api/projects", json={"name": name})

    data = _expect_dict(data)

    return Project(**data)


def get_project_by_name(config: ApiConfig, name: str) -> Project | None:
    """Get project by name, or None if not found."""

    try:
        data = _request(
            config,
            "GET",
            "/api/projects",
            params={"name": name},
        )
    except ApiError as err:
        if err.status_code == 404:
            return None
        raise

    data = _expect_dict(data)

    return Project(**data)


def create_experiment(
    config: ApiConfig, name: str, project_id: str
) -> Experiment:
    """Create a new experiment."""

    data = _request(
        config,
        "POST",
        f"/api/projects/{project_id}/experiments",
        json={"name": name},
    )

    data = _expect_dict(data)

    return Experiment(**data)


def get_experiment_by_name(
    config: ApiConfig, name: str, project_id: str
) -> Experiment | None:
    """Get experiment by name, or None if not found."""

    try:
        data = _request(
            config,
            "GET",
            f"/api/projects/{project_id}/experiments",
            params={"name": name},
        )
    except ApiError as err:
        if err.status_code == 404:
            return None
        raise

    data = _expect_dict(data)

    return Experiment(**data)


def create_run(
    config: ApiConfig,
    project_id: str,
    experiment_id: str,
    type: RunType,
    started_at: datetime,
    name: str | None = None,
) -> Run:
    """Create a new run."""

    payload = {"type": type.value}
    if name:
        payload["name"] = name
    payload["startedAt"] = started_at.isoformat()

    data = _request(
        config,
        "POST",
        f"/api/projects/{project_id}/experiments/{experiment_id}/runs",
        json=payload,
    )

    data = _expect_dict(data)

    return Run(**data)


def update_run(
    config: ApiConfig,
    project_id: str,
    experiment_id: str,
    run_id: str,
    status: CompletedRunStatus | None,
    ended_at: datetime | None,
    metrics: list[Metric] | None = None,
    params: list[Parameter] | None = None,
) -> None:
    """Update run status and end time."""

    payload = {}
    if status:
        payload["status"] = status.value
    if ended_at:
        payload["endedAt"] = ended_at.isoformat()
    if metrics:
        payload["metrics"] = [
            metric.model_dump(by_alias=True, exclude_defaults=True)
            for metric in metrics
        ]
    if params:
        payload["params"] = [
            param.model_dump(by_alias=True, exclude_defaults=True)
            for param in params
        ]

    _request(
        config,
        "PATCH",
        f"/api/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}",
        json=payload,
    )


def log_param(
    config: ApiConfig,
    name: str,
    value: str,
    project_id: str,
    experiment_id: str,
    run_id: str,
) -> Parameter:
    """Log a parameter for a run."""

    payload = {"name": name, "value": value}
    data = _request(
        config,
        "POST",
        f"/api/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/params",
        json=payload,
    )

    data = _expect_dict(data)

    return Parameter(**data)


def log_metric(
    config: ApiConfig,
    name: str,
    value: float,
    project_id: str,
    experiment_id: str,
    run_id: str,
    step: int | None = None,
) -> Metric:
    """Log a metric for a run."""

    payload = {"name": name, "value": value}
    if step is not None:
        payload["step"] = step

    data = _request(
        config,
        "POST",
        f"/api/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/metrics",
        json=payload,
    )

    data = _expect_dict(data)

    return Metric(**data)


def create_artifact(
    config: ApiConfig,
    run_id: str,
    file_name: str,
    file_size: int,
) -> Artifact:
    """Create an artifact for a given run.

    Uploading the file for the artifact must be done separately. See
    `create_artifact_upload_url()`.
    """

    payload = {
        "runId": run_id,
        "fileName": file_name,
        "fileSize": file_size,
    }
    data = _request(
        config,
        "POST",
        "/api/artifacts",
        json=payload,
    )

    data = _expect_dict(data)

    return Artifact(**data)


def create_artifact_upload_url(
    config: ApiConfig,
    artifact_id: str,
) -> ArtifactUploadResponse:
    """Create a temporary URL for uploading a file for an artifact."""

    data = _request(
        config,
        "POST",
        f"/api/artifacts/{artifact_id}/upload-url",
    )

    data = _expect_dict(data)

    return ArtifactUploadResponse(**data)


def upload_file_to_gcs(
    file_path: Path,
    upload_url: str,
    file_size: int | None = None,
) -> None:
    """Upload a file to the given Google Cloud Storage signed URL."""

    file_size = file_size or file_path.stat().st_size

    headers = {
        "Content-Type": "application/octet-stream",
        "x-goog-content-length-range": f"0,{file_size}",
    }

    upload_file(file_path, upload_url, headers=headers)


def update_artifact(
    config: ApiConfig, artifact_id: str, status: ArtifactStatus
) -> None:
    """Update an artifact."""

    _request(
        config,
        "PATCH",
        f"/api/artifacts/{artifact_id}",
        json={"status": status.value},
    )


def delete_artifact(
    config: ApiConfig,
    artifact_id: str,
) -> None:
    """Delete an artifact, cleaning up storage."""

    _request(
        config,
        "DELETE",
        f"/api/artifacts/{artifact_id}",
    )


def get_devices(
    config: ApiConfig,
) -> list[Device]:
    """Get the list of supported devices in the Embedl device cloud."""

    data = _request(
        config,
        "GET",
        "/api/device-cloud/devices",
    )

    data = _expect_list(data)

    return [Device(**item) for item in data]


def create_device_cloud_upload(
    config: ApiConfig,
) -> DeviceCloudUpload:
    """Create a resource for uploading a file for usage on the Embedl device cloud."""

    data = _request(
        config,
        "POST",
        "/api/device-cloud/uploads",
    )

    data = _expect_dict(data)

    return DeviceCloudUpload(**data)


def submit_device_cloud_job(
    config: ApiConfig,
    model_upload_id: str,
    device: str,
) -> DeviceCloudJob:
    """Create a job on the Embedl device cloud."""

    payload = {
        "modelUploadId": model_upload_id,
        "deviceName": device,
    }
    data = _request(
        config,
        "POST",
        "/api/device-cloud/jobs",
        json=payload,
    )

    data = _expect_dict(data)

    return DeviceCloudJob(**data)


def get_device_cloud_job(
    config: ApiConfig,
    job_id: str,
) -> DeviceCloudJob:
    """Get a device cloud job by ID."""

    data = _request(
        config,
        "GET",
        f"/api/device-cloud/jobs/{job_id}",
    )

    data = _expect_dict(data)

    return DeviceCloudJob(**data)


def get_device_cloud_job_artifacts(
    config: ApiConfig,
    job_id: str,
) -> DeviceCloudJobArtifacts:
    """Get details for the artifacts produced by a Embedl device cloud job."""

    data = _request(
        config,
        "GET",
        f"/api/device-cloud/jobs/{job_id}/artifacts",
    )

    data = _expect_dict(data)

    return DeviceCloudJobArtifacts(**data)


def upload_file(
    file_path: Path,
    url: str,
    headers: dict[str, str] | None = None,
) -> None:
    """Upload a file to the given URL."""

    try:
        with file_path.open("rb") as f:
            upload_response = requests.put(
                url,
                data=f,
                timeout=60,
                headers=headers,
            )
        upload_response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise NetworkRequestError(
            f"File upload to {url} failed: {exc}"
        ) from exc


def download_file(url: str) -> bytes:
    """Download a file from the given URL."""

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise NetworkRequestError(
            f"File download from {url} failed: {exc}"
        ) from exc
    return resp.content


def _expect_dict(data: JSONData | None) -> JSONObj:
    """Ensure data is a dict, else raise error."""

    if not isinstance(data, dict):
        raise RuntimeError("Unexpected response shape: expected object")
    return data


def _expect_list(data: JSONData | None) -> list[JSONObj]:
    """Ensure data is a list, else raise error."""

    if not isinstance(data, list):
        raise RuntimeError("Unexpected response shape: expected array")
    return data


def _request(
    config: ApiConfig,
    method: str,
    url: str,
    json: JSONObj | None = None,
    params: dict[str, str | int] | None = None,
) -> JSONData | None:
    """Send HTTP request and handle API response."""

    full_url = urljoin(config.base_url, url)

    try:
        resp = requests.request(
            method=method,
            url=full_url,
            headers=config.headers,
            json=json,
            params=params,
            timeout=10,
        )
    except requests.exceptions.RequestException as exc:
        raise NetworkRequestError(
            f"Request to {full_url} failed: {exc}"
        ) from exc

    try:
        payload: JSONObj = resp.json() if resp.content else {}
    except ValueError:
        payload = {}

    if resp.ok:
        if resp.status_code == 204:
            return None

        if "data" in payload:
            return payload["data"]

        raise ApiError(resp.status_code, "Missing `data` field", [], resp)

    errors = [
        ApiErrorDetail.from_dict(err) for err in payload.get("errors", [])
    ]
    message = payload.get("message") or resp.reason
    raise ApiError(resp.status_code, message, errors, resp)


class ErrorCode(Enum):
    """Specific error codes returned by the API."""

    STORAGE_QUOTA_EXCEEDED = "storage_quota_exceeded"
    FILE_TOO_LARGE = "file_too_large"
    JOB_QUOTA_EXCEEDED = "job_quota_exceeded"


@dataclass
class ApiErrorDetail:
    """An individual error contained in an API error response."""

    title: str | None = None
    status: int | None = None
    code: str | None = None
    detail: str | None = None
    source: dict[str, str] | None = None
    meta: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            title=data.get("title"),
            status=data.get("status"),
            code=data.get("code"),
            detail=data.get("detail"),
            source=data.get("source"),
            meta=data.get("meta"),
        )

    def __str__(self) -> str:
        parts: list[str] = []
        if self.title:
            parts.append(self.title)
        if self.code:
            parts.append(f"(code: {self.code})")
        if self.status:
            parts.append(f"[{self.status}]")
        if self.detail:
            parts.append(self.detail)
        if self.source:
            parts.append(f"-> {self.source}")
        return " ".join(parts) or "<empty>"


class ApiError(Exception):
    """Raised for API errors with JSON body."""

    def __init__(
        self,
        status_code: int,
        message: str,
        errors: list[ApiErrorDetail] | None = None,
        response: requests.Response | None = None,
    ) -> None:
        super().__init__(f"{status_code} {message}")
        self.status_code = status_code
        self.message = message
        self.errors = errors or []
        self.response = response

    def __str__(self) -> str:
        if not self.errors:
            return super().__str__()
        joined = "\n".join(map(str, self.errors))
        return f"{super().__str__()}\n{joined}"


class NetworkRequestError(Exception):
    """Raised when HTTP request fails."""
