import json

from arkindex_worker.models import Element


def test_create_classification(mock_classifier_worker):
    element = Element(id="mock_element_id")
    mock_classifier_worker._element_id = element.id

    mock_classifier_worker.create_classification(
        element,
        ml_class="Front_page",
        confidence=0.98,
    )

    assert json.loads(mock_classifier_worker.json_path.read_text()) == {
        "classification": {
            "ml_class": "Front_page",
            "confidence": 0.98,
            "high_confidence": False,
        }
    }
