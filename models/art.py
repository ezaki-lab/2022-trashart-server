import cv2
import numpy as np
from bson.objectid import ObjectId

import os
import math
from concurrent.futures import ThreadPoolExecutor

from models.data import Data
from utils.similarity import Similarity

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

class ArtSuggester(Data):
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.arts: list[Art] = []
        self.art_attentions: dict = {}
        self.materials: list = []
        self.scores: dict = {}
        self.__similarity = Similarity()

        if not self._exists_session_id(session_id):
            raise FileNotFoundError("This session does not exist")

        if not os.path.exists("storage/materials/" + session_id):
            raise FileNotFoundError("This session does not have materials")

    def suggest(self, num: int = 10) -> list[Art]:
        # 素材画像をセット
        self.__set_material_imgs()
        # 作品IDリストを取得
        art_ids = self.__get_art_ids()
        # 全ての作品情報をセット
        self.__set_arts(art_ids)
        # 各作品のスコアを計算
        self.__set_art_scores()
        # スコアが高い順に並ぶようにソート
        self.arts.sort(key=lambda art: art.score, reverse=True)
        # 指定した分だけ返す
        return self.arts[:num]

    def __set_material_imgs(self):
        self.materials = self.__load_images(
            self.__get_materials_path(),
            "storage/materials/" + self.session_id
        )

    def __set_arts(self, art_ids: list[str]):
        for art_id in art_ids:
            self.arts.append(Art(art_id))

    def __set_art_scores(self):
        with ThreadPoolExecutor(max_workers=5, thread_name_prefix="calc_scores") as e:
            futures = []

            for art in self.arts:
                attentions = self.__load_images(
                    self.__get_art_attentions_path(art.art_id),
                    "storage/arts/{}/attentions".format(art.art_id)
                )
                futures.append(
                    e.submit(self.__calc_score, attentions)
                )

            for i, f in enumerate(futures):
                self.arts[i].score = f.result()

    def __get_materials_path(self) -> list[str]:
        return os.listdir("storage/materials/" + self.session_id)

    def __load_images(self, paths: list[str], directory: str = None) -> list[np.ndarray]:
        if directory == None:
            return list(map(lambda p: cv2.imread(p), paths))

        return list(map(lambda p: cv2.imread(os.path.join(directory, p)), paths))

    def __get_art_ids(self) -> list[str]:
        with self._database() as c:
            db = c.trashart_db
            return list(map(lambda r: str(r["_id"]), db.arts.find()))

    def __get_art_attentions_path(self, art_id: int) -> list[str]:
        return os.listdir("storage/arts/{}/attentions".format(art_id))

    def __calc_score(self, attentions: list[np.ndarray]) -> float:
        score = 0.0
        for img in self.materials:
            for att in attentions:
                try:
                    score += self.__calc_sole_score(img, att)
                except:
                    continue

        return score

    def __calc_sole_score(self, img: np.ndarray, att: np.ndarray) -> float:
        sim = self.__similarity.calc(img, att)

        if sim == 0:
            raise ValueError("similarity is 0, maybe images are same or feature points are not completely similar")

        if sim > 100:
            return 0

        # 基準化する式 (simが0に近づくほどスコアが高くなり、100に近づくほどスコアが低くなる)
        #   a = sim
        #   100 : π/2 = a : a'
        #   a' = aπ / 200
        #   y = max(-tan(a' - π/2), 0)
        #   y = max(cot(a'), 0)
        #   y = max(cot(aπ / 200), 0)
        #   y = max(1 / tan(aπ / 200), 0)
        return max(1 / math.tan(sim * math.pi / 200), 0.0)
