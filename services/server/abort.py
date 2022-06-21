"""
Abort
"""

from flask import jsonify, make_response
from . import app

@app.route("/test")
def test():
    return "OK?"

@app.errorhandler(400)
def bad_request(e):
    return make_response(jsonify({
        "message": "Bad Request"
    }), 400)

@app.errorhandler(401)
def unauthorized(e):
    return make_response(jsonify({
        "message": "Unauthorized"
    }), 401)

@app.errorhandler(403)
def forbidden(e):
    return make_response(jsonify({
        "message": "Forbidden"
    }), 403)

@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify({
        "message": "Not Found"
    }), 404)

@app.errorhandler(405)
def not_found(e):
    return make_response(jsonify({
        "message": "Method Not Allowed"
    }), 405)

@app.errorhandler(409)
def conflict(e):
    return make_response(jsonify({
        "message": "Conflict"
    }), 409)

@app.errorhandler(500)
def server_error(e):
    return make_response(jsonify({
        "message": "Internal Server Error"
    }), 500)
