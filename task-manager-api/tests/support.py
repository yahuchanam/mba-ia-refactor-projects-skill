from secrets import token_hex, token_urlsafe

from app import create_app
from database import db
from models.category import Category
from models.task import Task
from models.user import User


EXPECTED_ROUTES = {
    ("GET", "/"),
    ("GET", "/health"),
    ("GET", "/tasks"),
    ("GET", "/tasks/<int:task_id>"),
    ("POST", "/tasks"),
    ("PUT", "/tasks/<int:task_id>"),
    ("DELETE", "/tasks/<int:task_id>"),
    ("GET", "/tasks/search"),
    ("GET", "/tasks/stats"),
    ("GET", "/users"),
    ("GET", "/users/<int:user_id>"),
    ("POST", "/users"),
    ("PUT", "/users/<int:user_id>"),
    ("DELETE", "/users/<int:user_id>"),
    ("GET", "/users/<int:user_id>/tasks"),
    ("POST", "/login"),
    ("GET", "/reports/summary"),
    ("GET", "/reports/user/<int:user_id>"),
    ("GET", "/categories"),
    ("POST", "/categories"),
    ("PUT", "/categories/<int:cat_id>"),
    ("DELETE", "/categories/<int:cat_id>"),
}


def build_test_app():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": token_hex(32),
        }
    )
    admin_password = token_urlsafe(16)

    with application.app_context():
        db.create_all()
        admin = User(
            name="Admin",
            email="admin@example.com",
            role="admin",
        )
        admin.set_password(admin_password)
        category = Category(name="Backend", description="API", color="#112233")
        db.session.add_all((admin, category))
        db.session.flush()
        task = Task(
            title="Seed task",
            description="Initial task",
            user_id=admin.id,
            category_id=category.id,
        )
        db.session.add(task)
        db.session.commit()
        return application, admin.id, category.id, task.id, admin_password


def exercise_all_routes():
    application, admin_id, category_id, task_id, admin_password = build_test_app()
    client = application.test_client()
    checked = []

    def check(method, path, expected_status, **kwargs):
        response = client.open(path, method=method, **kwargs)
        assert response.status_code == expected_status, (
            f"{method} {path}: expected {expected_status}, "
            f"received {response.status_code} with {response.get_json()}"
        )
        checked.append((method, path, response.status_code))
        return response

    check("GET", "/", 200)
    check("GET", "/health", 200)
    check("GET", "/tasks", 200)
    check("GET", f"/tasks/{task_id}", 200)
    check("GET", "/tasks/search?q=Seed", 200)
    check("GET", "/tasks/stats", 200)
    users_response = check("GET", "/users", 200)
    user_response = check("GET", f"/users/{admin_id}", 200)
    check("GET", f"/users/{admin_id}/tasks", 200)
    check("GET", "/reports/summary", 200)
    check("GET", f"/reports/user/{admin_id}", 200)
    check("GET", "/categories", 200)

    assert "password" not in str(users_response.get_json()).lower()
    assert "password" not in str(user_response.get_json()).lower()

    check("POST", "/tasks", 401, json={"title": "Blocked task"})
    login_response = check(
        "POST",
        "/login",
        200,
        json={"email": "admin@example.com", "password": admin_password},
    )
    login_data = login_response.get_json()
    assert "password" not in str(login_data).lower()
    token = login_data["token"]
    headers = {"Authorization": f"Bearer {token}"}

    check(
        "POST",
        "/users",
        400,
        headers=headers,
        json={
            "name": "Privilege Escalation",
            "email": "escalation@example.com",
            "password": token_urlsafe(16),
            "role": "admin",
        },
    )

    category_response = check(
        "POST",
        "/categories",
        201,
        headers=headers,
        json={"name": "Frontend", "color": "#abcdef"},
    )
    created_category_id = category_response.get_json()["id"]
    check(
        "PUT",
        f"/categories/{created_category_id}",
        200,
        headers=headers,
        json={"description": "UI"},
    )

    user_response = check(
        "POST",
        "/users",
        201,
        headers=headers,
        json={
            "name": "Course User",
            "email": "course@example.com",
            "password": token_urlsafe(16),
        },
    )
    created_user_id = user_response.get_json()["id"]
    check(
        "PUT",
        f"/users/{created_user_id}",
        200,
        headers=headers,
        json={"role": "manager"},
    )

    task_response = check(
        "POST",
        "/tasks",
        201,
        headers=headers,
        json={
            "title": "Created task",
            "user_id": created_user_id,
            "category_id": created_category_id,
            "tags": ["api", "test"],
        },
    )
    created_task_id = task_response.get_json()["id"]
    check(
        "PUT",
        f"/tasks/{created_task_id}",
        200,
        headers=headers,
        json={"status": "done"},
    )
    check("DELETE", f"/tasks/{created_task_id}", 200, headers=headers)
    check("DELETE", f"/users/{created_user_id}", 200, headers=headers)
    check(
        "DELETE",
        f"/categories/{created_category_id}",
        200,
        headers=headers,
    )

    with application.app_context():
        db.drop_all()

    assert category_id
    return application, checked


def route_surface(application):
    surface = set()
    for rule in application.url_map.iter_rules():
        if rule.rule == "/static/<path:filename>":
            continue
        for method in rule.methods - {"HEAD", "OPTIONS"}:
            surface.add((method, rule.rule))
    return surface
