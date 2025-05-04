import os

import pymongo
from datetime import datetime as dt

def update_data(data: dict) -> bool:
    """ Update data in MongoDB """
    try:
        client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        db = client[os.environ.get('MONGO_DB', 'calorie_calculator')]
        collection = db[os.environ.get('MONGO_COLL', 'records')]
        data['date'] = dt.now().date().isoformat()
        collection.insert_one(data)
        client.close()
        return True
    except Exception as e:
        raise e


def fetch_data(username: str) -> list[dict]:
    """ Fetch all data from MongoDB for current user / today's records """
    try:

        today = dt.now().date().isoformat()

        client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        db = client[os.environ.get('MONGO_DB', 'calorie_calculator')]
        collection = db[os.environ.get('MONGO_COLL', 'records')]
        data = collection.find({'username': username, 'date': today}).to_list()
        client.close()
        return data
    except Exception as e:
        raise e
