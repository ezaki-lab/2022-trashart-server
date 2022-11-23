import cv2
import numpy as np
from base64 import b64decode
import os
from common import config
from utils.image_color import ImageColorGuesser
from utils.random import generate_str

class Plastic:
    def __init__(self, p_name: str, possibility: float):
        self.name = p_name
        self.possibility = possibility

class PlasticSeparatorNext:
    plastic_names = ["PP", "PE"]

    color_name_map = {
        "white": 0,
        "gray": 1,
        "black": 2,
        "red": 3,
        "brown": 4,
        "yellow": 5,
        "green": 6,
        "blue": 7
    }

    def __init__(self, img_lighted_b64: str, img_led850_b64: str, img_led940_b64: str):
        self.results: list[Plastic] = [None] * len(self.plastic_names)
        self.model: any = config["PLASTIC_CLASSIFICATION_MODEL"]
        self.color: str = None

        # Base64形式の画像データをOpenCV画像データに変換
        try:
            self.img_lighted = self.__load_b64(img_lighted_b64)
            self.img_led850 = self.__load_b64(img_led850_b64)
            self.img_led940 = self.__load_b64(img_led940_b64)
        except:
            raise ValueError("These base64 image is not valid.")

        self.__crop_128()

    def separate(self):
        guesser = ImageColorGuesser(self.img_lighted)
        self.color = guesser.get_color()

        self.__predict()

    def to_json(self) -> dict:
        results = [None] * len(self.results)

        for i, r in enumerate(self.results):
            results[i] = {
                "name": r.name,
                "possibility": r.possibility
            }

        return {
            "results": results,
            "image": self.__save_img(self.img_lighted),
            "color": self.color
        }

    def __predict(self) -> np.ndarray:
        lum_850 = self.__calc_luminance(self.img_led850)
        lum_940 = self.__calc_luminance(self.img_led940)

        input_data = self.__format_for_predict(
            self.color,
            lum_850,
            lum_940
        )

        results = self.model.predict(input_data)[0]

        for i, name in enumerate(self.plastic_names):
            self.results[i] = Plastic(name, float(results[i]))

        self.results.sort(key=lambda x: x.possibility, reverse=True)

    def __format_for_predict(self, color: str, lum_850: np.ndarray, lum_940: np.ndarray) -> np.ndarray:
        color_no = self.color_name_map[color]

        info = np.concatenate([
            [color_no],
            lum_850,
            lum_940
        ])

        data = np.zeros((1,513), dtype=np.int32)
        data[0] = info

        return data

    def __crop_128(self):
        # 真ん中の128x128を切り取る
        size = 128

        self.img_lighted = self.__crop(self.img_lighted, size)
        self.img_led850 = self.__crop(self.img_led850, size)
        self.img_led940 = self.__crop(self.img_led940, size)

    def __crop(self, img: np.ndarray, size: int) -> np.ndarray:
        h, w = img.shape[:2]

        x = (w - size) // 2
        y = (h - size) // 2

        return img[y:y+size, x:x+size]

    def __load_b64(self, b64: str) -> np.ndarray:
        # Base64 -> OpenCV画像データ
        b64 = b64.split(",", 1)[1]

        return cv2.imdecode(
            np.frombuffer(
                b64decode(b64.encode()),
                np.uint8
            ),
            cv2.IMREAD_ANYCOLOR
        )

    def __calc_luminance(self, img: np.ndarray) -> np.ndarray:
        hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
        _,l,_ = cv2.split(hls)
        raveled = l.ravel()

        l_count = np.zeros(256, dtype=np.int32)
        for i in range(256):
            l_count[i] = raveled[raveled == i].shape[0]

        return l_count

    def __save_img(self, img: np.ndarray) -> np.ndarray:
        random_id = generate_str(8)
        save_folder = "storage/separates/"
        filepath = f"{save_folder}{random_id}.webp"

        # 保存フォルダーがなければ作成
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        cv2.imwrite(
            filepath,
            img
        )

        return os.path.join(config["API_URL"], filepath)
