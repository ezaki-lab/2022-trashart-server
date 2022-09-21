from bson.objectid import ObjectId
from datetime import datetime
from models.data import Data
from utils.random import generate_str
from utils.base64_to_file import Base64_to_file

class Crafting(Data):
    def __init__(self, crafting_id: str=None):
        self.crafting_id: str = crafting_id
        self.user_id: str = None
        self.title: str = None
        self.hashtags: list[str] = []
        self.image_url: str = None
        self.created_at = None

        if crafting_id != None:
            if not self._exists_crafting_id(crafting_id):
                raise FileNotFoundError("This crafting does not exist")
            self.__get()

    def post(self, user_id: str, title: str, hashtags: list[str], img_b64: str):
        if not self._exists_user_id(user_id):
            raise FileNotFoundError("This user does not exist")

        self.crafting_id = generate_str(24, hex_only=True)
        self.user_id = user_id
        self.title = title
        self.hashtags = hashtags
        self.created_at = datetime.now()

        self.__save_img(img_b64)
        self.image_url = self._get_storage_url(f"craftings/{self.crafting_id}.png")

        with self._database() as c:
            db = c.trashart_db

            db.craftings.insert_one({
                "user_id": ObjectId(self.user_id),
                "title": self.title,
                "hashtags": self.hashtags,
                "image_url": self.image_url,
                "created_at": self.created_at
            })

    def __get(self):
        with self._database() as c:
            db = c.trashart_db
            r = db.craftings.find_one(ObjectId(self.crafting_id))

            self.user_id = str(r["user_id"]) if "user_id" in r else ""
            self.title = r["title"] if "title" in r else ""
            self.hashtags = r["hashtags"] if "hashtags" in r else []
            self.image_url = r["image_url"] if "image_url" in r else ""
            self.created_at = r["created_at"] if "created_at" in r else ""

    def __save_img(self, img_b64: str) -> str:
        converter = Base64_to_file(img_b64)
        return converter.save("storage/craftings/", f"{self.crafting_id}.png")

class Craftings(Data):
    def __init__(self):
        self.craftings: list[dict] = []

        self.__get()

    def __get(self):
        with self._database() as c:
            db = c.trashart_db

            for r in db.craftings.find():
                self.craftings.append({
                    "id": str(r["_id"]),
                    "user_id": str(r["user_id"]) if "user_id" in r else "",
                    "title": r["title"] if "title" in r else "",
                    "hashtags": r["hashtags"] if "hashtags" in r else [],
                    "image_url": r["image_url"] if "image_url" in r else ""
                })
