from flask import jsonify

from controllers.helpers import load_json, load_query
from schemas import LoginSchema, PaginationSchema, UserCreateSchema, UserUpdateSchema


class UserController:
    def __init__(self, user_service):
        self.users = user_service
        self.pagination_schema = PaginationSchema()
        self.create_schema = UserCreateSchema()
        self.update_schema = UserUpdateSchema()
        self.login_schema = LoginSchema()

    def list_users(self):
        pagination = load_query(self.pagination_schema)
        return jsonify(self.users.list_users(**pagination)), 200

    def get_user(self, user_id):
        pagination = load_query(self.pagination_schema)
        return jsonify(self.users.get_user(user_id, **pagination)), 200

    def create_user(self):
        data = load_json(self.create_schema)
        return jsonify(self.users.create_user(data)), 201

    def update_user(self, user_id):
        data = load_json(self.update_schema)
        return jsonify(self.users.update_user(user_id, data)), 200

    def delete_user(self, user_id):
        self.users.delete_user(user_id)
        return jsonify({"message": "Usuário deletado com sucesso"}), 200

    def get_user_tasks(self, user_id):
        pagination = load_query(self.pagination_schema)
        return jsonify(self.users.get_user_tasks(user_id, **pagination)), 200

    def login(self):
        data = load_json(self.login_schema)
        return jsonify(self.users.login(data["email"], data["password"])), 200
