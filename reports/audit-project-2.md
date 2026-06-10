================================
ARCHITECTURE AUDIT REPORT
================================
Project:       ecommerce-api-legacy
Stack:         Node.js + Express 4.18.2 (sqlite3 callback driver)
Architecture:  God Class owns the in-memory database, schema, seeds, routes, checkout workflow, reporting, and user deletion.
Files:         3 analyzed | 180 lines
Date:          2026-06-10

## Phase 1 Summary

- **Domain:** Learning management API with checkout, enrollments, payments, users, and financial reporting.
- **Entry point:** `src/app.js`; boots with `npm start` on port 3000.
- **Database tables:** `users`, `courses`, `enrollments`, `payments`, `audit_logs`.
- **Route surface:** 3 method/path combinations.
- **Applicable stack rule:** `.claude/skills/refactor-arch/rules/stacks/node.md`.

## Summary

CRITICAL: 4 | HIGH: 4 | MEDIUM: 4 | LOW: 2 | DEPRECATED: 0
Total: 14 findings

## Findings

### [CRITICAL] 1. Hardcoded production credentials
- **File:** `src/utils.js:2`
- **Description:** Database credentials, a live payment key, and SMTP identity are committed as literals.
- **Impact:** Anyone with source access can reuse production secrets and compromise integrations.
- **Recommendation:** Load configuration from environment variables, validate it at startup, and rotate exposed values.

### [CRITICAL] 2. Payment data and secret exposure in logs
- **File:** `src/AppManager.js:45`
- **Description:** Checkout logs the complete card value together with the payment gateway key.
- **Impact:** Sensitive payment data and credentials are exposed to logs and log-processing systems.
- **Recommendation:** Never log card data or secrets; log only a generated payment reference with structured redaction.

### [CRITICAL] 3. Insecure password hashing
- **File:** `src/utils.js:17`
- **Description:** `badCrypto` repeats Base64 encoding and truncates the result to ten characters; the seed password at `src/AppManager.js:18` is plaintext.
- **Impact:** Passwords are deterministic, fast to reverse, unsalted, and trivial to crack.
- **Recommendation:** Use a vetted salted password KDF such as `scrypt` or `bcrypt`, including seed data.

### [CRITICAL] 4. God Class combining all architectural layers
- **File:** `src/AppManager.js:4`
- **Description:** `AppManager` creates infrastructure, defines schema/seeds, registers HTTP routes, executes business rules, and serializes responses.
- **Impact:** The application cannot be tested or evolved by responsibility, and every change risks unrelated behavior.
- **Recommendation:** Split config, database initialization, repositories, services, controllers, routes, middleware, and composition root.

### [HIGH] 5. Missing administrator authentication
- **File:** `src/AppManager.js:80`
- **Description:** Financial reporting is publicly accessible, and user deletion at `src/AppManager.js:131` has no authentication or role check.
- **Impact:** Anonymous callers can inspect financial data or delete arbitrary users.
- **Recommendation:** Preserve both routes but enforce verified administrator authorization middleware.

### [HIGH] 6. Checkout business logic in route handler
- **File:** `src/AppManager.js:28`
- **Description:** The route performs validation, user creation, payment decisions, enrollment, audit logging, and cache mutation.
- **Impact:** Business behavior is coupled to Express and cannot be tested independently of HTTP and SQLite.
- **Recommendation:** Move checkout orchestration into a service with injected repositories and payment abstraction.

### [HIGH] 7. Callback hell and manual async coordination
- **File:** `src/AppManager.js:37`
- **Description:** Checkout and reporting use deeply nested callbacks and mutable pending counters.
- **Impact:** Error paths are incomplete, control flow is fragile, and response completion can become inconsistent.
- **Recommendation:** Wrap the database driver with Promises and implement linear `async/await` services.

### [HIGH] 8. Mutable global cache
- **File:** `src/utils.js:9`
- **Description:** A process-global object is mutated by checkout through `logAndCache`.
- **Impact:** State leaks across requests and tests without lifecycle, bounds, or invalidation.
- **Recommendation:** Remove the implicit cache or inject a bounded cache abstraction with explicit ownership.

### [MEDIUM] 9. N+1 financial report queries
- **File:** `src/AppManager.js:89`
- **Description:** The report queries enrollments per course, then users and payments per enrollment.
- **Impact:** Query count grows with courses and enrollments and degrades report latency.
- **Recommendation:** Aggregate revenue and student data with joined or batched repository queries.

### [MEDIUM] 10. Missing referential integrity
- **File:** `src/AppManager.js:14`
- **Description:** Enrollment and payment tables have identifier columns without foreign keys or cascade behavior.
- **Impact:** User deletion leaves orphaned enrollment and payment records, as admitted by the response at line 135.
- **Recommendation:** Define foreign keys and delete related records transactionally or with explicit cascades.

### [MEDIUM] 11. Ignored database errors
- **File:** `src/AppManager.js:57`
- **Description:** Audit-log, report user/payment, and delete callbacks proceed without handling possible errors.
- **Impact:** Requests can return success with partially persisted or inconsistent data.
- **Recommendation:** Centralize async error handling and use transactions for checkout and deletion.

### [MEDIUM] 12. Weak input validation
- **File:** `src/AppManager.js:35`
- **Description:** Checkout only checks presence for some fields; email, password, course identifier, and card shape are not validated.
- **Impact:** Invalid or malformed data reaches persistence and payment logic.
- **Recommendation:** Validate and normalize an explicit request schema at the controller boundary.

### [LOW] 13. Cryptic naming
- **File:** `src/AppManager.js:29`
- **Description:** Request data is mapped to abbreviations such as `u`, `e`, `p`, `cid`, and `cc`.
- **Impact:** Intent is difficult to review in a security-sensitive workflow.
- **Recommendation:** Use domain names such as `userName`, `email`, `password`, `courseId`, and `cardNumber`.

### [LOW] 14. Dead exported state
- **File:** `src/utils.js:10`
- **Description:** `totalRevenue` is exported but never read or updated.
- **Impact:** The module exposes misleading state and unnecessary API surface.
- **Recommendation:** Remove unused state and exports.

## Deprecated APIs

No API definitively deprecated for Express 4.18.2 or sqlite3 5.1.6 was found.

================================
Total: 14 findings
================================
