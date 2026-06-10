from datetime import datetime, time

from sqlalchemy.exc import SQLAlchemyError

from errors import ApiError
from models.task import Task
from services.serializers import serialize_task
from utils.datetime_utils import utc_now


class TaskService:
    def __init__(self, task_repository, user_repository, category_repository):
        self.tasks = task_repository
        self.users = user_repository
        self.categories = category_repository

    def list_tasks(self, page, per_page):
        tasks = self.tasks.list_page(page, per_page)
        return [serialize_task(task, include_names=True) for task in tasks]

    def get_task(self, task_id):
        task = self._require_task(task_id)
        data = serialize_task(task)
        data["overdue"] = task.is_overdue()
        return data

    def create_task(self, data):
        self._validate_relations(data)
        task = Task(
            title=data["title"],
            description=data["description"],
            status=data["status"],
            priority=data["priority"],
            user_id=data["user_id"],
            category_id=data["category_id"],
            due_date=self._as_datetime(data["due_date"]),
            tags=self._serialize_tags(data["tags"]),
        )
        self.tasks.add(task)
        self._commit("Erro ao criar task")
        return serialize_task(task)

    def update_task(self, task_id, data):
        task = self._require_task(task_id)
        self._validate_relations(data)

        for field in (
            "title",
            "description",
            "status",
            "priority",
            "user_id",
            "category_id",
        ):
            if field in data:
                setattr(task, field, data[field])
        if "due_date" in data:
            task.due_date = self._as_datetime(data["due_date"])
        if "tags" in data:
            task.tags = self._serialize_tags(data["tags"])
        task.updated_at = utc_now()

        self._commit("Erro ao atualizar")
        return serialize_task(task)

    def delete_task(self, task_id):
        task = self._require_task(task_id)
        self.tasks.delete(task)
        self._commit("Erro ao deletar")

    def search_tasks(self, filters, page, per_page):
        tasks = self.tasks.search(filters, page, per_page)
        return [serialize_task(task) for task in tasks]

    def stats(self):
        status_counts = self.tasks.count_by_status()
        total = self.tasks.count_all()
        done = status_counts.get("done", 0)
        return {
            "total": total,
            "pending": status_counts.get("pending", 0),
            "in_progress": status_counts.get("in_progress", 0),
            "done": done,
            "cancelled": status_counts.get("cancelled", 0),
            "overdue": self.tasks.count_overdue(utc_now()),
            "completion_rate": round((done / total) * 100, 2) if total else 0,
        }

    def _require_task(self, task_id):
        task = self.tasks.get(task_id)
        if not task:
            raise ApiError("Task não encontrada", 404)
        return task

    def _validate_relations(self, data):
        if data.get("user_id") and not self.users.get(data["user_id"]):
            raise ApiError("Usuário não encontrado", 404)
        if data.get("category_id") and not self.categories.get(data["category_id"]):
            raise ApiError("Categoria não encontrada", 404)

    def _commit(self, message):
        try:
            self.tasks.commit()
        except SQLAlchemyError as error:
            self.tasks.rollback()
            raise ApiError(message, 500) from error

    @staticmethod
    def _as_datetime(value):
        if value is None or isinstance(value, datetime):
            return value
        return datetime.combine(value, time.min)

    @staticmethod
    def _serialize_tags(tags):
        if isinstance(tags, list):
            return ",".join(tags)
        return tags
