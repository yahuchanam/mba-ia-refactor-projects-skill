from flask import current_app, request


def load_json(schema):
    return schema.load(request.get_json(silent=True) or {})


def load_query(schema):
    data = schema.load(request.args)
    if "per_page" not in request.args:
        data["per_page"] = current_app.config["DEFAULT_PAGE_SIZE"]
    data["per_page"] = min(
        data["per_page"],
        current_app.config["MAX_PAGE_SIZE"],
    )
    return data
