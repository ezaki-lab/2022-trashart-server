"""
製作API
"""

from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, abort, Resource
from flask_restful.reqparse import RequestParser
from bson.objectid import ObjectId
from pymongo import MongoClient

import os
from shutil import copyfile
from logger import logger
from common import config
from services.inspector import content_type
from services.inspector.existed import existed_user_id
from utils.base64_to_file import Base64_to_file
from utils.random import generate_str

app = Blueprint("crafting", __name__)
api = Api(app, errors=Flask.errorhandler)

class Crafting(Resource):
    @logger
    def get(self, crafting_id: str=None):
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db

            if crafting_id == None:
                craftings = []
                for row in db.craftings.find():
                    craftings.append({
                        "id": str(row["_id"]),
                        "user_id": str(row["user_id"]),
                        "title": row["title"] if "title" in row else "",
                        "hashtags": row["hashtags"] if "hashtags" in row else [],
                        "image_url": row["image_url"] if "image_url" in row else ""
                    })

                return make_response(jsonify({
                    "craftings": craftings
                }), 200)

            if not existed_user_id(client, crafting_id):
                abort(404)

            data = db.craftings.find_one(ObjectId(crafting_id))
            return make_response(jsonify({
                "id": str(data["_id"]),
                "user_id": str(data["user_id"]),
                "title": data["title"] if "title" in data else "",
                "hashtags": row["hashtags"] if "hashtags" in row else [],
                "image_url": data["image_url"] if "image_url" in data else ""
            }), 200)

    @logger
    @content_type("application/json")
    def post(self):
        parser = RequestParser()
        parser.add_argument("user_id", type=str, location="json")
        args = parser.parse_args()

        crafting_id = generate_str(24, hex_only=True)
        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db

            if not existed_user_id(client, args["user_id"]):
                abort(404)

            db.craftings.insert_one({
                "_id": ObjectId(crafting_id),
                "user_id": ObjectId(args["user_id"])
            })

        return make_response(jsonify({
            "id": crafting_id
        }), 200)

api.add_resource(Crafting, "/craftings", "/craftings/<crafting_id>")
