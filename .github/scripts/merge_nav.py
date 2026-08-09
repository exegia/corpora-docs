#!/usr/bin/env python3
"""Merge a section's navigation into this repo's `docs.json`.

Replaces step 3 of "Activating a section" in contributing/multi-repo-docs.mdx:
read the source repo's `docs.json`, rewrite every page path with the section's
`content/<slug>/…` prefix, and splice the result into this repo's `docs.json`
as a single top-level group named after the section's `label`.

Nesting rather than flattening is deliberate. Mintlify's `navigation` picks one
top-level shape (`tabs` **or** `groups`, not both), and source repos routinely
use group names as generic as "Contributing" or "API". Wrapping each section in
one group named after its label keeps hierarchy intact, avoids collisions with
this repo's own groups, and makes the merge idempotent: re-running removes the
previous block for the slug before inserting the new one.

    # is the merge already present? (read-only, used by the reconciler)
    merge_nav.py check --section sections/corpora-auth.yml

    # what would change? (read-only)
    merge_nav.py merge --section sections/corpora-auth.yml \
        --source /tmp/src/docs.json --diff

    # apply it
    merge_nav.py merge --section sections/corpora-auth.yml \
        --source /tmp/src/docs.json --write
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sections import Section, load_section  # noqa: E402


class MergeError(Exception):
    """A merge that cannot be completed without a human decision."""


# ---------------------------------------------------------------- tree walking


def iter_page_paths(entry):
    """Yield every page-path string reachable from a navigation entry."""
    if isinstance(entry, str):
        yield entry
    elif isinstance(entry, dict):
        for child in entry.get("pages", []):
            yield from iter_page_paths(child)
    elif isinstance(entry, list):
        for child in entry:
            yield from iter_page_paths(child)


def prefix_entry(entry, prefix: str):
    """Copy a navigation entry with every page path rewritten under `prefix`.

    External links (`https://…`) and entries already carrying the prefix are
    left alone, so running this twice is harmless.
    """
    if isinstance(entry, str):
        if entry.startswith(("http://", "https://", "/")) or entry.startswith(prefix):
            return entry
        return prefix + entry.lstrip("./")
    if isinstance(entry, dict):
        out = dict(entry)
        if "pages" in out and isinstance(out["pages"], list):
            out["pages"] = [prefix_entry(child, prefix) for child in out["pages"]]
        return out
    raise MergeError(f"unsupported navigation entry: {entry!r}")


def source_entries(source_nav: dict, prefix: str) -> list:
    """Flatten a source repo's `navigation` into entries for one target group.

    `tabs` become nested groups so the source's own hierarchy survives; a tab
    holding a single identically-named group is collapsed rather than doubled.
    """
    if not isinstance(source_nav, dict):
        raise MergeError("source docs.json has no `navigation` object")

    if "tabs" in source_nav:
        entries = []
        for tab in source_nav["tabs"]:
            name = tab.get("tab") or tab.get("group") or "Docs"
            groups = tab.get("groups")
            if groups is None:
                children = [prefix_entry(p, prefix) for p in tab.get("pages", [])]
            elif len(groups) == 1 and groups[0].get("group") == name:
                entries.append(prefix_entry(groups[0], prefix))
                continue
            else:
                children = [prefix_entry(g, prefix) for g in groups]
            entries.append({"group": name, "pages": children})
        return entries

    if "groups" in source_nav:
        return [prefix_entry(g, prefix) for g in source_nav["groups"]]

    if "pages" in source_nav:
        return [prefix_entry(p, prefix) for p in source_nav["pages"]]

    raise MergeError(
        "source `navigation` uses none of `tabs`, `groups` or `pages` — "
        "anchors/dropdowns/versions are not supported by this merge yet"
    )


# ------------------------------------------------------------------- splicing


def belongs_to_section(entry, section: Section) -> bool:
    """Is this existing top-level entry the block previously written for `section`?"""
    paths = list(iter_page_paths(entry))
    if paths and all(p.startswith(section.content_prefix) for p in paths):
        return True
    # An empty placeholder group left behind by a partial activation.
    return isinstance(entry, dict) and not paths and entry.get("group") == section.label


def target_container(navigation: dict, section: Section) -> list:
    """The list this section's group lives in, given `nav_tab`.

    Returns the live list object so callers mutate `navigation` in place.
    """
    if section.nav_tab:
        if "tabs" not in navigation:
            raise MergeError(
                f"`nav_tab: {section.nav_tab}` was requested but this repo's "
                "docs.json navigation uses top-level `groups`. Mintlify allows "
                "one top-level shape, so adding a tab means converting the whole "
                "navigation to `tabs` first — a deliberate restructure, not "
                "something this script does on its own. Either do that "
                "conversion by hand or set `nav_tab: null`."
            )
        for tab in navigation["tabs"]:
            if tab.get("tab") == section.nav_tab:
                return tab.setdefault("groups", [])
        tab = {"tab": section.nav_tab, "groups": []}
        navigation["tabs"].append(tab)
        return tab["groups"]

    if "groups" in navigation:
        return navigation["groups"]
    if "tabs" in navigation:
        raise MergeError(
            "this repo's docs.json navigation uses `tabs`, so a section must say "
            "which one to join — set `nav_tab` in the section YAML."
        )
    raise MergeError("this repo's docs.json navigation has no `groups` or `tabs`")


def build_section_group(section: Section, source_nav: dict) -> dict:
    group = {"group": section.label}
    if section.icon:
        group["icon"] = section.icon
    group["pages"] = source_entries(source_nav, section.content_prefix)
    if not group["pages"]:
        raise MergeError("source navigation contains no pages")
    return group


def merge(docs: dict, section: Section, source_nav: dict) -> dict:
    """Return `docs` with the section's navigation block inserted or refreshed."""
    navigation = docs.get("navigation")
    if not isinstance(navigation, dict):
        raise MergeError("docs.json has no `navigation` object")

    container = target_container(navigation, section)
    group = build_section_group(section, source_nav)

    for index, entry in enumerate(container):
        if belongs_to_section(entry, section):
            container[index] = group
            # Drop any further stale blocks for the same slug.
            container[:] = [
                e
                for i, e in enumerate(container)
                if i <= index or not belongs_to_section(e, section)
            ]
            return docs

    container.append(group)
    return docs


def has_section_pages(docs: dict, section: Section) -> bool:
    """Does `docs.json` already carry navigation entries for this section?

    Covers the two top-level shapes this repo's `docs.json` can take. A target
    rooted at `pages`, `anchors`, `dropdowns` or `versions` would read as "not
    merged" — `merge()` refuses those shapes outright, so the two agree, but
    both would need extending together.
    """
    return any(
        path.startswith(section.content_prefix)
        for path in iter_page_paths(docs.get("navigation", {}).get("tabs", []))
    ) or any(
        path.startswith(section.content_prefix)
        for path in iter_page_paths(docs.get("navigation", {}).get("groups", []))
    )


# ------------------------------------------------------------------------ cli


def dump(docs: dict) -> str:
    return json.dumps(docs, indent=2, ensure_ascii=False) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("merge", "check"))
    parser.add_argument("--section", required=True, type=Path)
    parser.add_argument("--source", type=Path, help="source repo's docs.json")
    parser.add_argument("--docs-json", type=Path, default=Path("docs.json"))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--diff", action="store_true")
    args = parser.parse_args(argv)

    section = load_section(args.section)
    if not section.ok:
        for error in section.errors:
            print(f"::error file={args.section}::{error}", file=sys.stderr)
        return 1

    before = args.docs_json.read_text(encoding="utf-8")
    docs = json.loads(before)

    if args.command == "check":
        if has_section_pages(docs, section):
            print(f"✓ {section.slug}: navigation entries present in {args.docs_json}")
            return 0
        print(f"✗ {section.slug}: no `{section.content_prefix}*` entries in {args.docs_json}")
        return 1

    if not args.source:
        parser.error("merge requires --source")

    source = json.loads(args.source.read_text(encoding="utf-8"))
    try:
        after = dump(merge(docs, section, source.get("navigation", {})))
    except MergeError as exc:
        print(f"::error file={args.section}::{exc}", file=sys.stderr)
        return 1

    if args.diff or not args.write:
        sys.stdout.writelines(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=f"a/{args.docs_json}",
                tofile=f"b/{args.docs_json}",
            )
        )

    if args.write:
        args.docs_json.write_text(after, encoding="utf-8")
        print(f"Wrote {args.docs_json}")
    elif before == after:
        print("No change — navigation is already up to date.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
