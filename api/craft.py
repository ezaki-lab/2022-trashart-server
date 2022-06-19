"""
製作API
"""

from flask import Blueprint, jsonify, make_response
from flask_restful import Api, Resource
from pymongo import MongoClient

from logger import logger
from common import config
from services.inspector import content_type
import services.craft.api as service

app = Blueprint("craft", __name__)
api = Api(app)

class Craft(Resource):
    @logger
    @content_type("application/json")
    def post(self):
        args = service.post_parser.parse_args()
        print(args["base_id"])

        return make_response(jsonify({}), 200)

# class CraftBlueprint(Resource):
#     @logger
#     def put(self, user_id=None):
#         if user_id is not None:
#             return make_response(jsonify({
#                 "name": user_id
#             }), 200)

#         users = []
#         # データベースに接続
#         with MongoClient(config["DATABASE_URL"]) as client:
#             db = client.trashart_db
#             collection = db.test
#             cursor = collection.find()

#             # 全ての要素を取得
#             for user in cursor:
#                 user["id"] = str(user["_id"])
#                 del user["_id"]
#                 users.append(user)

#         return make_response(jsonify({
#             "users": users
#         }), 200)

api.add_resource(Craft, "/crafts", "/crafts/<craft_id>")
# api.add_resource(Craft, "/crafts/<craft_id>/blueprint")
