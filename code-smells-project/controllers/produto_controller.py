"""Produto controller — thin request→response adapter; logic lives in the service."""

from flask import jsonify, request

from utils.pagination import parse_pagination


class ProdutoController:
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

    def buscar(self):
        page, size, offset = parse_pagination()
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria", None)
        preco_min = request.args.get("preco_min", None)
        preco_max = request.args.get("preco_max", None)
        preco_min = float(preco_min) if preco_min else None
        preco_max = float(preco_max) if preco_max else None
        dados = self.service.buscar(
            termo, categoria, preco_min, preco_max, size, offset
        )
        return jsonify({"dados": dados, "total": len(dados), "sucesso": True}), 200

    def obter(self, produto_id):
        return jsonify({"dados": self.service.obter(produto_id), "sucesso": True}), 200

    def criar(self):
        produto_id = self.service.criar(request.get_json(silent=True))
        return jsonify(
            {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}
        ), 201

    def atualizar(self, produto_id):
        self.service.atualizar(produto_id, request.get_json(silent=True))
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def deletar(self, produto_id):
        self.service.deletar(produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
