"""
ユーザーAPI
"""

from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, Resource
from bson.objectid import ObjectId
from pymongo import MongoClient

from logger import logger
from datetime import datetime
from common import config
from services.inspector import content_type
from utils.random import generate_str

app = Blueprint("user", __name__)
api = Api(app, errors=Flask.errorhandler)

class User(Resource):
    @logger
    @content_type("application/json")
    def post(self):
        user_id = generate_str(24, hex_only=True)

        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            db.users.insert_one({
                "_id": ObjectId(user_id),
                "register_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return make_response(jsonify({
            "id": user_id
        }), 200)

api.add_resource(User, "/users")
