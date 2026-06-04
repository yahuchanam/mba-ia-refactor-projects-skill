# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is a **course challenge**, not a maintained application. The deliverable is a Claude Code Skill named `refactor-arch` that automatically analyzes, audits, and refactors legacy backends to the MVC pattern — agnostic of language and framework.

The three subdirectories (`code-smells-project/`, `ecommerce-api-legacy/`, `task-manager-api/`) are **the inputs to the skill**: small legacy apps seeded with *intentional* code smells (hardcoded credentials, SQL injection, God classes, mutable global state, deprecated APIs, N+1 queries, etc.). Do **not** spontaneously "fix" these projects — their smells are the test material the skill must detect. They only get refactored as the validated output of running the skill (Phase 3).

The full assignment spec lives in `README.md` (in Portuguese), including the severity scale, required knowledge areas, acceptance criteria, and the README sections to fill in.

## Target projects

| Project | Stack | Run | Notes |
|---|---|---|---|
| `code-smells-project/` | Python / Flask 3.1, raw SQLite | `pip install -r requirements.txt && python app.py` | Monolith: ~780 LOC across 4 files. Auto-creates `loja.db` with seed data on boot. E-commerce domain. Port 5000. |
| `ecommerce-api-legacy/` | Node.js / Express 4, sqlite3 | `npm install && npm start` | LMS-with-checkout, ~180 LOC. In-memory SQLite, auto-seeded. A `God` class (`AppManager`) does DB + routing + logic. Port 3000. See `api.http` for sample requests. |
| `task-manager-api/` | Python / Flask 3.0, Flask-SQLAlchemy | `pip install -r requirements.txt && python seed.py && python app.py` | Already partially layered (`models/ routes/ services/ utils/`), ~1160 LOC. **Run `seed.py` before first boot** or endpoints return empty. Port 5000. |

`task-manager-api` is deliberately the hardest case: it already has layers, so the skill must find smells (security/quality + architectural) *within* an organized project rather than rebuilding a monolith from scratch.

## The skill being built

Path (Claude Code convention): `<project>/.claude/skills/refactor-arch/SKILL.md` + Markdown reference files. The skill name `refactor-arch` and `SKILL.md` filename are fixed; reference file naming is free. The skill is created inside `code-smells-project/` then **copied** into the other two projects — so it must stay self-contained and project-agnostic (no hardcoded paths or stack assumptions).

`SKILL.md` orchestrates three sequential phases:
1. **Analysis** — detect language/framework/DB, map current architecture, print a summary.
2. **Audit** — cross-reference code against an anti-pattern catalog, emit a structured report with exact `file:line`, findings sorted CRITICAL→LOW, then **pause for human confirmation before touching any file**.
3. **Refactor** — restructure to MVC, then validate (app boots + endpoints still respond).

Reference files must cover five knowledge areas: project-analysis heuristics, anti-pattern catalog (≥8 patterns spanning all severities, including deprecated-API detection), audit-report template, MVC architecture guidelines, and a refactor playbook (≥8 before/after transformation examples).

### Severity scale (used in audit reports)
- **CRITICAL** — security exposure or architecture failure (hardcoded creds, SQL injection, God class mixing DB+logic+routing).
- **HIGH** — strong MVC/SOLID violation (business logic in controllers, tight coupling, global mutable state).
- **MEDIUM** — standardization/duplication/perf (N+1 queries, missing validation, middleware misuse).
- **LOW** — readability, naming, magic numbers.

## Deliverables (target end state)

- `refactor-arch` skill present inside all three projects' `.claude/skills/`.
- The three projects committed in their refactored (Phase 3) state.
- `reports/audit-project-{1,2,3}.md` — saved Phase 2 output per project.
- `README.md` filled with the four required sections: Análise Manual, Construção da Skill, Resultados, Como Executar.

## Validation

A refactor is "passing" only if the app **boots without errors and every original endpoint still responds**. Always verify by actually running the project (commands above) — for the Flask/SQLAlchemy project that means seeding first. `*.db`, `node_modules/`, and `.env` are gitignored, so DB files are recreated on each run.
