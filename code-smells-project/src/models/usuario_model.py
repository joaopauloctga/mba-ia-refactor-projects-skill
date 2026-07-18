"""Usuario data access.

- Parameterized queries (fixes SQL Injection).
- Passwords are hashed on create and verified with a real KDF (fixes Plaintext
  Passwords / weak auth).
- Serialization NEVER returns the password hash (fixes Sensitive Data Exposure).
"""
from werkzeug.security import check_password_hash, generate_password_hash

from src.database.connection import get_connection


def _public_dict(row):
    """Public representation — no password field."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    return [_public_dict(r) for r in rows]


def get_by_id(usuario_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    conn.close()
    return _public_dict(row) if row else None


def email_exists(email):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return row is not None


def create(nome, email, senha, tipo="cliente"):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def authenticate(email, senha):
    """Fetch by email, verify the hash in code (never compare passwords in SQL)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    if row and check_password_hash(row["senha"], senha):
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
        }
    return None
