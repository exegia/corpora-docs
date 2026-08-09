---
name: sketch-to-spec
description: Turns a Sketch design (page or frame) into a GitHub Spec Kit (spec.md/plan.md/tasks.md, issues, feature branches) plus Mintlify-ready MDX documentation with embedded design visuals. Use this whenever the user wants to go from a Sketch mockup to specs, GitHub issues, or docs — phrases like "turn this Sketch frame into a spec", "generate issues from this design", "document this design in Mintlify", "spec out this Sketch page", or "create a Spec Kit from Figma/Sketch". Also trigger if the user references a Sketch link/frame ID alongside words like "spec", "issues", "docs", "MDX", or "Mintlify", even without naming this skill directly. Do NOT use for pure Sketch editing/inspection (no docs/spec output involved) or for pure docs editing with no Sketch source — those are plain Sketch tool use or the docx/pptx skills.
---

# Sketch → Spec Kit → Mintlify Docs

Converts a Sketch design into two durable artifacts that live in the target repo: a **GitHub Spec Kit**
(spec/plan/tasks + issues + branches) and **Mintlify MDX documentation** with the design frame embedded. The
point is to make the design the single source of truth that both engineering (issues, branches) and docs
(MDX) trace back to — so a reviewer can always ask "where did this requirement come from?" and get a frame ID.

## Before you start: two things must both be true

1. **Sketch MCP is reachable.** Call `Sketch:get_document_info` first. If it errors or times out, don't
   guess — tell the user the Sketch MCP server isn't running and ask them to start it (Sketch app must be
   open with the target document loaded). Don't proceed to design analysis on a stale/wrong document.
2. **The target repo's Mintlify connection is actually live — verify this, don't assume it.** A `docs.json`
   file existing does NOT mean the Mintlify GitHub App is connected and publishing (see
   `references/mintlify-caveats.md`). Check programmatically: call `Mintlify:list_deployments` and confirm
   the target repo's subdomain appears in the result. If it does, the App is connected — proceed normally.
   If it doesn't (or the tool isn't available at all), generate the MDX anyway but flag clearly in your
   summary that publishing is not confirmed — don't imply it's live. If the repo has no docs setup at all,
   point the user at the `mintlify-section-request` skill instead of half-building one here.
3. **A GitHub MCP connector is available and preferred over `gh` CLI.** Verify presence each session with
   `tool_search` rather than assuming — connector availability can change between conversations.

## Workflow

### Step 1 — Get the design reference

Ask the user for the Sketch page/frame ID or a shareable link if not already given. Don't ask for anything
else yet (repo, labels, etc.) — gather those only where you actually need them, in later steps, so the user
isn't front-loaded with a long interview.

### Step 2 — Confirm Sketch MCP + resolve the target

- `Sketch:get_document_info` → confirms connection and gives you page names to match the user's reference against.
- If the user gave a link, extract the page/artboard identifiers from it; if they gave a name, resolve it
  against `get_document_info`'s page list — don't assume a fuzzy match is correct, confirm with the user if
  more than one candidate matches.

### Step 3 — Analyze the design

Pull structure, not pixels — you're extracting _requirements_, not redrawing the UI:

- `Sketch:get_layer_tree_summary` on the target frame(s) → component hierarchy (what's a button, a form, a
  list, a modal, a nav element).
- `Sketch:get_design_assets` → reusable components/symbols already in the library, so you can tell "new
  component" apart from "existing component, new usage."
- `Sketch:get_symbol_overrides` on any symbol instances → what varies per-instance (copy, state, icon) vs.
  what's fixed — this is often the difference between one user story and three.
- From the layer names, groupings, and any embedded copy, infer: distinct **user flows** (sequences of
  screens/states), **features** (independently shippable chunks), and **components** (reusable UI needing
  their own acceptance criteria, e.g. a date picker used in three flows).

Synthesize this into a short internal outline — features, each with its flows and components — before
writing anything to disk. Show this outline to the user before generating the Spec Kit; design→requirements
is the lossiest step in this whole pipeline and is worth a sanity check before you commit it to issues and
branches.

### Step 4 — Generate the GitHub Spec Kit

This repo's convention (see `references/spec-kit-conventions.md`) is the `github/spec-kit` triple — one
folder per spec, not a single flat spec file. Match it rather than inventing a new shape:

```
specs/<NNN-short-name>/
├── spec.md      # goals, non-goals, design, user stories, acceptance criteria — from references/spec-template.md
├── plan.md      # approach, phases, risks, dependencies
└── tasks.md     # checklist, "done when", out of scope
```

- Number `<NNN>` by continuing the existing sequence in `specs/` (check what's already there — don't
  restart at 001 in a repo that already has 003).
- One spec folder per **feature** identified in Step 3, not per screen — a login flow with 4 screens is one
  spec, not four.
- Write user stories and acceptance criteria directly from what the design shows (states, empty states,
  error states visible in the frame tree count as acceptance criteria).

**GitHub issues and branches are side-effectful — always confirm with the user before creating them,
regardless of which path below is used.** Show the planned issue titles/labels and branch names first; wait
for a clear go-ahead.

**Preferred: GitHub MCP connector.** This org has one connected with `github:issue_write`,
`github:create_branch`, `github:sub_issue_write`, and `github:create_pull_request` — use these directly
rather than shelling out:

- `github:issue_write` with `method: "create"` — one call per issue. Pass `title`, `body`, `labels`; capture
  the returned issue number for cross-linking in Step 6.
- For dependencies between issues, use `github:sub_issue_write` (`method: "add"`) to model a genuine
  parent/sub-issue relationship where the design implies one (e.g. a feature issue with per-screen
  sub-issues), in addition to writing `Depends on #N` in the body for anything that's an ordering dependency
  rather than a hierarchy. The two aren't interchangeable — sub-issues are for part-of relationships,
  `Depends on` is for must-happen-before.
- `github:create_branch` — one call per spec folder, `branch` matching the `<NNN-short-name>` convention,
  `from_branch` set to the repo's default unless the user specifies otherwise.
- If the user wants a PR scaffolded immediately (rather than just the branch), `github:create_pull_request`
  is available too — but only do this if asked; don't open PRs speculatively before there's any content on
  the branch.

Before any of the above, run `tool_search` for GitHub tools to confirm the connector is still present this
session (connector availability isn't guaranteed to persist across conversations) — if it's gone, fall back
to `gh` CLI below rather than failing silently.

**Fallback: `gh` CLI via bash**, only if no GitHub MCP connector is found:

```bash
gh auth status   # verify before doing anything else; if not authenticated, stop and tell the user
gh issue create --title "..." --body-file <path> --label "..." \
  --repo <owner/repo>
gh issue create ... # repeat per issue; capture returned issue numbers for cross-linking
git checkout -b <NNN-short-name>   # one branch per spec folder, matching the numbered convention
```

- Encode **dependencies** between issues as GitHub issue references (`Depends on #12`) in the issue body,
  not just prose — the built-in Spec Kit tooling and Mintlify skill in this org both rely on that being
  machine-findable.
- Priority and labels: ask the user for their label taxonomy once per session rather than inventing one
  (`priority:high`, `p1`, `P0` all mean different things in different orgs — don't guess).

### Step 5 — Export design visuals

- `Sketch:get_screenshot` on each frame that needs to appear in docs. Save to the repo's docs asset path
  (commonly `docs/images/` — confirm the convention if unsure).
- One export per distinct screen/state you're documenting, not one export per component — keep the MDX
  scannable.

### Step 6 — Generate Mintlify MDX

Use `references/mdx-template.md` as the shape. One MDX page per **feature** (matching the spec folders from
Step 4), containing:

- Overview (1–2 sentences, plain language)
- User problem (from the spec's Goals section)
- Solution (from the spec's Design section)
- UI reference — the exported frame image(s) from Step 5, embedded with real relative paths, not placeholders
- Acceptance criteria (mirrored from spec.md, not retyped from scratch — copy it so the two never drift)
- Related issues — linked by number/URL to the issues created in Step 4

Add each new page to the repo's `docs.json` navigation. If you can't determine where it belongs in the
existing nav structure, ask rather than guessing a nav position — a wrong nav placement is a worse failure
mode than a pending question.

## Output summary

At the end, report back clearly:

- Spec Kit folders created (paths)
- Issues created (numbers + links) and branches created (names) — or, if the user didn't confirm, what
  _would_ be created, unmodified
- MDX pages written (paths) and whether `docs.json` nav was updated
- Explicit publish status, based on the `Mintlify:list_deployments` check from the prerequisites: state
  plainly whether this repo's subdomain was found connected, or wasn't — never say "published" or "live"
  based on `docs.json` existing alone.
- Which path was used for issues/branches (GitHub MCP connector or `gh` CLI fallback) — useful context if
  the user is troubleshooting connector availability across sessions.

## Reference files

- `references/spec-kit-conventions.md` — the numbered-folder triple convention and templates, pulled from
  this org's existing usage
- `references/mintlify-caveats.md` — known gaps between "has docs.json" and "is actually publishing," so you
  don't overclaim
- `references/mdx-template.md` — the MDX page shape for Step 6
