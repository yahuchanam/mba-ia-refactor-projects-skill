from functools import wraps

from flask import g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from errors import ApiError


class TokenService:
    def __init__(self, secret_key, max_age_seconds):
        self.serializer = URLSafeTimedSerializer(
            secret_key,
            salt="task-manager-auth",
        )
        self.max_age_seconds = max_age_seconds

    def issue(self, user):
        return self.serializer.dumps(
            {"sub": user.id, "role": user.role},
        )

    def verify(self, token):
        try:
            return self.serializer.loads(
                token,
                max_age=self.max_age_seconds,
            )
        except SignatureExpired as error:
            raise ApiError("Token expirado", 401) from error
        except BadSignature as error:
            raise ApiError("Token inválido", 401) from error


def require_auth(token_service, allowed_roles=None):
    allowed_roles = set(allowed_roles or [])

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            authorization = request.headers.get("Authorization", "")
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() != "bearer" or not token:
                raise ApiError("Autenticação obrigatória", 401)

            identity = token_service.verify(token)
            if allowed_roles and identity.get("role") not in allowed_roles:
                raise ApiError("Acesso negado", 403)

            g.identity = identity
            return view(*args, **kwargs)

        return wrapped

    return decorator
