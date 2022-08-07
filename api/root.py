"""
ページAPI
"""

from flask import Blueprint, jsonify, make_response
from datetime import datetime

app = Blueprint("root", __name__)

@app.route("/")
def root():
    return make_response(jsonify({
        "message": "MARINE TRASHART",
        "time": datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
    }), 200)