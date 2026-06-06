"""Usuario business logic: registration with hashing + server-side role assignment."""

from models.serializers import usuario_to_dict
from utils.errors import NotFoundError, ValidationError


class UsuarioService:
    def __init__(self, repo, auth_service, db) -> None:
        self.repo = repo
        self.auth = auth_service
        self.db = db

    def listar(self, limit: int, offset: int):
        rows = self.repo.all(limit, offset)
        return [usuario_to_dict(r) for r in rows], self.repo.count()

    def obter(self, usuario_id: int) -> dict:
        row = self.repo.get(usuario_id)
        if not row:
            raise NotFoundError("Usuário não encontrado")
        return usuario_to_dict(row)

    def criar(self, dados: dict) -> int:
        if not dados:
            raise ValidationError("Dados inválidos")
        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not nome or not email or not senha:
            raise ValidationError("Nome, email e senha são obrigatórios")
        if "@" not in email or "." not in email:
            raise ValidationError("Email inválido")
        if self.repo.get_by_email(email):
            raise ValidationError("Email já cadastrado")

        senha_hash = self.auth.hash_password(senha)
        # Role is assigned server-side — never read from the request body.
        usuario_id = self.repo.create(nome, email, senha_hash, "cliente")
        self.db.commit()
        return usuario_id
