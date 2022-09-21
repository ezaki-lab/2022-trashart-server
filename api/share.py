"""
共有API
"""

from flask import Blueprint, Flask
from flask_restful import Api, abort, Resource
from logger import logger
from models.crafting import Crafting, Craftings
from services.inspector import content_type, json_scheme
from services.server import response as res

app = Blueprint("share", __name__)
api = Api(app, errors=Flask.errorhandler)

class Share(Resource):
    @logger
    def get(self, crafting_id: str=None):
        if crafting_id == None:
            return res.ok(Craftings().to_json())

        try:
            return res.ok(Crafting(crafting_id).to_json())
        except FileNotFoundError:
            return res.bad_request({
                "message": "This crafting does not exist."
            })

    @logger
    @content_type("application/json")
    @json_scheme({
        "user_id (required)": str,
        "title (required)": str,
        "hashtags (required)": list,
        "image (required)": str
    })
    def post(self, json: dict, crafting_id: str=None):
        if crafting_id != None:
            abort(404)

        crafting = Crafting()

        try:
            crafting.post(
                json["user_id"],
                json["title"],
                json["hashtags"],
                json["image"]
            )
        except FileNotFoundError:
            return res.bad_request({
                "message": "This user does not exist."
            })

        return res.created(crafting.to_json())

api.add_resource(Share, "/shares", "/shares/<crafting_id>")
