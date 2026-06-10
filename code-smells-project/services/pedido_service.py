"""Pedido business logic: stock checks, total, transactional creation, notifications."""

from models import constants
from models.serializers import item_pedido_to_dict, pedido_to_dict
from utils.errors import ValidationError


class PedidoService:
    def __init__(self, pedido_repo, produto_repo, notifications, db) -> None:
        self.pedidos = pedido_repo
        self.produtos = produto_repo
        self.notifications = notifications
        self.db = db

    def _assemble(self, rows) -> list:
        ids = [r["id"] for r in rows]
        items_by_pedido = self.pedidos.items_for(ids)
        return [
            pedido_to_dict(
                r, [item_pedido_to_dict(i) for i in items_by_pedido.get(r["id"], [])]
            )
            for r in rows
        ]

    def criar(self, usuario_id, itens: list) -> dict:
        if not usuario_id:
            raise ValidationError("Usuario ID é obrigatório")
        if not itens:
            raise ValidationError("Pedido deve ter pelo menos 1 item")

        total = 0.0
        validados = []
        for item in itens:
            produto_id = item.get("produto_id")
            quantidade = item.get("quantidade", 0)
            produto = self.produtos.get(produto_id)
            if produto is None:
                raise ValidationError(f"Produto {produto_id} não encontrado")
            if produto["estoque"] < quantidade:
                raise ValidationError(f"Estoque insuficiente para {produto['nome']}")
            total += produto["preco"] * quantidade
            validados.append((produto_id, quantidade, produto["preco"]))

        try:
            pedido_id = self.pedidos.create(usuario_id, constants.STATUS_PADRAO, total)
            for produto_id, quantidade, preco in validados:
                self.pedidos.add_item(pedido_id, produto_id, quantidade, preco)
                self.produtos.decrement_estoque(produto_id, quantidade)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.notifications.pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def listar_todos(self, limit: int, offset: int):
        rows = self.pedidos.list(limit, offset)
        return self._assemble(rows), self.pedidos.count()

    def listar_por_usuario(self, usuario_id: int, limit: int, offset: int):
        rows = self.pedidos.by_usuario(usuario_id, limit, offset)
        return self._assemble(rows), self.pedidos.count_by_usuario(usuario_id)

    def atualizar_status(self, pedido_id: int, novo_status: str) -> None:
        if novo_status not in constants.STATUS_VALIDOS:
            raise ValidationError("Status inválido")
        self.pedidos.update_status(pedido_id, novo_status)
        self.db.commit()
        self.notifications.status_alterado(pedido_id, novo_status)
