"""Sales report business logic — revenue aggregation and discount tiers.

The discount thresholds/rates that used to be magic numbers inside the data
layer now come from config (`DISCOUNT_TIERS`).
"""
from src.config.settings import settings
from src.models import pedido_model


def calcular_relatorio():
    total_pedidos = pedido_model.contar_todos()
    faturamento = pedido_model.somar_faturamento()

    desconto = 0
    for limite, taxa in settings.DISCOUNT_TIERS:
        if faturamento > limite:
            desconto = faturamento * taxa
            break

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pedido_model.contar_por_status("pendente"),
        "pedidos_aprovados": pedido_model.contar_por_status("aprovado"),
        "pedidos_cancelados": pedido_model.contar_por_status("cancelado"),
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
