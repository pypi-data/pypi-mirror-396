import os
import sys

import pytest
from PIL import Image
from ultralytics import YOLO

from arkindex.mock import MockApiClient
from arkindex_worker.worker.base import BaseWorker
from tests import SAMPLES
from worker_yolo.classifier import YOLOClassifier
from worker_yolo.segmenter import YOLOSegmenter
from worker_yolo.worker import YOLOWorker

MODELS_PATH = {
    YOLOClassifier: "yolov8n-cls.pt",
    YOLOSegmenter: "yolov9c-seg.pt",
}


@pytest.fixture
def mock_api_client() -> MockApiClient:
    return MockApiClient()


@pytest.fixture(autouse=True)
def _setup_environment(
    responses, tmp_path, monkeypatch, mock_api_client: MockApiClient
) -> None:
    """Setup needed environment variables"""

    # Allow accessing remote API schemas
    # defaulting to the prod environment
    schema_url = os.environ.get(
        "ARKINDEX_API_SCHEMA_URL",
        "https://demo.arkindex.org/api/v1/openapi/?format=openapi-json",
    )
    responses.add_passthru(schema_url)
    # Allow model download from Ultralytics
    responses.add_passthru(
        "https://api.github.com/repos/ultralytics/assets/releases/tags/v8.3.0"
    )

    # Set schema url in environment
    os.environ["ARKINDEX_API_SCHEMA_URL"] = schema_url
    # Setup a fake worker run ID
    os.environ["ARKINDEX_WORKER_RUN_ID"] = "1234-yolo"
    # Setup a fake corpus ID
    os.environ["ARKINDEX_CORPUS_ID"] = "1234-corpus-id"
    # Setup a fake task data dir
    os.environ["PONOS_DATA"] = str(tmp_path / "ponos-data")

    # Setup a mock api client instead of using a real one
    def mock_setup_api_client(self):
        self.api_client = mock_api_client

    monkeypatch.setattr(BaseWorker, "setup_api_client", mock_setup_api_client)


@pytest.fixture
def _mock_worker_run_api(mock_api_client: MockApiClient) -> None:
    """Provide a mock API response to get worker run information"""
    mock_api_client.add_response(
        "RetrieveWorkerRun",
        id=os.getenv("ARKINDEX_WORKER_RUN_ID"),
        response={
            "id": os.getenv("ARKINDEX_WORKER_RUN_ID"),
            "worker_version": {
                "id": "12341234-1234-1234-1234-123412341234",
                "revision": {"hash": "deadbeef1234"},
                "worker": {"name": "Fake worker"},
                "configuration": {
                    "user_configuration": {
                        "max_detection": {
                            "default": 300,
                        },
                        "iou": {
                            "default": 0.7,
                        },
                        "confidence_threshold": {
                            "default": 0.25,
                        },
                        "overlap.remove_overlapping_objects": {
                            "default": False,
                        },
                        "overlap.min_overlap_threshold": {
                            "default": 0.8,
                        },
                        "overlap.max_overlap_threshold": {
                            "default": 0.95,
                        },
                        "overlap.max_overlap_count": {
                            "default": 1,
                        },
                        "use_segment": {
                            "default": [],
                        },
                        "mode": {
                            "default": "default",
                        },
                    }
                },
            },
            "model_version": {
                "id": "12341234-1234-1234-1234-123412341234",
                "name": "My model version",
                "configuration": {
                    "thumbnail_size": None,
                    "padding": False,
                },
                "model": {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "name": "My model",
                },
            },
            "process": {"corpus": os.getenv("ARKINDEX_CORPUS_ID")},
            "summary": os.getenv("ARKINDEX_WORKER_RUN_ID") + " @ version 1",
        },
    )


@pytest.fixture
def mock_worker(
    monkeypatch,
    _mock_worker_run_api: None,
    WorkerClass: YOLOWorker,
) -> YOLOWorker:
    monkeypatch.setattr(sys, "argv", ["worker-yolo"])

    # Mock configuration
    def load_model(self):
        self.model = YOLO(MODELS_PATH.get(WorkerClass))

    monkeypatch.setattr(YOLOWorker, "load_model", load_model)
    monkeypatch.setattr(
        YOLOWorker, "check_required_types", lambda *args, **kwargs: None
    )

    worker = WorkerClass()
    worker.configure()

    worker.width_ratio = 1
    worker.height_ratio = 1

    return worker


@pytest.fixture
def image() -> Image.Image:
    return Image.open(SAMPLES / "abc90b80-6348-475d-914b-719fae0e7fc1.jpg")
