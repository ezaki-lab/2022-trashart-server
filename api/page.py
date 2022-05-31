"""
ページAPI
"""

import os
from flask import Blueprint, send_file, send_from_directory

app = Blueprint("user", __name__)

@app.route("/")
def page():
    return send_file(
        os.path.abspath("./frontend/index.html"),
        "index.html",
        download_name="index.html"
    )

@app.route("/<path:filepath>")
def static(filepath: str):
    return send_from_directory(
        os.path.abspath("./frontend"),
        filepath,
        download_name=filepath
    )
