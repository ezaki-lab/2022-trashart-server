import numpy as np
import cv2
from utils import average

class Similarity():
    def __init__(self):
        self.__bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        self.__detector = cv2.AKAZE_create()

    def calc_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        img1 = self.__scale_to_width(img1, 300)
        img2 = self.__scale_to_width(img2, 300)

        _, img1_des = self.__detector.detectAndCompute(img1, None)
        _, img2_des = self.__detector.detectAndCompute(img2, None)

        matches = self.__bf.knnMatch(img1_des, img2_des, k=2)
        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append([m])

        return average(good)

    def __scale_to_width(self, img: np.ndarray, width: int) -> np.ndarray:
        h, w = img.shape[:2]
        # TODO: 横, 縦 で正しくリサイズできるのかわからないので調べておく
        return cv2.resize(img, (width, int(h * width / w)))
