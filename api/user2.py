"""
ユーザーAPI (練習用)
"""

from flask import Blueprint, jsonify, make_response
from flask_restful import Api, Resource
from pymongo import MongoClient

from logger import logger
from common import config


app = Blueprint("user2", __name__)
api = Api(app)

class User2(Resource):
    @logger
    def get(self):
        users = []

        # データベースに接続し、ユーザーを取得
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            coll = db.users
            cursor = coll.find()

            for user in cursor:
                if "name" in user:
                    users.append(user["name"])
                else:
                    users.append("そんなもんないわ")

        # ユーザー情報を返す
        return make_response(jsonify({
            "users": users
        }), 200)

api.add_resource(User2, "/user2")
