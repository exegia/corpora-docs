"""Loading and validation for the `sections/` registry.

Every repo that wants a section on this docs site files `sections/<slug>.yml`.
This module is the single definition of what a valid one looks like; the PR
validator, the reconciler and the activation workflow all read it from here so
the three can never disagree about what "valid" means.

See contributing/multi-repo-docs.mdx for the human-facing description.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# A slug is interpolated into a clone URL and a filesystem path by the
# activation workflow. It is author-controlled text from a PR, so it is
# whitelisted here rather than sanitised at each use site.
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
REPO_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

STATUSES = ("pending", "active", "archived")
REQUIRED_KEYS = ("slug", "repo", "docs_path", "label", "status")
OPTIONAL_KEYS = ("icon", "requested_by", "requested_at", "nav_tab")
KNOWN_KEYS = REQUIRED_KEYS + OPTIONAL_KEYS


@dataclass
class Section:
    """One `sections/<slug>.yml` file, parsed and checked."""

    path: Path
    data: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def slug(self) -> str:
        return str(self.data.get("slug") or self.path.stem)

    @property
    def repo(self) -> str:
        return str(self.data.get("repo") or "")

    @property
    def label(self) -> str:
        return str(self.data.get("label") or self.slug)

    @property
    def status(self) -> str:
        return str(self.data.get("status") or "")

    @property
    def icon(self):
        return self.data.get("icon")

    @property
    def nav_tab(self):
        return self.data.get("nav_tab")

    @property
    def docs_path(self) -> str:
        return str(self.data.get("docs_path") or "")

    @property
    def content_prefix(self) -> str:
        """Navigation path prefix for pages from this section.

        A git submodule always clones a *whole* repository, so the source repo's
        `docs/` directory lands at `content/<slug>/docs/` — not at
        `content/<slug>/`. `docs_path` is therefore part of the prefix. (The
        example in contributing/multi-repo-docs.mdx omits it; the submodule
        layout is what the built site actually sees.)
        """
        parts = ["content", self.slug]
        rel = self.docs_path.strip("/")
        if rel and rel != ".":
            parts.extend(rel.split("/"))
        return "/".join(parts) + "/"


def _validate(section: Section) -> None:
    data = section.data
    stem = section.path.stem

    if not isinstance(data, dict):
        section.errors.append("file must contain a YAML mapping of keys to values")
        section.data = {}
        return

    for key in REQUIRED_KEYS:
        if data.get(key) in (None, ""):
            section.errors.append(f"missing required key `{key}`")

    for key in data:
        if key not in KNOWN_KEYS:
            section.warnings.append(f"unrecognised key `{key}` (ignored)")

    slug = data.get("slug")
    if slug is not None:
        if not isinstance(slug, str) or not SLUG_RE.match(slug):
            section.errors.append(
                f"`slug` must be lowercase alphanumeric with hyphens (got `{slug}`)"
            )
        elif slug != stem:
            section.errors.append(
                f"`slug` is `{slug}` but the file is named `{section.path.name}` — "
                f"rename the file to `{slug}.yml`"
            )

    repo = data.get("repo")
    if repo is not None and (not isinstance(repo, str) or not REPO_RE.match(repo)):
        section.errors.append(f"`repo` must be in `owner/name` form (got `{repo}`)")

    status = data.get("status")
    if status is not None and status not in STATUSES:
        section.errors.append(
            f"`status` must be one of {', '.join(STATUSES)} (got `{status}`)"
        )

    docs_path = data.get("docs_path")
    if docs_path is not None:
        if not isinstance(docs_path, str):
            section.errors.append("`docs_path` must be a string")
        elif docs_path.startswith("/") or ".." in docs_path.split("/"):
            section.errors.append(
                f"`docs_path` must be a relative path inside the repo (got `{docs_path}`)"
            )

    requested_at = data.get("requested_at")
    if requested_at is not None and not DATE_RE.match(str(requested_at)):
        section.warnings.append("`requested_at` should be an ISO date (YYYY-MM-DD)")

    for key in ("label", "icon", "nav_tab", "requested_by"):
        value = data.get(key)
        if value is not None and not isinstance(value, str):
            section.errors.append(f"`{key}` must be a string or null")


def load_section(path: Path) -> Section:
    section = Section(path=path)
    try:
        section.data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        section.errors.append(f"not valid YAML: {exc}")
        return section
    _validate(section)
    return section


def load_all(sections_dir: Path) -> list[Section]:
    """Load every `sections/*.yml`, including cross-file uniqueness checks."""
    sections = [load_section(p) for p in sorted(sections_dir.glob("*.yml"))]

    by_slug: dict[str, list[Section]] = {}
    by_repo: dict[str, list[Section]] = {}
    for section in sections:
        by_slug.setdefault(section.slug, []).append(section)
        if section.repo:
            by_repo.setdefault(section.repo.lower(), []).append(section)

    for slug, group in by_slug.items():
        if len(group) > 1:
            others = ", ".join(f"`{s.path.name}`" for s in group)
            for section in group:
                section.errors.append(f"slug `{slug}` is claimed by {others}")

    for repo, group in by_repo.items():
        if len(group) > 1:
            others = ", ".join(f"`{s.path.name}`" for s in group)
            for section in group:
                section.errors.append(f"repo `{repo}` already has a section: {others}")

    return sections
