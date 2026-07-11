"""Top-level driver — spec → source files per domain, written under ``avitoapi/``.

Two entry shapes:

* :func:`generate` — one domain, one-shot (fetch → build → emit → write). No cross-domain
  passes run, so shared-model dedup and facade collision resolution are *not* applied.
* :func:`generate_all` — every domain, two-phase: build **all** ``GeneratedDomain`` first,
  run the global passes (:mod:`collisions`, :mod:`dedup`) that need to see every domain at
  once, then emit + write. This is the path ``python -m avitoapi.codegen --all`` takes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .. import fetch, parser
from . import build, collisions, dedup, emit_enums, emit_facade, emit_methods, emit_models
from .build import GeneratedDomain

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent  # codegen/engine/ -> avitoapi/


def build_one(slug: str, *, use_cache: bool = True) -> GeneratedDomain:
    """Fetch + parse + build one domain into a :class:`GeneratedDomain` (no emit)."""

    info = next((d for d in fetch.list_domains() if d.slug == slug), None)
    title = info.title if info else slug
    document = fetch.fetch_spec(slug, use_cache=use_cache)
    domain = parser.build_domain(slug, title, document)
    return build.build_domain(domain)


def emit_one(gen: GeneratedDomain) -> dict[str, str]:
    """Render one already-built domain to ``{relative_path: source}``."""

    return {
        f"enums/{gen.module}.py": emit_enums.emit(gen),
        f"models/{gen.module}.py": emit_models.emit(gen),
        f"methods/{gen.module}.py": emit_methods.emit(gen),
        f"facade/{gen.module}.py": emit_facade.emit(gen),
    }


def render_domain(slug: str, *, use_cache: bool = True) -> dict[str, str]:
    """Return ``{relative_path: source}`` for one domain's enums/models/methods/facade."""

    return emit_one(build_one(slug, use_cache=use_cache))


def build_all(slugs: list[str], *, use_cache: bool = True) -> list[GeneratedDomain]:
    """Build every domain in ``slugs`` before any emission (phase one of ``--all``)."""

    return [build_one(slug, use_cache=use_cache) for slug in slugs]


def apply_global_passes(domains: list[GeneratedDomain]) -> dict[str, str]:
    """Run cross-domain passes that need the whole catalogue; return extra files to write.

    * :func:`collisions.resolve_facade_collisions` — make facade method names globally unique.
    * :func:`dedup.dedup_shared` — collapse structurally-identical models into ``models/_shared.py``
      and rewrite every reference to them.
    """

    collisions.resolve_facade_collisions(domains)
    return dedup.dedup_shared(domains)


def write_files(files: dict[str, str]) -> list[Path]:
    """Write rendered sources under the package root; return the paths written."""

    written: list[Path] = []
    for rel, source in files.items():
        target = _PACKAGE_ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
        written.append(target)
    return written


def format_files(paths: list[Path]) -> None:
    """Run ruff format + autofix over the generated files (best-effort)."""

    if not paths:
        return
    args = [str(p) for p in paths]
    subprocess.run(["ruff", "check", "--fix", "--quiet", *args], check=False, cwd=_PACKAGE_ROOT.parent)  # noqa: S603, S607
    subprocess.run(["ruff", "format", "--quiet", *args], check=False, cwd=_PACKAGE_ROOT.parent)  # noqa: S603, S607


def generate(slug: str, *, use_cache: bool = True, dry_run: bool = False) -> dict[str, str]:
    """Render one domain and (unless ``dry_run``) write + format the files.

    Single-domain path: no cross-domain passes, so a lone ``--slug`` run does not dedup
    shared models or resolve facade collisions. Use ``--all`` for a consistent catalogue.
    """

    files = render_domain(slug, use_cache=use_cache)
    if dry_run:
        return files
    written = write_files(files)
    format_files(written)
    return files


def generate_all(*, use_cache: bool = True, dry_run: bool = False) -> dict[str, str]:
    """Regenerate every domain two-phase: build all → global passes → emit → write."""

    domains = build_all(all_slugs(), use_cache=use_cache)
    extra = apply_global_passes(domains)
    files: dict[str, str] = {}
    for gen in domains:
        files.update(emit_one(gen))
    files.update(extra)
    if dry_run:
        return files
    written = write_files(files)
    format_files(written)
    return files


def all_slugs() -> list[str]:
    return [d.slug for d in fetch.list_domains()]
