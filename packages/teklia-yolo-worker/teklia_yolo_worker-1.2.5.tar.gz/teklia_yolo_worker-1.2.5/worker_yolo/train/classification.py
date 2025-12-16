from functools import reduce
from pathlib import Path

from peewee import Expression, Query, operator, prefetch

from arkindex_worker import logger
from arkindex_worker.cache import (
    CachedClassification,
    CachedDatasetElement,
    CachedElement,
)
from arkindex_worker.models import Set
from arkindex_worker.utils import MANUAL_SOURCE
from worker_yolo.train.base import (
    ARKINDEX_SET_TO_YOLO_SPLIT,
    YOLOSplit,
    YOLOTrain,
    _is_dir_with_children,
)


class YOLOTrainCls(YOLOTrain):
    def configure(self) -> None:
        super().configure()

        # Point to a default pretrained model if needed
        if not self.base_model:
            self.base_model = f"yolo{self.config['ultralytics_model_size']}-cls.pt"

        # Build common query filters for classifications
        self.cls_filters = self.build_classification_query_filters()

    def build_kwargs(self) -> tuple[dict[str, str], dict[str, str]]:
        training_kwargs, eval_kwargs = super().build_kwargs()
        training_kwargs["dropout"] = self.config["advanced.dropout"]
        return training_kwargs, eval_kwargs

    def build_classification_query_filters(self) -> list[Expression]:
        filters = []

        # Filter on source
        worker_runs = self.config["advanced.worker_runs"]
        if worker_runs:
            manual_idx = False
            try:
                manual_idx = worker_runs.index(MANUAL_SOURCE)
                worker_runs.pop(manual_idx)
                filters.append(
                    CachedClassification.worker_run_id.in_(worker_runs)
                    | CachedClassification.worker_run_id.is_null()
                )
            except ValueError:
                filters.append(CachedClassification.worker_run_id.in_(worker_runs))

        # Filter on classification name
        if self.config["class_names"]:
            filters.append(
                CachedClassification.class_name.in_(self.config["class_names"])
            )

        return filters

    def get_classifications(self, dataset_set: Set) -> Query:
        """
        List elements in a dataset set with their classifications
        """
        query = (
            CachedElement.select()
            .join(CachedDatasetElement)
            .where(
                CachedDatasetElement.dataset == self.cached_dataset,
                CachedDatasetElement.set_name == dataset_set.name,
            )
        )

        classifications = CachedClassification.select(CachedClassification).where(
            reduce(operator.and_, self.cls_filters, True)
        )

        return prefetch(query, classifications)

    def organize_split(self, dataset_set: Set) -> None:
        split = ARKINDEX_SET_TO_YOLO_SPLIT[dataset_set.name]

        data_dir: Path = self.training_data / split.value
        data_dir.mkdir(parents=True, exist_ok=True)

        element_classifications = self.get_classifications(dataset_set)

        logger.info(f"Extracting data for {dataset_set}...")
        logger.info(f"  - Images will be saved to {data_dir} directory")
        for element in element_classifications:
            if not element.classifications:
                continue

            # Take first classification
            classification = element.classifications[0]

            # Move at the proper place and resize the extracted image
            class_dir: Path = data_dir / classification.class_name
            class_dir.mkdir(exist_ok=True)
            self.move_preprocess_image(element, class_dir)

        logger.info(f"{dataset_set} fully downloaded.")

    def is_split_extracted(self, split: YOLOSplit, required: bool = False) -> bool:
        """Check if the data for a given split was properly extracted or not"""
        split_path = self.training_data / split.value
        extracted = _is_dir_with_children(split_path)

        if required:
            dataset_set_name = list(ARKINDEX_SET_TO_YOLO_SPLIT.keys())[
                list(ARKINDEX_SET_TO_YOLO_SPLIT.values()).index(split)
            ]
            assert extracted, (
                f'{split_path} path to data from "{dataset_set_name}" dataset set, does not exist or is empty'
            )

        return extracted


def main() -> None:
    YOLOTrainCls(
        description="YOLO Classification Training: To classify an image based on its content",
        support_cache=True,
    ).run()


if __name__ == "__main__":
    main()
