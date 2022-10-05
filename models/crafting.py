from bson.objectid import ObjectId
from datetime import datetime
import shutil
from models.data import Data
from utils.random import generate_str

class Crafting(Data):
    def __init__(self, crafting_id: str=None):
        self.crafting_id: str = crafting_id
        self.user_id: str = None
        self.title: str = None
        self.hashtags: list[str] = []
        self.image_url: str = None
        self.created_at: datetime = None

        if crafting_id != None:
            if not self._exists_crafting_id(crafting_id):
                raise FileNotFoundError("This crafting does not exist")
            self.__get()

    def post(self, user_id: str, title: str, hashtags: list[str], image_id: str):
        if not self._exists_user_id(user_id):
            raise FileNotFoundError("This user does not exist")

        self.crafting_id = generate_str(24, hex_only=True)
        self.image_id = image_id
        self.user_id = user_id
        self.title = title
        self.hashtags = hashtags
        self.created_at = datetime.now()

        try:
            self.__copy_img()
            self.__link_img()
        except:
            raise FileNotFoundError("This image does not exist")

        with self._database() as c:
            db = c.trashart_db

            db.craftings.insert_one({
                "user_id": ObjectId(self.user_id),
                "title": self.title,
                "hashtags": self.hashtags,
                "image_url": self.image_url,
                "created_at": self.created_at
            })

    def to_json(self):
        return {
            "id": self.crafting_id,
            "user_id": self.user_id,
            "title": self.title,
            "hashtags": self.hashtags,
            "image_url": self.image_url,
            "create_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __get(self):
        with self._database() as c:
            db = c.trashart_db
            r = db.craftings.find_one(ObjectId(self.crafting_id))

            self.title = r["title"] if "title" in r else ""
            self.hashtags = r["hashtags"] if "hashtags" in r else []
            self.image_url = r["image_url"] if "image_url" in r else ""
            self.created_at = r["created_at"] if "created_at" in r else None

    def __copy_img(self) -> str:
        shutil.copyfile(f"storage/photos/{self.image_id}.png", f"storage/craftings/{self.crafting_id}.png")
        self.image_url = self._get_storage_url(f"craftings/{self.crafting_id}.png")

    def __link_img(self) -> str:
        with self._database() as c:
            db = c.trashart_db
            db.photos.update_one(
                {"_id": ObjectId(self.image_id)},
                {"$set": {"crafting_id": ObjectId(self.crafting_id)}}
            )

class Craftings(Data):
    def __init__(self, user_id: str=None):
        self.craftings: list[dict] = []

        if user_id != None:
            if not self._exists_user_id(user_id):
                raise FileNotFoundError("This user does not exist")

        self.__get(user_id)

    def to_json(self):
        return {
            "craftings": self.craftings
        }

    def __get(self, user_id: str=None):
        with self._database() as c:
            db = c.trashart_db

            rows = None
            if user_id == None:
                rows = db.craftings.find()
            else:
                rows = db.craftings.find({"user_id": ObjectId(user_id)})

            for r in rows:
                created_at = ""
                if "created_at" in r:
                    created_at = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")

                self.craftings.append({
                    "id": str(r["_id"]),
                    "user_id": str(r["user_id"]) if "user_id" in r else "",
                    "title": r["title"] if "title" in r else "",
                    "hashtags": r["hashtags"] if "hashtags" in r else [],
                    "image_url": r["image_url"] if "image_url" in r else "",
                    "created_at": created_at
                })
