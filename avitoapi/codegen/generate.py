"""Top-level driver — spec → three source files per domain, written under ``avitoapi/``."""

from __future__ import annotations

import subprocess
from pathlib import Path

from . import build, emit_enums, emit_facade, emit_methods, emit_models, fetch, spec

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def render_domain(slug: str, *, use_cache: bool = True) -> dict[str, str]:
    """Return ``{relative_path: source}`` for one domain's enums/models/methods/facade."""

    info = next((d for d in fetch.list_domains() if d.slug == slug), None)
    title = info.title if info else slug
    document = fetch.fetch_spec(slug, use_cache=use_cache)
    domain = spec.build_domain(slug, title, document)
    gen = build.build_domain(domain)
    return {
        f"enums/{gen.module}.py": emit_enums.emit(gen),
        f"models/{gen.module}.py": emit_models.emit(gen),
        f"methods/{gen.module}.py": emit_methods.emit(gen),
        f"facade/{gen.module}.py": emit_facade.emit(gen),
    }


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
    """Render one domain and (unless ``dry_run``) write + format the files."""

    files = render_domain(slug, use_cache=use_cache)
    if dry_run:
        return files
    written = write_files(files)
    format_files(written)
    return files


def all_slugs() -> list[str]:
    return [d.slug for d in fetch.list_domains()]
