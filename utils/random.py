import random
import string

def generate_str(n: int, hex_only: bool=False) -> str:
    """
    指定した長さのランダムの文字列を生成する
    """

    lis = []

    if not hex_only:
        lis = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    else:
        lis = [random.choice("0123456789abcdef") for i in range(n)]

    return "".join(lis)
