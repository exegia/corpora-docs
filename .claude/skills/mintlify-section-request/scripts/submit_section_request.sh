#!/usr/bin/env bash
# Opens (or prepares) a PR against the central Mintlify docs registry repo, adding
# sections/<slug>.yml built from a local .mintlify/section-request.yml manifest.
#
# Safety: defaults to --dry-run. Nothing is pushed or PR'd until the caller passes --yes,
# per the standing rule that side-effectful actions (opening a PR) need explicit confirmation.
#
# Usage:
#   ./submit_section_request.sh --manifest .mintlify/section-request.yml \
#       --registry-repo <owner/central-docs-repo> [--yes]

set -euo pipefail

MANIFEST=""
REGISTRY_REPO=""
DRY_RUN=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest) MANIFEST="$2"; shift 2 ;;
    --registry-repo) REGISTRY_REPO="$2"; shift 2 ;;
    --yes) DRY_RUN=0; shift ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$MANIFEST" || -z "$REGISTRY_REPO" ]]; then
  echo "usage: $0 --manifest <path> --registry-repo <owner/name> [--yes]" >&2
  exit 1
fi
if [[ ! -f "$MANIFEST" ]]; then
  echo "manifest not found: $MANIFEST — run generate_section_manifest.py first" >&2
  exit 1
fi

SLUG=$(python3 -c "import yaml,sys; print(yaml.safe_load(open('$MANIFEST'))['section']['slug'])")
if [[ -z "$SLUG" ]]; then
  echo "could not read section.slug from $MANIFEST" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh (GitHub CLI) not found. Manual steps:" >&2
  echo "  1. git clone https://github.com/$REGISTRY_REPO" >&2
  echo "  2. mkdir -p sections && cp $MANIFEST sections/$SLUG.yml" >&2
  echo "  3. Add 'status: pending' if not already present" >&2
  echo "  4. git checkout -b section-request/$SLUG && git add sections/$SLUG.yml" >&2
  echo "  5. git commit -m 'Request Mintlify section: $SLUG' && git push -u origin section-request/$SLUG" >&2
  echo "  6. Open a PR by hand" >&2
  exit 0
fi

WORKDIR=$(mktemp -d)
trap 'rm -rf "$WORKDIR"' EXIT

echo "Cloning $REGISTRY_REPO ..."
gh repo clone "$REGISTRY_REPO" "$WORKDIR/registry" -- --depth 1 2>/dev/null \
  || { echo "Could not clone $REGISTRY_REPO — confirm the repo name/permissions with the user before retrying." >&2; exit 1; }

cd "$WORKDIR/registry"

if [[ -f "sections/$SLUG.yml" ]]; then
  echo "COLLISION: sections/$SLUG.yml already exists in $REGISTRY_REPO." >&2
  echo "Not overwriting. Pick a different --slug or coordinate with the existing owner." >&2
  diff -u "sections/$SLUG.yml" "$OLDPWD/$MANIFEST" || true
  exit 1
fi

mkdir -p sections
cp "$OLDPWD/$MANIFEST" "sections/$SLUG.yml"

BRANCH="section-request/$SLUG"
git checkout -b "$BRANCH"
git add "sections/$SLUG.yml"
git -c user.name="mintlify-section-request skill" -c user.email="noreply@localhost" \
  commit -m "Request Mintlify section: $SLUG"

echo
echo "=== Prepared change (dry-run=$DRY_RUN) ==="
git show --stat HEAD
echo

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run only — nothing pushed. Re-run with --yes after the user confirms the diff above."
  exit 0
fi

git push -u origin "$BRANCH"
gh pr create \
  --title "Request Mintlify section: $SLUG" \
  --body "Automated section request via mintlify-section-request skill. See sections/$SLUG.yml for the manifest. Status: pending — a maintainer needs to reconcile this into docs.json." \
  --base main \
  --head "$BRANCH"
