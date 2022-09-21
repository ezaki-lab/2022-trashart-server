from flask import jsonify, make_response

def ok(body: dict):
    return make_response(jsonify(body), 200)

def created(body: dict):
    return make_response(jsonify(body), 201)

def accepted(body: dict):
    return make_response(jsonify(body), 202)

def no_content(body: dict):
    return make_response(jsonify(body), 204)

def bad_request(body: dict):
    return make_response(jsonify(body), 400)

def unauthorized(body: dict):
    return make_response(jsonify(body), 401)

def forbidden(body: dict):
    return make_response(jsonify(body), 403)

def not_found(body: dict):
    return make_response(jsonify(body), 404)

def not_found(body: dict):
    return make_response(jsonify(body), 405)

def conflict(body: dict):
    return make_response(jsonify(body), 409)

def server_error(body: dict):
    return make_response(jsonify(body), 500)
