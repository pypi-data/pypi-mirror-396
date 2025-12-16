import json
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from logging import Logger, getLogger

import torch
from PIL import Image
from ultralytics import YOLO

from arkindex_worker.models import Element
from arkindex_worker.worker import ElementsWorker
from teklia_yolo.extract.utils import get_bbox, preprocess_image

logger: Logger = getLogger(__name__)

# Model names supported by YOLO
MODEL_NAMES = ["model.pt", "model-world.pt"]


class YOLOWorker(ElementsWorker):
    def configure(self) -> None:
        super().configure()

        self.confidence_threshold: float = self.config["confidence_threshold"]
        self.thumbnail_size: int | None = self.config.get("thumbnail_size")
        # Do not pad images by default
        self.padding: bool = self.config.get("padding", False)

        self.load_model()

    @property
    def device(self) -> str | int:
        return torch.cuda.current_device() if torch.cuda.is_available() else "cpu"

    def load_model(self) -> None:
        extras_path = self.find_extras_directory()
        model_name = next(
            filter(
                lambda model_name: (extras_path / model_name).is_file(), MODEL_NAMES
            ),
            None,
        )
        assert model_name, f"No model found matching these names {MODEL_NAMES}"
        self.model = YOLO(extras_path / model_name)

    def get_rotation_angle(self, element: Element) -> float | None:
        """
        Function to override to retrieve a specific rotation angle that should
        be applied to the processed element during the preprocessing step.
        """
        return

    @contextmanager
    def load_image(self, element: Element) -> Iterator[str]:
        with (
            element.open_image_tempfile(use_full_image=True) as image_file,
            tempfile.NamedTemporaryFile(suffix=".jpg") as preprocessed_image_file,
        ):
            x, y, self.original_width, self.original_height = get_bbox(
                json.dumps(element.polygon)
            )
            preprocess_image(
                from_path=image_file.name,
                # Use another path because `image_file` has no suffix
                # and Pillow cannot know the extension of the image to save it
                to_path=preprocessed_image_file.name,
                box=(x, y, self.original_width, self.original_height),
                resize=(
                    (self.thumbnail_size, self.thumbnail_size)
                    if self.thumbnail_size
                    else None
                ),
                padding=self.padding,
                rotation_angle=self.get_rotation_angle(element),
            )

            # To build polygons according to the original image later
            preprocessed_width, preprocessed_height = Image.open(
                preprocessed_image_file.name
            ).size
            self.width_ratio, self.height_ratio = (
                self.original_width / preprocessed_width,
                self.original_height / preprocessed_height,
            )

            yield preprocessed_image_file.name
