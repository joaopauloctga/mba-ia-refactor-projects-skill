"""System controllers — index, health and a guarded admin reset.

- `/health` no longer leaks the SECRET_KEY or debug flag (fixes Sensitive Data
  Exposure).
- The old `/admin/query` arbitrary-SQL endpoint (remote code execution) is
  REMOVED entirely.
- `/admin/reset-db` now requires an admin token from config; with no token
  configured the destructive operation is disabled (fixes missing auth on a
  destructive endpoint).
"""
from flask import jsonify, request

from src.config.settings import settings
from src.database.connection import get_connection


def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


def health_check():
    conn = get_connection()
    cur = conn.cursor()
    counts = {}
    for tabela in ("produtos", "usuarios", "pedidos"):
        counts[tabela] = cur.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    conn.close()
    return jsonify({"status": "ok", "database": "connected", "counts": counts, "versao": "1.0.0"}), 200


def reset_database():
    token = request.headers.get("X-Admin-Token", "")
    if not settings.ADMIN_TOKEN or token != settings.ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 403

    conn = get_connection()
    cur = conn.cursor()
    for tabela in ("itens_pedido", "pedidos", "produtos", "usuarios"):
        cur.execute(f"DELETE FROM {tabela}")
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
