# __init__.py
from flask import Flask


def create_app():
    app = Flask(__name__)
    # Configure your app settings, register blueprints, etc.
    return app
