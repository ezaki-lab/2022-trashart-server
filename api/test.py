from flask import Blueprint, Flask, request
from flask_restful import Api, abort, Resource
from utils.base64_to_file import Base64_to_file

app = Blueprint("test", __name__)
api = Api(app, errors=Flask.errorhandler)

class Test(Resource):
    def post(self):
        # JSONではないなら、400 Bad Request を返す
        if not request.headers["Content-Type"] == "application/json":
            abort(400)

        # JSONを取得
        json = request.json

        try:
            converter = Base64_to_file(json["image"])
            converter.save("image.png")
        except Exception as e:
            # 変換時にエラーが発生したら、不正なBase64
            print(e)
            abort(400)

        return "image.png"

        # 以下の文で構文エラーが発生していて、他のAPIに影響しているから、一時的にコメントアウト
        # with MongoClient(config["DATABASE_URL"]) as client:
        #     db = client.trashart_db
        #     client.trashart_db.insert_one{()}

api.add_resource(Test, "/test")
