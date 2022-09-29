import cv2
import numpy as np

class Trimmer:
    def __init__(self, img: np.ndarray):
        self.img = img

    @staticmethod
    def trim(img: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
        return img[y:y+h, x:x+w]

    def auto_trim(self) -> tuple[np.ndarray, int, int, int]:
        x1, y1, w1, h1 = self.__find_attention(self.img)
        img1 = self.trim(self.img, x1, y1, w1, h1)

        x2, y2, w2, h2 = self.__find_attention(img1)
        img2 = self.trim(img1, x2, y2, w2, h2)

        img3, x3, y3, one = self.__to_shape_img(img2)

        return img3, x1 + x2 + x3, y1 + y2 + y3, one

    def __find_attention(self, img: np.ndarray) -> tuple[int, int, int, int]:
        img_lighted = self.__adjust(img, 2.0, 1.0)
        img_gray = cv2.cvtColor(img_lighted, cv2.COLOR_BGR2GRAY)

        _, img_bin = cv2.threshold(img_gray, 0, 255, cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(
            img_bin, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        x, y, w, h = cv2.boundingRect(contours[0])

        return x, y, w, h

    def __to_shape_img(self, img: np.ndarray) -> tuple[np.ndarray, int, int, int]:
        size = img.shape
        x = 0
        y = 0
        length = 0

        if size[0] > size[1]:
            x = size[1] // 6
            y = size[0] // 2 - size[1] // 3
            length = 2 * size[1] // 3
        else:
            x = size[1] // 2 - size[0] // 3
            y = size[0] // 6
            length = 2 * size[0] // 3

        return self.trim(img, x, y, length, length), x, y, length

    def __adjust(self, img: np.ndarray, alpha: float=1.0, beta: float=0.0) -> np.ndarray:
        dst = alpha * img + beta
        return np.clip(dst, 0, 255).astype(np.uint8)
