"""Usuario data access — parameterized queries only."""


class UsuarioRepository:
    def __init__(self, db) -> None:
        self.db = db

    def all(self, limit: int, offset: int) -> list:
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT * FROM usuarios ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return cur.fetchall()

    def count(self) -> int:
        cur = self.db.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM usuarios")
        return cur.fetchone()[0]

    def get(self, usuario_id: int):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        return cur.fetchone()

    def get_by_email(self, email: str):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        return cur.fetchone()

    def create(self, nome, email, senha_hash, tipo) -> int:
        cur = self.db.connection.cursor()
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
        return cur.lastrowid
