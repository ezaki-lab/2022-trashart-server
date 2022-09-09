"""
回収API
"""

from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, abort, Resource
from flask_restful.reqparse import RequestParser
from bson.objectid import ObjectId
from pymongo import MongoClient

from datetime import datetime
from logger import logger
import os
import shutil
from common import config
from services.inspector import content_type
from services.pick.store.post import MaterialSeparator
from utils.base64_to_file import Base64_to_file

app = Blueprint("pick", __name__)
api = Api(app, errors=Flask.errorhandler)

class PickSeparate(Resource):
    @logger
    @content_type("application/json")
    def post(self):
        parser = RequestParser()
        parser.add_argument("data", required=True, type=str, location="json")
        args = parser.parse_args()

        try:
            converter = Base64_to_file(args["data"])
            basename = datetime.now().strftime("%H-%M-%S")
            path = converter.save("storage/chousa/", basename+".png")
        except Exception as e:
            abort(400)

        return make_response(jsonify({}), 200)

class PickStore(Resource):
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

        # フォルダーがあれば削除
        save_folder = "storage/materials/{}".format(self.session_id)
        if os.path.exists(save_folder):
            shutil.rmtree(save_folder)

        separator = MaterialSeparator(args["data"], session_id)
        try:
            separator.load_b64()
        except Exception as e:
            abort(400)

        separator.separate()

        return make_response(jsonify({
            "width": separator.width,
            "height": separator.height,
            "materials": separator.get_materials_info()
        }), 200)

api.add_resource(PickSeparate, "/pick/separate")
api.add_resource(PickStore, "/pick/store/<session_id>")
