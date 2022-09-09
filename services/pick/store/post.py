import cv2
import numpy as np

import os
from base64 import b64decode

from common import config
from utils.random import generate_str

class Material:
    def __init__(self, index: int, area: float, x: int, y: int, width: int, height: int):
        self.index: int = index
        self.id = generate_str(8, hex_only=True)
        self.area: float = area
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height

class MaterialSeparator:
    def __init__(self, b64_str: str, session_id: str):
        b64_splitted: list[str] = b64_str.split(",", 1)
        self.session_id = session_id

        # データ部
        self.data: str = b64_splitted[1]
        self.original_img: np.ndarray = np.array([])
        self.width: int = -1
        self.height: int = -1
        self.materials: list[Material] = []

    def load_b64(self):
        # Base64 -> OpenCV画像データ
        self.original_img = cv2.imdecode(
            np.frombuffer(
                b64decode(self.data.encode()),
                np.uint8
            ),
            cv2.IMREAD_ANYCOLOR
        )

        # 縦幅が 1000 になるようにリサイズ
        self.original_img = self.__scale_to_height(
            self.original_img, 1000
        )

        self.height, self.width = self.original_img.shape[:2]

    def separate(self):
        if self.original_img.shape[0] == 0:
            raise ValueError("image is not loaded")

        # ノイズを削除して二値化したものを、RGB色空間に変換
        dst = cv2.cvtColor(
            self.__remove_noise_to_bin(self.original_img),
            cv2.COLOR_GRAY2RGB
        )

        # 輪郭抽出
        contours = self.__find_contours(dst)

        # 輪郭から素材を切り出す
        self.__store_from_contours(contours)

    def get_materials_info(self) -> list:
        return list(map(lambda m: {
            "id": m.id,
            "area": m.area,
            "image_url": os.path.join(config["API_URL"], "storage/materials/{}/{}.webp".format(self.session_id, m.id))
        }, self.materials))

    def __remove_noise_to_bin(self, img: np.ndarray) -> np.ndarray:
        # ノイズ除去
        dst = cv2.fastNlMeansDenoising(img, h=20)
        dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

        block_size = self.width * self.height * 31 // 500000
        if block_size % 2 == 0:
            block_size += 1

        # 影を除去し、輪郭を黒、背景を白に
        return cv2.adaptiveThreshold(
            dst,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            2
        )

    def __find_contours(self, img: np.ndarray) -> list[np.ndarray]:
        dst = cv2.cvtColor(img, cv2.COLOR_RGB2HSV_FULL)

        # 色範囲によるマスク生成
        dst_mask = cv2.inRange(dst, np.array([0, 0, 0]), np.array([10, 10, 10]))

        # 輪郭抽出
        contours, hierarchy = cv2.findContours(
            dst_mask, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # 小さい輪郭は誤検出として削除
        min_area = self.width * self.height / 1000
        return list(filter(lambda x: cv2.contourArea(x) > min_area, contours))

    def __store_from_contours(self, contours: list[np.ndarray]):
        # 輪郭から素材を切り出す
        for i, cnt in enumerate(contours):
            x, y, width, height = cv2.boundingRect(cnt)
            self.materials.append(Material(
                i,
                cv2.contourArea(cnt),
                x,
                y,
                width,
                height,
            ))

        # 面積が大きい順にソート
        self.materials.sort(key=lambda item: item.area, reverse=True)

        # 保存フォルダーがなければ作成
        save_folder = "storage/materials/{}".format(self.session_id)
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # 素材画像を保存
        for i, m in enumerate(self.materials):
            filepath = "{}/{}.webp".format(save_folder, m.id)
            img = self.original_img[
                m.y:m.y+m.height,
                m.x:m.x+m.width
            ]
            cv2.imwrite(filepath, img)

    def __scale_to_height(self, img: np.ndarray, height: int) -> np.ndarray:
        h, w = img.shape[:2]
        # TODO: 横, 縦 で正しくリサイズできるのかわからないので調べておく
        return cv2.resize(img, (int(w * height / h), height))
