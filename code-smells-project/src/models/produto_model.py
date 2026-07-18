"""Produto data access. Parameterized queries only (fixes SQL Injection).

One serializer (`_to_dict`) removes the duplicated row->dict mapping that was
copy-pasted across the old God module.
"""
from src.database.connection import get_connection


def _to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM produtos").fetchall()
    conn.close()
    return [_to_dict(r) for r in rows]


def get_by_id(produto_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    conn.close()
    return _to_dict(row) if row else None


def create(nome, descricao, preco, estoque, categoria):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
        "VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update(produto_id, nome, descricao, preco, estoque, categoria):
    conn = get_connection()
    conn.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, "
        "categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    conn.commit()
    conn.close()
    return True


def delete(produto_id):
    conn = get_connection()
    conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()
    return True


def search(termo=None, categoria=None, preco_min=None, preco_max=None):
    sql = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        sql += " AND (nome LIKE ? OR descricao LIKE ?)"
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        sql += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        sql += " AND preco <= ?"
        params.append(preco_max)

    conn = get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [_to_dict(r) for r in rows]
