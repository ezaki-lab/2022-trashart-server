"""
ページAPI
"""

from flask import Blueprint, jsonify, make_response

app = Blueprint("root", __name__)

@app.route("/")
def root():
    return make_response(jsonify({
        "message": "MARINE TRASHART"
    }), 200)
