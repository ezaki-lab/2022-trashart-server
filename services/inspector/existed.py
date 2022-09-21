from bson.objectid import ObjectId
from pymongo import MongoClient

def existed_user_id(c: MongoClient, user_id: str):
    db = c.trashart_db
    try:
        return db.users.find_one(ObjectId(user_id)) != None
    except:
        return False

def existed_session_id(c: MongoClient, session_id: str):
    db = c.trashart_db
    try:
        return db.sessions.find_one(ObjectId(session_id)) != None
    except:
        return False

def existed_art_id(c: MongoClient, art_id: str):
    db = c.trashart_db
    try:
        return db.arts.find_one(ObjectId(art_id)) != None
    except:
        return False

def existed_crafting_id(c: MongoClient, crafting_id: str):
    db = c.trashart_db
    try:
        return db.craftings.find_one(ObjectId(crafting_id)) != None
    except:
        return False
