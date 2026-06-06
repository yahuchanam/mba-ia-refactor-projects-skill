"""Output DTOs — the single source of truth for what crosses the API boundary.

Sensitive fields (e.g. ``senha``) are never serialized.
"""


def produto_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def usuario_to_dict(row) -> dict:
    """Public user representation — deliberately omits ``senha``."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def usuario_auth_to_dict(row) -> dict:
    """Subset returned on successful login (no password)."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }


def item_pedido_to_dict(row) -> dict:
    return {
        "produto_id": row["produto_id"],
        "produto_nome": row["produto_nome"] if row["produto_nome"] else "Desconhecido",
        "quantidade": row["quantidade"],
        "preco_unitario": row["preco_unitario"],
    }


def pedido_to_dict(row, itens) -> dict:
    return {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "status": row["status"],
        "total": row["total"],
        "criado_em": row["criado_em"],
        "itens": itens,
    }
