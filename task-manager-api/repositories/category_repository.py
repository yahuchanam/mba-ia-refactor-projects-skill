from database import db
from models.category import Category
from models.task import Task


class CategoryRepository:
    def get(self, category_id):
        return db.session.get(Category, category_id)

    def list_with_task_counts(self, page, per_page):
        statement = (
            db.select(Category, db.func.count(Task.id))
            .outerjoin(Task, Task.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return db.session.execute(statement).all()

    def add(self, category):
        db.session.add(category)

    def delete(self, category):
        db.session.delete(category)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()
