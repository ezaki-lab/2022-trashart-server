from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

import common
import logger
from services.server import api

app = Flask(__name__)
# JSONを日本語でも表現できるようにする
app.config["JSON_AS_ASCII"] = False
# CORSを全面許可
CORS(app, supports_credentials=True)
# Blueprint を結合
app.register_blueprint(api.app)
# WebSocketを準備
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

if __name__ == "__main__":
    # APIサーバーを起動
    socketio.run(app, debug=True)
