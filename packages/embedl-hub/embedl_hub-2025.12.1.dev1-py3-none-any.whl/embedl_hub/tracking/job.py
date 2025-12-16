# Copyright (C) 2025 Embedl AB

import shutil
import tempfile
import time
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from embedl_hub.core.utils.tflite_utils import parse_tflite_profiling_artifacts
from embedl_hub.tracking.device_cloud import get_litert_output_files
from embedl_hub.tracking.rest_api import (
    DeviceCloudJobStatus,
    download_file,
    get_device_cloud_job,
    get_device_cloud_job_artifacts,
)

if TYPE_CHECKING:
    from embedl_hub.tracking.client import Client


class DeviceCloudJob:
    """A job on the Embedl device cloud."""

    poll_interval_seconds = 5
    timeout_seconds = 300

    def __init__(self, client: "Client", id: str) -> None:
        self._client = client
        self.id = id

        self._final_status: DeviceCloudJobStatus | None = None

    def get_status(self) -> DeviceCloudJobStatus:
        """Get the current status of the job."""

        if self._final_status is not None:
            return self._final_status

        job_dto = get_device_cloud_job(self._client.api_config, self.id)

        status = job_dto.status

        if status.is_final():
            self._final_status = status

        return status

    def is_completed(self) -> bool:
        """Returns True if the job is completed."""

        return self.get_status().is_final()

    def wait_for_completion(
        self,
        timeout: int | None = None,
    ) -> DeviceCloudJobStatus:
        """Wait for the job to complete.

        Timeout starts counting when the job starts running. While the job is queued,
        the function will wait indefinitely.

        Returns the status when completed.
        """

        status = self.get_status()

        if status.is_final():
            return status

        timeout = timeout or self.timeout_seconds
        sleep_seconds = self.poll_interval_seconds

        execution_time_elapsed = 0

        while True:
            time.sleep(sleep_seconds)

            status = self.get_status()

            if status.is_final():
                break

            if status.is_waiting():
                continue

            execution_time_elapsed += sleep_seconds

            if execution_time_elapsed > timeout:
                raise TimeoutError(f"Timeout while running job {self.id}")

        return status


class BenchmarkJob(DeviceCloudJob):
    """A benchmark job on the Embedl device cloud."""

    def __init__(
        self,
        client: "Client",
        id: str,
        model_upload_id: str,
        device: str,
    ) -> None:
        super().__init__(
            client=client,
            id=id,
        )

        self.model_upload_id = model_upload_id
        self.device = device

    def download_results(
        self, artifacts_dir: Path | str | None = None
    ) -> "BenchmarkJobResult":
        """Download the results of the job.

        If `artifacts_dir` is specified, write job artifacts to that directory.

        If the job is not ready, this function will block until completion.
        """

        status = self.wait_for_completion()

        if isinstance(artifacts_dir, str):
            artifacts_dir = Path(artifacts_dir)

        temp_dir: Path | str
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            self._download_artifacts(temp_dir)

            if artifacts_dir is not None:
                self._copy_files(src=temp_dir, dst=artifacts_dir)

            output_files = get_litert_output_files(temp_dir)

            summary_dict, execution_detail = parse_tflite_profiling_artifacts(
                proto_path=output_files.profile_pb,
                log_path=output_files.log_file,
            )

        artifacts: list[Path] = [
            artifacts_dir / file.name
            for file in asdict(output_files).values()
            if artifacts_dir is not None
        ]

        return BenchmarkJobResult(
            status=status,
            summary=summary_dict,
            execution_detail=execution_detail,
            artifacts=artifacts,
            artifacts_dir=artifacts_dir,
        )

    def _download_artifacts(self, dst: Path) -> None:
        """Download and extract the artifacts produced by the job."""

        artifacts = get_device_cloud_job_artifacts(
            self._client.api_config, self.id
        )

        zip_path = Path(dst) / "artifacts.zip"

        with open(zip_path, "wb") as f:
            file_content = download_file(artifacts.url)
            f.write(file_content)

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dst)

        zip_path.unlink()

    def _copy_files(self, src: Path, dst: Path) -> None:
        """Recursively copy all files in `src` to `dst`, skipping directories."""

        dst.mkdir(parents=True, exist_ok=True)

        for file in src.rglob("*"):
            if file.is_file():
                shutil.copy(file, dst)


@dataclass
class BenchmarkJobResult:
    """Result of a benchmark job on the Embedl device cloud."""

    status: DeviceCloudJobStatus
    summary: dict
    execution_detail: list[dict]
    artifacts: list[Path] | None = None
    artifacts_dir: Path | None = None
