import cv2
import numpy as np
from bson.objectid import ObjectId
from pymongo import MongoClient

import os
import math
from concurrent.futures import ThreadPoolExecutor

from common import config
from utils.similarity import Similarity

class Art:
    def __init__(
        self, art_id: str, name: str,
        width: int, height: int,
        cap_area: float, attentions_num: int,
        original_img_url: str, support_img_url: str
    ):
        self.id: str = art_id
        self.name: str = name
        self.width: float = width
        self.height: float = height
        self.cap_area: float = cap_area
        self.attentions_num: int = attentions_num
        self.original_img_url: str = original_img_url
        self.support_img_url: str = support_img_url
        self.score: float = -1

    @staticmethod
    def parse_dict_list(arts: list) -> list[dict]:
        lis = [None] * len(arts)
        for i, art in enumerate(arts):
            lis[i] = {
                "id": art.id,
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

class ArtSuggester:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.arts: list[Art] = []
        self.art_attentions: dict = {}
        self.materials: list = []
        self.scores: dict = {}
        self.__similarity = Similarity()

    def suggest(self, num: int = 10) -> list[Art]:
        # 素材画像をセット
        self.__set_material_imgs()
        # 作品IDリストを取得
        art_ids = self.__get_art_ids()
        # 全ての作品情報をセット
        self.__set_art_infos(art_ids)
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

    def __set_art_infos(self, art_ids: list[str]):
        for art_id in art_ids:
            row = {}
            try:
                row = self.__get_art_data(art_id)
            except:
                continue

            original_img_url = os.path.join(config["API_URL"], "storage/arts/{}/art.webp".format(art_id))
            support_img_url = os.path.join(config["API_URL"], "storage/arts/{}/art_support.webp".format(art_id))

            self.arts += [Art(
                art_id,
                row["name"],
                row["width"],
                row["height"],
                row["cap_area"],
                row["attentions_num"],
                original_img_url,
                support_img_url,
            )]

    def __set_art_scores(self):
        with ThreadPoolExecutor(max_workers=5, thread_name_prefix="calc_scores") as e:
            futures = []

            for art in self.arts:
                attentions = self.__load_images(
                    self.__get_art_attentions_path(art.id),
                    "storage/arts/{}/attentions".format(art.id)
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
        return [f for f in os.listdir("storage/arts")]

    def __get_art_attentions_path(self, art_id: int) -> list[str]:
        return os.listdir("storage/arts/{}/attentions".format(art_id))

    def __get_art_data(self, art_id: str) -> dict:
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            data = db.arts.find_one(ObjectId(art_id))

            if data == None:
                raise Exception("art data not found")

            return data

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
