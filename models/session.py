from bson.objectid import ObjectId
from datetime import datetime
from models.data import Data
from utils.random import generate_str

class Session(Data):
    def __init__(self, session_id: str=None):
        self.session_id: str = session_id
        self.start_at: datetime = None

        if session_id != None:
            if not self._exists_session_id(session_id):
                raise FileNotFoundError("This session does not exist")
            self.__get()

    def post(self):
        self.session_id = generate_str(24, hex_only=True)
        self.start_at = datetime.now()

        with self._database() as c:
            db = c.trashart_db

            db.sessions.insert_one({
                "_id": ObjectId(self.session_id),
                "start_at": self.start_at.strftime("%Y-%m-%d %H:%M:%S")
            })

    def to_json(self):
        return {
            "id": self.session_id,
            "start_at": self.start_at
        }

    def __get(self):
        with self._database() as c:
            db = c.trashart_db
            r = db.sessions.find_one(ObjectId(self.session_id))

            self.start_at = r["start_at"].strftime("%Y-%m-%d %H:%M:%S") if "start_at" in r else None

class Sessions(Data):
    def __init__(self):
        self.sessions: list[dict] = []

        self.__get()

    def to_json(self):
        return {
            "sessions": self.sessions
        }

    def __get(self):
        with self._database() as c:
            db = c.trashart_db

            for r in db.sessions.find():
                self.sessions.append({
                    "id": str(r["_id"]),
                    "start_at": r["start_at"].strftime("%Y-%m-%d %H:%M:%S") if "start_at" in r else "",
                })
