"""Authorization middleware: a ``require_auth`` decorator factory.

Verifies a signed, time-bound token from the ``Authorization: Bearer`` header and,
optionally, checks the role. Identity is attached to ``flask.g`` for handlers.
"""

from functools import wraps

from flask import g, jsonify, request


def make_require_auth(auth_service):
    def require_auth(roles=None):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                header = request.headers.get("Authorization", "")
                token = header[7:] if header.startswith("Bearer ") else None
                claims = auth_service.verify_token(token)
                if not claims:
                    return jsonify(
                        {"erro": "Autenticação necessária", "sucesso": False}
                    ), 401
                if roles and claims.get("role") not in roles:
                    return jsonify({"erro": "Acesso negado", "sucesso": False}), 403
                g.identity = claims
                return fn(*args, **kwargs)

            return wrapper

        return decorator

    return require_auth
