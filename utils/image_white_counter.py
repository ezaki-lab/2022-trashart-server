import cv2
import numpy as np

class ImageWhiteCounter:
    def __init__(self, img: np.ndarray):
        self.img = img

    def get_sum(self) -> int:
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        hsv_min = np.array([0, 0, 255])
        hsv_max = np.array([179, 255, 255])
        mask = cv2.inRange(hsv, hsv_min, hsv_max)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return 0

        return int(cv2.contourArea(contours[0]))
