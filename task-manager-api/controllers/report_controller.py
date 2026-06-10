from flask import jsonify

from controllers.helpers import load_json, load_query
from schemas import CategoryCreateSchema, CategoryUpdateSchema, PaginationSchema


class ReportController:
    def __init__(self, report_service, category_service):
        self.reports = report_service
        self.categories = category_service
        self.pagination_schema = PaginationSchema()
        self.category_create_schema = CategoryCreateSchema()
        self.category_update_schema = CategoryUpdateSchema()

    def summary(self):
        return jsonify(self.reports.summary()), 200

    def user_report(self, user_id):
        return jsonify(self.reports.user_report(user_id)), 200

    def list_categories(self):
        pagination = load_query(self.pagination_schema)
        return jsonify(self.categories.list_categories(**pagination)), 200

    def create_category(self):
        data = load_json(self.category_create_schema)
        return jsonify(self.categories.create_category(data)), 201

    def update_category(self, cat_id):
        data = load_json(self.category_update_schema)
        return jsonify(self.categories.update_category(cat_id, data)), 200

    def delete_category(self, cat_id):
        self.categories.delete_category(cat_id)
        return jsonify({"message": "Categoria deletada"}), 200
