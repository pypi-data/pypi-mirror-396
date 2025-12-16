import json
import logging
import uuid
from collections.abc import Mapping
from logging import Logger, getLogger
from pathlib import Path

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_incrementing,
)

from arkindex_worker.worker import ActivityState, ElementsWorker

logger: Logger = getLogger(__name__)


def deep_update(source, overrides):
    """
    Update a nested dictionary or similar mapping.
    Modify ``source`` in place.
    """
    for key, value in overrides.items():
        if isinstance(value, Mapping) and value:
            source[key] = deep_update(source.get(key, {}), value)
        else:
            source[key] = overrides[key]
    return source


class YOLOBaseWorker(ElementsWorker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set a default value to avoid errors
        self._element_id = ""

        # Create base folder where data is saved
        self.base_folder = (self.task_data_dir / "process").resolve()
        self.base_folder.mkdir(exist_ok=True, parents=True)

    @property
    def element_id(self) -> str:
        """
        Avoid TypeError when the element ID is a UUID
        """
        return str(self._element_id)

    @property
    def element_path(self) -> Path:
        return self.base_folder / self.element_id

    @property
    def image_path(self) -> Path:
        return self.element_path.with_suffix(".jpg")

    @property
    def json_path(self) -> Path:
        return self.element_path.with_suffix(".json")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_incrementing(start=5, increment=0),
        retry=retry_if_exception_type(AssertionError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def assert_exists(self, file_path: Path) -> None:
        """
        Try checking the file several times to avoid intermittent network storage errors
        """
        assert file_path.exists(), f"File {file_path} not found"

    def read_results(self) -> dict:
        """
        Load existing JSON file and return stored value
        """
        if not self.json_path.exists():
            return {}

        return json.loads(self.json_path.read_text())

    def store_results(self, results: dict) -> None:
        """
        Load existing JSON file and add results
        """
        output = self.read_results()
        deep_update(output, results)
        self.json_path.write_text(json.dumps(output))

    def update_activity(
        self, element_id: str | uuid.UUID, state: ActivityState
    ) -> bool:
        """
        Override this function to store the element ID
        """
        # This function is called before `process_element` so we store the element ID now
        # to be able to build the image and JSON paths later on.
        self._element_id = element_id

        return super().update_activity(element_id, state)
