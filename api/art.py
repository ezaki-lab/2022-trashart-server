"""
アートAPI
"""

from flask import Blueprint, Flask, jsonify, make_response
from flask_restful import Api, abort, Resource
from bson.objectid import ObjectId
from pymongo import MongoClient

import os
from logger import logger
from common import config
from services.art.suggestion.get import Art as ArtInfo, ArtSuggester
from services.inspector.existed import existed_art_id, existed_session_id

app = Blueprint("art", __name__)
api = Api(app, errors=Flask.errorhandler)

class Art(Resource):
    @logger
    def get(self, art_id=None):
        if art_id == None:
            with MongoClient(config["DATABASE_URL"]) as client:
                db = client.trashart_db
                cursor = db.arts.find()

                arts = []

                for row in cursor:
                    art_id = str(row["_id"])
                    original_img_url = os.path.join(config["API_URL"], "storage/arts/{}/art.webp".format(art_id))
                    support_img_url = os.path.join(config["API_URL"], "storage/arts/{}/art_support.webp".format(art_id))

                    arts.append({
                        "id": art_id,
                        "name": row["name"],
                        "width": row["width"],
                        "height": row["height"],
                        "cap_area": row["cap_area"],
                        "attentions_num": row["attentions_num"],
                        "original_image_url": original_img_url,
                        "support_image_url": support_img_url
                    })

                return make_response(jsonify({
                    "arts": arts
                }), 200)


        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            data = db.arts.find_one(ObjectId(art_id))

            if not existed_art_id(client, art_id):
                abort(404)

            original_img_url = os.path.join(config["API_URL"], "storage/arts/{}/art.webp".format(art_id))
            support_img_url = os.path.join(config["API_URL"], "storage/arts/{}/art_support.webp".format(art_id))

            return make_response(jsonify({
                "id": art_id,
                "name": data["name"],
                "width": data["width"],
                "height": data["height"],
                "cap_area": data["cap_area"],
                "attentions_num": data["attentions_num"],
                "original_image_url": original_img_url,
                "support_image_url": support_img_url
            }), 200)

class ArtHashtags(Resource):
    def get(self, art_id: str=None):
        if not existed_art_id(MongoClient(config["DATABASE_URL"]), art_id):
            abort(404)

        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            data = db.arts.find_one(ObjectId(art_id))

            return make_response(jsonify({
                "hashtags": data["hashtags"]
            }), 200)

class ArtSuggestion(Resource):
    def get(self, session_id: str):
        with MongoClient(config["DATABASE_URL"]) as client:
            if not existed_session_id(client, session_id):
                abort(404)

        # 素材画像をまだ撮影していないなら
        if not os.path.exists("storage/materials/" + session_id):
            abort(400)

        suggester = ArtSuggester(session_id)
        arts = suggester.suggest(10)

        arts_parsed = ArtInfo.parse_dict_list(arts)

        return make_response(jsonify({
            "arts": arts_parsed
        }), 200)

api.add_resource(Art, "/arts", "/arts/<art_id>")
api.add_resource(ArtHashtags, "/arts/<art_id>/hashtags")
api.add_resource(ArtSuggestion, "/art-suggestions/<session_id>")
