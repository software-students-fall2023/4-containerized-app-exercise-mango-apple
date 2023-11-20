import pymongo
import os
from flask import Flask, request, render_template, redirect

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

# Connecting to local host
connection = pymongo.MongoClient("mongodb://localhost:27017")
db = connection["test_database"]

if __name__ == "__main__":
    PORT = os.getenv(
        "PORT", 5000
    )  # use the PORT environment variable, or default to 5000

    # import logging
    # logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(port=PORT)