from bson.objectid import ObjectId
from pymongo import MongoClient
import os
from common import config

class Data:
    def _database(self):
        return MongoClient(config["DATABASE_URL"])

    def _get_storage_url(self, path: str):
        return os.path.join(config["API_URL"], "storage", path)

    def _exists_user_id(self, user_id: str):
        with self._database() as c:
            db = c.trashart_db
            try:
                return db.users.find_one(ObjectId(user_id)) != None
            except:
                return False

    def _exists_session_id(self, session_id: str):
        with self._database() as c:
            db = c.trashart_db
            try:
                return db.sessions.find_one(ObjectId(session_id)) != None
            except:
                return False

    def _exists_art_id(self, art_id: str):
        with self._database() as c:
            db = c.trashart_db
            try:
                return db.arts.find_one(ObjectId(art_id)) != None
            except:
                return False

    def _exists_crafting_id(self, crafting_id: str):
        with self._database() as c:
            db = c.trashart_db
            try:
                return db.craftings.find_one(ObjectId(crafting_id)) != None
            except:
                return False
