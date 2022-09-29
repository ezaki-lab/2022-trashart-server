"""
分別API
"""

from flask import Blueprint, Flask
from flask_restful import Api, Resource
from logger import logger
from services.inspector import content_type, json_scheme
from services.separate.plastic_separator import PlasticSeparator
from services.server import response as res

app = Blueprint("separate", __name__)
api = Api(app, errors=Flask.errorhandler)

class Separate(Resource):
    @logger
    @content_type("application/json")
    @json_scheme({
        "image_lighted (required)": str,
        "image_led850 (required)": str,
        "image_led940 (required)": str
    })
    def post(self, json: dict):
        separator = None

        try:
            separator = PlasticSeparator(
                json["image_lighted"],
                json["image_led850"],
                json["image_led940"]
            )
        except ValueError:
            return res.bad_request({
                "message": "This base64 image is not valid."
            })

        separator.separate()

        return res.ok(separator.to_json())

api.add_resource(Separate, "/separate")
