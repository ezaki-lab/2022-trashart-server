"""
JSONのスキーマをチェック
"""

from flask import jsonify, make_response, request
from functools import wraps
from utils.check_scheme import CheckScheme

def json_scheme(scheme):
    def _json_scheme(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CheckScheme(scheme).check(request.json):
                return make_response(jsonify({
                    'message': 'This request json is invalid.'
                }), 400)

            return func(json=request.json, *args, **kwargs)
        return wrapper
    return _json_scheme
