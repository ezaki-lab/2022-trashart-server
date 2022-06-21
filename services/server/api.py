"""
APIの Blueprint を統合
"""

from flask import Blueprint

import api.root as root
import api.user as user
import api.crafting as crafting

app = Blueprint(
    "api",
    __name__
)

app.register_blueprint(root.app)
app.register_blueprint(user.app)
app.register_blueprint(crafting.app)
