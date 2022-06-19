from flask_restful.reqparse import RequestParser

post_parser = RequestParser()
post_parser.add_argument("base_id", type=str, location="json")
