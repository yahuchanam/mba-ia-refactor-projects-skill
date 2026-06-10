"""Authentication: salted password hashing + signed, time-bound tokens.

Uses ``werkzeug.security`` (salted PBKDF2) for passwords and ``itsdangerous``
(signed, expiring) for session tokens — both ship with Flask, so no new dependency.
"""

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash


class AuthService:
    def __init__(self, usuario_repo, secret_key: str, token_max_age: int) -> None:
        self.usuarios = usuario_repo
        self.max_age = token_max_age
        self._serializer = URLSafeTimedSerializer(secret_key, salt="auth-token")

    def hash_password(self, plain: str) -> str:
        return generate_password_hash(plain)

    def authenticate(self, email: str, senha: str):
        user = self.usuarios.get_by_email(email)
        if user and check_password_hash(user["senha"], senha):
            return user
        return None

    def issue_token(self, user) -> str:
        return self._serializer.dumps({"sub": user["id"], "role": user["tipo"]})

    def verify_token(self, token: str | None):
        if not token:
            return None
        try:
            return self._serializer.loads(token, max_age=self.max_age)
        except (BadSignature, SignatureExpired):
            return None
