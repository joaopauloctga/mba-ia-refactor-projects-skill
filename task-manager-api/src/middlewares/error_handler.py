"""Centralized error handling.

Replaces the scattered bare `except:` blocks in the routes that returned a
generic 500 with no logging. Full detail is logged server-side; the client gets
a clean message.
"""
from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(400)
    def bad_request(_e):
        return jsonify({"error": "Requisição inválida"}), 400

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception("Erro não tratado: %s", e)
        return jsonify({"error": "Erro interno"}), 500
