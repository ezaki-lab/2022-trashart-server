"""
アートAPI
"""

from flask import Blueprint, Flask
from flask_restful import Api, Resource
from logger import logger
from models.art import Art as ArtData, Arts as ArtsData
from services.art.suggester import ArtSuggester
from services.server import response as res

app = Blueprint("art", __name__)
api = Api(app, errors=Flask.errorhandler)

class Art(Resource):
    @logger
    def get(self, art_id: str=None):
        if art_id == None:
            return res.ok(ArtsData().to_json())

        try:
            return res.ok(ArtData(art_id).to_json())
        except FileNotFoundError:
            return res.bad_request({
                "message": "This art does not exist."
            })

class ArtSuggestion(Resource):
    @logger
    def get(self, session_id: str):
        suggester = None

        try:
            suggester = ArtSuggester(session_id)
        except FileNotFoundError as e:
            msg = str(e)

            if msg == "This session does not exist":
                return res.not_found({
                    "message": "This session does not exist"
                })

            elif msg == "This session does not have materials":
                return res.bad_request({
                    "message": "This session does not have materials"
                })

        arts = suggester.suggest(10)
        arts_parsed = ArtsData.parse_dict_list(arts)

        return res.ok({
            "arts": arts_parsed
        })

class ArtRandoms(Resource):
    @logger
    def get(self):
        return res.ok(ArtsData(10).to_json())

api.add_resource(Art, "/arts", "/arts/<art_id>")
api.add_resource(ArtSuggestion, "/art-suggestions/<session_id>")
api.add_resource(ArtRandoms, "/art-randoms")
