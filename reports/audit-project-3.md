================================
ARCHITECTURE AUDIT REPORT
================================
Project:       task-manager-api
Stack:         Python 3 + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1 / SQLite)
Architecture:  Nominal layers exist, but routes contain business logic and data access while services and helpers are mostly disconnected.
Files:         15 analyzed | 1,158 lines
Date:          2026-06-10

## Phase 1 Summary

- **Domain:** Task manager with users, tasks, categories, authentication, statistics, and reports.
- **Entry point:** `app.py`; initializes SQLAlchemy and three Flask blueprints.
- **Database tables:** `users`, `tasks`, `categories`.
- **Route surface:** 22 method/path combinations.
- **Applicable stack rule:** `.claude/skills/refactor-arch/rules/stacks/python.md`.

## Summary

CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 3 | DEPRECATED: 2
Total: 15 findings

## Findings

### [CRITICAL] 1. Insecure MD5 password hashing
- **File:** `models/user.py:29`
- **Description:** Passwords are hashed with unsalted MD5 and verified by direct MD5 comparison at line 32.
- **Impact:** Password hashes are fast to crack and vulnerable to precomputed tables.
- **Recommendation:** Use Werkzeug, bcrypt, or Argon2 salted password hashing and verification.

### [CRITICAL] 2. Password hash exposure
- **File:** `models/user.py:21`
- **Description:** `User.to_dict()` includes the password field, which is reused by user creation, detail, and login responses.
- **Impact:** Credential hashes are returned to API clients and can be attacked offline.
- **Recommendation:** Remove password from all output serializers and use explicit response DTOs.

### [CRITICAL] 3. Hardcoded application and SMTP secrets
- **File:** `app.py:13`
- **Description:** The Flask secret is committed in source, while SMTP credentials are hardcoded at `services/notification_service.py:9`.
- **Impact:** Session/authentication signing and the mail account can be compromised from repository access.
- **Recommendation:** Load required secrets from environment-backed configuration and fail fast when absent.

### [HIGH] 4. Broken authentication and privilege escalation
- **File:** `routes/user_routes.py:210`
- **Description:** Login returns a predictable fake token, no route verifies it, and clients can assign their own role at lines 52 and 119.
- **Impact:** Any caller can impersonate authorization, become an administrator, or invoke destructive endpoints.
- **Recommendation:** Add signed, time-bound authentication middleware and server-controlled role assignment.

### [HIGH] 5. Business logic and persistence in routes
- **File:** `routes/report_routes.py:12`
- **Description:** Report aggregation, overdue calculations, statistics, validation, ORM queries, and serialization are implemented directly in handlers.
- **Impact:** Domain behavior is coupled to Flask and duplicated across task, user, and report routes.
- **Recommendation:** Introduce repositories, services, thin controllers, schemas, and route-only blueprints.

### [HIGH] 6. Dead service and helper layers
- **File:** `services/notification_service.py:4`
- **Description:** `NotificationService` is never imported, while validation/constants in `utils/helpers.py` are reimplemented in routes.
- **Impact:** The apparent architecture has multiple unused sources of truth and provides no dependency flow.
- **Recommendation:** Wire useful behavior through services or remove dead code; centralize each rule once.

### [MEDIUM] 7. N+1 task serialization
- **File:** `routes/task_routes.py:16`
- **Description:** Listing tasks performs separate user and category lookups per task at lines 42 and 51.
- **Impact:** Query count scales with the result set and increases endpoint latency.
- **Recommendation:** Use eager loading or joined repository queries.

### [MEDIUM] 8. N+1 report aggregation
- **File:** `routes/report_routes.py:53`
- **Description:** The summary loads every user and then runs a task query for each user at line 56.
- **Impact:** Report generation becomes progressively slower as users grow.
- **Recommendation:** Aggregate counts in SQL or fetch relationships in batches.

### [MEDIUM] 9. Unbounded collection endpoints
- **File:** `routes/task_routes.py:14`
- **Description:** Task, user, category, search, and report endpoints call `.all()` without limits or cursors.
- **Impact:** Response size and memory usage are unbounded.
- **Recommendation:** Add consistent page parameters, defaults, and maximum page size.

### [MEDIUM] 10. Bare exceptions and print logging
- **File:** `routes/task_routes.py:236`
- **Description:** Multiple handlers use bare `except` or broad exceptions, and operational events use `print`.
- **Impact:** Errors are masked, responses are inconsistent, and diagnostics lack structured context.
- **Recommendation:** Use typed errors, centralized Flask error handling, and structured logging.

### [LOW] 11. Duplicated magic constants
- **File:** `routes/task_routes.py:96`
- **Description:** Title limits, priority ranges, statuses, and password lengths are repeated inline despite constants in `utils/helpers.py`.
- **Impact:** Validation policies can diverge between endpoints.
- **Recommendation:** Define and consume named validation constants from one module or schema.

### [LOW] 12. Non-idiomatic boolean and type checks
- **File:** `models/user.py:34`
- **Description:** Boolean methods use verbose branches, and task routes use `type(tags) == list`.
- **Impact:** Code is harder to scan and extend than idiomatic expressions.
- **Recommendation:** Return boolean expressions directly and use `isinstance`.

### [LOW] 13. Dead imports and utilities
- **File:** `utils/helpers.py:3`
- **Description:** Several standard-library imports and helper functions are never used.
- **Impact:** Dead code obscures the actual application contract.
- **Recommendation:** Remove unused helpers/imports after consolidating active validation behavior.

## Deprecated APIs

- **`datetime.utcnow()`** at `models/task.py:15` and throughout routes/seeds → use timezone-aware `datetime.now(UTC)`.
- **`Model.query.get(id)`** at `routes/task_routes.py:67` and throughout routes → use `db.session.get(Model, id)`.

================================
Total: 15 findings
================================

Read-only report captured before Phase 3; no target-project file was modified by the audit.
