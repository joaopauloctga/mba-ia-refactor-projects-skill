"""User business logic and data access.

- `list_all` computes task counts with ONE grouped query instead of triggering a
  lazy load per user (fixes N+1 from `len(u.tasks)` in a loop).
- Uses `db.session.get(...)` instead of deprecated `Model.query.get(...)`.
- Authentication verifies the hashed password in code.
"""
from sqlalchemy import func

from src.extensions import db
from src.models.task import Task
from src.models.user import User


def get(user_id):
    return db.session.get(User, user_id)


def get_by_email(email):
    return User.query.filter_by(email=email).first()


def email_taken(email, exclude_id=None):
    existing = User.query.filter_by(email=email).first()
    return existing is not None and existing.id != exclude_id


def list_all():
    counts = dict(
        db.session.query(Task.user_id, func.count(Task.id))
        .group_by(Task.user_id)
        .all()
    )
    result = []
    for u in User.query.all():
        data = u.to_dict()
        data["task_count"] = counts.get(u.id, 0)
        result.append(data)
    return result


def get_with_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None
    data = user.to_dict()
    data["tasks"] = [t.to_dict() for t in user.tasks]
    return data


def create(name, email, password, role="user"):
    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role
    db.session.add(user)
    db.session.commit()
    return user


def update(user, data):
    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        user.email = data["email"]
    if "password" in data:
        user.set_password(data["password"])
    if "role" in data:
        user.role = data["role"]
    if "active" in data:
        user.active = data["active"]
    db.session.commit()
    return user


def delete(user):
    # Remove the user's tasks first to avoid orphaned rows.
    for t in list(user.tasks):
        db.session.delete(t)
    db.session.delete(user)
    db.session.commit()


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None, "invalid"
    if not user.active:
        return None, "inactive"
    return user, None
