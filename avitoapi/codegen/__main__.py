"""CLI — ``python -m avitoapi.codegen [--slug item | --all] [--dry-run] [--no-cache]``."""

from __future__ import annotations

import argparse
import sys

from .generate import generate, generate_all


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="avitoapi.codegen", description="Regenerate the SDK from the Avito OpenAPI spec.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--slug", help="Regenerate a single domain (e.g. 'item'). No cross-domain passes.")
    group.add_argument("--all", action="store_true", help="Regenerate every domain two-phase (dedup + collision passes).")
    parser.add_argument("--dry-run", action="store_true", help="Print target files without writing.")
    parser.add_argument("--no-cache", action="store_true", help="Bypass the on-disk spec cache.")
    args = parser.parse_args(argv)

    verb = "would write" if args.dry_run else "wrote"
    if args.all:
        files = generate_all(use_cache=not args.no_cache, dry_run=args.dry_run)
        print(f"[all] {verb} {len(files)} files across the catalogue.")  # noqa: T201 — CLI output
    else:
        files = generate(args.slug, use_cache=not args.no_cache, dry_run=args.dry_run)
        print(f"[{args.slug}] {verb}: {', '.join(sorted(files))}")  # noqa: T201 — CLI output
    return 0


if __name__ == "__main__":
    sys.exit(main())
