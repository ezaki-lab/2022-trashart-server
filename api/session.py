"""
セッションAPI
"""

from flask import Blueprint, Flask
from flask_restful import Api, abort, Resource
from logger import logger
from models.session import Session as SessionData
from models.session import Sessions as SessionsData
from services.inspector import content_type
from services.server import response as res

app = Blueprint("session", __name__)
api = Api(app, errors=Flask.errorhandler)

class Session(Resource):
    @logger
    def get(self, session_id: str=None):
        if session_id == None:
            return res.ok(SessionsData().to_json())

        try:
            return res.ok(SessionData(session_id).to_json())
        except FileNotFoundError:
            return res.bad_request({
                "message": "This session does not exist."
            })

    @logger
    @content_type("application/json")
    def post(self, session_id: str=None):
        if session_id != None:
            abort(404)

        session = SessionData()
        session.post()
        return res.created(session.to_json())

api.add_resource(Session, "/sessions", "/sessions/<session_id>")
