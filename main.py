import common
import logger
from services.server import create_server, socketio

server = create_server(debug=False)

if __name__ == "__main__":
    # サーバーを起動
    socketio.run(server)
