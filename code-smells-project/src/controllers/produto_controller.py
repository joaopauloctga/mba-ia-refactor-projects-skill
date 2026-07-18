"""Produto controllers — parse/validate request, call the model, shape response.

Thin: no SQL, no domain math. Validation lives at the edge (here); persistence
lives in the model.
"""
from flask import jsonify, request

from src.config.settings import settings
from src.models import produto_model


def listar_produtos():
    produtos = produto_model.get_all()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = produto_model.get_by_id(id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)
    preco_min = float(preco_min) if preco_min else None
    preco_max = float(preco_max) if preco_max else None

    resultados = produto_model.search(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def _validar_produto(dados):
    if not dados:
        return "Dados inválidos"
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            return f"{campo.capitalize()} é obrigatório"
    if dados["preco"] < 0:
        return "Preço não pode ser negativo"
    if dados["estoque"] < 0:
        return "Estoque não pode ser negativo"
    nome = dados["nome"]
    if len(nome) < settings.NOME_MIN:
        return "Nome muito curto"
    if len(nome) > settings.NOME_MAX:
        return "Nome muito longo"
    categoria = dados.get("categoria", "geral")
    if categoria not in settings.CATEGORIAS_VALIDAS:
        return f"Categoria inválida. Válidas: {settings.CATEGORIAS_VALIDAS}"
    return None


def criar_produto():
    dados = request.get_json(silent=True)
    erro = _validar_produto(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    novo_id = produto_model.create(
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    if not produto_model.get_by_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404

    dados = request.get_json(silent=True)
    erro = _validar_produto(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    produto_model.update(
        id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    if not produto_model.get_by_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    produto_model.delete(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
