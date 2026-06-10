"""Meta controller — index and health endpoints (no secrets leaked)."""

from flask import jsonify


class MetaController:
    def __init__(self, db) -> None:
        self.db = db

    def index(self):
        return jsonify(
            {
                "mensagem": "Bem-vindo à API da Loja",
                "versao": "1.0.0",
                "endpoints": {
                    "produtos": "/produtos",
                    "usuarios": "/usuarios",
                    "pedidos": "/pedidos",
                    "login": "/login",
                    "relatorios": "/relatorios/vendas",
                    "health": "/health",
                },
            }
        ), 200

    def health_check(self):
        cur = self.db.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM produtos")
        produtos = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cur.fetchone()[0]
        # No secret_key / internal config is exposed here.
        return jsonify(
            {
                "status": "ok",
                "database": "connected",
                "counts": {
                    "produtos": produtos,
                    "usuarios": usuarios,
                    "pedidos": pedidos,
                },
                "versao": "1.0.0",
            }
        ), 200
