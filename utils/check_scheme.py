"""
正しいスキーマが入力されているかをチェック

例:
    CheckScheme({
        "name": str,
        "age": int
    }).check({"name": "takara", "age": 18}) -> True

    CheckScheme({
        "name": str,
        "age": int
    }).check({"name": "takara", "age": "unknown"}) -> False

    CheckScheme({
        "name (required)": str,
        "age": int
    }).check({"age": 18}) -> False
"""

from typing import Tuple

class CheckScheme:
    def __init__(self, scheme: dict):
        self.scheme = scheme

    def check(self, dic: dict) -> bool:
        self.__check(self.scheme, dic)

    def __check(self, scheme, dic: any) -> bool:
        if isinstance(scheme, dict):
            if not isinstance(dic, dict):
                return False
            for key, value in scheme.items():
                key, required = self.__get_key_info(key)
                if key not in dic and required:
                    return False
                if key not in dic:
                    continue
                if not self.__check(value, dic[key]):
                    return False
            return True

        elif isinstance(scheme, list):
            if not isinstance(dic, list):
                return False
            for item in dic:
                if not self.__check(scheme[0], item):
                    return False
            return True

        else:
            return isinstance(dic, scheme)

    def __get_key_info(self, key: str) -> Tuple[str, bool]:
        return key.replace(" (required)", ""), key.endswith(" (required)")
