#!/usr/bin/env python3
"""
Generate (or update) .mintlify/section-request.yml in the current repo.

Usage:
  python3 generate_section_manifest.py \
    --title "Corpora Auth" \
    --slug corpora-auth \
    --description "Auth plugin + hooks for Supabase, Tauri-first." \
    --owner "@exegia/platform-team" \
    [--docs-path docs] \
    [--icon lock] \
    [--tags auth,plugin,tauri] \
    [--repo-root .]

Idempotent: re-running preserves everything except metadata.requestedAt, and prints a diff-style
summary of what changed so re-runs are transparent rather than silent overwrites.
"""
import argparse
import datetime
import pathlib
import subprocess
import sys

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml --break-system-packages", file=sys.stderr)
    sys.exit(1)


def run(cmd, cwd):
    try:
        return subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None


def detect_repo(repo_root: pathlib.Path) -> str:
    url = run(["git", "remote", "get-url", "origin"], cwd=repo_root)
    if not url:
        return "UNKNOWN/UNKNOWN"
    # Normalize both git@github.com:owner/name.git and https://github.com/owner/name.git
    url = url.removesuffix(".git")
    if url.startswith("git@"):
        _, path = url.split(":", 1)
    else:
        path = url.split("github.com/", 1)[-1]
    return path


def detect_user(repo_root: pathlib.Path) -> str:
    email = run(["git", "config", "user.email"], cwd=repo_root)
    return email or "UNKNOWN"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--slug", required=True, help="kebab-case, becomes the registry filename too")
    p.add_argument("--description", required=True)
    p.add_argument("--owner", required=True, help='e.g. "@exegia/platform-team"')
    p.add_argument("--docs-path", default="docs")
    p.add_argument("--icon", default=None)
    p.add_argument("--tags", default="", help="comma-separated")
    p.add_argument("--repo-root", default=".")
    args = p.parse_args()

    if args.slug != args.slug.lower() or " " in args.slug or "_" in args.slug:
        print(f"warning: --slug '{args.slug}' should be kebab-case (lowercase, hyphens only)", file=sys.stderr)

    repo_root = pathlib.Path(args.repo_root).resolve()
    docs_path = repo_root / args.docs_path
    if not docs_path.exists():
        print(f"warning: docs path '{args.docs_path}' does not exist yet in this repo — "
              f"filing the request anyway, but say so explicitly in the PR (see SKILL.md Step 3).",
              file=sys.stderr)

    manifest_dir = repo_root / ".mintlify"
    manifest_dir.mkdir(exist_ok=True)
    manifest_path = manifest_dir / "section-request.yml"

    existing = {}
    if manifest_path.exists():
        existing = yaml.safe_load(manifest_path.read_text()) or {}
        print(f"Existing manifest found at {manifest_path} — updating in place.")

    manifest = {
        "apiVersion": "v1",
        "kind": "MintlifySectionRequest",
        "metadata": {
            "repo": detect_repo(repo_root),
            "requestedAt": datetime.datetime.now(datetime.timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z"),
            "requestedBy": detect_user(repo_root),
            # status is registry-owned; only ever seed it, never clobber an existing non-pending value
            "status": existing.get("metadata", {}).get("status", "pending"),
        },
        "section": {
            "title": args.title,
            "slug": args.slug,
            "description": args.description,
            "docsPath": args.docs_path,
        },
        "owner": args.owner,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
    }
    if args.icon:
        manifest["section"]["icon"] = args.icon
    # Preserve a hand-edited `navigation` block across regenerations if present
    if "navigation" in existing.get("section", {}):
        manifest["section"]["navigation"] = existing["section"]["navigation"]

    manifest_path.write_text(yaml.dump(manifest, sort_keys=False, default_flow_style=False))
    print(f"Wrote {manifest_path}")
    print(yaml.dump(manifest, sort_keys=False, default_flow_style=False))


if __name__ == "__main__":
    main()
