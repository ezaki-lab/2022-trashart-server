"""
Content-Type ヘッダーをチェック
"""

from flask import request
from functools import wraps
from services.server import response as res

def content_type(value):
    def _content_type(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.headers.get("Content-Type") == value:
                return res.bad_request({
                    "message": "Content-Type \'{}\' required.".format(value)
                })

            return func(*args, **kwargs)
        return wrapper
    return _content_type
