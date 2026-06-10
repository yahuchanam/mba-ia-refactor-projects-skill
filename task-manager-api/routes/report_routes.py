from flask import Blueprint

from middlewares.auth import require_auth


def create_report_blueprint(controller, token_service):
    blueprint = Blueprint("reports", __name__)
    admin_only = require_auth(token_service, {"admin"})

    blueprint.add_url_rule(
        "/reports/summary",
        view_func=controller.summary,
        methods=["GET"],
    )
    blueprint.add_url_rule(
        "/reports/user/<int:user_id>",
        view_func=controller.user_report,
        methods=["GET"],
    )
    blueprint.add_url_rule(
        "/categories",
        view_func=controller.list_categories,
        methods=["GET"],
    )
    blueprint.add_url_rule(
        "/categories",
        endpoint="create_category",
        view_func=admin_only(controller.create_category),
        methods=["POST"],
    )
    blueprint.add_url_rule(
        "/categories/<int:cat_id>",
        endpoint="update_category",
        view_func=admin_only(controller.update_category),
        methods=["PUT"],
    )
    blueprint.add_url_rule(
        "/categories/<int:cat_id>",
        endpoint="delete_category",
        view_func=admin_only(controller.delete_category),
        methods=["DELETE"],
    )
    return blueprint
