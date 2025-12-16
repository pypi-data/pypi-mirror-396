from pathlib import Path

import pytest
from PIL import Image

from arkindex_worker.models import Element
from worker_yolo.worker import YOLOWorker


@pytest.mark.parametrize("thumbnail", [None, 320])
def test_load_image_ratio(thumbnail, image, responses):
    base_url = "https://iiif.url/cat.jpg"
    iiif_url = f"{base_url}/full/full/0/default.jpg"
    responses.add(responses.GET, iiif_url, body=Path(image.filename).read_bytes())

    worker = YOLOWorker()
    worker.thumbnail_size = thumbnail
    worker.padding = False

    with worker.load_image(
        Element(
            id="mock_element",
            zone={
                "image": {
                    "width": 5008,
                    "height": 3736,
                    "url": base_url,
                    "server": {"version": 2},
                },
                "polygon": [[0, 0], [0, 640], [427, 640], [427, 0]],
                "url": iiif_url,
            },
            requires_tiles=False,
            mirrored=False,
            rotation_angle=0,
        )
    ) as image_path:
        assert Path(image_path).exists()
        assert Image.open(image_path).size == ((214, 320) if thumbnail else (427, 640))

    assert not Path(image_path).exists()

    assert worker.width_ratio == (1.9953271028037383 if thumbnail else 1)
    assert worker.height_ratio == (2.0 if thumbnail else 1)
