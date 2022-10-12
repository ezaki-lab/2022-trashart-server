import os

def listdir_relative(folder_name: str) -> list[str]:
    files = os.listdir(folder_name)
    return [os.path.join(folder_name, files) for files in files]
