# Design Principles & Patterns Catalog

Design patterns catalog to be used when writing and refactoring code.
Covers: **SOLID**, **DRY**, **KISS**, **YAGNI**, **MVC**, and **Object Calisthenics**.

---

## SOLID

| Principle | What it says | How to apply | Sign of violation |
|---|---|---|---|
| **SRP** — Single Responsibility | A class/module has a single reason to change | Split responsibilities into layers (config / model / repository / service / controller); one reason to change per unit | God Class, "fat" controller, model that also does business |
| **OCP** — Open/Closed | Open for extension, closed for modification | Extend via abstraction/strategy/polymorphism instead of editing existing code | Giant `if/elif`/`switch` by type; changing the same function for every new case |
| **LSP** — Liskov Substitution | Subtypes must be substitutable for the base type without breaking the contract | Subclasses honor contracts and invariants; don't restrict input or widen effects | Subclass that throws `NotImplemented`/ignores a method; concrete type checks to divert flow |
| **ISP** — Interface Segregation | Many small, cohesive interfaces, not a "fat interface" | The client depends only on what it uses; split large interfaces by role | Implementers leave methods empty or throw because they don't use them |
| **DIP** — Dependency Inversion | Depend on abstractions, not implementations; high level doesn't depend on low level | Inject dependencies (constructor/factory); depend on an interface/port; wire everything in the composition root | Instantiating a concrete DB/service in the constructor; direct implementation import |

## DRY · KISS · YAGNI

| Principle | What it says | How to apply | Sign of violation |
|---|---|---|---|
| **DRY** — Don't Repeat Yourself | Each piece of knowledge has a single representation in the system | Extract repeated validation/serialization/rule; a single source of truth | Validation copied across handlers, repeated manual serialization, duplicated constants |
| **KISS** — Keep It Simple | The simplest solution that solves the current problem | Linear flow, short functions, no indirection/abstraction without payoff; prefer `async/await` over nested callbacks | Callback hell, deeply nested ifs, layers/abstractions that don't pay off |
| **YAGNI** — You Aren't Gonna Need It | Don't implement what isn't needed now | Remove dead code and speculative features; ship only what the current requirement asks | Helpers/layers never used, columns/flags never read, premature generalization |

## MVC (and supporting layers)

Target architecture: each layer with a single responsibility and dependencies flowing from
the outside (HTTP) inward (domain).

| Layer | Responsibility | Does | Doesn't do |
|---|---|---|---|
| **Config** | Configuration and secrets | Load settings from environment/`.env`; expose config constants | Hold business logic or hardcoded secrets |
| **Model** | Data and the data's own invariant rules | Define the entity, persistence mapping, invariant validations | HTTP parsing, routing, orchestration across entities |
| **Repository / Data Access** | Encapsulate data access | Parameterized queries, CRUD, specialized reads (with `JOIN`/eager loading) | Business logic, knowing request/response |
| **Service** | Business logic and orchestration (use cases) | Coordinate models/repositories, transactions, fire side-effects via abstraction | Know `request`/`response` or HTTP details |
| **Controller** | Adapt HTTP to the use case | Validate/parse input, call the service, build response and status code | Business logic, SQL, direct DB access |
| **View / Routes** | Declare endpoints and output serialization | Map route → controller; output DTO without sensitive fields | Business or data-access logic |
| **Middleware / Error handler** | Cross-cutting concerns | Auth, CORS, logging, central error handling | Domain-specific business logic |

## Object Calisthenics

Pragmatic guidelines for small, cohesive classes/methods (apply with good judgment).

| Rule | What it says | How to apply / benefit |
|---|---|---|
| **1. One level of indentation per method** | Avoid nested loops/ifs in the same method | Extract methods; each does one thing and becomes testable |
| **2. Don't use `else`** | Prefer early return / guard clauses | Reduces branching and nesting; clear happy path |
| **3. Wrap primitives that carry meaning** | Primitive types carrying a rule become value objects | `Email`, `Money`, `Priority` centralize validation and behavior |
| **4. First-class collections** | A collection with rules gets its own class | Encapsulates the collection's operations/invariants in one place |
| **5. One dot per line (Law of Demeter)** | Don't chain accesses across objects | Talk only to direct neighbors; reduces structural coupling |
| **6. Don't abbreviate** | Full, descriptive names | Explicit intent; fewer comments needed |
| **7. Keep entities small** | Short classes, files, and methods | Limits responsibility; eases reading and testing |
| **8. At most two instance variables** | Limit state per class | Forces cohesion and composition over "do-it-all" classes |
| **9. Tell, don't ask (no exposed getters/setters)** | Behavior lives in the class that owns the data | Avoids logic scattered manipulating others' raw state |

## Usage guide

While writing or refactoring code, each fixed anti-pattern should move the code toward one or
more of these principles (no limit on use, as long as the code stays simple and follows KISS).
The anti-pattern catalog points to **what is wrong**; this one points to **where to move**.
