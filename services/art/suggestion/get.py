import cv2
import numpy as np
from bson.objectid import ObjectId
from pymongo import MongoClient

import os
import math

from common import config
from utils.similarity import Similarity

class Art:
    def __init__(
        self, score: float, art_id: str, name: str,
        width: int, height: int,
        cap_area: float, attentions_num: int,
        original_img_url: str, support_img_url: str
    ):
        self.score: float = score,
        self.id: str = art_id,
        self.name: str = name,
        self.width: float = width,
        self.height: float = height,
        self.cap_area: float = cap_area,
        self.attentions_num: int = attentions_num,
        self.original_image_url: str = original_img_url,
        self.support_image_url: str = support_img_url

class ArtSuggester:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.arts: list[Art] = []
        self.art_attentions: dict = {}
        self.materials: list = []
        self.scores: dict = {}
        self.__similarity = Similarity()

    def suggest(self, num: int = 10) -> list[Art]:
        self.materials = self.__load_images(self.__get_materials_path())

        for art_id in self.__get_art_ids():
            row = {}
            try:
                row = self.__get_art_data(art_id)
            except Exception as e:
                continue

            attentions = self.__load_images(self.__get_art_attentions_path(art_id))

            self.arts += Art(
                self.__calc_score(attentions),
                art_id,
                row["name"],
                row["width"],
                row["height"],
                row["cap_area"],
                row["attentions_num"],
                row["original_image_url"],
                row["support_image_url"]
            )

        self.arts.sort(key=lambda art: art.score, reverse=True)

        return self.arts[:num]

    def __get_materials_path(self) -> list[str]:
        return os.listdir("storage/materials/" + self.session_id)

    def __load_images(self, paths: list[str]) -> list[np.ndarray]:
        return list(map(lambda p: cv2.imread(p), paths))

    def __get_art_ids(self) -> list[str]:
        return [f for f in os.listdir("storage/arts") if os.path.isdir(f)]

    def __get_art_attentions_path(self, art_id: int) -> list[str]:
        return os.listdir("storage/arts/{}/art_attentions".format(art_id))

    def __get_art_data(self, art_id: str) -> dict:
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            data = db.arts.find_one(ObjectId(art_id))

            if data == None:
                raise Exception("art data not found")

    def __calc_score(self, attentions: list[np.ndarray]) -> float:
        score = 0.0
        for img in self.materials:
            for att in attentions:
                try:
                    score += self.__calc_sole_score(img, att)
                except Exception as e:
                    continue

        return score

    def __calc_sole_score(self, img: np.ndarray, att: np.ndarray) -> float:
        sim = self.__similarity.calc(img, att)

        if sim == 0:
            raise ValueError("similarity is 0, maybe images are same")

        # 基準化する式 (simが0に近づくほどスコアが高くなり、100に近づくほどスコアが低くなる)
        #   a = sim
        #   100 : π/2 = a : a'
        #   a' = aπ / 200
        #   y = max(-tan(a' - π/2), 0)
        #   y = max(cot(a'), 0)
        #   y = max(cot(aπ / 200), 0)
        #   y = max(1 / tan(aπ / 200), 0)
        return max(1 / math.tan(sim * math.pi / 200), 0.0)
