---
name: mintlify-section-request
description: Registers a repository as a section of the org's central Mintlify docs site (exegia). Use this whenever a user wants to "add this repo to the docs site", "publish our docs as a section", "get this repo listed on the docs site", "request a Mintlify section", or asks to create a docs-registration config/YAML/manifest file for a repository. Also trigger if the user mentions wanting their repo's `docs/` folder surfaced on the shared documentation site, even if they don't name Mintlify explicitly (e.g. "our documentation site", "the company docs portal"). Works from inside any exegia/corpora repo that has (or will have) a Mintlify-compatible `docs/` folder. Do NOT use for editing existing docs content — use the docx/pptx/general editing tools for that; this skill is only for the registration/request step.
---

# Mintlify Section Request

Generates a local registration manifest inside a repo, declaring that the repo's `docs/` folder should be
onboarded as a **section** of the org's central Mintlify docs site, then opens a PR against the central docs
registry repo so a human (or later automation) can reconcile it into `docs.json` navigation.

This skill covers **registration/request only**. It does not publish anything by itself — publishing on Mintlify
happens via the Mintlify GitHub App watching a deploy branch, which is a separate, per-repo setup step (see
`references/central-registry.md` for the current state of that in this org).

## When this applies

Trigger on requests like:
- "add this repo as a section on the docs site"
- "create a config so our repo shows up in the Mintlify docs"
- "request our docs get parsed into the central site"
- "generate the YAML that registers us with the docs site"

## Prerequisites to check first

1. **Is there a `docs/` folder in this repo?** If not, ask whether one should be scaffolded first (a bare minimum
   `docs/docs.json` + one `.mdx` page) or whether the user just wants the *request* filed now for a docs folder
   that's coming later. Don't block on this — a request can be filed with `docsPath` pointing at a
   not-yet-existing path; note that clearly in the PR description.
2. **Do we know the central registry repo?** There is no single confirmed name for it in this org yet (see
   `references/central-registry.md`). Ask the user once per session; don't guess silently. Offer the two known
   candidates from project context (`exegia/docs`, or repointing the existing `exegia` Mintlify deployment) and a
   free-text option.
3. **Is `gh` (GitHub CLI) available and authenticated?** Check with `gh auth status`. If not available/authenticated,
   fall back to producing the branch + commit locally and give the user the manual PR steps — do not fabricate a
   PR link.

## Workflow

### Step 1 — Gather section metadata

Ask (or infer from the repo's `package.json`/`Cargo.toml`/README) — keep this quick, don't interview if
reasonable defaults exist:

- `title` — human-readable section name (default: repo name, title-cased)
- `slug` — kebab-case nav path segment (default: derived from repo name)
- `description` — one sentence, shown in nav tooltip/search (default: repo description from git remote/README)
- `docsPath` — path within this repo containing Mintlify-compatible docs (default: `docs`)
- `owner` — team or person responsible (ask; no safe default)
- `icon` — optional Mintlify icon name

### Step 2 — Generate the local manifest

Run `scripts/generate_section_manifest.py` from the target repo's root. It:
- Auto-detects `repo` (owner/name) from `git remote get-url origin`
- Writes `.mintlify/section-request.yml` (schema in `references/schema.md`)
- Validates `docsPath` exists and warns (does not fail) if it doesn't
- Is idempotent — re-running updates `metadata.requestedAt` and diffs the rest

```bash
python3 scripts/generate_section_manifest.py \
  --title "Corpora Auth" \
  --slug corpora-auth \
  --description "Auth plugin + hooks for Supabase, Tauri-first." \
  --owner "@exegia/platform-team" \
  --docs-path docs
```

Commit this file to the repo being registered (it's the durable, human-readable record of the request — keep it
even after the central side is reconciled, so re-running the skill later is a diff, not a mystery).

### Step 3 — Open the registration PR against the central registry

Run `scripts/submit_section_request.sh`, which:
1. Clones (or updates a local cache of) the central registry repo
2. Writes/updates `sections/<slug>.yml` there — **one file per requesting repo**, never a shared file — copying
   the manifest from Step 2 plus a `status: pending` field
3. Opens a branch `section-request/<slug>`, commits, and (if `gh` is available and the user confirms) opens a PR

```bash
./scripts/submit_section_request.sh \
  --manifest .mintlify/section-request.yml \
  --registry-repo <owner/central-docs-repo>   # confirmed with the user in Step 0, never guessed
```

**This step sends a message on the user's behalf (opens a PR) — always confirm with the user before running the
PR-creation part**, per standing rules on side-effectful actions. Show them the diff first.

### Step 4 — Report back

Summarize for the user:
- Path to the local manifest committed
- Central registry PR link (or, if `gh` wasn't available, the exact manual steps + local branch name)
- A pointer to `references/central-registry.md` if the Mintlify GitHub App isn't connected for their repo yet —
  that's a separate blocker from registration and shouldn't be conflated with "the request failed"

## Known limitation — flag, don't hide

The central "one docs site aggregating many repo sections" mechanism is **not yet a settled, built system in this
org** — this skill produces the *request artifact* (local manifest + registry-repo PR) on the assumption that a
human or a later automation reconciles `sections/*.yml` into the live `docs.json`. If the user expects the section
to go live immediately after this skill runs, correct that expectation explicitly rather than implying it's done.
