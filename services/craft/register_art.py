"""
アートを手動追加するためのスクリプト
"""

from bson.objectid import ObjectId
from pymongo import MongoClient
import cv2
import numpy as np
import shutil

import common
from utils.random import generate_str

"""
arts
    _id: Object id
    name: String
    width: Number
    height: Number
    cap_area: Number
"""

arts = [
    ["さかな", "fish"],
    ["はち", "bee"],
    ["イルカ", "dolphin"],
    ["ウサギ", "rabbit"],
    ["カニ", "crab"],
    ["クラゲ", "jellyfish"],
    ["ステゴサウルス", "stegosaurus"],
    ["ティラノサウルス", "tyrannosaurus"],
    ["マンボウ", "mammoth"],
    ["リス", "squirrel"],
    ["猫", "cat"],
    ["船", "ship"],
    ["蝶々", "butterfly"],
    ["車", "car"],
    ["雪だるま", "snowman"]
]

def main():
    with MongoClient(common.config["DATABASE_URL"]) as client:
        db = client.trashart_db

        for art in arts:
            art_id = generate_str(24, hex_only=True)

            shutil.copytree("storage/arts_tmp/" + art[1], "storage/arts/" + art_id)

            original_img = cv2.imread("storage/arts/" + art_id + "/art.png")
            height, width, _ = original_img.shape

            cap_img = cv2.imread("storage/arts/" + art_id + "/cap.png")

            hsv = cv2.cvtColor(cap_img, cv2.COLOR_BGR2HSV)

            hsv_min = np.array([0,0,255])
            hsv_max = np.array([0,0,255])
            mask = cv2.inRange(hsv, hsv_min, hsv_max)

            contours, hierarchy = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            db.arts.insert_one({
                "_id": ObjectId(art_id),
                "name": art[0],
                "width": width,
                "height": height,
                "cap_area": cv2.contourArea(contours[0])
            })

if __name__ == "__main__":
    main()
