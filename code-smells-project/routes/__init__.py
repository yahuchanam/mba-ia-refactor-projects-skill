"""Route surface (views): endpoint → controller mapping.

Preserves every original method+path. Reads stay public; PII listings, write
operations, sales report and admin actions are gated behind auth (admin where the
action is administrative/destructive). Auth-gated routes still respond — the normal
result for a valid (admin) credential, 401/403 otherwise.
"""


def register_routes(app, c, require_auth) -> None:
    admin_only = require_auth(["admin"])
    authenticated = require_auth()

    # Meta
    app.add_url_rule("/", "index", c["meta"].index, methods=["GET"])
    app.add_url_rule("/health", "health_check", c["meta"].health_check, methods=["GET"])

    # Produtos — reads public, writes admin
    app.add_url_rule(
        "/produtos", "listar_produtos", c["produto"].listar, methods=["GET"]
    )
    app.add_url_rule(
        "/produtos/busca", "buscar_produtos", c["produto"].buscar, methods=["GET"]
    )
    app.add_url_rule(
        "/produtos/<int:produto_id>",
        "buscar_produto",
        c["produto"].obter,
        methods=["GET"],
    )
    app.add_url_rule(
        "/produtos", "criar_produto", admin_only(c["produto"].criar), methods=["POST"]
    )
    app.add_url_rule(
        "/produtos/<int:produto_id>",
        "atualizar_produto",
        admin_only(c["produto"].atualizar),
        methods=["PUT"],
    )
    app.add_url_rule(
        "/produtos/<int:produto_id>",
        "deletar_produto",
        admin_only(c["produto"].deletar),
        methods=["DELETE"],
    )

    # Usuarios — listing/detail expose PII → admin; registration public; login public
    app.add_url_rule(
        "/usuarios", "listar_usuarios", admin_only(c["usuario"].listar), methods=["GET"]
    )
    app.add_url_rule(
        "/usuarios/<int:usuario_id>",
        "buscar_usuario",
        admin_only(c["usuario"].obter),
        methods=["GET"],
    )
    app.add_url_rule("/usuarios", "criar_usuario", c["usuario"].criar, methods=["POST"])
    app.add_url_rule("/login", "login", c["auth"].login, methods=["POST"])

    # Pedidos — create/list-own require auth; list-all and status changes are admin
    app.add_url_rule(
        "/pedidos", "criar_pedido", authenticated(c["pedido"].criar), methods=["POST"]
    )
    app.add_url_rule(
        "/pedidos",
        "listar_todos_pedidos",
        admin_only(c["pedido"].listar_todos),
        methods=["GET"],
    )
    app.add_url_rule(
        "/pedidos/usuario/<int:usuario_id>",
        "listar_pedidos_usuario",
        authenticated(c["pedido"].listar_por_usuario),
        methods=["GET"],
    )
    app.add_url_rule(
        "/pedidos/<int:pedido_id>/status",
        "atualizar_status_pedido",
        admin_only(c["pedido"].atualizar_status),
        methods=["PUT"],
    )

    # Relatórios — admin
    app.add_url_rule(
        "/relatorios/vendas",
        "relatorio_vendas",
        admin_only(c["relatorio"].vendas),
        methods=["GET"],
    )

    # Admin — destructive / arbitrary-SQL routes, gated to admin
    app.add_url_rule(
        "/admin/reset-db",
        "reset_database",
        admin_only(c["admin"].reset_db),
        methods=["POST"],
    )
    app.add_url_rule(
        "/admin/query",
        "executar_query",
        admin_only(c["admin"].executar_query),
        methods=["POST"],
    )
