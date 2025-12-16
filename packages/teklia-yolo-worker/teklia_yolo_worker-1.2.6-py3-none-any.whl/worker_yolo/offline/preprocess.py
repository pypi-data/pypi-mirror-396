import uuid
from logging import Logger, getLogger

from arkindex.exceptions import ErrorResponse
from arkindex_worker.models import Element
from arkindex_worker.worker import ActivityState
from worker_yolo.offline import YOLOBaseWorker

logger: Logger = getLogger(__name__)


class YOLOPreprocess(YOLOBaseWorker):
    # Whether all files for the element being processed have already been downloaded
    has_missing_files: bool | None = None

    def update_activity(
        self, element_id: str | uuid.UUID, state: ActivityState
    ) -> bool:
        """
        Override this function to check if files exist
        """
        if self._element_id != element_id:
            self._element_id = element_id
            self.has_missing_files = (
                not self.image_path.exists() or not self.json_path.exists()
            )

        # If files exist, do nothing special
        if not self.has_missing_files:
            return super().update_activity(element_id, state)

        # Try to follow the usual behaviour but it may fail if this element is already marked as `processed` in another process and files were missing
        try:
            super().update_activity(element_id, state)
        except ErrorResponse as e:
            if e.status_code != 409:
                raise

        # Always reprocess an element if files are missing
        return True

    def save_image(self, element: Element) -> None:
        logger.info("Loading element image...")
        image = element.open_image(use_full_image=True)

        logger.info("Saving image...")
        image.save(self.image_path)

    def save_element(self, element: Element) -> None:
        self.store_results({"element": element})
        logger.info("Saving element information...")

    def process_element(self, element: Element) -> None:
        self.save_image(element)
        self.save_element(element)


def main() -> None:
    YOLOPreprocess(
        description="Preprocess images for Ultralytics YOLO Classifier: Utility process"
    ).run()


if __name__ == "__main__":
    main()
