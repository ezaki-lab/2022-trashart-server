"""
    色を変換し、クライアントにBase64として返すAPI
"""

import base64
from flask import Blueprint, Flask, jsonify, make_response, request
from flask_restful import Api, abort, Resource
from utils.base64_to_file import Base64_to_file
from utils.random import generate_str
from utils.change_color import change_color
from common import config


app = Blueprint("color", __name__)
api = Api(app, errors=Flask.errorhandler)

class Color(Resource):
    def post():
        # JSONでなければ、400 Bad Request を返す
        if not request.headers["Content-Type"] == "application/json":
            abort(400)
        # JSONを取得
        json = request.json

        try:
            # 受け取ったBase64形式のデータをデコードする
            converter = Base64_to_file(json["image"])
            fname = generate_str(8) + ".png"
            converter.save(fname)
            # 保存した画像ファイルを変色させる
            change_color(fname, json["before_color"], json["after_color"])
            # 変色させたファイルをBase64形式にエンコードする
            file_data = open(fname, "rb").read()
            b64_data = base64.b64encode(file_data).decode('utf-8')
        except Exception as e:
            # 例外処理
            print(e)
            abort(400)

        # Base64を返す
        return make_response(jsonify({
            "image": b64_data
        }), 200)

api.add_resource(Color, "/color")
