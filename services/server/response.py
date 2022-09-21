from flask import jsonify, make_response

def ok(body: dict):
    return make_response(jsonify(body), 200)

def created(body: dict):
    return make_response(jsonify(body), 201)

def accepted(body: dict):
    return make_response(jsonify(body), 202)

def no_content(body: dict):
    return make_response(jsonify(body), 204)
