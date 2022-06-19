import common
import logger
from services.server import create_app, socketio

app = create_app(debug=False)

if __name__ == "__main__":
    # サーバーを起動
    socketio.run(app)
