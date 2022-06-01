"""
ページAPI
"""

from flask import abort, Blueprint, jsonify, make_response

app = Blueprint("root", __name__)

@app.route("/")
def root():
    return make_response(jsonify({
        "message": "MARINE TRASHART"
    }), 200)

@app.route("/<path:filepath>")
def error(filepath: str):
    abort(404)
