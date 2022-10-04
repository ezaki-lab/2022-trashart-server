from bson.objectid import ObjectId
from models.data import Data

class Art(Data):
    def __init__(self, art_id: str=None):
        self.art_id: str = art_id
        self.name: str = None
        self.width: float = None
        self.height: float = None
        self.cap_area: float = None
        self.attentions_num: int = None
        self.hashtags: list[str] = []
        self.original_img_url: str = None
        self.support_img_url: str = None
        self.score: float = None

        if art_id != None:
            self.original_img_url = self._get_storage_url(f"arts/{self.art_id}/art.webp")
            self.support_img_url = self._get_storage_url(f"arts/{self.art_id}/art_support.webp")

            if not self._exists_art_id(art_id):
                raise FileNotFoundError("This art does not exist")
            self.__get()

    def to_json(self):
        return {
            "id": self.art_id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "cap_area": self.cap_area,
            "attentions_num": self.attentions_num,
            "hashtags": self.hashtags,
            "original_image_url": self.original_img_url,
            "support_image_url": self.support_img_url
        }

    def __get(self):
        with self._database() as c:
            db = c.trashart_db
            r = db.arts.find_one(ObjectId(self.art_id))

            self.name = r["name"] if "name" in r else ""
            self.width = r["width"] if "width" in r else ""
            self.height = r["height"] if "height" in r else ""
            self.cap_area = r["cap_area"] if "cap_area" in r else ""
            self.attentions_num = r["attentions_num"] if "attentions_num" in r else ""
            self.hashtags = r["hashtags"] if "hashtags" in r else ""

class Arts(Data):
    def __init__(self, random_choice_num: int=None):
        self.arts: list[dict] = []

        if random_choice_num == None:
            self.__get()
        else:
            self.__random_choice(random_choice_num)

    def to_json(self):
        return {
            "arts": self.arts
        }

    def __get(self):
        with self._database() as c:
            db = c.trashart_db
            self.__set_arts_from_cursor(
                db.arts.find()
            )

    def __random_choice(self, num: int):
        with self._database() as c:
            db = c.trashart_db
            self.__set_arts_from_cursor(
                db.arts.aggregate([{"$sample": {"size": num}}])
            )

    def __set_arts_from_cursor(self, c: any):
        for r in c:
            self.arts.append({
                "id": str(r["_id"]),
                "name": r["name"] if "name" in r else "",
                "width": r["width"] if "width" in r else "",
                "height": r["height"] if "height" in r else "",
                "cap_area": r["cap_area"] if "cap_area" in r else "",
                "attentions_num": r["attentions_num"] if "attentions_num" in r else "",
                "hashtags": r["hashtags"] if "hashtags" in r else "",
                "original_image_url": self._get_storage_url(f"arts/{str(r['_id'])}/art.webp"),
                "support_image_url": self._get_storage_url(f"arts/{str(r['_id'])}/art_support.webp")
            })

    @staticmethod
    def parse_dict_list(arts: list) -> list[dict]:
        lis = [None] * len(arts)
        for i, art in enumerate(arts):
            lis[i] = {
                "id": art.art_id,
                "name": art.name,
                "width": art.width,
                "height": art.height,
                "cap_area": art.cap_area,
                "attentions_num": art.attentions_num,
                "original_image_url": art.original_img_url,
                "support_image_url": art.support_img_url,
                "score": art.score
            }

        return lis
