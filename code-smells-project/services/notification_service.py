"""Notification side-effects, extracted out of controllers.

Stubbed with leveled logging; a real implementation would enqueue/deliver async.
"""

from utils.logger import get_logger


class NotificationService:
    def __init__(self) -> None:
        self.log = get_logger("notification")

    def pedido_criado(self, pedido_id, usuario_id) -> None:
        self.log.info("email: pedido %s criado para usuario %s", pedido_id, usuario_id)
        self.log.info("sms: pedido %s recebido", pedido_id)
        self.log.info("push: novo pedido %s recebido", pedido_id)

    def status_alterado(self, pedido_id, status) -> None:
        if status == "aprovado":
            self.log.info("pedido %s aprovado — preparar envio", pedido_id)
        elif status == "cancelado":
            self.log.info("pedido %s cancelado — devolver estoque", pedido_id)
