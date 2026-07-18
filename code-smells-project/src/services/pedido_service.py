"""Order business logic — stock validation, total calculation, atomic creation.

Extracted out of the old God module: the controller now just parses the request
and calls this service (fixes: business logic buried in the data layer / fat
handlers). The whole order is created in a single transaction.
"""
from src.database.connection import get_connection
from src.models import pedido_model


def criar_pedido(usuario_id, itens):
    """Validate stock, compute the total, persist order + items, decrement stock.

    Returns {"pedido_id", "total"} on success or {"erro": ...} on a domain error.
    """
    conn = get_connection()
    try:
        total = 0
        # validate + price every item before writing anything
        produtos = {}
        for item in itens:
            produto = pedido_model.buscar_produto_para_pedido(conn, item["produto_id"])
            if produto is None:
                return {"erro": f"Produto {item['produto_id']} não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": f"Estoque insuficiente para {produto['nome']}"}
            produtos[item["produto_id"]] = produto
            total += produto["preco"] * item["quantidade"]

        pedido_id = pedido_model.inserir_pedido(conn, usuario_id, total)
        for item in itens:
            preco = produtos[item["produto_id"]]["preco"]
            pedido_model.inserir_item(
                conn, pedido_id, item["produto_id"], item["quantidade"], preco
            )
            pedido_model.baixar_estoque(conn, item["produto_id"], item["quantidade"])

        conn.commit()
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
