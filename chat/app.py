import os
import sys

from flask import Flask
from flask_cors import CORS

from chat.config import get_config

app = Flask(__name__, static_url_path="", static_folder="../client/build")
app.config.from_object(get_config())
CORS(app)

def run_app():
    # Get port from the command-line arguments or environment variables
    arg = sys.argv[1:]
    port = int(arg[0]) if len(arg) else int(os.environ.get("PORT", 8000))

    # Load demo users when running locally
    if os.environ.get("REDIS_ENDPOINT_URL", "127.0.0.1:6379") == "127.0.0.1:6379":
        try:
            from chat.demo_data import create
            create()
            print("Demo data loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not load demo data: {e}")
    
    app.run(port=port, debug=True, host="0.0.0.0")


# Import routes after app is created
try:
    from chat import routes
except ImportError:
    print("Warning: Could not import routes, creating basic route")
    @app.route('/')
    def hello():
        return app.send_static_file("index.html")