"""
ページAPI
"""

import os
from flask import Blueprint, send_file, send_from_directory
from utils.get_path_type import get_path_type

app = Blueprint("user", __name__)

@app.route("/")
def page():
    return send_from_directory(
        os.path.abspath("./frontend"),
        "index.html",
        download_name="index.html",
        mimetype="text/html"
    )

@app.route("/<path:filepath>")
def static(filepath: str):
    # パス先のファイルのタイプ
    path_type = get_path_type("./frontend", filepath)

    # パス先のファイルが存在するなら、そのまま返す
    if path_type == 0:
        return send_from_directory(
            os.path.abspath("./frontend"),
            filepath,
            download_name=filepath
        )

    # .html を末尾に付ければ存在するなら、HTMLとして返す
    elif path_type == 1:
        return send_from_directory(
            os.path.abspath("./frontend"),
            filepath+".html",
            download_name=filepath,
            mimetype="text/html"
        )

    # index.html を末尾に付ければ存在するなら、HTMLとして返す
    elif path_type == 2:
        return send_from_directory(
            os.path.abspath("./frontend"),
            filepath+"/index.html",
            download_name=filepath,
            mimetype="text/html"
        )

    # ファイルが存在しなければ、 404.html を返す
    else:
        return send_from_directory(
            os.path.abspath("./frontend"),
            "404.html",
            download_name="404",
            mimetype="text/html"
        )
