"""
共有API
"""
from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, abort, Resource
from bson.objectid import ObjectId
from pymongo import MongoClient

import os
from shutil import copyfile
from logger import logger
from common import config
from services.inspector import content_type
import services.share.api as service
from utils.base64_to_file import Base64_to_file
from utils.random import generate_str

app = Blueprint("share", __name__)
api = Api(app, errors=Flask.errorhandler)

class Share(Resource):
    @logger
    @content_type("application/json")
    def put(self, crafting_id=None):
        args = service.put_parser.parse_args()

        # Base64形式で表現された画像をファイルに書き出す
        try:
            converter = Base64_to_file(args["image"])
            converter.save("storage/arts/", crafting_id+".webp", webp=True)
        except Exception as e:
            abort(400)

        return make_response(jsonify({}), 200)

api.add_resource(Share, "/share/<crafting_id>")