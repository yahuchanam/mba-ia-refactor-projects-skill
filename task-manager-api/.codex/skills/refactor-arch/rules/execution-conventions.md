# Execution conventions

How to run shell commands during Phase 3 so the refactor stays a **one-shot** run — no permission
prompts, no surprises. Stack-agnostic; the per-stack mechanics live in [`stacks/`](./stacks/).

## Run commands the matcher can pre-authorize

Claude Code matches Bash permissions on the **program name at the start of the line**, and prompts
whenever it can't statically prove a command safe. Keep every call simple:

- **One simple command per call.** No `&&`, `||`, `;`, pipes `|`, subshells `( … )`, redirects
  (`>`, `2>/dev/null`), or command substitution `$( … )` — a compound line needs approval even when
  every part is allow-listed.
- **Program name first.** Start the line with the program (`uv`, `npm`, `go`, …). Anything before
  it breaks matching:
  - inline env assignments — `DB_PATH=… uv run …` → set env **inside** the script instead.
  - global options — `git -C /path …` → run from that directory's working context.
  - path-qualified binaries — `.venv/bin/pip`, `./node_modules/.bin/eslint` → use the launcher
    (`uv run <tool>`, `npx <tool>`).
- **Inspect files with native tools** — `Read`/`Glob`/`Grep`, never `cat`/`ls`/`find` for reading.

## Verify in-process, not over the network

To confirm the route surface still responds, **import the app and drive it with the framework's
in-process test client** — never boot a real server and probe it with `curl`. In-process needs no
server, no `sleep`, no network tool (often re-wrapped by a shell hook, e.g. `rtk curl`), and no env
prefix, so it runs without prompts. Each stack file names its test client and gives the
`verify_routes` shape. Real-server probing is a last resort that needs an explicit network grant.

## Deletion guardrail

Raw deletion is not allowed: never use `rm`, `rmdir`, or `git rm`. Remove obsolete files only with
the bundled guardrailed remover, from the target project root:

```
python3 .claude/skills/refactor-arch/scripts/safe_remove.py <path>
```

Run without `--confirm` first (dry-run); re-run with `--confirm` only when the listed targets are
clearly part of the plan. It refuses the project root, `.git`, `.claude`, `.codex`, `.env`,
dependency folders, virtualenvs, and anything resolving outside the project (including symlinks).
