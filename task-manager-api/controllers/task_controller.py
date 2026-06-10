from flask import jsonify

from controllers.helpers import load_json, load_query
from schemas import (
    PaginationSchema,
    TaskCreateSchema,
    TaskSearchSchema,
    TaskUpdateSchema,
)


class TaskController:
    def __init__(self, task_service):
        self.tasks = task_service
        self.pagination_schema = PaginationSchema()
        self.create_schema = TaskCreateSchema()
        self.update_schema = TaskUpdateSchema()
        self.search_schema = TaskSearchSchema()

    def list_tasks(self):
        pagination = load_query(self.pagination_schema)
        return jsonify(self.tasks.list_tasks(**pagination)), 200

    def get_task(self, task_id):
        return jsonify(self.tasks.get_task(task_id)), 200

    def create_task(self):
        data = load_json(self.create_schema)
        return jsonify(self.tasks.create_task(data)), 201

    def update_task(self, task_id):
        data = load_json(self.update_schema)
        return jsonify(self.tasks.update_task(task_id, data)), 200

    def delete_task(self, task_id):
        self.tasks.delete_task(task_id)
        return jsonify({"message": "Task deletada com sucesso"}), 200

    def search_tasks(self):
        filters = load_query(self.search_schema)
        page = filters.pop("page")
        per_page = filters.pop("per_page")
        return jsonify(self.tasks.search_tasks(filters, page, per_page)), 200

    def stats(self):
        return jsonify(self.tasks.stats()), 200
