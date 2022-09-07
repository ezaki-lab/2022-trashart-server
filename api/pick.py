"""
回収API
"""

from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, abort, Resource

from datetime import datetime
from logger import logger
from services.inspector import content_type
import services.crafting.api as service
from services.pick.store.post import MaterialSeparator
from utils.base64_to_file import Base64_to_file

app = Blueprint("pick", __name__)
api = Api(app, errors=Flask.errorhandler)

class PickSeparate(Resource):
    @logger
    @content_type("application/json")
    def post(self):
        args = service.store_parser.parse_args()

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
    def post(self):
        args = service.store_parser.parse_args()

        separator = MaterialSeparator(args["data"])
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
api.add_resource(PickStore, "/pick/store")
