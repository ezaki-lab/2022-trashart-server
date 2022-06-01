from flask import Flask
from flask_cors import CORS

import common
import logger
from services.server import api, frontend

app = Flask(__name__)
# JSONを日本語でも表現できるようにする
app.config["JSON_AS_ASCII"] = False
# CORSを全面許可
CORS(app, supports_credentials=True)
# Blueprint を結合
app.register_blueprint(frontend.app)
app.register_blueprint(api.app)

if __name__ == "__main__":
    # APIサーバーを起動
    app.run(debug=False)
