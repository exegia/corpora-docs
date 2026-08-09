#!/usr/bin/env python3
"""Validate the `sections/` registry and render a Markdown status report.

Used in three places, all read-only:

* `section-request.yml` — on PRs touching `sections/**`, to validate the request
  and post the report as a PR comment (drafts included).
* `reconcile-sections.yml` — on pushes to `main`, to re-check the registry plus
  the two activation invariants (submodule present, navigation merged).
* Locally, to see what CI will say before pushing.

    validate_sections.py                     # schema + uniqueness only
    validate_sections.py --check-activation  # also check submodules + docs.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import json  # noqa: E402

from merge_nav import has_section_pages  # noqa: E402
from sections import Section, load_all  # noqa: E402

STATUS_ICON = {"pending": "🟡", "active": "🟢", "archived": "⚪"}

# Step 2 of "Activating a section" has no API — it is a click in the Mintlify
# dashboard. Automation must say so out loud, otherwise `status: active` reads
# as "the App is connected" when nobody has checked.
MANUAL_CHECKLIST = """\
### Manual step — not automatable

Connecting the [Mintlify GitHub App](https://dashboard.mintlify.com) to a source
repo is dashboard-only; there is no API for it. Nothing in CI can do it or
verify it, so `status: active` does **not** imply the App is connected.

- [ ] In the Mintlify dashboard, add `{repo}` as a connected repository with \
path `/{docs_path}` and deploy branch `main`.

Until that box is ticked, changes in the source repo will not trigger a
rebuild; the submodule pin has to be bumped by hand here instead.\
"""


def activation_problems(section: Section, repo_root: Path) -> list[str]:
    """Invariants an `active` section must satisfy in this repo."""
    problems = []
    if section.status != "active":
        return problems

    if not (repo_root / "content" / section.slug).is_dir():
        problems.append(
            f"submodule missing — run "
            f"`git submodule add https://github.com/{section.repo} content/{section.slug}`"
        )

    docs_json = repo_root / "docs.json"
    if docs_json.is_file():
        docs = json.loads(docs_json.read_text(encoding="utf-8"))
        if not has_section_pages(docs, section):
            problems.append(
                f"navigation not merged — docs.json has no `{section.content_prefix}*` pages"
            )
    return problems


def render(sections: list[Section], check_activation: bool, repo_root: Path) -> tuple[str, bool]:
    lines = ["## Sections registry", ""]
    failed = False

    if not sections:
        return "## Sections registry\n\nNo `sections/*.yml` files found.\n", False

    lines.append("| Section | Status | Repo | Result |")
    lines.append("| --- | --- | --- | --- |")
    details: list[str] = []

    for section in sections:
        problems = section.errors + (
            activation_problems(section, repo_root) if check_activation else []
        )
        if problems:
            failed = True
            result = f"❌ {len(problems)} problem(s)"
        elif section.warnings:
            result = "⚠️ passes with warnings"
        else:
            result = "✅ valid"

        icon = STATUS_ICON.get(section.status, "❔")
        lines.append(
            f"| `{section.path.name}` | {icon} {section.status or '—'} "
            f"| `{section.repo or '—'}` | {result} |"
        )

        if problems or section.warnings:
            details.append(f"\n### `{section.path.name}`\n")
            details.extend(f"- ❌ {p}" for p in problems)
            details.extend(f"- ⚠️ {w}" for w in section.warnings)

        for problem in problems:
            print(f"::error file={section.path}::{problem}", file=sys.stderr)
        for warning in section.warnings:
            print(f"::warning file={section.path}::{warning}", file=sys.stderr)

    lines.extend(details)

    pending = [s for s in sections if s.ok and s.status == "pending"]
    if pending:
        lines.append("")
        lines.append("---")
        for section in pending:
            lines.append("")
            lines.append(
                f"`{section.slug}` is **pending**. Merging this PR records the "
                "request; it does not publish anything. Activation runs when "
                "`status` is set to `active` — see "
                "[the activation steps](https://github.com/exegia/corpora-docs/blob/main/contributing/multi-repo-docs.mdx)."
            )
            lines.append("")
            lines.append(
                MANUAL_CHECKLIST.format(
                    repo=section.repo, docs_path=section.docs_path.strip("/")
                )
            )

    return "\n".join(lines) + "\n", failed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sections-dir", type=Path, default=Path("sections"))
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--check-activation",
        action="store_true",
        help="also require active sections to have a submodule and merged nav",
    )
    parser.add_argument("--output", type=Path, help="write the Markdown report here")
    parser.add_argument(
        "--list-needing-activation",
        action="store_true",
        help="print the slug of every valid `active` section with unmet invariants, "
        "one per line, and nothing else (used by activate-section.yml)",
    )
    args = parser.parse_args(argv)

    if not args.sections_dir.is_dir():
        if not args.list_needing_activation:
            print(f"No {args.sections_dir}/ directory — nothing to validate.")
        return 0

    sections = load_all(args.sections_dir)

    if args.list_needing_activation:
        for section in sections:
            if section.ok and activation_problems(section, args.repo_root):
                print(section.slug)
        return 0

    report, failed = render(sections, args.check_activation, args.repo_root)

    print(report)
    if args.output:
        args.output.write_text(report, encoding="utf-8")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
