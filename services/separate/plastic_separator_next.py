import cv2
import numpy as np
from base64 import b64decode
import os
from common import config
from utils.random import generate_str

class Plastic:
    def __init__(self, p_name: str, possibility: float):
        self.name = p_name
        self.possibility = possibility

class PlasticSeparatorNext:
    plastic_names = ["PP", "PE", "PET", "PS", "ABS", "PVC"]

    def __init__(self, img_white_b64: str, img_850_b64: str, img_940_b64: str, start_x: int, start_y: int, width: int, height: int, img_size: int):
        self.results: list[Plastic] = []
        self.model: any = config["PLASTIC_CLASSIFICATION_NEXT_MODEL"]
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.img_size = img_size

        # Base64形式の画像データをOpenCV画像データに変換
        try:
            self.img_white = self.__load_b64(img_white_b64)
            self.img_850 = self.__load_b64(img_850_b64)
            self.img_940 = self.__load_b64(img_940_b64)
        except:
            raise ValueError("These base64 image is not valid.")

        self.imgs_white = self.__cut_image(self.img_white)
        self.imgs_850 = self.__cut_image(self.img_850)
        self.imgs_940 = self.__cut_image(self.img_940)

        self.cut_num = len(self.imgs_white)

        if self.cut_num != len(self.imgs_850) or self.cut_num != len(self.imgs_940):
            raise ValueError("These base64 image is not valid for separate.")

    def separate(self):
        self.results: list[Plastic] = []

        predicts = np.argmax(self.__predict(), axis=1)

        u, counts = np.unique(predicts, return_counts=True, axis=0)

        sorted_indices = np.argsort(counts)[::-1]
        sorted_results = u[sorted_indices]

        counts = np.sort(counts)[::-1]

        for i, p_no in enumerate(sorted_results):
            self.results.append(
                Plastic(self.plastic_names[p_no], counts[i] / self.cut_num)
            )

    def to_json(self) -> dict:
        results = [None] * len(self.results)

        for i, r in enumerate(self.results):
            results[i] = {
                "name": r.name,
                "possibility": r.possibility
            }

        self.__save_img(self.img_white)
        cropped_img = self.img_white[self.start_y:self.start_y+self.height, self.start_x:self.start_x+self.width]

        return {
            "results": results,
            "image": self.__save_img(cropped_img),
        }

    def __predict(self) -> int:
        input_data = np.zeros((self.cut_num, 768), dtype=np.int32)

        for i in range(self.cut_num):
            input_data[i] = self.__format_for_predict(
                self.__calc_hue(i),
                self.__calc_luminance(i)
            )

        return self.model.predict(input_data)

    def __format_for_predict(self, hue: np.ndarray, lum: np.ndarray) -> np.ndarray:
        info = np.concatenate([
            hue,
            lum
        ])

        data = np.zeros((1,768), dtype=np.int32)
        data[0] = info

        return data

    def __cut_image(self, img: np.ndarray) -> list:
        img = img[self.start_y:self.start_y+self.height, self.start_x:self.start_x+self.width]

        # 各グリッド数
        w_num = img.shape[1] // self.img_size
        h_num = img.shape[0] // self.img_size

        imgs: list[np.ndarray] = [None] * (w_num * h_num)

        for i in range(w_num):
            for j in range(h_num):
                crop_start_x = i * self.img_size
                crop_start_y = j * self.img_size

                imgs[i * h_num + j] = img[crop_start_y:crop_start_y+self.img_size, crop_start_x:crop_start_x+self.img_size]

        return imgs

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

    def __calc_hue(self, index: int) -> np.ndarray:
        """
        画像の色相ヒストグラムを計算する
        """

        h,l,s = self.__calc_hls(self.imgs_white[index])
        raveled = h.ravel()
        return self.__get_histogram_array(raveled, 255)

    def __calc_luminance(self, index: int) -> np.ndarray:
        """
        画像の輝度ヒストグラムを計算する (850nm, 940nm)
        """

        # 850nm
        h,l,s = self.__calc_hls(self.imgs_850[index])
        raveled = l.ravel()
        led850_count = self.__get_histogram_array(raveled, 255)

        # 940nm
        h,l,s = self.__calc_hls(self.imgs_940[index])
        raveled = l.ravel()
        led940_count = self.__get_histogram_array(raveled, 255)

        return np.concatenate([led850_count, led940_count])

    def __calc_hls(self, img: np.ndarray) -> tuple:
        """
        画像の色相、輝度、彩度を計算する
        """

        hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
        return cv2.split(hls)

    def __get_histogram_array(self, arr: np.ndarray, max_num: int) -> np.ndarray:
        """
        ヒストグラムの各値を計算する
        """

        hist = np.zeros(max_num + 1, dtype=np.int32)

        for i in range(max_num + 1):
            hist[i] = arr[arr == i].shape[0]

        return hist

    def __save_img(self, img: np.ndarray) -> np.ndarray:
        random_id = generate_str(8)
        save_folder = "storage/photos/"
        filepath = f"{save_folder}{random_id}.webp"

        # 保存フォルダーがなければ作成
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        cv2.imwrite(
            filepath,
            img
        )

        return os.path.join(config["API_URL"], filepath)
