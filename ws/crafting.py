"""
製作ソケット
"""

from flask import request
from flask_socketio import emit, sleep, start_background_task

from main import socketio

NAMESPACE = "/crafting"

thread = None
user_count = 0

@socketio.on("connect")
def connect():
    print("接続", request.sid)
    global user_count
    user_count += 1
    emit('count_update', {'user_count': user_count}, broadcast=True)
    # global thread
    # if thread is None:
    #     thread = start_background_task(target=background_thread)
    emit("my response", {"data": "Connected", "count": 0})

@socketio.on("disconnect")
def disconnect():
    print("切断", request.sid)
    global user_count
    user_count -= 1
    # 接続者数の更新（全員向け）
    emit('count_update', {'user_count': user_count}, broadcast=True)

# def background_thread():
#     count = 0
#     while True:
#         sleep(10)
#         count += 1
#         emit(
#             "my response",
#             {"data": "Server generated event", "count": count},
#             namespace=NAMESPACE
#         )
