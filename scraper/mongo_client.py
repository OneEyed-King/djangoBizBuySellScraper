# db/mongo_client.py
from pymongo import MongoClient

# You can later move the URI to a config file or environment variable
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "scraper_db"

def get_mongo_collection(collection_name: str):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]  # or whatever your database is named
    collection = db[collection_name]
    collection.create_index("url", unique=True)
    return collection


