import os

from flask import Blueprint, Flask
from flask_cors import CORS

import common
import logger
import api.page as page
import api.user as user

###################################
#  フロントエンド
###################################
frontend = Blueprint(
    "frontend",
    __name__,
    template_folder=os.path.abspath("./frontend"),
    url_prefix="/"
)
frontend.register_blueprint(page.app)

###################################
#  バックエンド
###################################
backend = Blueprint(
    "backend",
    __name__
)
backend.register_blueprint(user.app)

###################################
#  サーバー
###################################
app = Flask(__name__)
# JSONを日本語でも表現できるようにする
app.config["JSON_AS_ASCII"] = False
# CORSを全面許可
CORS(app, supports_credentials=True)
# フロントエンドとバックエンドを結合
app.register_blueprint(frontend)
app.register_blueprint(backend)

if __name__ == "__main__":
    # APIサーバーを起動
    app.run(debug=False)
