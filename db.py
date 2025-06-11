# db.py
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client['password_manager']  # Make sure the DB name matches your URI
