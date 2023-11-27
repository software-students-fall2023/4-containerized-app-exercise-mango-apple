import pytest
import numpy as np
import tensorflow as tf
from unittest.mock import patch, MagicMock
from bson import ObjectId
from ml_client import app, detect_objects
import cv2


@pytest.fixture
def client():
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def mock_image():
    return np.random.randint(0, 255, (320, 320, 3), dtype=np.uint8)


def generate_mock_detections():
    return {
        "detection_classes": tf.constant([[1.0]]),
        "detection_boxes": tf.constant([[[0.1, 0.1, 0.2, 0.2]]]),
        "detection_scores": tf.constant([[0.9]]),
    }


@patch(
    "ml_client.tf.saved_model.load",
    return_value=MagicMock(return_value=generate_mock_detections()),
)
@patch("ml_client.cv2.resize")
def test_detect_objects(mock_resize, mock_tf_load, mock_image):
    mock_model = mock_tf_load.return_value
    mock_resize.return_value = mock_image
    boxes, scores, labels = detect_objects(mock_image, mock_model)
    assert len(boxes) == 1
    assert len(scores) == 1
    assert len(labels) == 1


@patch("ml_client.fs.get")
@patch("ml_client.results.insert_one")
@patch(
    "ml_client.tf.saved_model.load",
    return_value=MagicMock(return_value=generate_mock_detections()),
)
def test_process_image_route(
    mock_tf_load, mock_insert_one, mock_fs_get, client, mock_image
):
    # Convert the mock image to a format that can be encoded by cv2.imencode
    success, encoded_image = cv2.imencode(".jpg", mock_image)
    assert success, "Image encoding failed"

    mock_file = MagicMock(read=MagicMock(return_value=encoded_image.tobytes()))
    mock_fs_get.return_value = mock_file
    mock_insert_one.return_value = None
    response = client.get("/process-image/" + str(ObjectId()))

    assert response.status_code == 200
    data = response.get_json()
    assert "Image processed" in data["message"]
    assert "boxes" in data
    assert "scores" in data
    assert "labels" in data


@patch("ml_client.fs.get")
def test_process_image_route_invalid_id(mock_fs_get, client):
    mock_fs_get.side_effect = Exception("Invalid ID")
    response = client.get("/process-image/" + str(ObjectId()))
    assert response.status_code == 500
    data = response.get_json()
    assert data is not None
    assert "error" in data


def test_main():
    with patch("ml_client.app.run") as mock_run:
        from ml_client import __name__ as name

        if name == "__main__":
            mock_run.assert_called()
