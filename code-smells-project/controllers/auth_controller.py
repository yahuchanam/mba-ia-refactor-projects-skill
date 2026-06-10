"""Auth controller — login adapter."""

from flask import jsonify, request


class AuthController:
    def __init__(self, login_service) -> None:
        self.login_service = login_service

    def login(self):
        dados = request.get_json(silent=True) or {}
        resultado = self.login_service.login(
            dados.get("email", ""), dados.get("senha", "")
        )
        return jsonify(
            {"dados": resultado, "sucesso": True, "mensagem": "Login OK"}
        ), 200
