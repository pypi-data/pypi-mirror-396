import json
import os
import tempfile
import uuid
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from logging import Logger, getLogger

import torch

from arkindex_worker.cache import CachedElement
from arkindex_worker.models import Element
from arkindex_worker.worker import ActivityState
from teklia_yolo.extract.utils import get_bbox, preprocess_image
from worker_yolo.classifier import YOLOClassifier
from worker_yolo.offline import YOLOBaseWorker

logger: Logger = getLogger(__name__)


class YOLOClassifierOffline(YOLOBaseWorker, YOLOClassifier):
    configured = False

    def configure(self):
        assert torch.cuda.is_available(), "CUDA is not available"

        super().configure()

        self.configured = True

    @property
    def slurm_mode(self) -> bool:
        return os.environ.get("SLURM_JOB_ID") is not None

    @property
    def is_read_only(self) -> bool:
        # Always run fully offline in slurm
        if self.slurm_mode:
            return True

        # On docker allow normal configuration, then force offline
        if not self.configured:
            return super().is_read_only

        return True

    def setup_api_client(self) -> None:
        """
        Do not setup the API client in offline mode
        """
        if not self.slurm_mode:
            super().setup_api_client()

    def get_elements(
        self,
    ) -> Iterable[CachedElement] | list[str] | list[Element]:
        """
        List the elements to be processed, either from the CLI arguments or
        the cache database when enabled.

        :return: An iterable of Element.
        """

        def retrieve_element(element_id) -> Element:
            """
            Used to mock the call to RetrieveElement.
            """
            self._element_id = element_id
            return Element(
                **self.read_results().get(
                    "element",
                    # Default value if there is no element information
                    {
                        "id": element_id,
                        # Needed for logs
                        "type": "?",
                        "name": "?",
                        # Needed to avoid error when accessing polygon
                        "zone": {"polygon": [[0, 0]]},
                    },
                )
            )

        return list(map(retrieve_element, super().get_elements()))

    def update_activity(
        self, element_id: str | uuid.UUID, state: ActivityState
    ) -> bool:
        """
        Override this function to store activity in a JSON file
        """
        super().update_activity(element_id, state)

        # Skip process if JSON file is already present
        # with a processed activity for the current worker run
        results = self.read_results()
        activities = results.get("activities", [])
        target_activity = {
            "state": ActivityState.Processed.value,
            "worker_run_id": self.worker_run_id,
        }
        if target_activity in activities:
            return False

        # Store all activities to respect the state transition
        activities.append(
            {
                "state": state.value,
                "worker_run_id": self.worker_run_id,
            }
        )
        self.store_results({"activities": activities})

        return True

    def create_classification(
        self,
        element: Element,
        ml_class: str,
        confidence: float,
        high_confidence: bool | None = False,
    ) -> dict[str, str]:
        """
        Override this function to store classification in a JSON file
        """
        super().create_classification(
            element=element,
            ml_class=ml_class,
            confidence=confidence,
            high_confidence=high_confidence,
        )

        self.store_results(
            {
                "classification": {
                    "ml_class": ml_class,
                    "confidence": confidence,
                    "high_confidence": high_confidence,
                }
            },
        )

        return {}

    @contextmanager
    def load_image(self, element: Element) -> Iterator[str]:
        self.assert_exists(self.image_path)

        # Do not override original image stored on the server
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp_file:
            preprocess_image(
                from_path=self.image_path,
                to_path=tmp_file.name,
                box=get_bbox(json.dumps(element.polygon)),
                resize=(
                    (self.thumbnail_size, self.thumbnail_size)
                    if self.thumbnail_size
                    else None
                ),
                padding=self.padding,
            )

            yield tmp_file.name


def main() -> None:
    YOLOClassifierOffline(
        description="Ultralytics YOLO Classifier in offline mode: Classify an image based on its content"
    ).run()


if __name__ == "__main__":
    main()
