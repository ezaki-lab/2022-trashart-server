"""
Socket.ioの名前空間を統合
"""

from . import socketio
from ws.test import Test

socketio.on_namespace(Test('/test'))
