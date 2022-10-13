import cv2
import numpy as np

import os
import math
from concurrent.futures import ThreadPoolExecutor

from models.data import Data
from models.art import Art
from utils.image_white_counter import ImageWhiteCounter
from utils.similarity import Similarity

class ArtSuggester(Data):
    cap_size: float = (14 ** 2) * math.pi

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
                    e.submit(self.__calc_score, attentions, art.cap_area)
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

    def __calc_score(self, attentions: list[np.ndarray], art_cap_area: float) -> float:
        score = 0.0
        picked_cap_area = 3000.0

        for img in self.materials:
            for att in attentions:
                area_diff = self.__diff_area(att, art_cap_area, img, picked_cap_area)

                # 大きさが全然違う場合は、このループのスコアを0に (ループスキップ)
                if math.sqrt(area_diff) >= 50:
                    continue

                try:
                    score += self.__calc_sole_score(img, att)
                except:
                    continue

        return score

    def __diff_area(self, att_img: np.ndarray, att_cap_area: float, material_img: np.ndarray, picked_cap_area: float) -> float:
        try:
            return math.fabs(
                ImageWhiteCounter(material_img).get_sum() / picked_cap_area
                - ImageWhiteCounter(att_img).get_sum() / att_cap_area
            ) * self.cap_size
        except:
            return 10000.0

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
