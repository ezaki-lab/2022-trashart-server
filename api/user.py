"""
ユーザーAPI
"""

from flask import Blueprint, jsonify, make_response
from flask_restful import Api, Resource
from pymongo import MongoClient
from logger import logger
from common import config

app = Blueprint("user", __name__)
api = Api(app)

class User(Resource):
    @logger
    def get(self, user_id=None):
        if user_id is not None:
            return make_response(jsonify({
                "name": user_id
            }), 200)

        users = []
        # データベースに接続
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            collection = db.test
            cursor = collection.find()

            # 全ての要素を取得
            for user in cursor:
                user["id"] = str(user["_id"])
                del user["_id"]
                users.append(user)

        return make_response(jsonify({
            "users": users
        }), 200)

api.add_resource(User, "/users", "/users/<user_id>")
