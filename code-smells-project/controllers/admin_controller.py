"""Admin controller — thin adapter. Routes are gated to the admin role in the wiring."""

from flask import jsonify, request

from utils.errors import ValidationError


class AdminController:
    def __init__(self, service) -> None:
        self.service = service

    def reset_db(self):
        self.service.reset_db()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200

    def executar_query(self):
        dados = request.get_json(silent=True) or {}
        query = dados.get("sql", "")
        if not query:
            raise ValidationError("Query não informada")
        return jsonify(self.service.run_query(query)), 200
