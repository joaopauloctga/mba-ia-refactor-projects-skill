"""Composition root — application factory.

Loads config from the environment, initializes the ORM, enables CORS with an
allowlist, registers the blueprints (Views) and the centralized error handlers,
and creates the tables. No business logic here.
"""
import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import settings
from src.extensions import db
from src.middlewares.error_handler import register_error_handlers


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    CORS(app, origins=settings.CORS_ORIGINS)
    db.init_app(app)

    # Import models so SQLAlchemy is aware of them before create_all().
    from src import models  # noqa: F401
    from src.routes.report_routes import report_bp
    from src.routes.system_routes import system_bp
    from src.routes.task_routes import task_bp
    from src.routes.user_routes import user_bp

    app.register_blueprint(system_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app
