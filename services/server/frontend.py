"""
フロントエンドの Blueprint を統合
"""

import os
from flask import Blueprint

import api.page as page

app = Blueprint(
    "frontend",
    __name__,
    template_folder=os.path.abspath("./frontend"),
    url_prefix="/"
)

app.register_blueprint(page.app)
