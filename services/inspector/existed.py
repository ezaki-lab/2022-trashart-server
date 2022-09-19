from bson.objectid import ObjectId
from pymongo import MongoClient

def existed_art_id(client: MongoClient, art_id: str):
    db = client.trashart_db
    try:
        data = db.arts.find_one(ObjectId(art_id))

        if data == None:
            return False
    except:
        return False

    return True

def existed_crafting_id(client: MongoClient, crafting_id: str):
    db = client.trashart_db
    try:
        data = db.craftings.find_one(ObjectId(crafting_id))

        if data == None:
            return False
    except:
        return False

    return True

def existed_user_id(client: MongoClient, user_id: str):
    db = client.trashart_db
    try:
        data = db.users.find_one(ObjectId(user_id))

        if data == None:
            return False
    except:
        return False

    return True

def existed_session_id(client: MongoClient, session_id: str):
    db = client.trashart_db
    try:
        data = db.sessions.find_one(ObjectId(session_id))

        if data == None:
            return False
    except:
        return False

    return True
