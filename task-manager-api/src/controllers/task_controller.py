"""Task controllers — parse/validate request, call the service, shape response.

Thin: no queries, no serialization loops. Business logic and data access live in
`task_service`.
"""
from flask import jsonify, request

from src.config.settings import settings
from src.services import task_service


def _validate_common(data, partial=False):
    """Return an error string or None. `partial` allows missing fields (PUT)."""
    if "title" in data:
        title = data["title"]
        if not title or len(title) < settings.MIN_TITLE_LENGTH:
            return "Título muito curto"
        if len(title) > settings.MAX_TITLE_LENGTH:
            return "Título muito longo"
    elif not partial:
        return "Título é obrigatório"

    if "status" in data and data["status"] not in settings.VALID_STATUSES:
        return "Status inválido"
    if "priority" in data:
        p = data["priority"]
        if p < settings.MIN_PRIORITY or p > settings.MAX_PRIORITY:
            return f"Prioridade deve ser entre {settings.MIN_PRIORITY} e {settings.MAX_PRIORITY}"
    return None


def get_tasks():
    return jsonify(task_service.list_all()), 200


def get_task(task_id):
    data = task_service.get_serialized(task_id)
    if data:
        return jsonify(data), 200
    return jsonify({"error": "Task não encontrada"}), 404


def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    err = _validate_common(data, partial=False)
    if err:
        return jsonify({"error": err}), 400

    from src.services import category_service, user_service

    if data.get("user_id") and not user_service.get(data["user_id"]):
        return jsonify({"error": "Usuário não encontrado"}), 404
    if data.get("category_id") and not category_service.get(data["category_id"]):
        return jsonify({"error": "Categoria não encontrada"}), 404

    due_parsed, date_err = task_service.parse_due_date(data.get("due_date"))
    if date_err:
        return jsonify({"error": date_err}), 400
    data["due_date_parsed"] = due_parsed

    task = task_service.create(data)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = task_service.get(task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    err = _validate_common(data, partial=True)
    if err:
        return jsonify({"error": err}), 400

    from src.services import category_service, user_service

    if data.get("user_id") and not user_service.get(data["user_id"]):
        return jsonify({"error": "Usuário não encontrado"}), 404
    if data.get("category_id") and not category_service.get(data["category_id"]):
        return jsonify({"error": "Categoria não encontrada"}), 404

    if "due_date" in data:
        due_parsed, date_err = task_service.parse_due_date(data.get("due_date"))
        if date_err:
            return jsonify({"error": date_err}), 400
        data["due_date_parsed"] = due_parsed

    task_service.update(task, data)
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = task_service.get(task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    task_service.delete(task)
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    return jsonify(
        task_service.search(
            request.args.get("q", ""),
            request.args.get("status", ""),
            request.args.get("priority", ""),
            request.args.get("user_id", ""),
        )
    ), 200


def task_stats():
    return jsonify(task_service.stats()), 200
