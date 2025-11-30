import os
from dotenv import load_dotenv
from flask import Flask

from app.routes import bp as main_bp

load_dotenv()  # Load environment variables from .env file


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "my-secret-key")  # For flash messages

    # Register routes blueprint
    app.register_blueprint(main_bp)

    return app
