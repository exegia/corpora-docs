#!/usr/bin/env python3
"""Mirror docs from source repositories into this repo and merge their navigation.

Mintlify builds from a single repository and does not resolve git submodules
(verified: https://github.com/exegia/corpora-docs/pull/12), so content from other
exegia repos has to physically exist in this repo's tree at build time. This
script is what puts it there.

For every `sections/*.yml` with `status: active` it:

  1. clones the source repo at its configured branch,
  2. copies `<docs_path>/` into `content/<slug>/`,
  3. rewrites root-relative links in the mirrored pages so they stay inside the
     section (a source page linking to `/quickstart` must not land on the hub's
     own `/quickstart`),
  4. regenerates that section's navigation group in `docs.json` from the source
     repo's own `docs.json`.

Run with --check to fail instead of writing when the mirror is out of date.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SECTIONS_DIR = REPO_ROOT / "sections"
CONTENT_DIR = REPO_ROOT / "content"
DOCS_JSON = REPO_ROOT / "docs.json"

# Assets are copied wholesale; pages are copied only if the source navigation
# references them (see copy_docs). docs.json is never copied — it is the
# source's own site config and would collide with this repo's.
ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"}
SKIP_NAMES = {"docs.json", ".git", "node_modules"}


class SectionError(Exception):
    """A section is misconfigured. Message is surfaced as a CI annotation."""


def load_sections() -> list[dict]:
    sections = []
    for path in sorted(SECTIONS_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text())
        data["_file"] = path.relative_to(REPO_ROOT).as_posix()
        sections.append(data)
    return sections


def active_sections(sections: list[dict]) -> list[dict]:
    return [s for s in sections if s.get("status") == "active"]


def clone(repo: str, branch: str, dest: Path) -> None:
    # SOURCES_TOKEN is only needed for private source repos. It is interpolated
    # into the URL rather than passed as an arg so it never reaches the process
    # list; git still prints it on failure, so callers must not echo stderr raw.
    token = os.environ.get("SOURCES_TOKEN")
    auth = f"x-access-token:{token}@" if token else ""
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", branch,
         f"https://{auth}github.com/{repo}.git", str(dest)],
        check=True, capture_output=True, text=True,
    )


def redact(text: str) -> str:
    token = os.environ.get("SOURCES_TOKEN")
    return text.replace(token, "***") if token else text


def copy_docs(src: Path, dest: Path, wanted: set[str]) -> list[str]:
    """Copy the pages the source navigation references, plus every asset.

    Only navigation-referenced pages are mirrored. A source `docs/` directory
    routinely holds non-page Markdown — agent SKILL.md files, notes, templates —
    that is not documentation and whose contents (bare `<placeholder>` angle
    brackets, stray braces) are a hard MDX parse error that would fail the whole
    site build. Mirroring exactly what the nav asks for avoids that entirely.
    """
    if dest.exists():
        shutil.rmtree(dest)

    pages: list[str] = []
    missing: list[str] = []
    for page in sorted(wanted):
        for suffix in (".mdx", ".md"):
            source_file = src / f"{page}{suffix}"
            if source_file.is_file():
                target = dest / f"{page}{suffix}"
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target)
                pages.append(page)
                break
        else:
            missing.append(page)
    if missing:
        raise SectionError(
            "navigation references pages that do not exist: " + ", ".join(missing))

    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        if any(part in SKIP_NAMES for part in rel.parts):
            continue
        if not path.is_file() or path.suffix.lower() not in ASSET_SUFFIXES:
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

    return pages


def rewrite_links(dest: Path, slug: str, pages: set[str]) -> int:
    """Prefix root-relative links that point at pages inside this section.

    Source repos are written as standalone sites, so they link to `/quickstart`
    meaning *their* quickstart. Mirrored into the hub, that URL belongs to the
    hub. Only links resolving to a known page of this section are rewritten;
    anything else is left alone, so external and hub links keep working.
    """
    pattern = re.compile(r'(?P<open>\]\(|href=")(?P<path>/[A-Za-z0-9._~\-/]*)')
    count = 0

    def replace(match: re.Match) -> str:
        nonlocal count
        target = match["path"].rstrip("/").lstrip("/")
        if target not in pages:
            return match[0]
        count += 1
        return f'{match["open"]}/content/{slug}/{target}'

    for path in dest.rglob("*"):
        if path.suffix.lower() not in {".mdx", ".md"}:
            continue
        original = path.read_text()
        updated = pattern.sub(replace, original)
        if updated != original:
            path.write_text(updated)
    return count


def source_nav_groups(source_docs: Path, slug: str, label: str) -> dict:
    """Build this section's top-level nav group from the source repo's docs.json.

    Source navigation is either `tabs` (each holding groups) or `groups`. Both
    collapse into nested groups under a single top-level group named `label`,
    which keeps the source's own structure visible in the hub sidebar.
    """
    config_path = source_docs / "docs.json"
    if not config_path.exists():
        raise SectionError(f"{config_path.name} not found in source docs directory")
    try:
        nav = json.loads(config_path.read_text()).get("navigation")
    except json.JSONDecodeError as exc:
        raise SectionError(f"docs.json is not valid JSON: {exc}") from exc
    if not nav:
        raise SectionError("docs.json has no `navigation` block")

    def prefix(pages: list) -> list:
        out = []
        for page in pages:
            if isinstance(page, str):
                out.append(f"content/{slug}/{page}")
            elif isinstance(page, dict) and "group" in page:
                out.append({"group": page["group"], "pages": prefix(page.get("pages", []))})
        return out

    children: list = []
    if "tabs" in nav:
        for tab in nav["tabs"]:
            groups = [
                {"group": g["group"], "pages": prefix(g.get("pages", []))}
                for g in tab.get("groups", [])
            ]
            # A single-tab source adds a meaningless nesting level; hoist it.
            children.extend(groups if len(nav["tabs"]) == 1
                            else [{"group": tab["tab"], "pages": groups}])
    elif "groups" in nav:
        children.extend(
            {"group": g["group"], "pages": prefix(g.get("pages", []))}
            for g in nav["groups"]
        )
    else:
        raise SectionError("docs.json navigation has neither `tabs` nor `groups`")

    return {"group": label, "pages": collapse_repeated(children)}


def collapse_repeated(children: list) -> list:
    """Flatten a nested group that repeats its parent's name.

    A source tab named "Get started" holding a group also named "Get started"
    would otherwise render as Auth > Get started > Get started. Mintlify allows
    page strings and nested groups to share a `pages` array, so the inner
    group's contents can be hoisted in place.
    """
    out: list = []
    for child in children:
        if not isinstance(child, dict):
            out.append(child)
            continue
        pages = collapse_repeated(child.get("pages", []))
        inner = [p for p in pages if isinstance(p, dict) and p.get("group") == child["group"]]
        if inner:
            rest = [p for p in pages if p not in inner]
            pages = [p for group in inner for p in group.get("pages", [])] + rest
        out.append({"group": child["group"], "pages": pages})
    return out


def nav_page_paths(node) -> set[str]:
    """Every page path referenced anywhere in a nav subtree."""
    if isinstance(node, str):
        return {node}
    if isinstance(node, dict):
        return nav_page_paths(node.get("pages", []))
    return {p for item in node for p in nav_page_paths(item)}


def is_generated(group: dict) -> bool:
    """True if every page in this group is mirrored content.

    Section groups are identified structurally rather than by name. Matching on
    the section `label` would mean a label colliding with one of this repo's own
    group names silently deleted that group, and would strand a group whose
    label was renamed or whose section file was deleted outright.
    """
    paths = nav_page_paths(group)
    return bool(paths) and all(p.startswith("content/") for p in paths)


def splice_nav(docs: dict, generated: list[dict]) -> dict:
    """Replace all generated groups, leaving this repo's own groups untouched."""
    kept = [g for g in docs["navigation"]["groups"] if not is_generated(g)]
    docs["navigation"]["groups"] = kept + generated
    return docs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if the mirror is out of date instead of writing")
    args = parser.parse_args()

    sections = load_sections()
    active = active_sections(sections)

    docs = json.loads(DOCS_JSON.read_text())

    # A section label is a top-level sidebar group name. It must not collide with
    # one of this repo's own groups (the sidebar would show two "Backend" groups)
    # nor with another section's.
    hub_groups = {g["group"] for g in docs["navigation"]["groups"] if not is_generated(g)}
    seen: set[str] = set()
    for section in sections:
        label = section.get("label")
        if label in hub_groups:
            print(f"::error file={section['_file']}::label '{label}' collides with this "
                  f"repo's own navigation group of the same name — choose another label")
            return 1
        if label in seen:
            print(f"::error file={section['_file']}::label '{label}' is already used by "
                  f"another section — labels must be unique")
            return 1
        seen.add(label)
    generated: list[dict] = []
    failed = False

    if CONTENT_DIR.exists():
        shutil.rmtree(CONTENT_DIR)

    for section in active:
        slug = section["slug"]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                clone(section["repo"], section.get("branch", "main"), Path(tmp))
                source_docs = Path(tmp) / section.get("docs_path", "docs")
                if not source_docs.is_dir():
                    raise SectionError(
                        f"docs_path '{section.get('docs_path', 'docs')}' does not exist in "
                        f"{section['repo']}")

                # Navigation first: it determines which pages get mirrored.
                group = source_nav_groups(source_docs, slug, section["label"])
                prefix = f"content/{slug}/"
                wanted = {p[len(prefix):] for p in nav_page_paths(group)}
                if not wanted:
                    raise SectionError("navigation references no pages")

                dest = CONTENT_DIR / slug
                pages = copy_docs(source_docs, dest, wanted)
                rewritten = rewrite_links(dest, slug, set(pages))
                generated.append(group)
                print(f"✓ {slug}: {len(pages)} pages, {rewritten} links rewritten")
        except SectionError as exc:
            print(f"::error file={section['_file']}::{slug}: {exc}")
            failed = True
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip().splitlines()[-1] if exc.stderr else str(exc)
            print(f"::error file={section['_file']}::{slug}: clone failed: {redact(detail)}")
            failed = True

    if failed:
        return 1

    splice_nav(docs, generated)
    DOCS_JSON.write_text(json.dumps(docs, indent=2) + "\n")

    if args.check:
        # The mirror has been regenerated in the working tree; anything git sees
        # as changed means the committed mirror had drifted from its sources.
        diff = subprocess.run(
            ["git", "status", "--porcelain", "--", "content", "docs.json"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if diff:
            print("::error::The committed mirror is out of date. Run "
                  "`python3 scripts/mirror_sections.py` and commit the result.")
            print(diff)
            return 1
        print(f"Mirror is up to date ({len(generated)} section(s))")
        return 0

    print(f"Mirrored {len(generated)} section(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
