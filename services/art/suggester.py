import cv2
import numpy as np
from bson.objectid import ObjectId

import os
import math
from concurrent.futures import ThreadPoolExecutor

from models.data import Data
from models.art import Art
from utils.image_white_counter import ImageWhiteCounter
from utils.listdir_relative import listdir_relative
from utils.possibility import Possibility
from utils.similarity import Similarity

class AttentionInfo(Data):
    def __init__(self, attention_id: str):
        self.attention_id: str = attention_id
        self.x: int = None
        self.y: int = None
        self.width: int = None
        self.height: int = None
        self.most_similar_material_id: str = None
        self.__get()

    def __get(self):
        with self._database() as c:
            db = c.trashart_db
            r = db.attentions.find_one(ObjectId(self.attention_id))
            self.x = r["x"] if "x" in r else ""
            self.y = r["y"] if "y" in r else ""
            self.width = r["width"] if "width" in r else ""
            self.height = r["height"] if "height" in r else ""

class ArtSuggester(Data):
    cap_size: float = (14 ** 2) * math.pi

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.arts: list[Art] = []
        self.art_attentions: dict[str, dict[str, AttentionInfo]] = {}
        self.materials: list = []
        self.material_ids: list = []
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
        paths = self.__get_materials_path()
        self.materials = self.__load_images(paths)
        self.material_ids = list(map(self.__get_id_from_path, paths))

    def __set_arts(self, art_ids: list[str]):
        for art_id in art_ids:
            self.arts.append(Art(art_id))

    def __set_art_scores(self):
        with ThreadPoolExecutor(max_workers=5, thread_name_prefix="calc_scores") as e:
            futures = []

            for art in self.arts:
                attentions_paths = self.__get_art_attentions_path(art.art_id)
                attentions = self.__load_images(attentions_paths)
                attention_ids = list(map(self.__get_id_from_path, attentions_paths))
                self.__set_art_attentions(art.art_id, attention_ids)

                futures.append(
                    e.submit(self.__calc_score, art.art_id, attention_ids, attentions, art.cap_area)
                )

            for i, f in enumerate(futures):
                self.arts[i].score = f.result()

    def __get_materials_path(self) -> list[str]:
        folder = "storage/materials/{}".format(self.session_id)
        return listdir_relative(folder)

    def __set_art_attentions(self, art_id: str, attention_ids: list[str]):
        self.art_attentions[art_id] = {}

        for att_id in attention_ids:
            self.art_attentions[art_id][att_id] = AttentionInfo(att_id)

    def __load_images(self, paths: list[str], directory: str = None) -> list[np.ndarray]:
        if directory == None:
            return list(map(lambda p: cv2.imread(p), paths))

        return list(map(lambda p: cv2.imread(os.path.join(directory, p)), paths))

    def __get_art_ids(self) -> list[str]:
        with self._database() as c:
            db = c.trashart_db
            return list(map(lambda r: str(r["_id"]), db.arts.find()))

    def __get_art_attentions_path(self, art_id: int) -> list[str]:
        folder = "storage/arts/{}/attentions".format(art_id)
        return listdir_relative(folder)

    def __get_id_from_path(self, path: str) -> str:
        return os.path.splitext(os.path.basename(path))[0]

    def __calc_score(self, art_id: str, att_ids: list[str], atts: list[np.ndarray], art_cap_area: float) -> float:
        score = 0.0
        picked_cap_area = 3000.0

        for i, att in enumerate(atts):
            material_scores: list[Possibility] = []

            for j, img in enumerate(self.materials):
                area_diff = self.__diff_area(att, art_cap_area, img, picked_cap_area)

                # 大きさが全然違う場合は、このループのスコアを0に (ループスキップ)
                if math.sqrt(area_diff) >= 50:
                    continue

                try:
                    sole_score = self.__calc_sole_score(att, img)
                    score += sole_score
                    material_scores.append(Possibility(
                        self.material_ids[j],
                        sole_score
                    ))
                except:
                    continue

            material_scores.sort(key=lambda material: material.possibility, reverse=True)
            self.art_attentions[art_id][att_ids[i]].most_similar_material_id = material_scores[0].name

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
