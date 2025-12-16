import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import permutations
from operator import attrgetter, itemgetter

from shapely.geometry.polygon import Polygon

from arkindex_worker.utils import pluralize

logger = logging.getLogger(__name__)


@dataclass
class Zone:
    name: str
    type: str
    polygon: list
    confidence: float

    @property
    def geometry(self):
        return Polygon(self.polygon)

    @property
    def is_valid(self):
        return self.geometry.is_valid

    @property
    def area(self):
        return self.geometry.area

    @property
    def min_x(self):
        return min(map(itemgetter(0), self.polygon))

    @property
    def min_y(self):
        return min(map(itemgetter(1), self.polygon))

    def intersection(self, other: "Zone"):
        return self.geometry.intersection(other.geometry)

    def intersects(self, other: "Zone"):
        return self.geometry.intersects(other.geometry)

    def overlap(self, other: "Zone"):
        # If input is invalid, the intersection may raise GEOSException.
        if not self.intersects(other) or not (self.is_valid and other.is_valid):
            return 0.0
        return self.intersection(other).area / other.area

    def __str__(self) -> str:
        return f"{self.type} {self.name} (confidence {self.confidence * 100}%)"


def rename_zones(zones: list[Zone]):
    child_types = Counter()
    for zone in zones:
        child_types.update({zone.type: 1})
        zone.name = str(child_types[zone.type])


def remove_overlapping_zones(
    zones: list[Zone],
    thresholds: tuple[float, float] = (0.80, 0.95),
    max_overlap_count: int = 1,
):
    """Algorithm that removes overlapping zones according to the following rules.
    - If a zone overlaps more than max_overlap_count other zone (of the same type) above a low_threshold (first threshold provided), it is removed.
    - If two zones (of different types) overlap one another above a high_threshold (second threshold provided), the least confident is removed.
    """
    low_threshold, high_threshold = thresholds
    overlaps = defaultdict(list)
    to_remove = set()

    for base, target in permutations(zones, 2):
        overlap = base.overlap(target)
        if overlap < low_threshold:
            continue

        logger.info(f"{base} and {target} overlap ({round(overlap * 100, 2)}%)")

        # Check if same type
        if base.type == target.type:
            # Keep track of the number of zones this zone overlaps.
            overlaps[zones.index(base)].append(target)

        # Different types
        # Objects of different types must be overlapping even more to be removed.
        elif target.overlap(base) > high_threshold and overlap > high_threshold:
            # Only the least confident will be removed.
            least_confident = base if base.confidence < target.confidence else target
            logger.info(f"Zone {least_confident} will be removed.")
            # Remove least confident
            to_remove.add(zones.index(least_confident))

    # Remove the zones that overlap too many zones with the same type.
    for base_idx, overlapped_zones in overlaps.items():
        if len(overlapped_zones) <= max_overlap_count:
            continue

        # Only keep top max_overlap_count confident
        overlapped_zones.append(zones[base_idx])
        # Sort by confidence
        overlapped_zones.sort(key=attrgetter("confidence"), reverse=True)
        for zone in overlapped_zones[max_overlap_count + 1 :]:
            to_remove.add(zones.index(zone))

    # Remove the criminal zones. In reverse order so that the idx are not changed.
    for idx in sorted(to_remove, reverse=True):
        zones.pop(int(idx))

    logger.info(
        f"Removed {len(to_remove)} {pluralize('zone', len(to_remove))} that didn't follow overlapping rules."
    )
