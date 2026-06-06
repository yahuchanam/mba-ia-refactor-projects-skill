from flask import Blueprint

from middlewares.auth import require_auth


def create_user_blueprint(controller, token_service):
    blueprint = Blueprint("users", __name__)
    admin_only = require_auth(token_service, {"admin"})

    blueprint.add_url_rule("/users", view_func=controller.list_users, methods=["GET"])
    blueprint.add_url_rule(
        "/users/<int:user_id>",
        view_func=controller.get_user,
        methods=["GET"],
    )
    blueprint.add_url_rule(
        "/users",
        endpoint="create_user",
        view_func=admin_only(controller.create_user),
        methods=["POST"],
    )
    blueprint.add_url_rule(
        "/users/<int:user_id>",
        endpoint="update_user",
        view_func=admin_only(controller.update_user),
        methods=["PUT"],
    )
    blueprint.add_url_rule(
        "/users/<int:user_id>",
        endpoint="delete_user",
        view_func=admin_only(controller.delete_user),
        methods=["DELETE"],
    )
    blueprint.add_url_rule(
        "/users/<int:user_id>/tasks",
        view_func=controller.get_user_tasks,
        methods=["GET"],
    )
    blueprint.add_url_rule("/login", view_func=controller.login, methods=["POST"])
    return blueprint
