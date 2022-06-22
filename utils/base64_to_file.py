"""
Base64形式で表現されたバイナリデータをファイルとして書きこむ
"""

from mimetypes import guess_extension
import os
from base64 import b64decode
from utils.random import generate_str

class Base64_to_file:
    def __init__(self, base64_str: str, save_folder: str):
        base64_str_splitted = base64_str.split(",", 1)
        # Content-Type
        self.content_type = self.pick_content_type(base64_str_splitted[0])
        # データ部
        self.data = base64_str_splitted[1]
        # ファイル名
        self.filename = generate_str(8) + guess_extension(self.content_type)
        # セーブフォルダー
        self.save_folder = save_folder

    def pick_content_type(self, mime_info: str) -> str:
        # Content-Type を返す
        return mime_info[mime_info.find(":")+1:mime_info.find(";")]

    def save(self) -> str:
        # 保存フォルダーがなければ作成
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        path = os.path.join(self.save_folder, self.filename)

        # ファイルに書き出し
        with open(path, "wb") as f:
            f.write(
                b64decode(self.data.encode())
            )

        return path
