#!/usr/bin/env python3
"""Validate `docs.json` and the MDX pages it points at.

This is the docs-repo equivalent of a compiler: Mintlify only reports a broken
navigation entry as a 404 on the deployed site, long after the merge that
introduced it. Everything checked here is checkable offline, which is the whole
point — `make ci` must not depend on the network or on a Mintlify build.

    validate_docs.py            # check docs.json + every page it references

Checks:

* `docs.json` is valid JSON and declares a `navigation`.
* Every page path in `navigation` resolves to a `<path>.mdx` or `<path>.md`.
* Every referenced page carries YAML frontmatter with a non-empty `title`.
* No page is listed twice in the navigation.

Pages under `content/<slug>/` come from a section submodule. When the submodule
has not been checked out (a plain `actions/checkout` without `submodules: true`)
the directory is empty, and those entries are skipped rather than failed —
otherwise this check would be red on every PR in a repo whose activated
sections are, by design, not vendored into the working tree.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_JSON = REPO_ROOT / "docs.json"
PAGE_SUFFIXES = (".mdx", ".md")
SECTION_CONTENT = "content/"


def iter_pages(node, in_pages: bool = False):
    """Yield every page path under a `navigation` object.

    Not `merge_nav.iter_page_paths`: that one takes a single group entry and
    descends `pages` only, so handing it the whole `navigation` object yields
    nothing — the top level is keyed `groups` (or `tabs`, `anchors`,
    `versions`, `languages`, depending on the shape Mintlify is given). A path
    string counts as a page only when it is reached through a `pages` list;
    every other key is just a container to descend through, which keeps
    `"openapi": "spec.json"` and friends from being mistaken for pages.
    """
    if isinstance(node, str):
        if in_pages:
            yield node
    elif isinstance(node, list):
        for child in node:
            yield from iter_pages(child, in_pages)
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from iter_pages(value, in_pages=(key == "pages"))


def page_file(page: str) -> Path | None:
    """Return the file backing a navigation page path, or None if missing."""
    for suffix in PAGE_SUFFIXES:
        candidate = REPO_ROOT / f"{page}{suffix}"
        if candidate.is_file():
            return candidate
    return None


def submodule_absent(page: str) -> bool:
    """True for a `content/<slug>/…` page whose submodule is not checked out."""
    if not page.startswith(SECTION_CONTENT):
        return False
    parts = Path(page).parts
    if len(parts) < 2:
        return False
    root = REPO_ROOT / parts[0] / parts[1]
    return not root.is_dir() or not any(root.iterdir())


def frontmatter_title(path: Path) -> str | None:
    """Read `title:` out of a page's YAML frontmatter without a YAML parser.

    Frontmatter here is a handful of scalar keys, and the section scripts are
    the only place pyyaml is warranted; a line scan keeps this check runnable
    on a bare interpreter.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep and key.strip() == "title":
            return value.strip().strip("'\"") or None
    return None


def main() -> int:
    errors: list[str] = []
    notes: list[str] = []

    if not DOCS_JSON.is_file():
        print("::error::docs.json is missing")
        return 1

    try:
        docs = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"::error file=docs.json,line={exc.lineno}::invalid JSON: {exc.msg}")
        return 1

    navigation = docs.get("navigation")
    if not navigation:
        print("::error file=docs.json::navigation is missing or empty")
        return 1

    seen: set[str] = set()
    checked = 0

    for page in iter_pages(navigation):
        if page.startswith(("http://", "https://")):
            continue
        if page in seen:
            errors.append(f"{page} appears more than once in the navigation")
            continue
        seen.add(page)

        if submodule_absent(page):
            notes.append(f"{page} (section submodule not checked out)")
            continue

        path = page_file(page)
        if path is None:
            errors.append(
                f"{page} is in the navigation but no {page}.mdx or {page}.md exists"
            )
            continue

        if not frontmatter_title(path):
            errors.append(
                f"{path.relative_to(REPO_ROOT)} has no `title` in its frontmatter"
            )
        checked += 1

    # A navigation shape this walk cannot descend would otherwise report zero
    # problems over zero pages, which reads exactly like a pass.
    if not seen:
        print("::error file=docs.json::navigation contains no page entries")
        return 1

    for note in notes:
        print(f"  skipped {note}")
    for error in errors:
        print(f"::error file=docs.json::{error}")

    if errors:
        print(f"\ndocs.json: {len(errors)} problem(s) in {len(seen)} navigation entries")
        return 1

    print(f"docs.json: {checked} page(s) validated, {len(notes)} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
