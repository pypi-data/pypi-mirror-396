import pytest

from arkindex_worker.models import Element


def test_publish_activities(mock_publish_worker):
    element = Element(id="mock_element_id")
    worker_run_id = "1234-worker-run-id"

    mock_publish_worker.api_client.add_response(
        "UpdateWorkerActivity",
        id=worker_run_id,
        body={
            "element_id": element.id,
            "process_id": "my_process_id",
            "state": "started",
        },
        response={},
    )
    mock_publish_worker.api_client.add_response(
        "UpdateWorkerActivity",
        id=worker_run_id,
        body={
            "element_id": element.id,
            "process_id": "my_process_id",
            "state": "processed",
        },
        response={},
    )

    mock_publish_worker.process_information = {
        "id": "my_process_id",
        "activity_state": "ready",
        "mode": "workers",
    }
    mock_publish_worker.publish_activities(
        element,
        [
            {"state": "started", "worker_run_id": worker_run_id},
            {"state": "processed", "worker_run_id": worker_run_id},
        ],
    )

    assert mock_publish_worker.worker_run_id == "1234-yolo"

    # Make sure every mock response has been called
    assert len(mock_publish_worker.api_client.history) == 2
    assert len(mock_publish_worker.api_client.responses) == 0


# Whether the ml class is already available in the corpus
@pytest.mark.parametrize("missing", [True, False])
def test_publish_classification(missing, mock_publish_worker):
    element = Element(id="mock_element_id")
    classification = {
        "ml_class": "Front_page",
        "confidence": 0.98,
        "high_confidence": False,
    }

    ml_class = {
        "name": classification["ml_class"],
        "id": "ml_class_id",
    }

    if missing:
        # Listing returns empty list
        mock_publish_worker.api_client.add_response(
            "ListCorpusMLClasses",
            id=mock_publish_worker.corpus_id,
            response=[],
        )
        # ML class will be created
        mock_publish_worker.api_client.add_response(
            "CreateMLClass",
            id=mock_publish_worker.corpus_id,
            body={"name": classification["ml_class"]},
            response=ml_class,
        )
    else:
        mock_publish_worker.api_client.add_response(
            "ListCorpusMLClasses",
            id=mock_publish_worker.corpus_id,
            response=[ml_class],
        )
    # Create classification
    mock_publish_worker.api_client.add_response(
        "CreateClassification",
        response={"id": "mock_classification_id"},
        body={
            **classification,
            "ml_class": ml_class["id"],
            "element": element.id,
            "worker_run_id": mock_publish_worker.worker_run_id,
        },
    )

    mock_publish_worker.publish_classification(element, classification)

    # Make sure every mock response has been called
    # One more if the ml class has to be created
    assert len(mock_publish_worker.api_client.history) == 2 + int(missing)
    assert len(mock_publish_worker.api_client.responses) == 0
