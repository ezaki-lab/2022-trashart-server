from flask_restful.reqparse import RequestParser

put_parser = RequestParser()
put_parser.add_argument("image", type=str, location="json")
put_parser.add_argument("trash", type=str, location="json")