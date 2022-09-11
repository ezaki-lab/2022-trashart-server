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

class SharePhoto(Resource):
    @logger
    @content_type("application/json")
    def post(self, session_id: str):
        parser = RequestParser()
        parser.add_argument("data", required=True, type=str, location="json")
        args = parser.parse_args()

        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            data = db.sessions.find_one(ObjectId(session_id))

            if data == None:
                abort(404)

        try:
            converter = Base64_to_file(args["data"])
            path = converter.save("storage/works/", session_id+".png")
        except Exception as e:
            abort(400)

        return make_response(jsonify({}), 200)

api.add_resource(SharePhoto, "/share/<session_id>/photo")
