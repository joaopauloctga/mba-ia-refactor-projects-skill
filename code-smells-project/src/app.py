"""Composition root — application factory.

Assembles the app: loads config, enables CORS with an allowlist, initializes the
database, registers the routing blueprint and the centralized error handlers.
Contains no business logic.
"""
import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import settings
from src.database.connection import init_db
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import api


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    CORS(app, origins=settings.CORS_ORIGINS)

    init_db()

    app.register_blueprint(api)
    register_error_handlers(app)

    return app
