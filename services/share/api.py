from flask_restful.reqparse import RequestParser

put_parser = RequestParser()
put_parser.add_argument("image", type=str, location="json")