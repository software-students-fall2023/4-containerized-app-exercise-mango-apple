"""
This is the app.py boilerplate
"""
import os
import pymongo
from flask import Flask, render_template, request, jsonify
import gridfs
import requests
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)

client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DBNAME")]
images = db.images
fs = gridfs.GridFS(db)


@app.route("/", methods=["GET"])
def index():
    """
    Home Route - Display the upload form
    """
    return render_template("capture.html")


@app.route("/trigger-ml-processing", methods=["POST"])
def trigger_ml_processing():
    """
    api endpoint
    """
    if "frame" in request.files:
        frame = request.files["frame"]
        content_type = frame.content_type
        image_id = fs.put(frame, content_type=content_type, filename=frame.filename)
        images.insert_one(
            {
                "filename": frame.filename,
                "contentType": content_type,
                "gridfs_id": image_id,
            }
        )

        response = requests.get(
            f"http://ml_client:5001/process-image/{image_id}", timeout=20
        )
        return jsonify(response.json())
    return jsonify({"error": "No frame received"}), 400


if __name__ == "__main__":
    PORT = 5000
    app.run(host="0.0.0.0", port=PORT)
