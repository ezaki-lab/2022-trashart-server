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
            return res.ok(Craftings().craftings)

        try:
            return res.ok(Crafting(crafting_id).__dict__)
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
    def post(self, json: any, crafting_id: str=None):
        if crafting_id != None:
            abort(404)

        try:
            crafting = Crafting().post(
                json["user_id"],
                json["title"],
                json["hashtags"],
                json["image"]
            )
            return res.created({
                "id": crafting.id
            })

        except FileNotFoundError:
            return res.bad_request({
                "message": "This user does not exist."
            })

api.add_resource(Share, "/shares", "/shares/<crafting_id>")
