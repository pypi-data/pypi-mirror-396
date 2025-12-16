import pytest
from PIL import Image

from worker_yolo.classifier import YOLOClassifier


@pytest.mark.parametrize("WorkerClass", [YOLOClassifier])
def test_process_image(mock_worker, image: Image.Image):
    assert mock_worker.process_image(image) == ("doormat", 0.231)
