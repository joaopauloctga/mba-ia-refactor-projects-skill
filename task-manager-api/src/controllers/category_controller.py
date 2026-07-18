"""Category controllers — thin orchestration."""
from flask import jsonify, request

from src.services import category_service


def get_categories():
    return jsonify(category_service.list_with_counts()), 200


def create_category():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    name = data.get("name")
    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400

    category = category_service.create(
        name, data.get("description", ""), data.get("color", "#000000")
    )
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    category = category_service.get(cat_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404
    data = request.get_json(silent=True) or {}
    category_service.update(category, data)
    return jsonify(category.to_dict()), 200


def delete_category(cat_id):
    category = category_service.get(cat_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404
    category_service.delete(category)
    return jsonify({"message": "Categoria deletada"}), 200
