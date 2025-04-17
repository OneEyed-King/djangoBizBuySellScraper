# db/mongo_client.py
from pymongo import MongoClient

# You can later move the URI to a config file or environment variable
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "scraper_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def get_mongo_collection(collection_name):
    collection_name.create_index("url", unique=True)
    return db[collection_name]

