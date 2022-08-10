"""
APIの Blueprint を統合
"""

from flask import Blueprint
from glob import glob
import importlib

app = Blueprint(
    "api",
    __name__
)

# APIフォルダーのファイルを全てインポート
for path in glob("api/*.py"):
    name = path.split("/")[1].split(".")[0]
    module = importlib.import_module(f"api.{name}")
    app.register_blueprint(module.app)
