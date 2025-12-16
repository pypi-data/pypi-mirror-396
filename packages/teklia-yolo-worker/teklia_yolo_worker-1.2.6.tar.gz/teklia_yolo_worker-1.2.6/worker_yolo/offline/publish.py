import contextlib
from logging import Logger, getLogger

from arkindex_worker.models import Element
from arkindex_worker.worker import ActivityState, ElementsWorker
from worker_yolo.offline import YOLOBaseWorker

logger: Logger = getLogger(__name__)


class YOLOPublish(YOLOBaseWorker, ElementsWorker):
    def publish_activities(self, element: Element, activities: list[dict]) -> None:
        logger.info("Updating activity of the parent worker...")

        worker_run_id = self.worker_run_id

        # Do not raise error if activities have already been updated previously
        with contextlib.suppress(Exception):
            for activity in activities:
                # Cast state to expected type
                state = ActivityState(activity["state"])

                # Override the worker version ID to avoid reimplementing the `update_activity` function
                self.worker_run_id = activity["worker_run_id"]
                super().update_activity(element.id, state)

        # Restore the real worker version ID
        self.worker_run_id = worker_run_id

    def publish_classification(
        self, element: Element, classification: dict
    ) -> dict[str, str]:
        logger.info("Publishing classification on Arkindex...")
        return self.create_classification(
            element=element,
            **classification,
        )

    def process_element(self, element: Element) -> None:
        self.assert_exists(self.json_path)

        yolo_results = self.read_results()

        self.publish_activities(element, activities=yolo_results["activities"])

        classification = yolo_results.get("classification")
        if not classification:
            # The classification can be missing because YOLO predicted nothing
            # but it can also be missing because the previous worker failed on this element.
            assert ActivityState.Processed in map(
                lambda activity: ActivityState(activity["state"]),
                yolo_results["activities"],
            ), "Classification not found"
            logger.warning("No classification predicted, skipping...")
            return

        self.publish_classification(element, classification=classification)


def main() -> None:
    YOLOPublish(
        description="Publish Ultralytics YOLO Classifier results: Utility process"
    ).run()


if __name__ == "__main__":
    main()
