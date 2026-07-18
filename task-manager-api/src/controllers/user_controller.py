"""User controllers — thin orchestration + edge validation."""
from flask import jsonify, request

from src.config.settings import settings
from src.services import task_service, user_service
from src.utils.helpers import validate_email


def get_users():
    return jsonify(user_service.list_all()), 200


def get_user(user_id):
    data = user_service.get_with_tasks(user_id)
    if data is None:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(data), 200


def create_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400
    if not email:
        return jsonify({"error": "Email é obrigatório"}), 400
    if not password:
        return jsonify({"error": "Senha é obrigatória"}), 400
    if not validate_email(email):
        return jsonify({"error": "Email inválido"}), 400
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        return jsonify({"error": "Senha deve ter no mínimo 4 caracteres"}), 400
    if user_service.email_taken(email):
        return jsonify({"error": "Email já cadastrado"}), 409
    if role not in settings.VALID_ROLES:
        return jsonify({"error": "Role inválido"}), 400

    user = user_service.create(name, email, password, role)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = user_service.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "email" in data:
        if not validate_email(data["email"]):
            return jsonify({"error": "Email inválido"}), 400
        if user_service.email_taken(data["email"], exclude_id=user_id):
            return jsonify({"error": "Email já cadastrado"}), 409
    if "password" in data and len(data["password"]) < settings.MIN_PASSWORD_LENGTH:
        return jsonify({"error": "Senha muito curta"}), 400
    if "role" in data and data["role"] not in settings.VALID_ROLES:
        return jsonify({"error": "Role inválido"}), 400

    user_service.update(user, data)
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = user_service.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    user_service.delete(user)
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id):
    user = user_service.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(task_service.search(user_id=str(user_id))), 200


def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    user, err = user_service.authenticate(email, password)
    if err == "invalid":
        return jsonify({"error": "Credenciais inválidas"}), 401
    if err == "inactive":
        return jsonify({"error": "Usuário inativo"}), 403

    return jsonify(
        {
            "message": "Login realizado com sucesso",
            "user": user.to_dict(),
            "token": "fake-jwt-token-" + str(user.id),
        }
    ), 200
