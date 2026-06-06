from sqlalchemy.exc import SQLAlchemyError

from errors import ApiError
from models.category import Category
from services.serializers import serialize_category


class CategoryService:
    def __init__(self, category_repository):
        self.categories = category_repository

    def list_categories(self, page, per_page):
        result = []
        for category, task_count in self.categories.list_with_task_counts(
            page, per_page
        ):
            data = serialize_category(category)
            data["task_count"] = task_count
            result.append(data)
        return result

    def create_category(self, data):
        category = Category(**data)
        self.categories.add(category)
        self._commit("Erro ao criar categoria")
        return serialize_category(category)

    def update_category(self, category_id, data):
        category = self._require_category(category_id)
        for field in ("name", "description", "color"):
            if field in data:
                setattr(category, field, data[field])
        self._commit("Erro ao atualizar")
        return serialize_category(category)

    def delete_category(self, category_id):
        category = self._require_category(category_id)
        self.categories.delete(category)
        self._commit("Erro ao deletar")

    def _require_category(self, category_id):
        category = self.categories.get(category_id)
        if not category:
            raise ApiError("Categoria não encontrada", 404)
        return category

    def _commit(self, message):
        try:
            self.categories.commit()
        except SQLAlchemyError as error:
            self.categories.rollback()
            raise ApiError(message, 500) from error
