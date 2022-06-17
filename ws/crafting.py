"""
製作ソケット
"""

from flask import request
from flask_socketio import emit, sleep, start_background_task

from main import socketio

NAMESPACE = "/crafting"

thread = None

@socketio.on("connect", namespace=NAMESPACE)
def connect():
    print("接続", request.sid)
    global thread
    if thread is None:
        thread = start_background_task(target=background_thread)
    emit("my response", {"data": "Connected", "count": 0})

@socketio.on("disconnect", namespace=NAMESPACE)
def disconnect():
    print("切断", request.sid)

def background_thread():
    count = 0
    while True:
        sleep(10)
        count += 1
        emit(
            "my response",
            {"data": "Server generated event", "count": count},
            namespace=NAMESPACE
        )
