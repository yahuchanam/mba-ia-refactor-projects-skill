"""Login use case — authenticate and issue a token."""

from models.serializers import usuario_auth_to_dict
from utils.errors import AuthError, ValidationError


class LoginService:
    def __init__(self, auth_service) -> None:
        self.auth = auth_service

    def login(self, email: str, senha: str) -> dict:
        if not email or not senha:
            raise ValidationError("Email e senha são obrigatórios")
        user = self.auth.authenticate(email, senha)
        if not user:
            raise AuthError("Email ou senha inválidos")
        return {
            "usuario": usuario_auth_to_dict(user),
            "token": self.auth.issue_token(user),
        }
