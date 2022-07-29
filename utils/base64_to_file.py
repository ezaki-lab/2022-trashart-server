"""
Base64形式で表現されたバイナリデータをファイルとして書きこむ
"""

from PIL import Image
from mimetypes import guess_extension
import io
import os
from base64 import b64decode
from utils.random import generate_str

class Base64_to_file:
    def __init__(self, base64_str: str):
        base64_str_splitted = base64_str.split(",", 1)
        # Content-Type
        self.content_type = self.pick_content_type(base64_str_splitted[0])
        # データ部
        self.data = base64_str_splitted[1]

    def pick_content_type(self, mime_info: str) -> str:
        # Content-Type を返す
        return mime_info[mime_info.find(":")+1:mime_info.find(";")]

    def save(self, save_folder: str, filename: str=None, webp: bool=False) -> str:
        if filename == None:
            filename = generate_str(8) + guess_extension(self.content_type)

        # 保存フォルダーがなければ作成
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        path = os.path.join(save_folder, filename)

        # ファイルに書き出し
        Image.open(
            io.BytesIO(
                b64decode(self.data.encode())
            )
        ).save(path, "webp" if webp else "png")

        return path
