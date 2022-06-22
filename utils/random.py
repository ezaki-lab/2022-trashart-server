import random
import string

def generate_str(n: int) -> str:
    """
    指定した長さのランダムの文字列を生成する
    """
    lis = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return "".join(lis)
