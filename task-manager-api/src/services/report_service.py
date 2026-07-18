"""Reporting business logic.

The old summary route ran a per-user query inside a loop over all users (N+1).
Here the per-user productivity is computed with two grouped aggregate queries.
Output shapes are preserved.
"""
from datetime import timedelta

from sqlalchemy import func

from src.extensions import db
from src.models.category import Category
from src.models.task import Task
from src.models.user import User
from src.utils.helpers import calculate_percentage
from src.utils.timeutils import utcnow


def summary():
    now = utcnow()
    seven_days_ago = now - timedelta(days=7)

    status_counts = dict(
        db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
    )
    priority_counts = dict(
        db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    )

    overdue_tasks = Task.query.filter(
        Task.due_date.isnot(None),
        Task.due_date < now,
        Task.status.notin_(["done", "cancelled"]),
    ).all()
    overdue_list = [
        {
            "id": t.id,
            "title": t.title,
            "due_date": str(t.due_date),
            "days_overdue": (now - t.due_date).days,
        }
        for t in overdue_tasks
    ]

    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == "done", Task.updated_at >= seven_days_ago
    ).count()

    # Per-user productivity in 2 grouped queries (no N+1).
    totals = dict(
        db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all()
    )
    completed = dict(
        db.session.query(Task.user_id, func.count(Task.id))
        .filter(Task.status == "done")
        .group_by(Task.user_id)
        .all()
    )
    user_stats = []
    for u in User.query.all():
        total = totals.get(u.id, 0)
        done = completed.get(u.id, 0)
        user_stats.append(
            {
                "user_id": u.id,
                "user_name": u.name,
                "total_tasks": total,
                "completed_tasks": done,
                "completion_rate": calculate_percentage(done, total),
            }
        )

    return {
        "generated_at": str(now),
        "overview": {
            "total_tasks": Task.query.count(),
            "total_users": User.query.count(),
            "total_categories": Category.query.count(),
        },
        "tasks_by_status": {
            "pending": status_counts.get("pending", 0),
            "in_progress": status_counts.get("in_progress", 0),
            "done": status_counts.get("done", 0),
            "cancelled": status_counts.get("cancelled", 0),
        },
        "tasks_by_priority": {
            "critical": priority_counts.get(1, 0),
            "high": priority_counts.get(2, 0),
            "medium": priority_counts.get(3, 0),
            "low": priority_counts.get(4, 0),
            "minimal": priority_counts.get(5, 0),
        },
        "overdue": {"count": len(overdue_list), "tasks": overdue_list},
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }


def user_report(user):
    tasks = user.tasks
    total = len(tasks)
    done = pending = in_progress = cancelled = overdue = high_priority = 0
    for t in tasks:
        if t.status == "done":
            done += 1
        elif t.status == "pending":
            pending += 1
        elif t.status == "in_progress":
            in_progress += 1
        elif t.status == "cancelled":
            cancelled += 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():
            overdue += 1

    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "cancelled": cancelled,
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": calculate_percentage(done, total),
        },
    }
