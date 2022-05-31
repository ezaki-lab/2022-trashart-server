"""
ユーザーAPI
"""

from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from logger import logger

app = Blueprint("user", __name__)
api = Api(app)

class User(Resource):
    @logger
    def get(self, user_id=None):
        if user_id is not None:
            return jsonify({
                "name": user_id
            }), 200

        return jsonify({
            "users": [
                {
                    "name": "たから"
                },
                {
                    "name": "もう一人のたから"
                }
            ]
        }), 200

api.add_resource(User, "/users", "/users/<id>")
