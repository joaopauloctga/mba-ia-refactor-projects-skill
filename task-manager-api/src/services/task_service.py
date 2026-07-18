"""Task business logic and data access.

- `list_all` eager-loads user + category in one query (fixes the N+1 that ran
  `User.query.get()` and `Category.query.get()` once per task).
- Uses `db.session.get(...)` instead of the deprecated `Model.query.get(...)`.
- The "overdue" rule lives on the model (`Task.is_overdue`) — no more duplicated
  nested if/else across routes.
"""
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from src.extensions import db
from src.models.task import Task
from src.utils.timeutils import utcnow


def _serialize(task):
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    return data


def get(task_id):
    return db.session.get(Task, task_id)


def get_serialized(task_id):
    task = db.session.get(Task, task_id)
    return _serialize(task) if task else None


def list_all():
    tasks = (
        Task.query.options(joinedload(Task.user), joinedload(Task.category))
        .all()
    )
    result = []
    for t in tasks:
        data = _serialize(t)
        data["user_name"] = t.user.name if t.user else None
        data["category_name"] = t.category.name if t.category else None
        result.append(data)
    return result


def create(data):
    task = Task()
    task.title = data["title"]
    task.description = data.get("description", "")
    task.status = data.get("status", "pending")
    task.priority = data.get("priority", 3)
    task.user_id = data.get("user_id")
    task.category_id = data.get("category_id")
    if data.get("due_date_parsed") is not None:
        task.due_date = data["due_date_parsed"]
    tags = data.get("tags")
    if tags is not None:
        task.tags = ",".join(tags) if isinstance(tags, list) else tags
    db.session.add(task)
    db.session.commit()
    return task


def update(task, data):
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "status" in data:
        task.status = data["status"]
    if "priority" in data:
        task.priority = data["priority"]
    if "user_id" in data:
        task.user_id = data["user_id"]
    if "category_id" in data:
        task.category_id = data["category_id"]
    if "due_date" in data:
        task.due_date = data.get("due_date_parsed")
    if "tags" in data:
        tags = data["tags"]
        task.tags = ",".join(tags) if isinstance(tags, list) else tags
    task.updated_at = utcnow()
    db.session.commit()
    return task


def delete(task):
    db.session.delete(task)
    db.session.commit()


def search(query="", status="", priority="", user_id=""):
    q = Task.query
    if query:
        q = q.filter(
            db.or_(Task.title.like(f"%{query}%"), Task.description.like(f"%{query}%"))
        )
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == int(priority))
    if user_id:
        q = q.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in q.all()]


def stats():
    total = Task.query.count()
    by_status = dict(
        db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
    )
    overdue = Task.query.filter(
        Task.due_date.isnot(None),
        Task.due_date < utcnow(),
        Task.status.notin_(["done", "cancelled"]),
    ).count()
    done = by_status.get("done", 0)
    return {
        "total": total,
        "pending": by_status.get("pending", 0),
        "in_progress": by_status.get("in_progress", 0),
        "done": done,
        "cancelled": by_status.get("cancelled", 0),
        "overdue": overdue,
        "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
    }


def parse_due_date(value):
    """Return (parsed_datetime_or_None, error_message_or_None)."""
    if not value:
        return None, None
    try:
        return datetime.strptime(value, "%Y-%m-%d"), None
    except ValueError:
        return None, "Formato de data inválido. Use YYYY-MM-DD"
