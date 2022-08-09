"""
APIの Blueprint を統合
"""

from flask import Blueprint

import api.root as root
import api.user as user
import api.crafting as crafting
import api.storage as storage
import api.user2 as user2
import api.share as share

app = Blueprint(
    "api",
    __name__
)

app.register_blueprint(root.app)
app.register_blueprint(user.app)
app.register_blueprint(crafting.app)
app.register_blueprint(storage.app)
app.register_blueprint(user2.app)
app.register_blueprint(share.app)
