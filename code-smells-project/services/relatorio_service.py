"""Sales report business logic — discount tiers from named constants."""

from models import constants


class RelatorioService:
    def __init__(self, pedido_repo) -> None:
        self.pedidos = pedido_repo

    def _desconto(self, faturamento: float) -> float:
        for limiar, taxa in constants.DISCOUNT_TIERS:
            if faturamento > limiar:
                return faturamento * taxa
        return 0.0

    def vendas(self) -> dict:
        s = self.pedidos.summary()
        faturamento = s["faturamento"]
        desconto = self._desconto(faturamento)
        total_pedidos = s["total_pedidos"]
        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": s["pendentes"],
            "pedidos_aprovados": s["aprovados"],
            "pedidos_cancelados": s["cancelados"],
            "ticket_medio": round(faturamento / total_pedidos, 2)
            if total_pedidos
            else 0,
        }
