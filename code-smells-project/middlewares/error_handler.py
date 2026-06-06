"""Central error handling — one consistent contract; internals never leak to clients."""

from flask import jsonify

from utils.errors import AppError
from utils.logger import get_logger

log = get_logger("error")


def register_error_handlers(app) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        return jsonify({"erro": exc.message, "sucesso": False}), exc.status

    @app.errorhandler(Exception)
    def handle_unexpected(exc: Exception):
        log.exception("erro não tratado: %s", exc)
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
