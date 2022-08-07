"""
製作API
"""

from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, abort, Resource
from bson.objectid import ObjectId
from pymongo import MongoClient

import os
from datetime import datetime
from shutil import copyfile
from logger import logger
from common import config
from services.inspector import content_type
import services.crafting.api as service
from utils.base64_to_file import Base64_to_file
from utils.random import generate_str

app = Blueprint("crafting", __name__)
api = Api(app, errors=Flask.errorhandler)

class Crafting(Resource):
    @logger
    @content_type("application/json")
    def post(self):
        args = service.post_parser.parse_args()

        # 製作IDを新規作成
        crafting_id = generate_str(24, hex_only=True)
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            db.craftings.insert_one({
                "_id": ObjectId(crafting_id),
                "base_id": args["base_id"]
            })

        crafting_id_spare = generate_str(24, hex_only=True)

        print(0 / 0)

        # ベースとなる作品があるなら、設計図をコピー
        if args["base_id"] != None and args["base_id"] != "":
            base_blueprint_path = "storage/blueprints/" + args["base_id"] + ".webp"
            if os.path.exists(base_blueprint_path):
                new_blueprint_path = "storage/blueprints/" + crafting_id + ".webp"
                copyfile(base_blueprint_path, new_blueprint_path)
            else:
                abort(404)

        return make_response(jsonify({
            "id": crafting_id,
            "create_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "favorite":"イチゴ",
            "spare_id": crafting_id_spare
        }), 200)

class CraftingBlueprint(Resource):
    @logger
    @content_type("application/json")
    def put(self, crafting_id=None):
        args = service.blueprint_put_parser.parse_args()

        # 製作IDが存在しなければ404を返す
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            data = db.craftings.find_one(ObjectId(crafting_id))

            if data == None:
                abort(404)

        # Base64形式で表現された画像をファイルに書き出す
        path = None
        try:
            converter = Base64_to_file(args["data"])
            path = converter.save("storage/blueprints/", crafting_id+".webp", webp=True)
        except Exception as e:
            abort(400)

        return make_response(jsonify({
            "url": os.path.join(config["API_URL"], path)
        }), 200)

api.add_resource(Crafting, "/craftings", "/craftings/<crafting_id>")
api.add_resource(CraftingBlueprint, "/craftings/<crafting_id>/blueprint")
