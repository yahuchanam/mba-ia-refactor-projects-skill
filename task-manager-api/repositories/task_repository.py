from sqlalchemy.orm import joinedload

from database import db
from models.task import Task


class TaskRepository:
    def get(self, task_id):
        return db.session.get(
            Task,
            task_id,
            options=(joinedload(Task.user), joinedload(Task.category)),
        )

    def list_page(self, page, per_page):
        statement = (
            db.select(Task)
            .options(joinedload(Task.user), joinedload(Task.category))
            .order_by(Task.id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return db.session.scalars(statement).all()

    def search(self, filters, page, per_page):
        statement = db.select(Task).order_by(Task.id)
        query = filters.get("q")
        if query:
            pattern = f"%{query}%"
            statement = statement.where(
                db.or_(
                    Task.title.ilike(pattern),
                    Task.description.ilike(pattern),
                )
            )
        if filters.get("status"):
            statement = statement.where(Task.status == filters["status"])
        if filters.get("priority") is not None:
            statement = statement.where(Task.priority == filters["priority"])
        if filters.get("user_id") is not None:
            statement = statement.where(Task.user_id == filters["user_id"])

        statement = statement.offset((page - 1) * per_page).limit(per_page)
        return db.session.scalars(statement).all()

    def list_for_user(self, user_id, page, per_page):
        statement = (
            db.select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return db.session.scalars(statement).all()

    def count_all(self):
        return db.session.scalar(db.select(db.func.count(Task.id))) or 0

    def count_by_status(self):
        statement = db.select(Task.status, db.func.count(Task.id)).group_by(Task.status)
        return dict(db.session.execute(statement).all())

    def count_overdue(self, now):
        statement = db.select(db.func.count(Task.id)).where(
            Task.due_date.is_not(None),
            Task.due_date < now,
            Task.status.not_in(("done", "cancelled")),
        )
        return db.session.scalar(statement) or 0

    def add(self, task):
        db.session.add(task)

    def delete(self, task):
        db.session.delete(task)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()
