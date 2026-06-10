"""Composition root: builds the dependency graph and wires the layers together.

Flow: routes → controllers → services → repositories → models.
config and middlewares are cross-cutting.
"""

from flask import Flask
from flask_cors import CORS

from config import settings
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController
from controllers.meta_controller import MetaController
from controllers.pedido_controller import PedidoController
from controllers.produto_controller import ProdutoController
from controllers.relatorio_controller import RelatorioController
from controllers.usuario_controller import UsuarioController
from middlewares.auth import make_require_auth
from middlewares.error_handler import register_error_handlers
from repositories.database import Database
from repositories.pedido_repository import PedidoRepository
from repositories.produto_repository import ProdutoRepository
from repositories.seed import seed
from repositories.usuario_repository import UsuarioRepository
from routes import register_routes
from services.admin_service import AdminService
from services.auth_controller_service import LoginService
from services.auth_service import AuthService
from services.notification_service import NotificationService
from services.pedido_service import PedidoService
from services.produto_service import ProdutoService
from services.relatorio_service import RelatorioService
from services.usuario_service import UsuarioService
from utils.logger import get_logger


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app, origins=settings.CORS_ORIGINS)

    # Infrastructure
    db = Database(settings.DB_PATH)
    app.teardown_appcontext(db.close)

    # Repositories
    produto_repo = ProdutoRepository(db)
    usuario_repo = UsuarioRepository(db)
    pedido_repo = PedidoRepository(db)

    # Services
    auth_service = AuthService(
        usuario_repo, settings.SECRET_KEY, settings.TOKEN_MAX_AGE
    )
    notifications = NotificationService()
    produto_service = ProdutoService(produto_repo, db)
    usuario_service = UsuarioService(usuario_repo, auth_service, db)
    pedido_service = PedidoService(pedido_repo, produto_repo, notifications, db)
    relatorio_service = RelatorioService(pedido_repo)
    admin_service = AdminService(db)
    login_service = LoginService(auth_service)

    # Controllers
    controllers = {
        "meta": MetaController(db),
        "produto": ProdutoController(produto_service),
        "usuario": UsuarioController(usuario_service),
        "auth": AuthController(login_service),
        "pedido": PedidoController(pedido_service),
        "relatorio": RelatorioController(relatorio_service),
        "admin": AdminController(admin_service),
    }

    # Cross-cutting + routes
    require_auth = make_require_auth(auth_service)
    register_routes(app, controllers, require_auth)
    register_error_handlers(app)

    # Schema + seed (idempotent), inside an application context so `g` is available
    with app.app_context():
        db.init_schema()
        seed(db, produto_repo, usuario_repo, auth_service)

    return app


app = create_app()

if __name__ == "__main__":
    log = get_logger("app")
    log.info("=" * 50)
    log.info("SERVIDOR INICIADO — http://localhost:%s", settings.PORT)
    log.info("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
