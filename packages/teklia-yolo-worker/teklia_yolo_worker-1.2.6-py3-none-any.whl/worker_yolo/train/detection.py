from operator import attrgetter
from pathlib import Path

import yaml
from peewee import Expression

from arkindex_worker import logger
from arkindex_worker.cache import CachedDatasetElement, CachedElement
from arkindex_worker.models import Dataset, Set
from arkindex_worker.utils import MANUAL_SOURCE
from teklia_yolo.extract.bbox import (
    CONFIG_PATH,
    ZONE_CLASS_BY_TASKS,
    ElementData,
    YoloTask,
)
from worker_yolo.train.base import (
    ARKINDEX_SET_TO_YOLO_SPLIT,
    YOLOSplit,
    YOLOTrain,
    _is_dir_with_children,
)

# Only these sizes are supported for oriented bounding box mode
SUPPORTED_OBB_MODEL_SIZES = [
    "v8n",
    "v8s",
    "v8m",
    "v8l",
    "v8x",
    "11n",
    "11s",
    "11m",
    "11l",
    "11x",
]
# Only these sizes are supported for segmentation mode
SUPPORTED_SEGM_MODEL_SIZES = [
    "v8n",
    "v8s",
    "v8m",
    "v8l",
    "v8x",
    "v9c",
    "v9e",
    "11n",
    "11s",
    "11m",
    "11l",
    "11x",
]

YOLO_TASK_BY_MODES = {
    "bbox": YoloTask.Detect,
    "segment": YoloTask.Segment,
    "obb": YoloTask.OBB,
}


class YOLOTrainDetect(YOLOTrain):
    def configure(self) -> None:
        super().configure()

        self.yolo_task = YOLO_TASK_BY_MODES[self.config["mode"]]
        self.zone_class = ZONE_CLASS_BY_TASKS[self.yolo_task]

        # Point to a default pretrained model if needed
        if not self.base_model:
            size = self.config["ultralytics_model_size"]

            # Not all sizes are supported in oriented bounding box mode
            if self.yolo_task == YoloTask.OBB and size not in SUPPORTED_OBB_MODEL_SIZES:
                # Defaulting to largest checkpoint
                default_size = SUPPORTED_OBB_MODEL_SIZES[-1]
                logger.warning(
                    f"Size `{size}` is not supported for the oriented bounding box task. Defaulting to `{default_size}`."
                )
                size = default_size

            # Not all sizes are supported in segmentation mode
            if (
                self.yolo_task == YoloTask.Segment
                and size not in SUPPORTED_SEGM_MODEL_SIZES
            ):
                # Defaulting to largest checkpoint
                default_size = SUPPORTED_SEGM_MODEL_SIZES[-1]
                logger.warning(
                    f"Size `{size}` is not supported for the segmentation task. Defaulting to `{default_size}`."
                )
                size = default_size

            if self.yolo_task == YoloTask.Detect:
                self.base_model = f"yolo{size}.pt"
            elif self.yolo_task == YoloTask.OBB:
                self.base_model = f"yolo{size}-obb.pt"
            else:
                self.base_model = f"yolo{size}-seg.pt"

        self.train_from = self.training_data.parent / CONFIG_PATH

        self.class_names = self.config["class_names"]

        # Create directories where to store datasets images and labels
        self.images_dir = self.training_data / "images"
        self.labels_dir = self.training_data / "labels"

        # Build common query filter for elements
        self.elem_filter = self.build_element_query_filter()

        # Shared storage to generate the training dataset description
        self.split_elements = {}
        for split_name in map(attrgetter("value"), YOLOSplit):
            self.split_elements[split_name] = []

    def build_kwargs(self) -> tuple[dict[str, str], dict[str, str]]:
        training_kwargs, eval_kwargs = super().build_kwargs()
        training_kwargs["overlap_mask"] = self.config["advanced.overlap_mask"]
        training_kwargs["mask_ratio"] = self.config["advanced.mask_ratio"]
        return training_kwargs, eval_kwargs

    def build_element_query_filter(self) -> Expression:
        worker_runs = self.config["advanced.worker_runs"]
        if not worker_runs:
            return None

        manual_idx = False
        try:
            manual_idx = worker_runs.index(MANUAL_SOURCE)
            worker_runs.pop(manual_idx)
            return (
                CachedElement.worker_run_id.in_(worker_runs)
                | CachedElement.worker_run_id.is_null()
            )
        except ValueError:
            return CachedElement.worker_run_id.in_(worker_runs)

    def get_dataset_elements(self, dataset_set: Set):
        return (
            CachedDatasetElement.select(CachedElement)
            .join(CachedElement)
            .where(
                CachedDatasetElement.dataset == self.cached_dataset,
                CachedDatasetElement.set_name == dataset_set.name,
            )
        )

    def process_element(self, element: CachedElement) -> ElementData:
        # Find the direct children of the dataset element
        children = CachedElement.select().where(
            CachedElement.parent_id == element.id,
            CachedElement.type.in_(self.class_names),
        )
        if self.elem_filter:
            children = children.where(self.elem_filter)

        zones = [
            self.zone_class(
                class_idx=self.class_names.index(child.type),
                polygon=child.polygon,
                parent_polygon=element.polygon,
            )
            for child in children
        ]

        return ElementData(zones=zones)

    def organize_split(self, dataset_set: Set) -> None:
        split = ARKINDEX_SET_TO_YOLO_SPLIT[dataset_set.name]

        split_images_dir: Path = self.images_dir / split.value
        split_images_dir.mkdir(parents=True, exist_ok=True)
        split_labels_dir: Path = self.labels_dir / split.value
        split_labels_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting data for {dataset_set}...")
        logger.info(f"  - Images will be saved to {split_images_dir} directory")
        logger.info(f"  - Labels will be saved to {split_labels_dir} directory")
        for dataset_element in self.get_dataset_elements(dataset_set):
            element = dataset_element.element

            # Move the extracted image at the proper place
            self.move_preprocess_image(element, split_images_dir)

            # Generate the labels for the current element
            element_data = self.process_element(element)
            (split_labels_dir / str(element.id)).with_suffix(".txt").write_text(
                element_data.export()
            )

            self.split_elements[split.value].append(str(element.id))

        logger.info(f"{dataset_set} fully downloaded.")

    def check_classes(self):
        """
        Assert all classes to predict are available in the dataset
        """
        query = (
            CachedElement.select(CachedElement.type)
            .distinct()
            .order_by(CachedElement.type)
        )
        # Look for all element types
        types = [res[0] for res in query.tuples()]
        assert all([name in types for name in self.class_names]), (
            "All classes are not present in the corpus."
        )

    def load_parent_dataset(self, dataset: Dataset) -> None:
        super().load_parent_dataset(dataset)

        self.check_classes()

    def generate_dataset_description(
        self,
    ) -> None:
        """
        Structure is
        ---
        path: <name/of/dataset> # relative to `datasets` folder
        train: train.txt # where we save the paths of images for training set
        val: val.txt # where we save the paths of images for validation set
        test: test.txt # where we save the paths of images for testing set if present
        names: # Dictionary of class_idx: class_name
        """
        data = {"path": str(self.training_data)}

        for split_name in map(attrgetter("value"), YOLOSplit):
            split_desc = (self.labels_dir.with_name(split_name)).with_suffix(".txt")
            split_desc.write_text(
                "\n".join(
                    str((self.images_dir / split_name / element_id).with_suffix(".jpg"))
                    for element_id in self.split_elements[split_name]
                )
            )
            data[split_name] = split_desc.name

        data["names"] = {idx: name for idx, name in enumerate(self.class_names)}

        self.train_from.write_text(
            yaml.safe_dump(data, explicit_start=True, sort_keys=False)
        )
        logger.info(
            f"The description of the training dataset has been saved at {self.train_from}"
        )

    def is_split_extracted(self, split: YOLOSplit, required: bool = False) -> bool:
        """Check if the data for a given split was properly extracted or not"""
        extracted = True
        for data_dir in [self.images_dir, self.labels_dir]:
            split_path = data_dir / split.value
            extracted &= _is_dir_with_children(split_path)

            if required:
                dataset_set_name = list(ARKINDEX_SET_TO_YOLO_SPLIT.keys())[
                    list(ARKINDEX_SET_TO_YOLO_SPLIT.values()).index(split)
                ]
                assert extracted, (
                    f'{split_path} path to {data_dir.name} from "{dataset_set_name}" dataset set, does not exist or is empty'
                )

        return extracted

    def run_training_preprocessing(self) -> None:
        """Optional preprocessing steps to run before training the model"""
        self.generate_dataset_description()

    def get_model_config(self) -> dict | None:
        """Optional configuration to publish along with the trained model"""
        return {
            **super().get_model_config(),
            "use_segment": self.class_names,
        }


def main() -> None:
    YOLOTrainDetect(
        description="YOLO Object Detection Training: To process image and detect objects with its precise shape",
        support_cache=True,
    ).run()


if __name__ == "__main__":
    main()
