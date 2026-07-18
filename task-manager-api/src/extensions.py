"""Shared Flask extensions (the SQLAlchemy handle).

Kept in its own module so models, services and the app factory can all import
`db` without importing the application (avoids circular imports).
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
