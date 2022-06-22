"""
製作API
"""

from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, abort, Resource
from bson.objectid import ObjectId
from pymongo import MongoClient

from logger import logger
from common import config
from services.inspector import content_type
import services.crafting.api as service
from utils.base64_to_file import Base64_to_file

app = Blueprint("crafting", __name__)
api = Api(app, errors=Flask.errorhandler)

class Crafting(Resource):
    @logger
    @content_type("application/json")
    def post(self):
        args = service.post_parser.parse_args()

        # 製作IDを新規作成
        crafting_id = None
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            result = db.craftings.insert_one({"base_id": args["base_id"]})
            crafting_id = str(result.inserted_id)

        return make_response(jsonify({
            "id": crafting_id
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
            converter = Base64_to_file(args["data"], "./storage/blueprints/")
            path = converter.save()
        except Exception as e:
            abort(400)

        return make_response(jsonify({
            "path": path
        }), 200)

api.add_resource(Crafting, "/craftings", "/craftings/<crafting_id>")
api.add_resource(CraftingBlueprint, "/craftings/<crafting_id>/blueprint")