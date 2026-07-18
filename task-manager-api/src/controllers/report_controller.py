"""Report controllers — thin orchestration."""
from flask import jsonify

from src.services import report_service, user_service


def summary_report():
    return jsonify(report_service.summary()), 200


def user_report(user_id):
    user = user_service.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(report_service.user_report(user)), 200
