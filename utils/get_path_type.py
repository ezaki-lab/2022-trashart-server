import os

def get_path_type(directory: str, filepath: str) -> int:
    """
    指定されたパス先の種別を返す
        0: ファイルは存在する
        1: .html を末尾に付ければ存在する
        2: index.html を末尾に付ければ存在する
        -1: ファイルは存在しない
    """

    path = os.path.join(
        os.path.abspath(directory),
        filepath
    )

    if os.path.isfile(path):
        return 0

    if os.path.isfile(path+".html"):
        return 1

    if os.path.isfile(path+"/index.html"):
        return 2

    return -1
