================================
ARCHITECTURE AUDIT REPORT
================================
Project:       code-smells-project
Stack:         Python 3 + Flask 3.1.1 (raw SQLite)
Architecture:  Monolith split across four modules; routes, HTTP concerns, business rules, persistence, schema, and seeding are tightly coupled.
Files:         4 analyzed | 780 lines
Date:          2026-06-10

## Phase 1 Summary

- **Domain:** E-commerce API for products, users, orders, authentication, and sales reports.
- **Entry point:** `app.py`; boots with `python app.py` on port 5000.
- **Database tables:** `produtos`, `usuarios`, `pedidos`, `itens_pedido`.
- **Route surface:** 19 method/path combinations, including two administrative endpoints.
- **Applicable stack rule:** `.claude/skills/refactor-arch/rules/stacks/python.md`.

## Summary

CRITICAL: 6 | HIGH: 4 | MEDIUM: 4 | LOW: 1 | DEPRECATED: 0
Total: 15 findings

## Findings

### [CRITICAL] 1. Arbitrary SQL execution endpoint
- **File:** `app.py:59`
- **Description:** `POST /admin/query` accepts SQL from the request body and executes it directly at `app.py:69`.
- **Impact:** Any caller can read, modify, or destroy the entire database.
- **Recommendation:** Preserve the route but require verified administrator authorization and constrain allowed operations.

### [CRITICAL] 2. SQL injection
- **File:** `models.py:48`
- **Description:** Product creation interpolates request-controlled values into SQL. The same pattern appears in updates, login, user creation, order operations, and product search.
- **Impact:** Attackers can alter query structure, bypass authentication, or corrupt data.
- **Recommendation:** Move queries into repositories and bind every value with SQLite placeholders.

### [CRITICAL] 3. Hardcoded secret and secret disclosure
- **File:** `app.py:7`
- **Description:** The Flask secret key is committed in source and returned by `/health` at `controllers.py:289`.
- **Impact:** Session or token signing can be forged, and operational secrets are exposed over HTTP.
- **Recommendation:** Load secrets from environment configuration and remove them from response DTOs.

### [CRITICAL] 4. Insecure password storage
- **File:** `database.py:76`
- **Description:** Seed users contain plaintext passwords, and new passwords are inserted unchanged at `models.py:127`.
- **Impact:** A database leak immediately exposes every user credential.
- **Recommendation:** Hash passwords with a vetted salted password KDF and verify hashes during login.

### [CRITICAL] 5. Sensitive data exposure
- **File:** `models.py:83`
- **Description:** User list and detail serializers include the `senha` column in API responses.
- **Impact:** Authenticated or unauthenticated callers can retrieve stored passwords.
- **Recommendation:** Use explicit output serializers that never include password or secret fields.

### [CRITICAL] 6. God module and absent MVC boundaries
- **File:** `models.py:1`
- **Description:** A 314-line module mixes SQL, serialization, order rules, stock mutation, reporting, and discount calculation.
- **Impact:** Responsibilities cannot be tested or changed independently, and defects propagate across domains.
- **Recommendation:** Split models/serializers, repositories, services, controllers, routes, and a composition root.

### [HIGH] 7. Broken authentication and authorization
- **File:** `app.py:47`
- **Description:** Database reset, arbitrary query, product writes, user reads, order reads, and reports have no access-control middleware.
- **Impact:** Anonymous callers can destroy data, inspect users, and perform privileged operations.
- **Recommendation:** Add signed, time-bound authentication and role-based authorization while preserving all routes.

### [HIGH] 8. Business logic in controllers
- **File:** `controllers.py:24`
- **Description:** HTTP handlers perform product validation, category policy, notification orchestration, and status workflow rules.
- **Impact:** Domain behavior is coupled to Flask and duplicated across create/update flows.
- **Recommendation:** Move rules and use-case orchestration into services; keep controllers as thin adapters.

### [HIGH] 9. Mutable global database state
- **File:** `database.py:4`
- **Description:** A process-global SQLite connection is mutated and shared with `check_same_thread=False`.
- **Impact:** Requests share lifecycle and transaction state, creating race, isolation, and test contamination risks.
- **Recommendation:** Manage connections per application/request context and inject the database dependency.

### [HIGH] 10. Infrastructure side effects in controller
- **File:** `controllers.py:208`
- **Description:** Order creation simulates email, SMS, and push delivery directly with `print`.
- **Impact:** Delivery concerns are coupled to HTTP handling and cannot be replaced or tested independently.
- **Recommendation:** Extract a notification service and inject it into the order use case.

### [MEDIUM] 11. N+1 query pattern
- **File:** `models.py:187`
- **Description:** Order listing queries items per order and then products per item; the same pattern repeats at `models.py:219`.
- **Impact:** Query count grows with both orders and items, causing avoidable latency.
- **Recommendation:** Fetch order details with joins or batched repository queries.

### [MEDIUM] 12. Missing referential integrity
- **File:** `database.py:37`
- **Description:** Order and item tables declare identifier columns without foreign keys or delete behavior.
- **Impact:** Deletions can leave orphaned orders and items and produce inconsistent reports.
- **Recommendation:** Add foreign keys and explicit cascade or transactional cleanup rules.

### [MEDIUM] 13. Unbounded collection endpoints
- **File:** `models.py:7`
- **Description:** Product, user, order, and search queries return all matching rows without limits or cursors.
- **Impact:** Payload size, memory use, and latency grow without a bound.
- **Recommendation:** Apply consistent pagination defaults and a hard maximum in repositories and controllers.

### [MEDIUM] 14. Inconsistent error handling and print logging
- **File:** `controllers.py:10`
- **Description:** Broad exceptions expose raw messages while operational events and failures use `print`.
- **Impact:** Internal details leak to clients and failures lack structured, centralized observability.
- **Recommendation:** Introduce typed application errors, a central Flask error handler, and structured logging.

### [LOW] 15. Magic business thresholds
- **File:** `models.py:256`
- **Description:** Revenue discount thresholds and percentages are embedded as unnamed literals.
- **Impact:** Pricing intent is obscure and changes require editing implementation code.
- **Recommendation:** Move thresholds to named constants or an explicit pricing policy.

## Deprecated APIs

No framework or library API definitively deprecated for the declared dependency versions was found.

================================
Total: 15 findings
================================

Read-only report captured before Phase 3; no target-project file was modified by the audit.
