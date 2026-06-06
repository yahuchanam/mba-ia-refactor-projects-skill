# Refactoring Playbook

Concrete **before/after** transformations that turn the anti-patterns from
[`anti-patterns-catalog.md`](./anti-patterns-catalog.md) into code aligned with
[`design-patterns-catalog.md`](./design-patterns-catalog.md).

Examples are written in **language-neutral pseudocode** — they describe the *move*, not a
specific stack. Apply each pattern using the project's actual language, framework, and
standard libraries. Always **preserve behavior**: every endpoint that responded before must
still respond after.

## Target MVC layout

```
config/        # settings from env, no hardcoded secrets
models/        # entities + invariant rules
repositories/  # data access (parameterized queries)
services/      # business logic / use cases
controllers/   # thin request→response adapters
routes/        # endpoint → controller mapping (views)
middlewares/   # error handler, auth, CORS, logging
<entry point>  # composition root: wires everything together
```

Dependencies flow inward: `routes → controllers → services → repositories → models`.
`config` and `middlewares` are cross-cutting. Names/extensions vary by stack; the
**responsibilities** are what matter.

---

## 1. SQL Injection → parameterized query

Anti-pattern: *SQL Injection*. Principle: security; KISS.

**Before**
```
query = "SELECT * FROM users WHERE email = '" + userInput + "'"
db.run(query)
```

**After**
```
db.run("SELECT * FROM users WHERE email = ?", [userInput])   # value is bound, not interpolated
```
**Why:** the driver binds the value, so user input can never alter the query structure. Use
parameter binding, a query builder, or an ORM — never string concatenation.

---

## 2. Hardcoded secrets → config from environment

Anti-pattern: *Hardcoded secrets and credentials*. Principle: SRP (Config layer); 12-factor.

**Before**
```
SECRET_KEY = "literal-secret-committed-in-code"
```

**After**
```
# config module — the single owner of configuration
SECRET_KEY = env("SECRET_KEY")          # read from environment; fail fast if missing
DEBUG      = env("DEBUG", default=false)
```
**Why:** secrets leave the codebase and history; one place owns configuration and can differ
per environment.

---

## 3. Insecure password storage → salted hash

Anti-pattern: *Insecure password storage*. Principle: security.

**Before**
```
stored = md5(password)                  # unsalted / fast / homemade — broken
```

**After**
```
stored = strongHash(password)           # salted, slow KDF: bcrypt / argon2 / scrypt
isValid = strongHashVerify(stored, attempt)
```
**Why:** salted, slow hashing resists rainbow tables and brute force. Always use the
platform's vetted hashing library — never a homemade hash.

---

## 4. Sensitive data exposure → output DTO

Anti-pattern: *Sensitive data exposure*. Principle: DRY (one serializer); least exposure.

**Before**
```
serialize(user) -> { id, email, password, ssn }   # leaks secret/PII
```

**After**
```
serialize(user) -> { id, email }        # explicit allow-list of safe fields only
```
**Why:** the output DTO is the public contract; sensitive fields never cross the boundary.
Apply the same redaction to logs.

---

## 5. Monolith / God Class → layered MVC

Anti-pattern: *God Class / God Module*, *Business logic in the wrong layer*. Principle: SRP, DIP.

**Before**
```
class App:                              # DB + routing + business logic in one place
    db
    route("POST /checkout"):
        validate(); charge(); persist(); notify()
```

**After**
```
Repository  -> data access only (parameterized queries)
Service     -> business rules only (charge, enroll, record); dependencies injected
Controller  -> thin: read request → call service → write response
Routes/Root -> compose: build dependencies and wire them together
```
**Why:** each unit has one reason to change and is testable in isolation.

---

## 6. Business logic in controller → service layer

Anti-pattern: *Business logic in the wrong layer*. Principle: SRP.

**Before**
```
handler("GET /reports/sales"):
    rows     = db.query("SELECT total FROM orders")
    revenue  = sum(rows.total)
    discount = revenue > 10000 ? revenue * 0.1 : 0     # business rule inside the HTTP handler
    return { revenue, discount }
```

**After**
```
service SalesService(orders):
    report(): revenue = orders.totalRevenue(); return { revenue, discount: rule(revenue) }

handler("GET /reports/sales", salesService):
    return salesService.report()                       # controller only delegates
```
**Why:** the rule is testable without HTTP/DB and reusable across entry points.

---

## 7. Global mutable state → injected dependency

Anti-pattern: *Mutable global state*. Principle: DIP.

**Before**
```
global connection = null
getDb():
    if connection == null: connection = connect(...)   # shared mutable singleton
    return connection
```

**After**
```
class ProductRepository(db):            # receives its dependency
    all(): return db.query("SELECT * FROM products")

# the entry point owns the connection lifecycle (per request/scope) and injects it
```
**Why:** no shared mutable global; thread-safe and mockable in tests.

---

## 8. N+1 query → single set-based query

Anti-pattern: *N+1 query*. Principle: performance.

**Before**
```
orders = db.query("SELECT * FROM orders")
for o in orders:
    items = db.query("SELECT * FROM items WHERE order_id = ?", [o.id])   # one query per row
```

**After**
```
rows = db.query("SELECT o.id, i.* FROM orders o LEFT JOIN items i ON i.order_id = o.id")
# single query; group in memory  (or use the ORM's eager-loading equivalent)
```
**Why:** query count stays constant instead of growing with the result set.

---

## 9. Duplicated validation → single validator/schema

Anti-pattern: *Duplicated logic*, *Missing or weak input validation*. Principle: DRY.

**Before**
```
# copied in create() and update():
if empty(input.title):        fail("title required")
if length(input.title) > 200: fail("title too long")
```

**After**
```
schema TaskSchema: title is string, required, length 3..200
data = TaskSchema.validate(input)       # one source of truth, reused by create and update
```
**Why:** validation lives in one place; create/update cannot drift apart.

---

## 10. Scattered errors + prints → central handler + logging

Anti-pattern: *Poor error handling + logging via `print`*. Principle: SRP (middleware).

**Before**
```
try: ...
catch e:
    print("ERR " + e)                   # swallowed, no levels, leaks internals
    return 500, e.message
```

**After**
```
log = logger()
# central error middleware:
onError(e): log.error("unhandled", e); return 500, { error: "internal error" }
```
**Why:** one consistent error contract and real observability; internals never leak. Use a
leveled logger, not prints.

---

## 11. Mass-assignment / broken auth → allow-list + guard

Anti-pattern: *Broken authentication + privilege escalation*. Principle: security.

**Before**
```
user = new User(allFieldsFrom(request.body))   # client can set role = "admin"
```

**After**
```
user = new User({ name: body.name, email: body.email })   # explicit allow-list
user.role = "user"                                        # privileged fields set server-side
# destructive/admin routes sit behind an auth + authorization middleware
```
**Why:** clients cannot escalate privileges; sensitive fields are server-controlled.

---

## 12. Deprecated API → modern equivalent

Anti-pattern: *Use of deprecated API*. Principle: maintainability.

**Before**
```
t = utcnow()                 # deprecated / naive timestamp
u = Model.query.get(id)      # legacy data-access API
```

**After**
```
t = now(UTC)                 # timezone-aware, current API
u = session.get(Model, id)   # current data-access API
```
**Why:** removes deprecation warnings and avoids subtly wrong behavior. General rule: check
each dependency's deprecation notes and migrate to the documented replacement.

---

## 13. Missing authentication/authorization → token/session + guard middleware

Anti-pattern: *Broken authentication + privilege escalation*, *no real access control*.
Principle: security; SRP (middleware).

**Before**
```
handler("POST /login"):
    user = repo.findByEmail(body.email)
    if user and verify(user.secret, body.password):
        return { ok: true }              # no token/session issued; caller stays anonymous

handler("DELETE /products/:id"):         # any anonymous caller can reach this
    repo.delete(id)
```

**After**
```
# on login: issue a signed, time-bound credential carrying identity + role
handler("POST /login"):
    user = service.authenticate(body.email, body.password)
    return { token: issueToken({ sub: user.id, role: user.role }) }   # signed session/JWT

# one authorization middleware guards sensitive / state-changing / admin routes
middleware requireAuth(allowedRoles):
    claims = verifyToken(request.authorization)   # reject if missing / invalid / expired
    if allowedRoles and claims.role not in allowedRoles: deny(403)
    request.identity = claims

route("DELETE /products/:id", requireAuth(["admin"]), controller.delete)
```
**Why:** identity is verified per request and privileged actions are gated by role instead of
left open. Keep public read endpoints public; protect mutating/admin routes. Credentials are
signed and expiring; roles are assigned server-side — never read from the request body.

---

## 14. Unbounded list → pagination with safe defaults

Anti-pattern: *Listing without pagination*. Principle: performance; robustness.

**Before**
```
handler("GET /items"):
    return repo.query("SELECT * FROM items")     # returns the entire table
```

**After**
```
handler("GET /items"):
    page = clamp(request.query.page or 1, min=1)
    size = clamp(request.query.size or DEFAULT_SIZE, min=1, max=MAX_SIZE)
    rows = repo.page(limit=size, offset=(page - 1) * size)   # bounded query
    return { data: rows, page, size, total: repo.count() }
```
**Why:** payload and memory stay bounded as data grows. Use a sane default page size and a hard
maximum; prefer cursor/keyset pagination for large or frequently-changing tables. Apply the
same defaults to every list endpoint so the response contract stays consistent.

---

## Validation after refactor (Phase 3 exit criteria)

A refactor is only **done** when:

1. The app **boots without errors** (run the project's start command).
2. **Every original endpoint still responds** — compare against the route surface captured in
   Phase 1 (same method + path → same status/shape).
3. No catalog anti-pattern from the audit remains in the touched code.

If any check fails, fix and re-validate before declaring completion.
