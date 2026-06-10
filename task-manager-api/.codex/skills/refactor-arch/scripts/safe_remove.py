#!/usr/bin/env python3
"""Guardrailed file/directory removal for refactoring tasks.

Default mode is dry-run. Pass --confirm to actually remove targets.
Targets must resolve inside the project root, which defaults to cwd.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


PROTECTED_PARTS = {
    ".git",
    ".claude",
    ".codex",
    ".env",
    "node_modules",
    ".venv",
    "venv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely remove files/directories inside the current project only."
    )
    parser.add_argument("targets", nargs="+", help="Files or directories to remove")
    parser.add_argument(
        "--root",
        default=".",
        help="Project root boundary. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually remove targets. Without this flag, only prints a dry-run.",
    )
    return parser.parse_args()


def resolve_candidate(root: Path, raw_target: str) -> tuple[Path, Path]:
    candidate = Path(raw_target)
    candidate_abs = candidate if candidate.is_absolute() else root / candidate

    if candidate_abs.exists() or candidate_abs.is_symlink():
        resolved = candidate_abs.resolve()
    else:
        resolved = candidate_abs.parent.resolve() / candidate_abs.name

    return candidate_abs, resolved


def assert_safe(root: Path, candidate_abs: Path, resolved: Path) -> None:
    if resolved == root:
        raise ValueError("refusing to remove the project root")

    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"target resolves outside project root: {resolved}") from exc

    protected = PROTECTED_PARTS.intersection(candidate_abs.parts)
    if protected:
        names = ", ".join(sorted(protected))
        raise ValueError(f"refusing to remove protected project artifact: {names}")


def remove_target(candidate_abs: Path) -> None:
    if not candidate_abs.exists() and not candidate_abs.is_symlink():
        print(f"SKIP missing: {candidate_abs}")
        return

    if candidate_abs.is_symlink() or candidate_abs.is_file():
        candidate_abs.unlink()
        print(f"REMOVE file: {candidate_abs}")
        return

    if candidate_abs.is_dir():
        shutil.rmtree(candidate_abs)
        print(f"REMOVE dir: {candidate_abs}")
        return

    raise ValueError(f"unsupported target type: {candidate_abs}")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if not root.exists() or not root.is_dir():
        print(f"DENY invalid project root: {root}", file=sys.stderr)
        return 2

    planned: list[Path] = []
    for raw_target in args.targets:
        try:
            candidate_abs, resolved = resolve_candidate(root, raw_target)
            assert_safe(root, candidate_abs, resolved)
        except ValueError as exc:
            print(f"DENY {raw_target}: {exc}", file=sys.stderr)
            return 2

        planned.append(candidate_abs)
        action = "REMOVE" if args.confirm else "DRY-RUN"
        print(f"{action}: {candidate_abs}")

    if not args.confirm:
        print("No files removed. Re-run with --confirm to delete the listed targets.")
        return 0

    for target in planned:
        try:
            remove_target(target)
        except ValueError as exc:
            print(f"DENY {target}: {exc}", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
