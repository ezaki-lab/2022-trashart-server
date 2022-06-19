"""
ロギングデコレータ
"""

from functools import wraps
import logging
from flask import abort, request

def logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # アクセス解析のためのロギング
        logging.info("|{}| {} |{}|".format(
            request.method, request.full_path, request.remote_addr
        ))

        result = None
        try:
            result = func(*args, **kwargs)

        except Exception as e:
            print(
                "\n###################################\n#  ERROR\n###################################\n")
            print(e)
            logging.debug(e)
            abort(e.code)

        return result

    return wrapper
