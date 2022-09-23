from bson.objectid import ObjectId
from datetime import datetime
from models.crafting import Craftings
from models.data import Data
from utils.random import generate_str

class User(Data):
    def __init__(self, user_id: str=None):
        self.user_id: str = user_id
        self.register_at: datetime = None
        self.craftings: list[dict] = []

        if user_id != None:
            if not self._exists_user_id(user_id):
                raise FileNotFoundError("This user does not exist")
            self.__get()

    def post(self):
        self.user_id = generate_str(24, hex_only=True)
        self.register_at = datetime.now()

        with self._database() as c:
            db = c.trashart_db

            db.users.insert_one({
                "_id": ObjectId(self.user_id),
                "register_at": self.register_at.strftime("%Y-%m-%d %H:%M:%S")
            })

    def to_json(self):
        return {
            "id": self.user_id,
            "register_at": self.register_at.strftime("%Y-%m-%d %H:%M:%S"),
            "craftings": self.craftings,
            "crafting_num": len(self.craftings)
        }

    def __get(self):
        with self._database() as c:
            db = c.trashart_db
            r = db.users.find_one(ObjectId(self.user_id))

            self.register_at = r["register_at"].strftime("%Y-%m-%d %H:%M:%S") if "register_at" in r else ""

        self.craftings = Craftings(self.user_id).craftings

class Users(Data):
    def __init__(self):
        self.users: list[dict] = []

        self.__get()

    def to_json(self):
        return {
            "users": self.users
        }

    def __get(self):
        with self._database() as c:
            db = c.trashart_db

            for r in db.users.find():
                self.users.append({
                    "id": str(r["_id"]),
                    "register_at": r["register_at"].strftime("%Y-%m-%d %H:%M:%S") if "register_at" in r else "",
                })
