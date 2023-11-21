"""
This is the app.py boilerplate
"""
import os
import pymongo
from flask import Flask, render_template, request, redirect, url_for, jsonify
import gridfs
import requests
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)

# Connecting to local host
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


@app.route("/upload", methods=["POST"])
def upload():
    """
    Handle image upload
    """
    if "image" in request.files:
        image = request.files["image"]
        content_type = image.content_type
        image_id = fs.put(image, content_type=content_type, filename=image.filename)
        images.insert_one(
            {
                "filename": image.filename,
                "contentType": content_type,
                "gridfs_id": image_id,
            }
        )
        return redirect(url_for("index"))
    return render_template("capture.html")


@app.route("/trigger-ml-processing", methods=["GET"])
def trigger_ml_processing():
    """
    api endpoint
    """
    response = requests.get("http://localhost:5001/process-latest", timeout=15)
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({"error": "Failed to process image"}), 500


if __name__ == "__main__":
    PORT = 5000
    app.run(debug=True, host="0.0.0.0", port=PORT)
