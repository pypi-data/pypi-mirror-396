import json
from dataclasses import asdict
from pathlib import Path

import pytest
from PIL import Image

from tests import SAMPLES
from worker_yolo.segmenter import Mode, YOLOSegmenter


@pytest.mark.parametrize("WorkerClass", [YOLOSegmenter])
def test_process_image(mock_worker, image: Image.Image):
    mock_worker.use_segment = ["cat"]
    mock_worker.original_width = image.width
    mock_worker.original_height = image.height

    zones = mock_worker.process_image(image)
    expected = json.loads(Path(image.filename).with_suffix(".json").read_text())
    assert list(map(asdict, zones)) == expected


@pytest.mark.parametrize("WorkerClass", [YOLOSegmenter])
def test_process_image_minimum_rotated_rectangle(mock_worker, image: Image.Image):
    mock_worker.mode = Mode.MINIMUM_ROTATED_RECTANGLE
    mock_worker.original_width = image.width
    mock_worker.original_height = image.height

    expected = json.loads(
        (
            SAMPLES / f"{Path(image.filename).stem}-minimum-rotated-rectangle.json"
        ).read_text()
    )
    zones = mock_worker.process_image(image)
    assert list(map(asdict, zones)) == expected
