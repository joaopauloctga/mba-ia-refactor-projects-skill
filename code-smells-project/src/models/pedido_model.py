"""Pedido data access.

- Parameterized queries (fixes SQL Injection).
- List endpoints use a single JOIN instead of nested per-row queries
  (fixes N+1: was 1 + N + N*M queries, now 2 queries total).
- Write helpers accept a shared connection so the order workflow runs in one
  transaction (used by pedido_service).
"""
from src.database.connection import get_connection


# --- write helpers (operate on a caller-provided connection / transaction) ---

def buscar_produto_para_pedido(conn, produto_id):
    return conn.execute(
        "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
        (produto_id,),
    ).fetchone()


def inserir_pedido(conn, usuario_id, total):
    cur = conn.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    return cur.lastrowid


def inserir_item(conn, pedido_id, produto_id, quantidade, preco_unitario):
    conn.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
        "VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )


def baixar_estoque(conn, produto_id, quantidade):
    conn.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id),
    )


def update_status(pedido_id, novo_status):
    conn = get_connection()
    conn.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id)
    )
    conn.commit()
    conn.close()
    return True


# --- read helpers (own their connection) ---

def _com_itens(conn, pedidos):
    """Attach items to a list of order rows using ONE JOIN query (no N+1)."""
    ids = [p["id"] for p in pedidos]
    itens_por_pedido = {}
    if ids:
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(
            f"""
            SELECT ip.pedido_id, ip.produto_id, ip.quantidade,
                   ip.preco_unitario, p.nome AS produto_nome
            FROM itens_pedido ip
            LEFT JOIN produtos p ON p.id = ip.produto_id
            WHERE ip.pedido_id IN ({placeholders})
            """,
            ids,
        ).fetchall()
        for r in rows:
            itens_por_pedido.setdefault(r["pedido_id"], []).append(
                {
                    "produto_id": r["produto_id"],
                    "produto_nome": r["produto_nome"] or "Desconhecido",
                    "quantidade": r["quantidade"],
                    "preco_unitario": r["preco_unitario"],
                }
            )

    result = []
    for p in pedidos:
        result.append(
            {
                "id": p["id"],
                "usuario_id": p["usuario_id"],
                "status": p["status"],
                "total": p["total"],
                "criado_em": p["criado_em"],
                "itens": itens_por_pedido.get(p["id"], []),
            }
        )
    return result


def list_by_user(usuario_id):
    conn = get_connection()
    pedidos = conn.execute(
        "SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)
    ).fetchall()
    result = _com_itens(conn, pedidos)
    conn.close()
    return result


def list_all():
    conn = get_connection()
    pedidos = conn.execute("SELECT * FROM pedidos").fetchall()
    result = _com_itens(conn, pedidos)
    conn.close()
    return result


# --- aggregates for reporting ---

def contar_todos():
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    conn.close()
    return n


def somar_faturamento():
    conn = get_connection()
    total = conn.execute("SELECT SUM(total) FROM pedidos").fetchone()[0]
    conn.close()
    return total or 0


def contar_por_status(status):
    conn = get_connection()
    n = conn.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,)
    ).fetchone()[0]
    conn.close()
    return n
