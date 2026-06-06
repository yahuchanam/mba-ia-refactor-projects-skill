from marshmallow import Schema, fields, validate, validates_schema, ValidationError


VALID_STATUSES = ("pending", "in_progress", "done", "cancelled")
VALID_ROLES = ("user", "admin", "manager")


class PaginationSchema(Schema):
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=50, validate=validate.Range(min=1))


class TaskCreateSchema(Schema):
    title = fields.String(
        required=True,
        validate=validate.Length(min=3, max=200),
    )
    description = fields.String(load_default="")
    status = fields.String(
        load_default="pending",
        validate=validate.OneOf(VALID_STATUSES),
    )
    priority = fields.Integer(
        load_default=3,
        validate=validate.Range(min=1, max=5),
    )
    user_id = fields.Integer(allow_none=True, load_default=None)
    category_id = fields.Integer(allow_none=True, load_default=None)
    due_date = fields.Date(allow_none=True, load_default=None)
    tags = fields.Raw(allow_none=True, load_default=None)

    @validates_schema
    def validate_tags(self, data, **kwargs):
        tags = data.get("tags")
        if tags is not None and not isinstance(tags, (list, str)):
            raise ValidationError(
                "Tags devem ser uma lista ou texto", field_name="tags"
            )


class TaskUpdateSchema(Schema):
    title = fields.String(validate=validate.Length(min=3, max=200))
    description = fields.String()
    status = fields.String(validate=validate.OneOf(VALID_STATUSES))
    priority = fields.Integer(validate=validate.Range(min=1, max=5))
    user_id = fields.Integer(allow_none=True)
    category_id = fields.Integer(allow_none=True)
    due_date = fields.Date(allow_none=True)
    tags = fields.Raw(allow_none=True)

    @validates_schema
    def validate_tags(self, data, **kwargs):
        tags = data.get("tags")
        if tags is not None and not isinstance(tags, (list, str)):
            raise ValidationError(
                "Tags devem ser uma lista ou texto", field_name="tags"
            )


class TaskSearchSchema(PaginationSchema):
    q = fields.String(load_default="")
    status = fields.String(
        load_default="",
        validate=lambda value: not value or value in VALID_STATUSES,
    )
    priority = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, max=5),
    )
    user_id = fields.Integer(allow_none=True, load_default=None)


class UserCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))


class UserUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=100))
    email = fields.Email()
    password = fields.String(validate=validate.Length(min=8))
    role = fields.String(validate=validate.OneOf(VALID_ROLES))
    active = fields.Boolean()


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class CategoryCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(load_default="")
    color = fields.String(
        load_default="#000000",
        validate=validate.Regexp(r"^#[0-9a-fA-F]{6}$"),
    )


class CategoryUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=100))
    description = fields.String()
    color = fields.String(validate=validate.Regexp(r"^#[0-9a-fA-F]{6}$"))
