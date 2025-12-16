import contextlib
import shutil
from enum import Enum
from pathlib import Path
from tempfile import mkdtemp
from uuid import UUID

import torch
from ultralytics import YOLO
from ultralytics.utils.checks import check_amp

from arkindex_worker import logger
from arkindex_worker.cache import CachedDataset, CachedElement, init_cache_db
from arkindex_worker.models import Dataset, Set
from arkindex_worker.utils import create_zip_archive, extract_tar_zst_archive
from arkindex_worker.worker import DatasetWorker
from arkindex_worker.worker.training import TrainingMixin
from teklia_yolo.extract.utils import get_bbox, preprocess_image

RESULTS_ARTIFACT = "results.zip"


def _is_dir_with_children(path: Path) -> bool:
    """Check if the given path exists, is a directory and has children, all at once"""
    return bool(path.exists() and path.is_dir() and next(path.iterdir(), None))


class YOLOSplit(Enum):
    Training = "train"
    Validation = "val"
    Testing = "test"


# Mapping between Arkindex DatasetSet names and the split names needed by YOLO
ARKINDEX_SET_TO_YOLO_SPLIT = {
    "train": YOLOSplit.Training,
    "dev": YOLOSplit.Validation,
    "test": YOLOSplit.Testing,
}


class YOLOTrain(DatasetWorker, TrainingMixin):
    def configure(self) -> None:
        super().configure()

        # Point to an existing model to fine-tune if any
        self.base_model = self.load_model_version() if self.is_finetuning else None

        # Retrieve training related information
        self.model_id = UUID(self.config["target_model_id"])

        # Build model training and validation kwargs
        self.img_size = self.config["image_size"]
        # Do not pad images by default
        # YOLOTrainDetect worker doesn't have the `advanced.padding` parameter
        self.padding = self.config.get("advanced.padding", False)
        self.training_kwargs, self.eval_kwargs = self.build_kwargs()

        # Create the directory where to store datasets training data
        self.training_data = Path(mkdtemp(suffix="-training-data")) / "all"
        logger.info(f"Training-related data will be available at {self.training_data}")
        self.train_from = self.training_data

        # Initialize cache variables
        self.dataset_archive: Path | None = None
        self.cached_dataset: CachedDataset | None = None

    def load_model_version(self) -> None:
        model_path = self.find_extras_directory() / "model.pt"
        logger.info(f"Try to load model @ {model_path}")

        assert model_path.exists(), f"Missing model @ {model_path}"

        return model_path

    def build_kwargs(self) -> tuple[dict[str, str], dict[str, str]]:
        common_kwargs = {
            "imgsz": self.img_size,
            "device": 0 if torch.cuda.is_available() else "cpu",
            "plots": True,
        }

        training_kwargs = {
            **common_kwargs,
            "epochs": self.config["num_epochs"],
            "batch": self.config["advanced.batch_size"],
            "verbose": True,
        }
        for param, value in self.config["advanced.training_kwargs"].items():
            # Try to convert integer, float and boolean values
            with contextlib.suppress(NameError):
                value = eval(value)
            training_kwargs[param] = value

        eval_kwargs = {**common_kwargs, "batch": 1}

        return training_kwargs, eval_kwargs

    def load_parent_dataset(self, dataset: Dataset) -> None:
        # Clean up the previously extracted dataset archive
        self.cleanup_dataset_archive()

        # Extract the existing Dataset artifact
        self.extract_archive(dataset)

        # Build the training dataset
        self.cached_dataset = self.load_dataset_from_cache(dataset)

    def cleanup_dataset_archive(self) -> None:
        """
        Cleanup the extracted dataset archive if any
        """
        if not self.dataset_archive:
            return

        shutil.rmtree(self.dataset_archive, ignore_errors=True)

    def extract_archive(self, dataset: Dataset) -> None:
        self.dataset_archive = Path(mkdtemp(suffix=f"-{dataset.id}")) / "archive"
        logger.info(f"Extracting the dataset archive at {self.dataset_archive}")
        extract_tar_zst_archive(self.downloaded_dataset_artifact, self.dataset_archive)

    def load_dataset_from_cache(self, dataset: Dataset) -> CachedDataset:
        init_cache_db(self.dataset_archive / "db.sqlite")
        return CachedDataset.get_by_id(dataset.id)

    def move_preprocess_image(self, element: CachedElement, to_path: Path) -> None:
        """Preprocess the image (with ID `image_id`) located in the "images" folder of the
        downloaded dataset archive and copy it to `to_path`.

        :param str image_id: UUID of the element image to move and preprocess
        :param Path to_path: Path to save the preprocessed image
        """
        preprocess_image(
            from_path=(
                self.dataset_archive / "images" / str(element.image_id)
            ).with_suffix(".jpg"),
            to_path=(to_path / str(element.id)).with_suffix(".jpg"),
            box=get_bbox(element.polygon),
            resize=(self.img_size, self.img_size),
            padding=self.padding,
        )

    def process_set(self, dataset_set: Set) -> None:
        if dataset_set.name not in ARKINDEX_SET_TO_YOLO_SPLIT:
            logger.warning(
                f"Skipping {dataset_set} as it is not a supported dataset set in this worker"
            )
            return

        if (
            not self.cached_dataset
            or str(self.cached_dataset.id) != dataset_set.dataset.id
        ):
            self.load_parent_dataset(dataset_set.dataset)

        self.organize_split(dataset_set)

    def run_training_preprocessing(self) -> None:
        """Optional preprocessing steps to run before training the model"""

    def get_model_config(self) -> dict | None:
        """Optional configuration to publish along with the trained model"""
        return {
            "thumbnail_size": self.img_size,
            "padding": self.padding,
        }

    def run(self) -> None:
        super().run()

        # Clean up the previously extracted dataset archive
        self.cleanup_dataset_archive()

        # Check that data is available for train and val splits
        for split in [YOLOSplit.Training, YOLOSplit.Validation]:
            self.is_split_extracted(split, required=True)

        self.run_training_preprocessing()

        # Load the pretrained model (recommended for training)
        model = YOLO(self.base_model)

        # Train a new version of YOLO on this dataset
        model.train(data=self.train_from, amp=check_amp(model), **self.training_kwargs)

        # Evaluate all splits from the dataset
        for split in YOLOSplit:
            # If no testing split was extracted, skip its evaluation
            if split == YOLOSplit.Testing and not self.is_split_extracted(split):
                continue

            model.val(name=f"eval_{split.value}", split=split.value, **self.eval_kwargs)

        # Publish the new version on Arkindex
        logger.info(f"Publishing the new model version on model {self.model_id}")

        train_dir: Path = model.trainer.save_dir
        model_dir: Path = train_dir / "weights"
        # - Remove last.pt
        Path(model_dir / "last.pt").unlink()
        # - Rename best.pt to model.pt
        model_path: Path = Path(model_dir / "best.pt")
        model_path.rename(model_path.with_stem("model"))
        # - Publish the directory with only model.pt in it
        self.publish_model_version(
            model_path=model_dir,
            model_id=self.model_id,
            configuration=self.get_model_config(),
            parent=self.model_version_id,
        )

        # Once the model is published, we can clean up and publish an archive with the results
        logger.info(
            f"Publishing training and evaluation results in an artifact named {RESULTS_ARTIFACT}"
        )

        shutil.rmtree(model_dir)
        zip_archive_path: Path = self.work_dir / RESULTS_ARTIFACT
        create_zip_archive(train_dir.parent, zip_archive_path)
