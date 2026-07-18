"""System routes — health and index."""
from flask import Blueprint, jsonify

from src.utils.timeutils import utcnow

system_bp = Blueprint("system", __name__)


@system_bp.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": str(utcnow())})


@system_bp.route("/")
def index():
    return jsonify({"message": "Task Manager API", "version": "1.0"})
