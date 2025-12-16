from logging import Logger, getLogger

import torch

from arkindex_worker.models import Element
from worker_yolo.worker import YOLOWorker

logger: Logger = getLogger(__name__)


class YOLOClassifier(YOLOWorker):
    def process_image(self, image: str) -> tuple[str, float]:
        results = self.model(image, device=self.device, conf=0).pop()

        data: torch.Tensor = results.probs.data

        # Get the predicted ml_class and confidence
        ml_class = results.names[torch.argmax(data).item()]
        confidence = torch.max(data).item()

        return ml_class, round(confidence, 3)

    def process_element(self, element: Element) -> None:
        logger.info("Loading element image...")
        with self.load_image(element) as image:
            logger.info("Predicting a class on the image...")
            ml_class, confidence = self.process_image(image)

        if confidence < self.confidence_threshold:
            logger.warning(
                f"Ignoring the classification `{ml_class}` since its confidence ({confidence * 100:.2f}%) is below the threshold."
            )
            return

        logger.info("Publishing classification on Arkindex...")
        self.create_classification(
            element=element, ml_class=ml_class, confidence=confidence
        )


def main() -> None:
    YOLOClassifier(
        description="Ultralytics YOLO Classifier: Classify an image based on its content"
    ).run()


if __name__ == "__main__":
    main()
