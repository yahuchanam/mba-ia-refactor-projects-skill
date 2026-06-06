"""Pedido data access — parameterized queries; item loading avoids N+1 via a JOIN."""


class PedidoRepository:
    def __init__(self, db) -> None:
        self.db = db

    def create(self, usuario_id, status, total) -> int:
        cur = self.db.connection.cursor()
        cur.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, status, total),
        )
        return cur.lastrowid

    def add_item(self, pedido_id, produto_id, quantidade, preco_unitario) -> None:
        cur = self.db.connection.cursor()
        cur.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
            "VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco_unitario),
        )

    def list(self, limit: int, offset: int) -> list:
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT * FROM pedidos ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return cur.fetchall()

    def count(self) -> int:
        cur = self.db.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM pedidos")
        return cur.fetchone()[0]

    def by_usuario(self, usuario_id: int, limit: int, offset: int) -> list:
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT * FROM pedidos WHERE usuario_id = ? ORDER BY id LIMIT ? OFFSET ?",
            (usuario_id, limit, offset),
        )
        return cur.fetchall()

    def count_by_usuario(self, usuario_id: int) -> int:
        cur = self.db.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM pedidos WHERE usuario_id = ?", (usuario_id,))
        return cur.fetchone()[0]

    def items_for(self, pedido_ids: list) -> dict:
        """Return {pedido_id: [item rows]} in a single JOIN query (no N+1)."""
        if not pedido_ids:
            return {}
        placeholders = ",".join("?" * len(pedido_ids))
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT i.pedido_id, i.produto_id, i.quantidade, i.preco_unitario, "
            "p.nome AS produto_nome "
            "FROM itens_pedido i LEFT JOIN produtos p ON p.id = i.produto_id "
            f"WHERE i.pedido_id IN ({placeholders}) ORDER BY i.id",
            pedido_ids,
        )
        grouped: dict = {pid: [] for pid in pedido_ids}
        for row in cur.fetchall():
            grouped[row["pedido_id"]].append(row)
        return grouped

    def update_status(self, pedido_id, status) -> None:
        cur = self.db.connection.cursor()
        cur.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))

    def get(self, pedido_id: int):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
        return cur.fetchone()

    # --- aggregates for the sales report (computed in SQL) ---

    def summary(self) -> dict:
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT "
            "COUNT(*) AS total_pedidos, "
            "COALESCE(SUM(total), 0) AS faturamento, "
            "SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS pendentes, "
            "SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) AS aprovados, "
            "SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados "
            "FROM pedidos"
        )
        row = cur.fetchone()
        return {
            "total_pedidos": row["total_pedidos"] or 0,
            "faturamento": row["faturamento"] or 0,
            "pendentes": row["pendentes"] or 0,
            "aprovados": row["aprovados"] or 0,
            "cancelados": row["cancelados"] or 0,
        }
