"""Category business logic and data access."""
from sqlalchemy import func

from src.extensions import db
from src.models.category import Category
from src.models.task import Task


def get(cat_id):
    return db.session.get(Category, cat_id)


def list_with_counts():
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )
    result = []
    for c in Category.query.all():
        data = c.to_dict()
        data["task_count"] = counts.get(c.id, 0)
        result.append(data)
    return result


def create(name, description="", color="#000000"):
    category = Category()
    category.name = name
    category.description = description
    category.color = color
    db.session.add(category)
    db.session.commit()
    return category


def update(category, data):
    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]
    if "color" in data:
        category.color = data["color"]
    db.session.commit()
    return category


def delete(category):
    db.session.delete(category)
    db.session.commit()
