"""Pedido controller — thin adapter."""

from flask import g, jsonify, request

from utils.pagination import parse_pagination


class PedidoController:
    def __init__(self, service) -> None:
        self.service = service

    def criar(self):
        dados = request.get_json(silent=True) or {}
        identity = getattr(g, "identity", {})
        # Non-admins may only create orders for themselves; admins may target any user.
        usuario_id = dados.get("usuario_id")
        if identity.get("role") != "admin":
            usuario_id = identity.get("sub")
        resultado = self.service.criar(usuario_id, dados.get("itens", []))
        return jsonify(
            {
                "dados": resultado,
                "sucesso": True,
                "mensagem": "Pedido criado com sucesso",
            }
        ), 201

    def listar_todos(self):
        page, size, offset = parse_pagination()
        dados, total = self.service.listar_todos(size, offset)
        return jsonify(
            {
                "dados": dados,
                "total": total,
                "page": page,
                "size": size,
                "sucesso": True,
            }
        ), 200

    def listar_por_usuario(self, usuario_id):
        page, size, offset = parse_pagination()
        dados, total = self.service.listar_por_usuario(usuario_id, size, offset)
        return jsonify(
            {
                "dados": dados,
                "total": total,
                "page": page,
                "size": size,
                "sucesso": True,
            }
        ), 200

    def atualizar_status(self, pedido_id):
        dados = request.get_json(silent=True) or {}
        self.service.atualizar_status(pedido_id, dados.get("status", ""))
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
