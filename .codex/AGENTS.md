# Codex Configuration

This folder mirrors the Claude Code setup so the `refactor-arch` workflow can be used from Codex.

## Skill Location

Use the Codex copy at:

`./.codex/skills/refactor-arch/`

The skill keeps the same name, `$refactor-arch`, and includes the same reference files as the Claude version.

## Permission Policy Equivalent

Claude's `.claude/settings.json` allowlist is not a native Codex configuration format. In Codex, apply the same policy through these operating rules:

- Prefer file/search tools for inspection.
- Use `rtk` before shell commands when available.
- Do not read `.env` files.
- Ask for approval before dependency installs, writes outside the workspace, GUI/browser actions, and destructive operations.
- Treat `rm -rf` and similar destructive commands as denied unless the user explicitly requests them.
- Keep shell commands focused and easy to approve.

## Validation Policy

For Phase 3 refactors, validate with the target app's own toolchain. At minimum, boot the app and confirm every original endpoint still responds.
