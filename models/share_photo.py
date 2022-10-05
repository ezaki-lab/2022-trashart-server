from bson.objectid import ObjectId
from datetime import datetime
from models.data import Data
from utils.random import generate_str
from utils.base64_to_file import Base64_to_file

class SharePhoto(Data):
    def __init__(self, photo_id: str=None):
        self.photo_id: str = photo_id
        self.crafting_id: str = None

        if photo_id != None:
            if not self._exists_photo_id(photo_id):
                raise FileNotFoundError("This photo does not exist")
            self.__get()

    def post(self, img_b64: str):
        self.photo_id = generate_str(24, hex_only=True)
        self.created_at = datetime.now()

        self.__save_img(img_b64)
        self.image_url = self._get_storage_url(f"photos/{self.photo_id}.png")

        with self._database() as c:
            db = c.trashart_db

            db.photos.insert_one({
                "_id": ObjectId(self.photo_id),
                "created_at": self.created_at
            })

    def to_json(self):
        return {
            "id": self.photo_id,
            "crafting_id": self.crafting_id
        }

    def __get(self):
        with self._database() as c:
            db = c.trashart_db
            r = db.photos.find_one(ObjectId(self.photo_id))

            self.crafting_id = str(r["crafting_id"]) if "crafting_id" in r else ""

    def __save_img(self, img_b64: str) -> str:
        converter = Base64_to_file(img_b64)
        return converter.save("storage/photos/", f"{self.photo_id}.png")
