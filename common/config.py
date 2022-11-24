"""
コンフィグを読み込み、共通変数に挿入する
"""

import yaml
from tensorflow.keras.models import load_model

config = {}

with open("./config.yaml") as f:
    config = yaml.safe_load(f)

    if "includes" in config:
        for path in config["includes"]:
            with open("./"+path) as f:
                tmp = yaml.safe_load(f)
                config.update(**tmp)
        del config["includes"]

config["PLASTIC_CLASSIFICATION_MODEL"] = load_model("ml_models/plastic-classification.h5")
config["PLASTIC_CLASSIFICATION_NEXT_MODEL"] = load_model("ml_models/plastic-classification-next.h5")
