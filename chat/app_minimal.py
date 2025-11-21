import os
import sys

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from chat import utils
from chat.config import get_config
from chat.socketio_signals import io_connect, io_disconnect, io_join_room, io_on_message

app = Flask(__name__, static_url_path="", static_folder="../client/build")
app.config.from_object(get_config())
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


def run_app():
    # Create redis connection etc.
    # Here we initialize our database, create demo data (if it's necessary)
    # TODO: maybe we need to do it for gunicorn run also?
    utils.init_redis()
    # Skip session initialization for now
    # sess.init_app(app)

    # moved to this method bc it only applies to app.py direct launch
    # Get port from the command-line arguments or environment variables
    arg = sys.argv[1:]
    # TODO: js client is hardcoded to proxy all to 8000 port, maybe change it?
    port = int(arg[0]) if len(arg) else int(os.environ.get("PORT", 8000))

    # Load demo users when running locally
    if os.environ.get("REDIS_ENDPOINT_URL", "127.0.0.1:6379") == "127.0.0.1:6379":
        from chat.demo_data import init_demo_users

        init_demo_users()
    socketio.run(app, port=port, debug=False, host="0.0.0.0")


# Import routes after app is created
from chat import routes