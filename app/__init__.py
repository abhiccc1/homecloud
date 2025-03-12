# homecloud/app/__init__.py
from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuration (could be loaded from a config object)
    app.config['SECRET_KEY'] = os.getenv('DATABASE_ENCRYPTION_KEY') # Example - use a different secret!
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

    # Initialize extensions (if any - e.g., database, mail) here

    # Register blueprints (views)
    from .views import main_bp
    app.register_blueprint(main_bp)

    return app