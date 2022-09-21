"""
JSONのスキーマをチェック
"""

from flask import request
from functools import wraps
from services.server import response as res
from utils.check_scheme import CheckScheme

def json_scheme(scheme):
    def _json_scheme(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CheckScheme(scheme).check(request.json):
                return res.bad_request({
                    "message": "This request json is invalid."
                })

            return func(json=request.json, *args, **kwargs)
        return wrapper
    return _json_scheme
