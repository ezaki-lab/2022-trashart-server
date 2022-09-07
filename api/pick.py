"""
回収API
"""

from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, abort, Resource

from logger import logger
from services.inspector import content_type
import services.crafting.api as service
from services.pick.store.post import MaterialSeparator

app = Blueprint("pick", __name__)
api = Api(app, errors=Flask.errorhandler)

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

api.add_resource(PickStore, "/pick/store")
