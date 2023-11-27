# test_app.py

import pytest
from app import app
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from io import BytesIO


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """
    Test the home route.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>Live Video Capture</title>" in response.get_data(as_text=True)
    assert "Live Video Capture" in response.get_data(as_text=True)


@patch("app.fs.put")
@patch("app.images.insert_one")
@patch("app.requests.get")
def test_trigger_ml_processing(
    mock_requests_get, mock_images_insert, mock_fs_put, client
):
    """
    Test the trigger_ml_processing route.
    """
    mock_fs_put.return_value = ObjectId()
    mock_images_insert.return_value = None
    mock_requests_get.return_value = MagicMock(
        status_code=200, json=MagicMock(return_value={"result": "success"})
    )

    data = {"frame": (BytesIO(b"dummy image data"), "image.jpg")}
    response = client.post(
        "/trigger-ml-processing", content_type="multipart/form-data", data=data
    )

    assert response.status_code == 200
    assert response.json.get("result") == "success"


def test_trigger_ml_processing_no_frame(client):
    """
    Test the trigger_ml_processing route with no frame uploaded.
    """
    response = client.post("/trigger-ml-processing")
    assert response.status_code == 400
    assert "error" in response.json
