from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017")
db = client["ims"]
signals_collection = db["signals"]
