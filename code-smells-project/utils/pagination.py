"""Parse and clamp pagination query params with shared defaults."""

from flask import request

from models import constants


def parse_pagination():
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        size = int(request.args.get("size", constants.PAGE_SIZE_DEFAULT))
    except (TypeError, ValueError):
        size = constants.PAGE_SIZE_DEFAULT

    page = max(page, 1)
    size = max(1, min(size, constants.PAGE_SIZE_MAX))
    offset = (page - 1) * size
    return page, size, offset
