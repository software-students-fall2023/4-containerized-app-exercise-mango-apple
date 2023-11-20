"""
This is the app.py boilerplate
"""
import os
import pymongo
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    """
    Test Route
    """
    return render_template("home.html")


# Connecting to local host
connection = pymongo.MongoClient("mongodb://localhost:27017")
db = connection["test_database"]

if __name__ == "__main__":
    PORT = os.getenv("5000")

    # import logging
    # logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(port=PORT)
