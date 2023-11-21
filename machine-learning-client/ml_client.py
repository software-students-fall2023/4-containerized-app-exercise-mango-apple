"""
This is the ml_client.py boilerplate
"""
import os
from pymongo import MongoClient
from gridfs import GridFS
from flask import Flask, jsonify
import cv2
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


model = tf.saved_model.load('ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8/saved_model')

client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DBNAME')]
fs = GridFS(db)
results = db.results
images = db.images


COCO_LABELS = {

    1: 'person',
    2: 'bicycle',
    3: 'car',
    4: 'motorcycle',
    5: 'airplane',
    6: 'bus',
    7: 'train',
    8: 'truck',
}


def detect_objects(image):
    '''
    Detect objects in the image
    '''
    image_resized = cv2.resize(image, (320, 320))

    image_uint8 = np.array(image_resized).astype(np.uint8)

    input_tensor = tf.convert_to_tensor([image_uint8], dtype=tf.uint8)

    detections = model(input_tensor)

    class_ids = detections['detection_classes'][0].numpy().astype(np.int32)
    labels = [COCO_LABELS.get(class_id, 'unknown') for class_id in class_ids]

    box_coordinates = detections['detection_boxes'][0].numpy()
    scores = detections['detection_scores'][0].numpy()

    return box_coordinates, scores, labels


@app.route('/process-latest', methods=['GET'])
def process_latest_image():
    '''
    Process the latest image
    '''
    latest_image = images.find_one(sort=[('_id', -1)])
    if latest_image is not None:
        image_id = latest_image['gridfs_id']
        image_file = fs.get(image_id)
        image_data = image_file.read()
        image_nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_nparr, cv2.IMREAD_COLOR)
        boxes, scores,labels = detect_objects(image)
        results.insert_one({"image_id": image_id, "boxes": boxes.tolist(),
                            "scores": scores.tolist()})
        final_result = {"message": "Image processed", "boxes": boxes.tolist(),
                        "scores": scores.tolist(), "labels": labels}
        return jsonify(final_result)
    return jsonify({"message": "No images to process"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
