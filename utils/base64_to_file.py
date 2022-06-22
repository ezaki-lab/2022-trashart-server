"""
Base64形式で表現されたバイナリデータをファイルとして書きこむ
"""

import os
from base64 import b64decode
from utils.random import generate_str

class Base64_to_file:
    def __init__(self, base64_str: str, save_folder: str):
        # 先頭のMIME情報は削除 (例: data:image/png;base64,)
        self.base64_str = base64_str.split(",", 1)[1]
        self.filename = generate_str(8)
        self.save_folder = save_folder

    def save(self) -> str:
        # 保存フォルダーがなければ作成
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        path = os.path.join(self.save_folder, self.filename)

        # ファイルに書き出し
        with open(path, "wb") as f:
            f.write(
                b64decode(self.base64_str.encode())
            )

        return path
