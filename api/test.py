from flask import Flask, request
from flask_restful import Api, abort, Resource
from base64_to_file import Base64_to_file

app = Flask(__name__)
api = Api(app)

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

        with MongoClient(config["DATABASE_URL"]) as client:
            db = client.trashart_db
            client.trashart_db.insert_one{()}

api.add_resource(Test, "/test")

if __name__ == "__main__":
    app.run(debug=True)
