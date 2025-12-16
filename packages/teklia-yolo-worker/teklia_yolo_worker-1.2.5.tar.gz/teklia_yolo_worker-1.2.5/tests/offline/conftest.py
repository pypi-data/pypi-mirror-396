import os
from argparse import Namespace

import pytest

from worker_yolo.offline.classifier import YOLOClassifierOffline
from worker_yolo.offline.publish import YOLOPublish


def setup_worker(worker, dev=False):
    worker.args = Namespace(dev=dev)

    # Load corpus_id from environment
    worker._corpus_id = os.getenv("ARKINDEX_CORPUS_ID")

    return worker


@pytest.fixture
def mock_classifier_worker():
    # Setup Mock Worker
    worker = YOLOClassifierOffline()
    return setup_worker(worker, dev=True)


@pytest.fixture
def mock_publish_worker():
    # Setup Mock Worker
    worker = YOLOPublish()
    return setup_worker(worker)
