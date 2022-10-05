"""
アートを手動追加するためのスクリプト
"""

from bson.objectid import ObjectId
from pymongo import MongoClient
import cv2
import os
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
    attentions_num: Number
"""

arts = [
    ["さかな", "fish", ["魚", "海"]],
    ["イルカ", "dolphin", ["イルカ", "青", "海"]],
    ["ウサギ", "rabbit", ["ウサギ", "ピンク"]],
    ["カニ", "crab", ["カニ", "海岸"]],
    ["クラゲ", "jellyfish", ["クラゲ", "海"]],
    ["ステゴサウルス", "stegosaurus", ["ステゴサウルス", "恐竜"]],
    ["ティラノサウルス", "tyrannosaurus", ["ティラノサウルス", "恐竜"]],
    ["マンボウ", "mammoth", ["マンボウ", "海"]],
    ["リス", "squirrel", ["リス", "森"]],
    ["猫", "cat", ["猫", "かわいい"]],
    ["船", "ship", ["船", "海"]],
    ["車", "car", ["車"]],
    ["ちょうちょ", "butterfly", ["ちょうちょ", "虫"]],
    ["雪だるま", "snowman", ["雪だるま", "雪", "冬"]],
    ["チョウチンアンコウ", "footballfish", ["チョウチンアンコウ", "魚", "深海生物"]],
    ["ナンヨウハギ", "bluetang", ["ナンヨウハギ", "魚"]],
    ["エビ", "prawn", ["エビ", "魚"]],
    ["プテラノドン", "pteranodon", ["プテラノドン", "恐竜"]],
    ["ロケット", "rocket", ["ロケット", "宇宙"]],
    ["タツノオトシゴ", "seahorse", ["タツノオトシゴ", "魚"]],
    ["クワガタムシ", "stag", ["クワガタムシ", "虫"]],
    ["カメ", "turtle", ["カメ", "海"]],
    ["クジラ", "whale", ["クジラ", "海"]]
]

def main():
    print("アートを登録する作業を開始します。")

    with MongoClient(common.config["DATABASE_URL"]) as client:
        db = client.trashart_db

        for art in arts:
            art_id = generate_str(24, hex_only=True)

            shutil.copytree("storage/arts_tmp/" + art[1], "storage/arts/" + art_id)

            ###################################
            #  DBに登録する情報
            ###################################
            original_img = cv2.imread("storage/arts/" + art_id + "/art.png")
            cv2.imwrite("storage/arts/" + art_id + "/art.webp", original_img)
            height, width, _ = original_img.shape

            cap_img = cv2.imread("storage/arts/" + art_id + "/cap.png")

            hsv = cv2.cvtColor(cap_img, cv2.COLOR_BGR2HSV)

            hsv_min = np.array([0, 0, 255])
            hsv_max = np.array([0, 0, 255])
            mask = cv2.inRange(hsv, hsv_min, hsv_max)

            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            cap_area = cv2.contourArea(contours[0])

            ###################################
            #  製作補助画像
            ###################################
            art_bin = cv2.imread("storage/arts/" + art_id + "/art_bin.png")
            art_att = cv2.imread("storage/arts/" + art_id + "/art_attention.png")

            # art_bin.png と art_attention.png のサイズが異なるなら、統一
            if art_bin.shape != art_att.shape:
                art_att = cv2.resize(art_att, dsize=(art_bin.shape[1], art_bin.shape[0]))
                cv2.imwrite("storage/arts/" + art_id + "/art_attention.png", art_att)

            art_support = np.zeros((art_bin.shape[0], art_bin.shape[1], 4), np.uint8)

            hsv = cv2.cvtColor(art_att, cv2.COLOR_BGR2HSV)
            hsv_min = np.array([0, 0, 255])
            hsv_max = np.array([0, 0, 255])
            mask = cv2.inRange(hsv, hsv_min, hsv_max)

            contours_att, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 作品の特徴部分を描画
            cv2.drawContours(art_support, contours_att, -1, color=(68, 68, 239, 127), thickness=-1)

            hsv = cv2.cvtColor(art_bin, cv2.COLOR_BGR2HSV)
            hsv_min = np.array([0, 0, 255])
            hsv_max = np.array([0, 0, 255])
            mask = cv2.inRange(hsv, hsv_min, hsv_max)

            contours_bin, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 作品の輪郭を描画
            cv2.drawContours(art_support, contours_bin, -1, color=(68, 68, 239, 255), thickness=3)

            cv2.imwrite("storage/arts/" + art_id + "/art_support.webp", art_support)

            ###################################
            #  特徴パーツ画像
            ###################################
            save_folder = "storage/arts/" + art_id + "/attentions"
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            for i, cont in enumerate(contours_att):
                x, y, w, h = cv2.boundingRect(cont)
                img = np.zeros((art_att.shape[0], art_att.shape[1], 3), np.uint8)
                cv2.drawContours(img, [cont], -1, color=(255, 255, 255), thickness=-1)
                filepath = "%s/%d.png" % (save_folder, i+1)
                cv2.imwrite(filepath, img[y:y+h, x:x+w])

            ###################################
            #  DBに書き込み
            ###################################
            db.arts.insert_one({
                "_id": ObjectId(art_id),
                "name": art[0],
                "width": width,
                "height": height,
                "cap_area": cap_area,
                "attentions_num": len(contours_att),
                "hashtags": art[2]
            })

            print("{} ({}) OK - {}".format(art[0], art[1], art_id))

if __name__ == "__main__":
    main()
