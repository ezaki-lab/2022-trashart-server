"""
ユーザーAPI
"""

from flask import Blueprint, Flask
from flask_restful import Api, abort, Resource
from logger import logger
from models.user import User as UserData
from models.user import Users as UsersData
from services.inspector import content_type
from services.server import response as res

app = Blueprint("user", __name__)
api = Api(app, errors=Flask.errorhandler)

class User(Resource):
    @logger
    def get(self, user_id: str=None):
        if user_id == None:
            return res.ok(UsersData().to_json())

        try:
            return res.ok(UserData(user_id).to_json())
        except FileNotFoundError:
            return res.bad_request({
                "message": "This user does not exist."
            })

    @logger
    @content_type("application/json")
    def post(self, user_id: str=None):
        if user_id != None:
            abort(404)

        user = UserData()
        user.post()
        return res.created(user.to_json())

api.add_resource(User, "/users", "/users/<user_id>")
