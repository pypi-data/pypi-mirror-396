import json
import shutil
from pathlib import Path

import pytest

from arkindex_worker.cache import CachedElement, CachedImage
from tests.conftest import SAMPLES
from worker_yolo.train.base import YOLOTrain


@pytest.mark.parametrize(
    ("polygon", "suffix"),
    [
        # Full page
        ([[0, 0], [0, 640], [427, 640], [427, 0], [0, 0]], "thumbnail"),
        # Sub element
        ([[265, 312], [265, 595], [427, 595], [427, 312], [265, 312]], "crop"),
    ],
)
@pytest.mark.parametrize("padding", [True, False])
def test_move_preprocess_image(padding, polygon, suffix, image, tmp_path):
    element = CachedElement(
        id="element_id",
        type="page",
        image=CachedImage(id="image_id", width=2000, height=2998, url="http://fake"),
        polygon=json.dumps(polygon),
    )

    worker = YOLOTrain()
    worker.dataset_archive = tmp_path
    worker.img_size = 320
    worker.padding = padding

    image_path = worker.dataset_archive / "images"
    image_path.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        image.filename,
        image_path / f"{element.image_id}.jpg",
    )

    worker.move_preprocess_image(element, tmp_path)

    assert (tmp_path / f"{element.id}.jpg").read_bytes() == (
        SAMPLES
        / f"{Path(image.filename).stem}-{suffix}{'-padding' if padding else ''}.jpg"
    ).read_bytes()
