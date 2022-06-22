"""
ストレージAPI
"""

import os
from flask import Blueprint, send_from_directory

app = Blueprint("storage", __name__)

@app.route("/storage/<path:filepath>", methods=["GET"])
def storage(filepath: str):
    return send_from_directory(
        os.path.abspath("./storage"),
        filepath,
        download_name=filepath
    )
