import cv2
import numpy as np

class ColorArea:
    def __init__(self, c_name: str, area: int):
        self.name = c_name
        self.area = area

class ImageColorGuesser:
    color_range = {
        "white": [
            np.array([0, 0, 0]),
            np.array([179, 30, 255])
        ],
        "gray": [
            np.array([0, 0, 97]),
            np.array([0, 58, 192])
        ],
        "black": [
            np.array([0, 0, 0]),
            np.array([44, 255, 107])
        ],
        "red.1": [
            np.array([0, 120, 0]),
            np.array([10, 255, 255])
        ],
        "red.2": [
            np.array([160, 0, 0]),
            np.array([179, 255, 255])
        ],
        "brown": [
            np.array([4, 0, 0]),
            np.array([10, 255, 255])
        ],
        "yellow": [
            np.array([15, 0, 0]),
            np.array([30, 255, 255])
        ],
        "green": [
            np.array([30, 0, 0]),
            np.array([90, 255, 255])
        ],
        "blue": [
            np.array([88, 0, 0]),
            np.array([132, 255, 255])
        ]
    }

    def __init__(self, img: np.ndarray):
        self.img = img

    # 白・灰・黒・赤・茶・黄・緑・青のどの色に近いかを返す
    def get_color(self) -> str:
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        color_info = [None] * len(self.color_range)

        for i, colors in enumerate(self.color_range.items()):
            c_name, c_range = colors
            mask = cv2.inRange(hsv, c_range[0], c_range[1])
            color_info[i] = ColorArea(c_name, int(mask.sum()))

        color_info.sort(key=lambda x: x.area, reverse=True)

        return self.__remove_color_tag(
            color_info[0].name
        )

    def __remove_color_tag(self, name: str) -> str:
        return name.split(".")[0]
