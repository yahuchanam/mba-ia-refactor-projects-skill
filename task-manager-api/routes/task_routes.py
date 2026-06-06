from flask import Blueprint

from middlewares.auth import require_auth


def create_task_blueprint(controller, token_service):
    blueprint = Blueprint("tasks", __name__)
    admin_only = require_auth(token_service, {"admin"})

    blueprint.add_url_rule("/tasks", view_func=controller.list_tasks, methods=["GET"])
    blueprint.add_url_rule(
        "/tasks/<int:task_id>",
        view_func=controller.get_task,
        methods=["GET"],
    )
    blueprint.add_url_rule(
        "/tasks",
        endpoint="create_task",
        view_func=admin_only(controller.create_task),
        methods=["POST"],
    )
    blueprint.add_url_rule(
        "/tasks/<int:task_id>",
        endpoint="update_task",
        view_func=admin_only(controller.update_task),
        methods=["PUT"],
    )
    blueprint.add_url_rule(
        "/tasks/<int:task_id>",
        endpoint="delete_task",
        view_func=admin_only(controller.delete_task),
        methods=["DELETE"],
    )
    blueprint.add_url_rule(
        "/tasks/search",
        view_func=controller.search_tasks,
        methods=["GET"],
    )
    blueprint.add_url_rule("/tasks/stats", view_func=controller.stats, methods=["GET"])
    return blueprint
