"""
回収API
"""

from flask import Blueprint, Flask
from flask_restful import Api, Resource
from pymongo import MongoClient
from datetime import datetime
from logger import logger
import os
import shutil
from common import config
from services.inspector import content_type, json_scheme
from services.inspector.existed import existed_session_id
from services.server import response as res
from services.pick.store.post import MaterialSeparator
from utils.base64_to_file import Base64_to_file

app = Blueprint("pick", __name__)
api = Api(app, errors=Flask.errorhandler)

class PickSeparate(Resource):
    @logger
    @content_type("application/json")
    @json_scheme({
        "image (required)": str
    })
    def post(self, json: dict):
        try:
            converter = Base64_to_file(json["image"])
            basename = datetime.now().strftime("%H-%M-%S")
            converter.save("storage/chousa/", basename+".png")
        except Exception:
            return res.bad_request({
                "message": "This base64 image is not valid."
            })

        return res.ok({})

class PickStore(Resource):
    @logger
    @content_type("application/json")
    @json_scheme({
        "image (required)": str
    })
    def post(self, json: dict, session_id: str):
        with MongoClient(config["DATABASE_URL"]) as c:
            if not existed_session_id(c, session_id):
                return res.not_found({
                    "message": "This session does not exist."
                })

        # フォルダーがあれば削除
        save_folder = "storage/materials/{}".format(session_id)
        if os.path.exists(save_folder):
            shutil.rmtree(save_folder)

        separator = MaterialSeparator(json["image"], session_id)
        try:
            separator.load_b64()
        except Exception:
            return res.bad_request({
                "message": "This base64 image is not valid."
            })

        separator.separate()

        return res.ok({
            "width": separator.width,
            "height": separator.height,
            "materials": separator.get_materials_info()
        })

api.add_resource(PickSeparate, "/pick/separate")
api.add_resource(PickStore, "/pick/<session_id>/store")
