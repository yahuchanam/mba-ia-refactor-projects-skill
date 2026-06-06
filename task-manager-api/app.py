from flask import Flask
from flask_cors import CORS

from config import Config
from controllers.report_controller import ReportController
from controllers.task_controller import TaskController
from controllers.user_controller import UserController
from database import db
from errors import register_error_handlers
from middlewares.auth import TokenService
from repositories.category_repository import CategoryRepository
from repositories.report_repository import ReportRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from routes.report_routes import create_report_blueprint
from routes.task_routes import create_task_blueprint
from routes.user_routes import create_user_blueprint
from services.category_service import CategoryService
from services.report_service import ReportService
from services.task_service import TaskService
from services.user_service import UserService
from utils.datetime_utils import utc_now


def create_app(config_override=None):
    application = Flask(__name__)
    application.config.from_object(Config)
    if config_override:
        application.config.update(config_override)

    CORS(application)
    db.init_app(application)
    register_error_handlers(application)

    token_service = TokenService(
        application.config["SECRET_KEY"],
        application.config["TOKEN_MAX_AGE_SECONDS"],
    )
    task_repository = TaskRepository()
    user_repository = UserRepository()
    category_repository = CategoryRepository()
    report_repository = ReportRepository()

    task_service = TaskService(
        task_repository,
        user_repository,
        category_repository,
    )
    user_service = UserService(user_repository, task_repository, token_service)
    category_service = CategoryService(category_repository)
    report_service = ReportService(report_repository, user_repository)

    task_controller = TaskController(task_service)
    user_controller = UserController(user_service)
    report_controller = ReportController(report_service, category_service)

    application.register_blueprint(
        create_task_blueprint(task_controller, token_service)
    )
    application.register_blueprint(
        create_user_blueprint(user_controller, token_service)
    )
    application.register_blueprint(
        create_report_blueprint(report_controller, token_service)
    )

    @application.get("/health")
    def health():
        return {"status": "ok", "timestamp": str(utc_now())}

    @application.get("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    return application


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, host="0.0.0.0", port=5000)
