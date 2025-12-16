# Copyright (C) 2025 Embedl AB


from embedl_hub.tracking.client import Client as _Client
from embedl_hub.tracking.errors import (
    ArtifactUploadError,
    FileTooLargeError,
    StorageQuotaExceededError,
    UnsupportedDeviceError,
)
from embedl_hub.tracking.job import BenchmarkJob
from embedl_hub.tracking.rest_api import Device, Metric, Parameter, RunType

global_client = _Client()

set_project = global_client.set_project
set_experiment = global_client.set_experiment
start_run = global_client.start_run
log_param = global_client.log_param
log_metric = global_client.log_metric
log_artifact = global_client.log_artifact
update_run = global_client.update_active_run
get_devices = global_client.get_devices
validate_device = global_client.validate_device
submit_benchmark_job = global_client.submit_benchmark_job

__all__ = [
    "set_project",
    "set_experiment",
    "start_run",
    "log_param",
    "log_metric",
    "log_artifact",
    "get_devices",
    "validate_device",
    "submit_benchmark_job",
    "RunType",
    "global_client",
    "update_run",
    "Parameter",
    "Metric",
    "Device",
    "BenchmarkJob",
    "StorageQuotaExceededError",
    "FileTooLargeError",
    "ArtifactUploadError",
    "UnsupportedDeviceError",
]
