"""
ユーザーAPI
"""

# TODO: 手が空いたときにリファクタリングする

from flask import abort, Blueprint, Flask, jsonify, make_response
from flask_restful import Api, Resource
from bson.objectid import ObjectId
from pymongo import MongoClient

from logger import logger
from datetime import datetime
from common import config
from services.inspector import content_type
from services.inspector.existed import existed_user_id
from utils.random import generate_str

app = Blueprint("user", __name__)
api = Api(app, errors=Flask.errorhandler)

class User(Resource):
    @logger
    def get(self, user_id: str=None):
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db

            if user_id == None:
                users = []
                for row in db.users.find():
                    users.append({
                        "id": str(row["_id"]),
                        "register_at": row["register_at"]
                    })

                return make_response(jsonify({
                    "users": users
                }), 200)

            if not existed_user_id(client, user_id):
                abort(404)

            craftings = []
            for row in db.craftings.find({"user_id": ObjectId(user_id)}):
                craftings.append({
                    "id": str(row["_id"]),
                    "user_id": str(row["user_id"]),
                    "title": row["title"] if "title" in row else "",
                    "hashtags": row["hashtags"] if "hashtags" in row else [],
                    "image_url": row["image_url"] if "image_url" in row else ""
                })

            data = db.users.find_one(ObjectId(user_id))
            return make_response(jsonify({
                "id": user_id,
                "register_at": data["register_at"],
                "craftings": craftings
            }), 200)

    @logger
    @content_type("application/json")
    def post(self):
        user_id = generate_str(24, hex_only=True)

        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            db.users.insert_one({
                "_id": ObjectId(user_id),
                "register_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return make_response(jsonify({
            "id": user_id
        }), 200)

api.add_resource(User, "/users", "/users/<user_id>")
