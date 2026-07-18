"""Centralized error handling.

One place maps exceptions and 404s to clean JSON responses. Full detail is logged
server-side; the client only gets a generic message (fixes: try/except leaking
str(e) in every handler, verbose errors).
"""
from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(400)
    def bad_request(_e):
        return jsonify({"erro": "Requisição inválida"}), 400

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception("Erro não tratado: %s", e)
        return jsonify({"erro": "Erro interno"}), 500
