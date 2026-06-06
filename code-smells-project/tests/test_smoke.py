"""Smoke test: boots the app and exercises every original endpoint.

Run: ``uv run python tests/test_smoke.py``
Uses a throwaway SQLite file and a fixed SECRET_KEY so tokens are stable.
"""

import os
import sys
import tempfile

# Configure environment BEFORE importing the app (config reads env at import time).
_TMP_DB = os.path.join(tempfile.gettempdir(), "loja_smoke_test.db")
if os.path.exists(_TMP_DB):
    os.remove(_TMP_DB)
os.environ["DB_PATH"] = _TMP_DB
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DEBUG"] = "false"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

app = create_app()
client = app.test_client()

passed = 0
failed = 0


def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}")


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


# --- auth: obtain tokens ---
r = client.post("/login", json={"email": "admin@loja.com", "senha": "admin123"})
check("POST /login admin -> 200", r.status_code == 200)
admin_token = r.get_json()["dados"]["token"]

r = client.post("/login", json={"email": "joao@email.com", "senha": "123456"})
check("POST /login cliente -> 200", r.status_code == 200)
client_token = r.get_json()["dados"]["token"]

# security: bad credentials + SQL-injection attempt must fail
check(
    "POST /login wrong pw -> 401",
    client.post("/login", json={"email": "admin@loja.com", "senha": "x"}).status_code
    == 401,
)
check(
    "POST /login SQLi blocked -> 401",
    client.post(
        "/login", json={"email": "' OR '1'='1", "senha": "' OR '1'='1"}
    ).status_code
    == 401,
)

# --- public reads ---
check("GET / -> 200", client.get("/").status_code == 200)

rh = client.get("/health")
check("GET /health -> 200", rh.status_code == 200)
check("GET /health hides secret_key", "secret_key" not in rh.get_data(as_text=True))

check("GET /produtos -> 200", client.get("/produtos").status_code == 200)
check(
    "GET /produtos/busca -> 200",
    client.get("/produtos/busca?q=note").status_code == 200,
)
check("GET /produtos/1 -> 200", client.get("/produtos/1").status_code == 200)

# --- auth enforcement ---
check(
    "POST /produtos no token -> 401",
    client.post("/produtos", json={}).status_code == 401,
)
check(
    "POST /produtos cliente -> 403",
    client.post(
        "/produtos",
        json={"nome": "X", "preco": 1, "estoque": 1},
        headers=bearer(client_token),
    ).status_code
    == 403,
)

# --- produto writes (admin) ---
r = client.post(
    "/produtos",
    json={"nome": "Produto Teste", "preco": 10.0, "estoque": 5, "categoria": "geral"},
    headers=bearer(admin_token),
)
check("POST /produtos admin -> 201", r.status_code == 201)
novo_id = r.get_json()["dados"]["id"]
check(
    "PUT /produtos/<id> admin -> 200",
    client.put(
        f"/produtos/{novo_id}",
        json={"nome": "Produto Editado", "preco": 12.0, "estoque": 3},
        headers=bearer(admin_token),
    ).status_code
    == 200,
)
check(
    "DELETE /produtos/<id> admin -> 200",
    client.delete(f"/produtos/{novo_id}", headers=bearer(admin_token)).status_code
    == 200,
)

# --- usuarios ---
ru = client.get("/usuarios", headers=bearer(admin_token))
check("GET /usuarios admin -> 200", ru.status_code == 200)
check("GET /usuarios hides senha", "senha" not in ru.get_data(as_text=True))
check(
    "GET /usuarios/1 admin -> 200",
    client.get("/usuarios/1", headers=bearer(admin_token)).status_code == 200,
)
check(
    "POST /usuarios register -> 201",
    client.post(
        "/usuarios", json={"nome": "Novo", "email": "novo@x.com", "senha": "segredo"}
    ).status_code
    == 201,
)

# --- pedidos ---
r = client.post(
    "/pedidos",
    json={"itens": [{"produto_id": 1, "quantidade": 1}]},
    headers=bearer(client_token),
)
check("POST /pedidos cliente -> 201", r.status_code == 201)
pedido_id = r.get_json()["dados"]["pedido_id"]
check(
    "GET /pedidos admin -> 200",
    client.get("/pedidos", headers=bearer(admin_token)).status_code == 200,
)
check(
    "GET /pedidos/usuario/<id> -> 200",
    client.get("/pedidos/usuario/2", headers=bearer(client_token)).status_code == 200,
)
check(
    "PUT /pedidos/<id>/status admin -> 200",
    client.put(
        f"/pedidos/{pedido_id}/status",
        json={"status": "aprovado"},
        headers=bearer(admin_token),
    ).status_code
    == 200,
)

# --- relatorios ---
check(
    "GET /relatorios/vendas admin -> 200",
    client.get("/relatorios/vendas", headers=bearer(admin_token)).status_code == 200,
)

# --- admin (gated) ---
check(
    "POST /admin/query no token -> 401",
    client.post("/admin/query", json={"sql": "SELECT 1"}).status_code == 401,
)
check(
    "POST /admin/query admin -> 200",
    client.post(
        "/admin/query", json={"sql": "SELECT 1 AS x"}, headers=bearer(admin_token)
    ).status_code
    == 200,
)
check(
    "POST /admin/reset-db no token -> 401",
    client.post("/admin/reset-db").status_code == 401,
)
check(
    "POST /admin/reset-db admin -> 200",
    client.post("/admin/reset-db", headers=bearer(admin_token)).status_code == 200,
)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
