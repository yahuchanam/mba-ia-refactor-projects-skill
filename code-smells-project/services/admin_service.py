"""Admin operations. Routes that reach these are auth-gated to the admin role
(see middlewares/auth + routes wiring); the operations themselves stay intact."""

from utils.logger import get_logger


class AdminService:
    def __init__(self, db) -> None:
        self.db = db
        self.log = get_logger("admin")

    def reset_db(self) -> None:
        cur = self.db.connection.cursor()
        cur.execute("DELETE FROM itens_pedido")
        cur.execute("DELETE FROM pedidos")
        cur.execute("DELETE FROM produtos")
        cur.execute("DELETE FROM usuarios")
        self.db.commit()
        self.log.warning("base de dados resetada por um administrador")

    def run_query(self, query: str) -> dict:
        """Execute an admin-supplied SQL statement (admin-only route)."""
        cur = self.db.connection.cursor()
        cur.execute(query)
        if query.strip().upper().startswith("SELECT"):
            rows = cur.fetchall()
            return {"dados": [dict(r) for r in rows], "sucesso": True}
        self.db.commit()
        return {"mensagem": "Query executada", "sucesso": True}
