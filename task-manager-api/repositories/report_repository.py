from sqlalchemy import case

from database import db
from models.category import Category
from models.task import Task
from models.user import User


class ReportRepository:
    def entity_counts(self):
        return {
            "total_tasks": self._count(Task.id),
            "total_users": self._count(User.id),
            "total_categories": self._count(Category.id),
        }

    def task_counts_by_status(self):
        statement = db.select(Task.status, db.func.count(Task.id)).group_by(Task.status)
        return dict(db.session.execute(statement).all())

    def task_counts_by_priority(self):
        statement = db.select(Task.priority, db.func.count(Task.id)).group_by(
            Task.priority
        )
        return dict(db.session.execute(statement).all())

    def overdue_tasks(self, now, limit=100):
        statement = (
            db.select(Task)
            .where(
                Task.due_date.is_not(None),
                Task.due_date < now,
                Task.status.not_in(("done", "cancelled")),
            )
            .order_by(Task.due_date)
            .limit(limit)
        )
        return db.session.scalars(statement).all()

    def count_recent_created(self, since):
        statement = db.select(db.func.count(Task.id)).where(Task.created_at >= since)
        return db.session.scalar(statement) or 0

    def count_recent_completed(self, since):
        statement = db.select(db.func.count(Task.id)).where(
            Task.status == "done",
            Task.updated_at >= since,
        )
        return db.session.scalar(statement) or 0

    def user_productivity(self, limit=100):
        completed = db.func.sum(case((Task.status == "done", 1), else_=0))
        statement = (
            db.select(
                User.id,
                User.name,
                db.func.count(Task.id),
                completed,
            )
            .outerjoin(Task, Task.user_id == User.id)
            .group_by(User.id, User.name)
            .order_by(User.id)
            .limit(limit)
        )
        return db.session.execute(statement).all()

    def user_task_statistics(self, user_id, now):
        statement = db.select(
            db.func.count(Task.id).label("total"),
            db.func.sum(case((Task.status == "done", 1), else_=0)).label("done"),
            db.func.sum(case((Task.status == "pending", 1), else_=0)).label("pending"),
            db.func.sum(case((Task.status == "in_progress", 1), else_=0)).label(
                "in_progress"
            ),
            db.func.sum(case((Task.status == "cancelled", 1), else_=0)).label(
                "cancelled"
            ),
            db.func.sum(
                case(
                    (
                        db.and_(
                            Task.due_date.is_not(None),
                            Task.due_date < now,
                            Task.status.not_in(("done", "cancelled")),
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("overdue"),
            db.func.sum(case((Task.priority <= 2, 1), else_=0)).label("high_priority"),
        ).where(Task.user_id == user_id)
        return db.session.execute(statement).one()

    def _count(self, column):
        return db.session.scalar(db.select(db.func.count(column))) or 0
