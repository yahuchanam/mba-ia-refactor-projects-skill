from database import db
from models.task import Task
from models.user import User


class UserRepository:
    def get(self, user_id):
        return db.session.get(User, user_id)

    def get_by_email(self, email):
        statement = db.select(User).where(User.email == email)
        return db.session.scalar(statement)

    def list_with_task_counts(self, page, per_page):
        statement = (
            db.select(User, db.func.count(Task.id))
            .outerjoin(Task, Task.user_id == User.id)
            .group_by(User.id)
            .order_by(User.id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return db.session.execute(statement).all()

    def add(self, user):
        db.session.add(user)

    def delete(self, user):
        db.session.delete(user)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()
