"""
セッションAPI
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

app = Blueprint("session", __name__)
api = Api(app, errors=Flask.errorhandler)

class Session(Resource):
    @logger
    def get(self):
        sessions = []

        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            for row in db.sessions.find():
                sessions.append({
                    "id": str(row["_id"]),
                    "start_at": row["start_at"]
                })

        return make_response(jsonify({
            "sessions": sessions
        }), 200)

    @logger
    @content_type("application/json")
    def post(self):
        session_id = generate_str(24, hex_only=True)

        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            db.sessions.insert_one({
                "_id": ObjectId(session_id),
                "start_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return make_response(jsonify({
            "id": session_id
        }), 200)

api.add_resource(Session, "/sessions")
