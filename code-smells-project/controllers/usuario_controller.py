"""Usuario controller — thin adapter."""

from flask import jsonify, request

from utils.pagination import parse_pagination


class UsuarioController:
    def __init__(self, service) -> None:
        self.service = service

    def listar(self):
        page, size, offset = parse_pagination()
        dados, total = self.service.listar(size, offset)
        return jsonify(
            {
                "dados": dados,
                "total": total,
                "page": page,
                "size": size,
                "sucesso": True,
            }
        ), 200

    def obter(self, usuario_id):
        return jsonify({"dados": self.service.obter(usuario_id), "sucesso": True}), 200

    def criar(self):
        usuario_id = self.service.criar(request.get_json(silent=True))
        return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201
