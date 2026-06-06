# Repository Guidelines

## Project Structure & Module Organization

This repository is a course challenge for building a `refactor-arch` agent skill. The target apps are intentionally flawed fixtures; do not refactor them unless you are executing and validating the skill workflow.

- `.claude/skills/refactor-arch/`: the skill deliverable, including `SKILL.md` and Markdown reference files.
- `code-smells-project/`: Python/Flask e-commerce API with raw SQLite.
- `ecommerce-api-legacy/`: Node.js/Express LMS API with checkout flow and SQLite.
- `task-manager-api/`: Python/Flask task API with partial layering in `models/`, `routes/`, `services/`, and `utils/`.
- `refinement/`: manual analysis and phase notes for the challenge.

## Build, Test, and Development Commands

Prefix shell commands with `rtk`, per local agent instructions.

- `rtk npm install` from `ecommerce-api-legacy/`: install Node dependencies.
- `rtk npm start` from `ecommerce-api-legacy/`: start the Express API on port `3000`.
- `rtk pip install -r requirements.txt` from either Python app: install Flask dependencies.
- `rtk python app.py` from `code-smells-project/`: start the e-commerce API on port `5000`.
- `rtk python seed.py && rtk python app.py` from `task-manager-api/`: seed SQLite data, then start the task API on port `5000`.

There is no repository-wide build command.

## Coding Style & Naming Conventions

Use the existing style in each subproject. Python files use 4-space indentation, snake_case for functions and modules, and explicit package folders where present. JavaScript uses CommonJS (`require`, `module.exports`) and camelCase for functions and variables. Keep skill references in Markdown with clear headings, exact file names, and actionable detection/refactoring rules.

## Testing Guidelines

No automated test suite is currently configured. Validate changes by booting the relevant app and exercising original endpoints. For `ecommerce-api-legacy/`, use examples in `api.http`. For skill runs, save Phase 2 audit output under `reports/audit-project-{1,2,3}.md` when applicable and confirm Phase 3 only after reviewing the audit.

## Commit & Pull Request Guidelines

Git history uses concise Conventional Commit-style messages, such as `feat(skill): ...`, `fix(skill): ...`, and `chore: ...`. Keep that pattern for new commits. Pull requests should describe the skill or fixture changes, list validation commands run, mention any reports generated, and include screenshots only when documenting UI or browser-visible behavior.

## Agent-Specific Instructions

Treat the three apps as test material containing deliberate code smells. Preserve those smells unless the task explicitly asks to run the refactoring workflow. Before modifying files, inspect the relevant project README and current git status, and avoid overwriting unrelated user changes.
