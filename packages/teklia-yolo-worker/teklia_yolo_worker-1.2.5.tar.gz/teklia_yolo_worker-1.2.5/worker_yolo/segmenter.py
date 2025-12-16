import re
from collections import Counter
from dataclasses import asdict
from enum import Enum
from logging import Logger, getLogger

from shapely import Polygon, minimum_rotated_rectangle

from arkindex_worker.cache import CachedElement
from arkindex_worker.image import revert_orientation, trim_polygon
from arkindex_worker.models import Element
from arkindex_worker.utils import pluralize
from worker_yolo.utils import Zone, remove_overlapping_zones, rename_zones
from worker_yolo.worker import YOLOWorker

logger: Logger = getLogger(__name__)

SLUG_PATTERN = re.compile(r"[^-a-zA-Z0-9_]")


def slugify(name: str) -> str:
    return SLUG_PATTERN.sub("", name.replace(" ", "_"))


def minimum_rotated_rectangle_polygon(polygon: list[list[int]]) -> list[list[int]]:
    # Convert the polygon to a shapely.Polygon
    geometry = Polygon(polygon)
    # Compute its minimal rectangle
    geometry = minimum_rotated_rectangle(geometry)
    # Retrieve its external envelope
    geometry = geometry.normalize()
    return list(geometry.exterior.coords)


class Mode(str, Enum):
    DEFAULT = "default"
    MINIMUM_ROTATED_RECTANGLE = "minimum_rotated_rectangle"

    def __str__(self):
        return self.value


class YOLOSegmenter(YOLOWorker):
    def configure(self) -> None:
        super().configure()

        try:
            self.mode = Mode(self.config["mode"])
        except ValueError as e:
            raise Exception(f"{e}. Mode should be either {list(map(str, Mode))}") from e
        self.use_segment = self.config["use_segment"]

        self.remove_overlapping_objects: bool = self.config.get(
            "overlap.remove_overlapping_objects", False
        )
        self.min_overlap_threshold: float = self.config["overlap.min_overlap_threshold"]
        self.max_overlap_threshold: float = self.config["overlap.max_overlap_threshold"]
        self.max_overlap_count: int = self.config["overlap.max_overlap_count"]

        self.max_detection: int = self.config["max_detection"]
        self.iou: float = self.config["iou"]

        logger.info("Checking required element types...")
        self.check_required_types(
            list(map(slugify, self.model.names.values())), create_missing=True
        )

    def create_elements(
        self,
        parent: Element | CachedElement,
        elements: list[dict[str, str | list[list[int | float]] | float | None]],
    ) -> list[dict[str, str]]:
        """
        Override ElementsWorker's method to update polygon according to the parent offset
        """
        # Update polygons according to the parent offset
        for element in elements:
            element["polygon"] = revert_orientation(parent, element["polygon"])

        return super().create_elements(parent, elements)

    def get_polygon(
        self, child_type: str, segment: list[list[int]] | None, box: list[list[int]]
    ) -> list[list[int]]:
        # Always use the box if there is no segment
        if not segment:
            return box

        # Use the minimum rectangle algorithm
        if self.mode == Mode.MINIMUM_ROTATED_RECTANGLE:
            return minimum_rotated_rectangle_polygon(segment)

        # By default, use the segment or the box according to the `use_segment` parameter
        return segment if child_type in self.use_segment else box

    def process_image(self, image: str) -> list[dict]:
        logger.info(f"Using device {self.device}")

        results = self.model(
            image,
            device=self.device,
            conf=0,
            iou=self.iou,
            max_det=self.max_detection,
        ).pop()
        # Retrieve (oriented bounding) boxes
        result_polygons = results.boxes or results.obb

        if not result_polygons:
            return []

        # Extract boxes and segments
        children, child_types, low_confidence, invalid = [], Counter(), 0, 0
        for i in range(result_polygons.xyxy.shape[0]):
            min_x, min_y, max_x, max_y = result_polygons.xyxy[i].cpu().tolist()
            box = (
                result_polygons.xyxyxyxy[i].cpu().tolist()
                if hasattr(result_polygons, "xyxyxyxy")
                else [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]
            )
            segment = results.masks.xy[i].tolist() if results.masks else None

            child_type = results.names[result_polygons.cls[i].cpu().item()]
            child_confidence = result_polygons.conf[i].cpu().item()

            # Filter out objects with a confidence below the configured threshold
            if child_confidence < self.confidence_threshold:
                # Avoid polluting the logs when filtering out truly uncertain objects
                if child_confidence >= 0.01:
                    logger.warning(
                        f"Removing an object with class `{child_type}` since its confidence ({child_confidence * 100:.2f}%) is below the threshold."
                    )
                low_confidence += 1
                continue

            # Update type counts
            child_types.update({child_type: 1})

            child_polygon = self.get_polygon(child_type, segment, box)

            # Trim any part of the child's polygon that may be outside the element's image due to resizing
            trimmed_polygon = trim_polygon(
                # Resize the child's polygon according to the resizing of the original image
                [
                    [round(x * self.width_ratio), round(y * self.height_ratio)]
                    for (x, y) in child_polygon
                ],
                self.original_width,
                self.original_height,
            )
            child = Zone(
                name=str(child_types[child_type]),
                type=slugify(child_type),
                polygon=trimmed_polygon,
                confidence=round(child_confidence, 2),
            )

            # Filter out invalid geometries
            if not child.is_valid:
                invalid += 1
                continue

            children.append(child)

        if low_confidence:
            logger.warning(
                f"Removed {low_confidence} {pluralize('object', low_confidence)} predicted with insufficient confidence."
            )

        if invalid:
            logger.warning(
                f"Removed {invalid} {pluralize('zone', invalid)} holding an invalid geometry."
            )

        if self.remove_overlapping_objects:
            logger.info("Filtering out overlapping objects...")
            remove_overlapping_zones(
                children,
                thresholds=(self.min_overlap_threshold, self.max_overlap_threshold),
                max_overlap_count=self.max_overlap_count,
            )

        # Sort remaining zones by top left coords
        sorted_children = sorted(
            children,
            key=lambda child: (child.min_y, child.min_x),
        )

        # Remapping so that we have indexing by type
        rename_zones(sorted_children)

        return sorted_children

    def process_element(self, element: Element) -> None:
        logger.info("Loading element image...")
        with self.load_image(element) as image:
            logger.info("Predicting boxes and segments on the image...")
            children = self.process_image(image)

        if children:
            logger.info("Publishing elements on Arkindex...")
            self.create_elements(parent=element, elements=list(map(asdict, children)))
        else:
            logger.warning("No detections. Skipping element creation.")


def main() -> None:
    YOLOSegmenter(
        description="Ultralytics YOLO Segmenter: Process image and detect objects with its precise shape"
    ).run()


if __name__ == "__main__":
    main()
