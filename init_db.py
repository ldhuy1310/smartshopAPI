import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

URI_MONGO = os.getenv("URI_MONGO", "mongodb://db:27017/")
DB_MONGO = os.getenv("DB_MONGO", "smart_shop")
client = MongoClient(URI_MONGO)
db = client[DB_MONGO]

if 'smart_shop' not in db.list_collection_names():
    db.create_collection('smart_shop')
    print("Collection 'smart_shop' created.")
else:
    print("Collection 'smart_shop' already exists.")
