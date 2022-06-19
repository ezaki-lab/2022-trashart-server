"""
Content-Type ヘッダーをチェック
"""

from functools import wraps
from flask import jsonify, make_response, request

def content_type(value):
    def _content_type(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            if not request.headers.get("Content-Type") == value:
                return make_response(jsonify({
                    'message': 'Content-Type \'{}\' required.'.format(value)
                }), 400)

            return func(*args,**kwargs)
        return wrapper
    return _content_type
