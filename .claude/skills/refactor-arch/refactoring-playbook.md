# Refactoring Playbook

Concrete **before/after** transformations that turn the anti-patterns from
[`anti-patterns-catalog.md`](./anti-patterns-catalog.md) into code aligned with
[`design-patterns-catalog.md`](./design-patterns-catalog.md).

Examples use Python (Flask) and JavaScript (Express) as representatives — the **transformation
pattern is language-independent**; apply the same move in the project's actual stack. Always
**preserve behavior**: every endpoint that responded before must still respond after.

## Target MVC layout

```
src/
├── config/        # settings from env, no hardcoded secrets
├── models/        # entities + invariant rules
├── repositories/  # data access (parameterized queries)
├── services/      # business logic / use cases
├── controllers/   # thin HTTP adapters
├── routes/        # endpoint → controller mapping (views)
├── middlewares/   # error handler, auth, CORS, logging
└── app.py|app.js  # composition root (entry point)
```

Dependencies flow inward: `routes → controllers → services → repositories → models`.
`config` and `middlewares` are cross-cutting.

---

## 1. SQL Injection → parameterized query

Anti-pattern: *SQL Injection*. Principle: security; KISS.

**Before**
```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
```

**After**
```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```
**Why:** the driver binds the value; user input can never alter the query structure.

---

## 2. Hardcoded secrets → config from environment

Anti-pattern: *Hardcoded secrets and credentials*. Principle: SRP (Config layer); 12-factor.

**Before**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```

**After**
```python
# config/settings.py
import os
class Settings:
    SECRET_KEY = os.environ["SECRET_KEY"]          # fail fast if missing
    DEBUG = os.environ.get("DEBUG", "false") == "true"

# app.py
app.config.from_object(Settings)
```
**Why:** secrets leave the codebase/history; one place owns configuration.

---

## 3. Insecure password storage → salted hash

Anti-pattern: *Insecure password storage*. Principle: security.

**Before**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()        # unsalted, broken
```

**After**
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password_hash = generate_password_hash(pwd)          # salted (pbkdf2/scrypt)

def check_password(self, pwd):
    return check_password_hash(self.password_hash, pwd)
```
**Why:** salted, slow hashing resists rainbow tables and brute force.

---

## 4. Sensitive data exposure → output serializer

Anti-pattern: *Sensitive data exposure*. Principle: DRY (one serializer); least exposure.

**Before**
```python
def to_dict(self):
    return {"id": self.id, "email": self.email, "password": self.password}  # leaks hash
```

**After**
```python
def to_dict(self):
    return {"id": self.id, "email": self.email}   # never serialize secrets/PII
```
**Why:** the output DTO is the contract; sensitive fields never cross the boundary.

---

## 5. Monolith / God Class → layered MVC

Anti-pattern: *God Class / God Module*, *Business logic in the wrong layer*. Principle: SRP, DIP.

**Before**
```js
class AppManager {                       // DB + routing + business logic
  constructor() { this.db = new sqlite3.Database(":memory:"); }
  setupRoutes(app) {
    app.post("/checkout", (req, res) => { /* validate + charge + persist + notify */ });
  }
}
```

**After**
```js
// repositories/enrollmentRepository.js — data access only
class EnrollmentRepository { constructor(db){ this.db = db; } create(userId, courseId){ /* parametrized */ } }

// services/checkoutService.js — business logic only
class CheckoutService {
  constructor(enrollments, payments, gateway){ /* injected deps */ }
  execute({ userId, courseId, card }) { /* charge + enroll + record */ }
}

// controllers/checkoutController.js — thin HTTP adapter
const checkout = (service) => (req, res) => {
  const result = service.execute(req.body);
  res.status(201).json(result);
};

// routes + app.js wire everything (composition root)
```
**Why:** each unit has one reason to change and is testable in isolation.

---

## 6. Business logic in controller → service layer

Anti-pattern: *Business logic in the wrong layer*. Principle: SRP.

**Before**
```python
@app.route("/reports/sales")
def sales():
    rows = db.execute("SELECT total FROM orders").fetchall()
    revenue = sum(r["total"] for r in rows)
    discount = revenue * 0.1 if revenue > 10000 else 0          # business rule in controller
    return jsonify({"revenue": revenue, "discount": discount})
```

**After**
```python
# services/sales_service.py
class SalesService:
    def __init__(self, orders): self.orders = orders
    def report(self):
        revenue = self.orders.total_revenue()
        return {"revenue": revenue, "discount": self._discount(revenue)}
    def _discount(self, revenue): ...

# controllers/sales_controller.py
def sales(service):
    return jsonify(service.report()), 200
```
**Why:** the rule is testable without HTTP/DB and reusable across entry points.

---

## 7. Global mutable connection → injected, request-scoped access

Anti-pattern: *Mutable global state*. Principle: DIP.

**Before**
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("loja.db", check_same_thread=False)  # shared singleton
    return db_connection
```

**After**
```python
# repository receives the connection/session; the app wires its lifecycle per request
class ProductRepository:
    def __init__(self, db): self.db = db
    def all(self): return self.db.execute("SELECT * FROM products").fetchall()

# app factory provides a fresh, properly-scoped connection (e.g. Flask `g`, or a session per request)
```
**Why:** no shared mutable global; thread-safe and mockable in tests.

---

## 8. N+1 query → single JOIN / eager load

Anti-pattern: *N+1 query*. Principle: performance.

**Before**
```python
orders = db.execute("SELECT * FROM orders").fetchall()
for o in orders:
    items = db.execute("SELECT * FROM items WHERE order_id = ?", (o["id"],)).fetchall()  # N queries
```

**After**
```python
rows = db.execute("""
    SELECT o.id AS order_id, i.*
    FROM orders o
    LEFT JOIN items i ON i.order_id = o.id
""").fetchall()                                # one query, grouped in memory
```
**Why:** query count is constant instead of proportional to the result set.

---

## 9. Duplicated validation → reusable schema/validator

Anti-pattern: *Duplicated logic*, *Missing or weak input validation*. Principle: DRY.

**Before**
```python
# repeated in create() and update()
if not data.get("title"): return error("title required")
if len(data["title"]) > 200: return error("title too long")
```

**After**
```python
# schemas/task_schema.py
class TaskSchema(Schema):
    title = fields.Str(required=True, validate=Length(min=3, max=200))

# controllers reuse it
data = TaskSchema().load(request.get_json())   # one source of truth for validation
```
**Why:** validation lives in one place; create/update can't drift apart.

---

## 10. Scattered errors + `print` → central handler + logging

Anti-pattern: *Poor error handling + logging via `print`*. Principle: SRP (middleware).

**Before**
```python
try:
    ...
except Exception as e:
    print("ERRO: " + str(e))                   # swallowed, no levels
    return jsonify({"erro": str(e)}), 500
```

**After**
```python
import logging
log = logging.getLogger(__name__)

# middlewares/error_handler.py
@app.errorhandler(Exception)
def handle(e):
    log.exception("unhandled error")           # structured, with stack
    return jsonify({"error": "internal error"}), 500
```
**Why:** one consistent error contract and real observability; no leaked internals.

---

## 11. Mass-assignment / broken auth → allow-list + guard

Anti-pattern: *Broken authentication + privilege escalation*. Principle: security.

**Before**
```python
user = User(**request.get_json())              # client can set role="admin"
```

**After**
```python
body = request.get_json()
user = User(name=body["name"], email=body["email"])   # explicit allow-list
user.role = "user"                                    # privileged fields set server-side
# destructive/admin routes go behind an auth + authorization middleware
```
**Why:** clients can't escalate privileges; sensitive fields are server-controlled.

---

## 12. Deprecated API → modern equivalent

Anti-pattern: *Use of deprecated API*. Principle: maintainability.

**Before**
```python
created_at = datetime.utcnow()                 # deprecated (naive datetime)
user = User.query.get(user_id)                 # legacy SQLAlchemy API
```

**After**
```python
from datetime import datetime, UTC
created_at = datetime.now(UTC)                 # timezone-aware
user = db.session.get(User, user_id)           # SQLAlchemy 2.0 API
```
**Why:** removes deprecation warnings and avoids subtly wrong (naive) timestamps.

---

## Validation after refactor (Phase 3 exit criteria)

A refactor is only **done** when:

1. The app **boots without errors** (run the project's start command).
2. **Every original endpoint still responds** — compare against the route surface captured in
   Phase 1 (same method + path → same status/shape).
3. No catalog anti-pattern from the audit remains in the touched code.

If any check fails, fix and re-validate before declaring completion.
