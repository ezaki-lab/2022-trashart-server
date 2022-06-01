"""
コンフィグを読み込み、共通変数に挿入する
"""

import yaml

config = {}

with open("./config.yaml") as f:
    config = yaml.safe_load(f)

    if "includes" in config:
        for path in config["includes"]:
            with open("./"+path) as f:
                tmp = yaml.safe_load(f)
                config.update(**tmp)
        del config["includes"]
