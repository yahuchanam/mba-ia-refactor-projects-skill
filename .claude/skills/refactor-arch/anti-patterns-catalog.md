# Anti-Pattern Catalog

A **stack-agnostic** catalog for classifying audit findings in any backend, regardless of
language, framework, or level of organization. Each entry carries **actionable detection
signals** (greppable, not generic), **severity**, **impact**, and **fix direction**.

## Severity scale

| Level | Definition |
|---|---|
| 🔴 **CRITICAL** | Serious architecture/security failure: exposes sensitive data (hardcoded credentials, SQL Injection) or completely violates separation of concerns (God Class mixing DB + logic + routing). |
| 🟠 **HIGH** | Strong MVC/SOLID violation that severely hampers maintenance and testing: business logic trapped in controllers, coupling without DI, mutable global state. |
| 🟡 **MEDIUM** | Standardization, duplication, or moderate performance: N+1 queries, missing validation, improper middleware use. |
| 🟢 **LOW** | Readability, poor naming, magic numbers. |
| ⏳ **DEPRECATED** | Use of an obsolete API; effective severity varies (usually LOW–MEDIUM) with the breakage risk. |

## Catalog

| Anti-pattern | Severity | Signals | Impact | Fix |
|---|:---:|---|---|---|
| **SQL Injection** | 🔴 CRITICAL | SQL built with concatenation/f-string/template interpolating user input into `execute/query/run`, instead of placeholders (`?`, `:name`, `$1`) | Read/alter/destroy data and authentication bypass | Parameterized queries / query builder / ORM |
| **Hardcoded secrets and credentials** | 🔴 CRITICAL | Literal `SECRET_KEY`/password/API key/token in code; no `.env` or environment variables (even with an env lib installed) | Versioned, exposed secret; session/integration compromisable | Load from environment/secret manager; remove from history |
| **Sensitive data exposure** | 🔴 CRITICAL | Password/secret field present in output serialization; `print`/log of card, token, key, or PII | Direct leak of credentials/PII to clients or logs | Output DTO without sensitive fields; redact/filter logs |
| **Insecure password storage** | 🔴 CRITICAL | Password stored without hashing; `md5`/`sha1` for passwords; homemade hashing function; direct password comparison | Crackable/exposed passwords; unreliable authentication | `bcrypt`/`argon2`/`werkzeug.security` with salt |
| **God Class / God Module** | 🔴 CRITICAL | One class/file holds the DB connection, registers routes **and** implements business logic; a "model" file that also does business | Zero isolated testability; any change risks everything; violates SRP/MVC | Split into config / model / repository / service / controller |
| **Arbitrary execution endpoint** | 🔴 CRITICAL | Route that takes SQL/command from the body and runs it directly; destructive route without authentication | RCE-equivalent over the database; clients read/write/reset everything | Remove; replace with specific authenticated operations |
| **Business logic in the wrong layer** | 🟠 HIGH | Domain calculation/aggregation/orchestration inside the route handler or data access; "fat" controllers; service layer absent or ignored | Logic untestable without HTTP/DB, scattered and divergent | Move logic to the service layer; controller only orchestrates HTTP |
| **Mutable global state** | 🟠 HIGH | Mutable global connection/variable; object exported and mutated by another module; singleton shared across threads | Race conditions, global coupling, state not isolatable; memory leak | Per-request scope / injection; cache with explicit lifecycle |
| **Infrastructure side-effects in the controller** | 🟠 HIGH | Controller firing email/SMS/push/notification directly, with no service/queue | Controller coupled to infra, impossible to test/mock; mixes HTTP with delivery | Extract to a service/notification layer; ideally async |
| **Coupling without dependency injection** | 🟠 HIGH | Concrete dependencies instantiated in the constructor/top; direct implementation imports; no interface/inversion | Impossible to swap/mock the DB or services without editing the class | Inject dependencies (constructor/factory/container) |
| **Dead layers / dependency that doesn't flow** | 🟠 HIGH | Service/util defined and **never imported**; controllers reimplement what the layer already offers (validation/serialization) | Illusion of architecture; two sources of truth; worse maintenance | Wire the layers or remove the dead code; one source of truth |
| **Broken authentication + privilege escalation** | 🟠 HIGH | Predictable/fake token; destructive routes without an auth guard; `role`/permission field accepted from the request body (mass-assignment) | No real access control; client becomes admin or deletes data | Real verified auth, authorization middleware, field allow-list |
| **Callback hell / poor async orchestration** | 🟠 HIGH | Business flow nested in many callbacks (pyramid of doom); manual coordination with counters instead of `Promise.all`/`async-await` | Unreadable, fragile, hard to test; termination logic bug-prone | `async/await` + Promise-based driver; transactions |
| **N+1 query** | 🟡 MEDIUM | Query inside a loop; relation access triggering a lazy-load per item; one query per collection element | Queries proportional to volume; performance degradation | `JOIN`/eager loading/aggregation in SQL |
| **Duplicated logic** | 🟡 MEDIUM | Validation blocks copied across handlers; same serialization repeated; same rule in several files | Fixes must be replicated; source of divergence/bugs | Extract reusable validators/serializers/utilities |
| **Missing or weak input validation** | 🟡 MEDIUM | Route without format validation (email, date, types); validates presence only; no schema | Invalid data persisted; late errors | Schema validation at the edge; consistent messages |
| **Poor error handling + logging via `print`** | 🟡 MEDIUM | `except`/`catch` with no action; callbacks ignoring the error; `print`/`console.log` for logging; inconsistent error responses | Masked failures; no observability | Structured logging; central error handler; specific exceptions |
| **Missing referential integrity** | 🟡 MEDIUM | Schema without FK/`ON DELETE CASCADE`; `DELETE` of the parent that leaves orphan children | Orphan/inconsistent data; reports count broken records | FKs + cascade or explicit transactional handling |
| **Listing without pagination** | 🟡 MEDIUM | Returning the whole table (`.all()`/`SELECT *`); no `limit`/`offset`/cursor | Unbounded payload and memory; latency | Pagination (limit/offset or cursor) with sane defaults |
| **Magic numbers / unnamed literals** | 🟢 LOW | Loose business numbers/strings (limits, ranges, percentages) without a named constant | Obscure intent; hard to adjust safely | Named constants/config |
| **Poor naming / shadowing** | 🟢 LOW | Shadowed builtin; single-letter variables; mixed languages | Reduced readability and consistency | Descriptive, consistent names |
| **Dead code / unused imports** | 🟢 LOW | Unused import; function defined and never called; column/field created and never read | Noise; confusion about what is in use | Remove; keep only what is used |
| **Verbose / non-idiomatic code** | 🟢 LOW | `if cond: return True else: return False`; `type(x) == list`; nested ifs for a boolean; dict built by hand where a serializer exists | Reduced maintenance and readability | Return the boolean expression; `isinstance`; reuse the serializer |
| **Inconsistent response shape** | 🟢 LOW | Varying envelopes (raw object/text/wrapper); irregular status codes across routes | Unpredictable contract for the client | Standardize envelope and codes (response/error handler) |
| **Use of deprecated API** | ⏳ DEPRECATED | Import/use of a symbol marked deprecated in the lib version in use; pattern superseded by a newer API (e.g., `datetime.utcnow()`, legacy ORM API like `query.get()`, callbacks where a Promise exists, homemade hashing) | Future breakage, deprecation warnings, subtly incorrect behavior (e.g., naive datetime) | Migrate to the modern equivalent (e.g., `datetime.now(UTC)`, `session.get()`, `async/await`, `bcrypt`/`argon2`) |
