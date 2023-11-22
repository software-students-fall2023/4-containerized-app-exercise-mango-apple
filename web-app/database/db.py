"""
MongoDB database for web app - storing user's images
"""

import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Create a MongoDB client
client = MongoClient(os.getenv("MONGO_URI"))
name = os.getenv("MONGO_DBNAME")
DB = None

# Confirm a successful connection
try:
    client.admin.command("ping")
    db = client[name]
    print("Successfully connected to MongoDB!")
except Exception as e:  # pylint: disable=broad-except
    print(e)