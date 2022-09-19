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
from services.inspector.existed import existed_crafting_id
from utils.base64_to_file import Base64_to_file

app = Blueprint("share", __name__)
api = Api(app, errors=Flask.errorhandler)

class Share(Resource):
    @logger
    @content_type("application/json")
    def post(self, crafting_id: str):
        parser = RequestParser()
        parser.add_argument("title", required=True, type=str, location="json")
        args = parser.parse_args()

        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db

            if not existed_crafting_id(client, crafting_id):
                abort(404)

            db.craftings.update_one({
                "_id": ObjectId(crafting_id)
            }, {
                "$set": {
                    "title": args["title"]
                }
            })

        return make_response(jsonify({}), 200)

class SharePhoto(Resource):
    @logger
    @content_type("application/json")
    def post(self, crafting_id: str):
        parser = RequestParser()
        parser.add_argument("data", required=True, type=str, location="json")
        args = parser.parse_args()

        with MongoClient(config["DATABASE_URL"]) as client:
            if not existed_crafting_id(client, crafting_id):
                abort(404)

        try:
            converter = Base64_to_file(args["data"])
            path = converter.save("storage/craftings/", crafting_id+".png")
        except Exception as e:
            abort(400)

        return make_response(jsonify({}), 200)

api.add_resource(Share, "/share/<crafting_id>")
api.add_resource(SharePhoto, "/share/<crafting_id>/photo")
