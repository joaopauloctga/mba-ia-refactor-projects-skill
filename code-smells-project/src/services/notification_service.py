"""Notification side-effects behind a small interface.

Replaces the raw `print("ENVIANDO EMAIL/SMS/PUSH ...")` calls that were mixed
into the controllers. Uses the logging module (fixes: print-as-logging, side
effects in the controller). In a real system this would call email/SMS/push
providers; here it logs through a proper logger.
"""
import logging

logger = logging.getLogger("loja.notifications")


def notificar_pedido_criado(pedido_id, usuario_id):
    logger.info("Pedido %s criado para usuário %s (email/sms/push)", pedido_id, usuario_id)


def notificar_mudanca_status(pedido_id, status):
    if status == "aprovado":
        logger.info("Pedido %s aprovado — preparar envio.", pedido_id)
    elif status == "cancelado":
        logger.info("Pedido %s cancelado — devolver estoque.", pedido_id)
