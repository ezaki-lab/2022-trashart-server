"""
製作ソケット
"""

from flask import request
from flask_socketio import emit, Namespace

class Test(Namespace):
    def __init__(self, namespace):
        super().__init__(namespace)
        self.user_count = 0
        self.text = ""

    def on_connect(self):
        print("接続", request.sid)
        self.user_count += 1

        # 接続者数の更新 (broadcast)
        emit("count_update",
            {
                "count": self.user_count
            },
            broadcast=True
        )
        # テキストエリアの更新
        emit("text_update",
            {
                "text": self.text
            }
        )

    def on_disconnect(self):
        print("切断", request.sid)
        self.user_count -= 1

        # 接続者数の更新 (broadcast)
        emit("count_update",
            {
                "count": self.user_count
            },
            broadcast=True
        )

    def on_text_update_request(self, json):
        self.text = json["text"]

        # 全員向けに送信すると入力の途中でテキストエリアが変更されて日本語入力がうまくできない
        emit("text_update",
            {
                "text": self.text
            },
            broadcast=True,
            include_self=False
        )
