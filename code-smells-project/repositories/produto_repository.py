"""Produto data access — parameterized queries only (no string concatenation)."""


class ProdutoRepository:
    def __init__(self, db) -> None:
        self.db = db

    def all(self, limit: int, offset: int) -> list:
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT * FROM produtos ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return cur.fetchall()

    def count(self) -> int:
        cur = self.db.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM produtos")
        return cur.fetchone()[0]

    def get(self, produto_id: int):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        return cur.fetchone()

    def create(self, nome, descricao, preco, estoque, categoria) -> int:
        cur = self.db.connection.cursor()
        cur.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        return cur.lastrowid

    def update(self, produto_id, nome, descricao, preco, estoque, categoria) -> None:
        cur = self.db.connection.cursor()
        cur.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, "
            "categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )

    def delete(self, produto_id) -> None:
        cur = self.db.connection.cursor()
        cur.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))

    def decrement_estoque(self, produto_id, quantidade) -> None:
        cur = self.db.connection.cursor()
        cur.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto_id),
        )

    def search(self, termo, categoria, preco_min, preco_max, limit, offset) -> list:
        clauses = ["1=1"]
        params: list = []
        if termo:
            clauses.append("(nome LIKE ? OR descricao LIKE ?)")
            like = f"%{termo}%"
            params.extend([like, like])
        if categoria:
            clauses.append("categoria = ?")
            params.append(categoria)
        if preco_min is not None:
            clauses.append("preco >= ?")
            params.append(preco_min)
        if preco_max is not None:
            clauses.append("preco <= ?")
            params.append(preco_max)

        query = "SELECT * FROM produtos WHERE " + " AND ".join(clauses)
        query += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cur = self.db.connection.cursor()
        cur.execute(query, params)
        return cur.fetchall()
