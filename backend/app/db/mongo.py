from pymongo import MongoClient

from app.core.config import settings


client = MongoClient(settings.mongodb_uri)

db = client[settings.mongodb_db_name]


def get_database():
    return db