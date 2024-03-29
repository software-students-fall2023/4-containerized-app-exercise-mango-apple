"""
This is the ml_client.py boilerplate
"""
import os
import logging
from bson.objectid import ObjectId
from dotenv import load_dotenv
import cv2
import numpy as np
import tensorflow as tf
from flask import Flask, jsonify
from pymongo import MongoClient
from gridfs import GridFS

load_dotenv()

app = Flask(__name__)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

model = tf.saved_model.load(os.getenv("MODEL"))


def get_mongo_client(uri):
    """Create and return a MongoDB client."""
    return MongoClient(uri)


mongo_uri = os.getenv("MONGO_URI")
client = get_mongo_client(mongo_uri)
db = client[os.getenv("MONGO_DBNAME")]
fs = GridFS(db)
results = db.results
images = db.images

COCO_LABELS = {
    1: "person",
    2: "bicycle",
    3: "car",
    4: "motorcycle",
    5: "airplane",
    6: "bus",
    7: "train",
    8: "truck",
    9: "boat",
    10: "traffic light",
    11: "fire hydrant",
    13: "stop sign",
    14: "parking meter",
    15: "bench",
    16: "bird",
    17: "cat",
    18: "dog",
    19: "horse",
    20: "sheep",
    21: "cow",
    22: "elephant",
    23: "bear",
    24: "zebra",
    25: "giraffe",
    27: "backpack",
    28: "umbrella",
    31: "handbag",
    32: "tie",
    33: "suitcase",
    34: "frisbee",
    35: "skis",
    36: "snowboard",
    37: "sports ball",
    38: "kite",
    39: "baseball bat",
    40: "baseball glove",
    41: "skateboard",
    42: "surfboard",
    43: "tennis racket",
    44: "bottle",
    46: "wine glass",
    47: "cup",
    48: "fork",
    49: "knife",
    50: "spoon",
    51: "bowl",
    52: "banana",
    53: "apple",
    54: "sandwich",
    55: "orange",
    56: "broccoli",
    57: "carrot",
    58: "hot dog",
    59: "pizza",
    60: "donut",
    61: "cake",
    62: "chair",
    63: "couch",
    64: "potted plant",
    65: "bed",
    67: "dining table",
    70: "toilet",
    72: "tv",
    73: "laptop",
    74: "mouse",
    75: "remote",
    76: "keyboard",
    77: "cell phone",
    78: "microwave",
    79: "oven",
    80: "toaster",
    81: "sink",
    82: "refrigerator",
    84: "book",
    85: "clock",
    86: "vase",
    87: "scissors",
    88: "teddy bear",
    89: "hair drier",
    90: "toothbrush",
}


def detect_objects(image, tf_model):
    """
    Detect objects in the image using the provided TensorFlow model.
    """
    try:
        image_resized = cv2.resize(image, (320, 320))
        image_uint8 = np.array(image_resized).astype(np.uint8)
        input_tensor = tf.convert_to_tensor([image_uint8], dtype=tf.uint8)
        detections = tf_model(input_tensor)
    except Exception as e:
        logging.error("Error in object detection: %s", e)
        raise

    class_ids = detections["detection_classes"][0].numpy().astype(np.int32)
    labels = [COCO_LABELS.get(class_id, "unknown") for class_id in class_ids]
    box_coordinates = detections["detection_boxes"][0].numpy()
    scores = detections["detection_scores"][0].numpy()

    return box_coordinates, scores, labels


@app.route("/process-image/<image_id>", methods=["GET"])
def process_image(image_id):
    """
    Process the image with the given image_id and return the detection results.
    """
    try:
        image_file = fs.get(ObjectId(image_id))
        image_data = image_file.read()
        image_nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_nparr, cv2.IMREAD_COLOR)
        boxes, scores, labels = detect_objects(image, model)
        results.insert_one(
            {
                "image_id": ObjectId(image_id),
                "boxes": boxes.tolist(),
                "scores": scores.tolist(),
                "labels": labels,
            }
        )
    except FileNotFoundError as e:
        logging.error("Error processing image: %s", e)
        return jsonify({"error": str(e)}), 500

    final_result = {
        "message": "Image processed",
        "boxes": boxes.tolist(),
        "scores": scores.tolist(),
        "labels": labels,
    }
    return jsonify(final_result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
