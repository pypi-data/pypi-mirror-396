# Copyright (C) 2025 Embedl AB

import os
import tempfile
import zipfile
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from embedl_hub.core.context import load_ctx_config
from embedl_hub.tracking.errors import (
    ArtifactUploadError,
    UnsupportedDeviceError,
    raise_if_artifact_error,
    raise_if_job_error,
)
from embedl_hub.tracking.job import BenchmarkJob
from embedl_hub.tracking.rest_api import (
    ApiConfig,
    ApiError,
    Artifact,
    ArtifactStatus,
    CompletedRunStatus,
    Device,
    DeviceCloudUpload,
    Experiment,
    Metric,
    Parameter,
    Project,
    Run,
    RunStatus,
    RunType,
    create_artifact,
    create_artifact_upload_url,
    create_device_cloud_upload,
    create_experiment,
    create_project,
    create_run,
    get_devices,
    get_experiment_by_name,
    get_project_by_name,
    log_metric,
    log_param,
    submit_device_cloud_job,
    update_artifact,
    update_run,
    upload_file,
    upload_file_to_gcs,
)

API_KEY_ENV_VAR_NAME = "EMBEDL_HUB_API_KEY"
BASE_URL_ENV_VAR_NAME = "EMBEDL_HUB_API_BASE_URL"

DEFAULT_API_BASE_URL = "https://hub.embedl.com/"


class Client:
    """Tracks projects, experiments and runs for the Embedl Hub web app."""

    _api_config: ApiConfig | None
    _project: Project | None
    _experiment: Experiment | None
    _active_run: Run | None

    def __init__(self, api_config: ApiConfig | None = None) -> None:
        self._api_config = api_config
        self._project = None
        self._experiment = None
        self._active_run = None

    def set_project(self, name: str) -> Project:
        """Set or create the current project by name."""

        project = get_project_by_name(self.api_config, name)

        if not project:
            project = create_project(self.api_config, name)

        self._project = project

        return project

    def set_experiment(self, name: str) -> Experiment:
        """Set or create the current experiment by name."""

        project_id = self.project.id
        experiment = get_experiment_by_name(self.api_config, name, project_id)

        if not experiment:
            experiment = create_experiment(self.api_config, name, project_id)

        self._experiment = experiment

        return experiment

    def create_run(self, type: RunType, name: str | None = None) -> Run:
        """Create a new run for the current project and experiment."""

        project = self.project
        experiment = self.experiment

        run = create_run(
            self.api_config,
            type=type,
            name=name,
            started_at=datetime.now(UTC),
            project_id=project.id,
            experiment_id=experiment.id,
        )

        return run

    def update_active_run(
        self,
        status: CompletedRunStatus | None = None,
        ended_at: datetime | None = None,
        metrics: list[Metric] | None = None,
        params: list[Parameter] | None = None,
    ) -> None:
        """Update the status and end time of the active run."""

        project = self.project
        experiment = self.experiment
        run = self.active_run

        update_run(
            self.api_config,
            status=status,
            ended_at=ended_at,
            project_id=project.id,
            experiment_id=experiment.id,
            run_id=run.id,
            metrics=metrics,
            params=params,
        )

    @contextmanager
    def start_run(self, type: RunType, name: str | None = None):
        """Context manager to start and finish a run."""

        run = self.create_run(type, name)
        self._active_run = run

        status: CompletedRunStatus = RunStatus.FINISHED

        try:
            yield run
        except KeyboardInterrupt:
            status = RunStatus.KILLED
            raise
        except Exception:
            status = RunStatus.FAILED
            raise
        finally:
            self.update_active_run(status=status, ended_at=datetime.now(UTC))
            self._active_run = None

    def log_param(self, name: str, value: str) -> Parameter:
        """Log a parameter for the current run."""

        project = self.project
        experiment = self.experiment
        active_run = self.active_run

        param = log_param(
            self.api_config,
            name=name,
            value=value,
            project_id=project.id,
            experiment_id=experiment.id,
            run_id=active_run.id,
        )

        return param

    def log_metric(
        self, name: str, value: float, step: int | None = None
    ) -> Metric:
        """Log a metric for the current run."""

        project = self.project
        experiment = self.experiment
        active_run = self.active_run

        metric = log_metric(
            self.api_config,
            name=name,
            value=value,
            step=step,
            project_id=project.id,
            experiment_id=experiment.id,
            run_id=active_run.id,
        )

        return metric

    def log_artifact(
        self,
        file_path: Path | str,
        file_name: str | None = None,
        run_id: str | None = None,
    ) -> Artifact:
        """
        Log an artifact file for a run and upload it to Cloud Storage.

        If no `run_id` is given, the current active run is used.

        Raises an exception if:
         - the file is too large
         - the storage quota is exceeded
         - the upload to Cloud Storage fails
        """

        file_path = Path(file_path)

        if file_name is None:
            file_name = file_path.name

        file_size = file_path.stat().st_size

        run_id = run_id or self.active_run.id

        try:
            artifact = create_artifact(
                self.api_config, run_id, file_name, file_size
            )
        except ApiError as exc:
            raise_if_artifact_error(exc, file_path=file_path)
            raise

        try:
            upload_response = create_artifact_upload_url(
                self.api_config, artifact.id
            )

            upload_file_to_gcs(file_path, upload_response.url, file_size)
        except Exception as exc:
            update_artifact(
                self.api_config, artifact.id, ArtifactStatus.FAILED
            )
            raise ArtifactUploadError(file_path=file_path) from exc

        update_artifact(self.api_config, artifact.id, ArtifactStatus.UPLOADED)

        return artifact

    def get_devices(self) -> list[Device]:
        """Get the list of supported devices in the Embedl device cloud."""

        devices = get_devices(self.api_config)

        return devices

    def validate_device(self, device: str) -> None:
        """Check if the specified device is supported in the Embedl device cloud."""

        supported_devices = self.get_devices()
        if device not in [d.name for d in supported_devices]:
            raise UnsupportedDeviceError(device)

    def submit_benchmark_job(
        self,
        model_path: Path | str,
        device: str,
    ) -> BenchmarkJob:
        """Benchmark a model in the Embedl device cloud."""

        self.validate_device(device)

        model_upload = self._upload_model_to_device_cloud(model_path)

        try:
            job_dto = submit_device_cloud_job(
                self.api_config,
                model_upload_id=model_upload.id,
                device=device,
            )
        except ApiError as exc:
            raise_if_job_error(exc)
            raise

        return BenchmarkJob(
            client=self,
            id=job_dto.id,
            model_upload_id=model_upload.id,
            device=device,
        )

    def _upload_model_to_device_cloud(
        self,
        file_path: Path | str,
    ) -> DeviceCloudUpload:
        """Upload a model file for execution on the Embedl device cloud.

        The model must be a .tflite model file.
        """

        file_path = Path(file_path)

        if file_path.suffix != ".tflite":
            raise ValueError(
                f"Model file must have .tflite extension, received: {file_path.suffix}"
            )

        model_upload = create_device_cloud_upload(self.api_config)

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "model.tflite.zip"

            with zipfile.ZipFile(zip_path, "w") as z:
                z.write(file_path, arcname="model.tflite")

            upload_file(
                zip_path,
                model_upload.url,
                headers={"Content-Type": "application/zip"},
            )

        return model_upload

    @property
    def api_config(self) -> ApiConfig:
        """Get or create the API config from environment variables."""

        if self._api_config is None:
            # environment variable takes precedence over context
            def get_api_key() -> str | None:
                """Get API key from environment or context."""
                if key := os.getenv(API_KEY_ENV_VAR_NAME):
                    return key
                # TODO: receive api key from CLI context instead of reading from file here?
                return load_ctx_config().get("api_key")

            if api_key := get_api_key():
                api_base_url = os.getenv(
                    BASE_URL_ENV_VAR_NAME, DEFAULT_API_BASE_URL
                )
                self._api_config = ApiConfig(
                    api_key=api_key, base_url=api_base_url
                )
            else:
                raise RuntimeError(
                    "No API key found. "
                    f"{API_KEY_ENV_VAR_NAME} must be set as an environment variable or stored in context."
                )

        return self._api_config

    @property
    def project(self) -> Project:
        if self._project is None:
            raise RuntimeError("Project is not set. Use set_project() first.")

        return self._project

    @property
    def experiment(self) -> Experiment:
        if self._experiment is None:
            raise RuntimeError(
                "Experiment is not set. Use set_experiment() first."
            )

        return self._experiment

    @property
    def active_run(self) -> Run:
        if self._active_run is None:
            raise RuntimeError(
                "There is no active run. Use start_run() as a context manager first."
            )

        return self._active_run
