from flask_restful.reqparse import RequestParser

post_parser = RequestParser()
post_parser.add_argument("base_id", type=str, location="json")

blueprint_put_parser = RequestParser()
blueprint_put_parser.add_argument("data", required=True, type=str, location="json")