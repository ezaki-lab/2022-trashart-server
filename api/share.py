"""
共有API
"""
from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, abort, Resource
from flask_restful.reqparse import RequestParser
from bson.objectid import ObjectId
from pymongo import MongoClient

from logger import logger
from common import config
from services.inspector import content_type
from utils.base64_to_file import Base64_to_file

app = Blueprint("share", __name__)
api = Api(app, errors=Flask.errorhandler)

class Share(Resource):
    @logger
    @content_type("application/json")
    def put(self, crafting_id=None):
        parser = RequestParser()
        parser.add_argument("image", type=str, location="json")
        parser.add_argument("trash", type=str, location="json")
        args = parser.parse_args()

        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            db.arts.insert_one({
                "_id": ObjectId(crafting_id),
                "trash": args["trash"]
            })

        # Base64形式で表現された画像をファイルに書き出す
        try:
            converter = Base64_to_file(args["image"])
            converter.save("storage/arts/", crafting_id+".webp", webp=True)
        except Exception as e:
            abort(400)

        return make_response(jsonify({}), 200)

api.add_resource(Share, "/share/<crafting_id>")
