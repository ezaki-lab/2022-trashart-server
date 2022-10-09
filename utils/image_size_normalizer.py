import cv2
import numpy as np

class ImageSizeNormalizer:
    def __init__(self, img: np.ndarray, size: int):
        self.img = img
        self.h, self.w = img.shape[:2]
        self.size = size
        self.ratio: float = None

        if self.h > self.w:
            self.__scale_to_height()
        else:
            self.__scale_to_width()

    def __scale_to_height(self):
        self.ratio = self.size / self.h
        self.img = cv2.resize(
            self.img,
            (int(self.w * self.ratio), self.size)
        )

    def __scale_to_width(self):
        self.ratio = self.size / self.w
        self.img = cv2.resize(
            self.img,
            (self.size, int(self.h * self.ratio))
        )
