from sqlalchemy.exc import SQLAlchemyError

from errors import ApiError
from models.user import User
from services.serializers import serialize_task, serialize_user


class UserService:
    def __init__(self, user_repository, task_repository, token_service):
        self.users = user_repository
        self.tasks = task_repository
        self.tokens = token_service

    def list_users(self, page, per_page):
        result = []
        for user, task_count in self.users.list_with_task_counts(page, per_page):
            data = serialize_user(user)
            data["task_count"] = task_count
            result.append(data)
        return result

    def get_user(self, user_id, page, per_page):
        user = self._require_user(user_id)
        data = serialize_user(user)
        data["tasks"] = [
            serialize_task(task)
            for task in self.tasks.list_for_user(user_id, page, per_page)
        ]
        return data

    def create_user(self, data):
        if self.users.get_by_email(data["email"]):
            raise ApiError("Email já cadastrado", 409)

        user = User(
            name=data["name"],
            email=data["email"],
            role="user",
        )
        user.set_password(data["password"])
        self.users.add(user)
        self._commit("Erro ao criar usuário")
        return serialize_user(user)

    def update_user(self, user_id, data):
        user = self._require_user(user_id)
        if "email" in data:
            existing = self.users.get_by_email(data["email"])
            if existing and existing.id != user_id:
                raise ApiError("Email já cadastrado", 409)

        for field in ("name", "email", "role", "active"):
            if field in data:
                setattr(user, field, data[field])
        if "password" in data:
            user.set_password(data["password"])

        self._commit("Erro ao atualizar")
        return serialize_user(user)

    def delete_user(self, user_id):
        user = self._require_user(user_id)
        self.users.delete(user)
        self._commit("Erro ao deletar")

    def get_user_tasks(self, user_id, page, per_page):
        self._require_user(user_id)
        result = []
        for task in self.tasks.list_for_user(user_id, page, per_page):
            data = serialize_task(task)
            data["overdue"] = task.is_overdue()
            result.append(data)
        return result

    def login(self, email, password):
        user = self.users.get_by_email(email)
        if not user or not user.check_password(password):
            raise ApiError("Credenciais inválidas", 401)
        if not user.active:
            raise ApiError("Usuário inativo", 403)
        return {
            "message": "Login realizado com sucesso",
            "user": serialize_user(user),
            "token": self.tokens.issue(user),
        }

    def _require_user(self, user_id):
        user = self.users.get(user_id)
        if not user:
            raise ApiError("Usuário não encontrado", 404)
        return user

    def _commit(self, message):
        try:
            self.users.commit()
        except SQLAlchemyError as error:
            self.users.rollback()
            raise ApiError(message, 500) from error
