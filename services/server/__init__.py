from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

import common
from . import api

socketio = SocketIO(async_mode=None, cors_allowed_origins="*")

def create_server(debug=False) -> Flask:
    app = Flask(__name__)
    app.debug = debug
    # JSONを日本語でも表現できるようにする
    app.config["JSON_AS_ASCII"] = False
    # 通信を認証するための鍵
    app.config["SECRET_KEY"] = common.config["SECRET_KEY"]
    # CORSを全面許可
    CORS(app, supports_credentials=True)

    # APIハンドラー
    app.register_blueprint(api.app)
    # Socket.ioハンドラー
    from . import ws

    # Socket.ioのサーバーとして登録
    socketio.init_app(app)
    return app
