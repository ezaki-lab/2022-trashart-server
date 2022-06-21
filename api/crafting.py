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
import services.craft.api as service

app = Blueprint("craft", __name__)
api = Api(app, errors=Flask.errorhandler)

class Crafting(Resource):
    @logger
    @content_type("application/json")
    def post(self):
        args = service.post_parser.parse_args()
        print(args["base_id"])

        return make_response(jsonify({}), 200)

class CraftingBlueprint(Resource):
    @logger
    @content_type("application/json")
    def put(self, craft_id=None):
        # データベースに接続
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            data = db.craftings.find_one(ObjectId(craft_id))

            if data == None:
                abort(404)

            print(data)

            # # 全ての要素を取得
            # for user in cursor:
            #     user["id"] = str(user["_id"])
            #     del user["_id"]
            #     users.append(user)

        return make_response(jsonify({}), 200)

api.add_resource(Crafting, "/craftings", "/craftings/<craft_id>")
api.add_resource(CraftingBlueprint, "/craftings/<craft_id>/blueprint")
