# Current state of the org's Mintlify setup (as of this skill's creation)

This is context, not gospel — re-check if it's been a while, things may have moved.

## What's confirmed (from `corpora-auth`'s `CLAUDE.md`)

- The docs site framework is **Mintlify**, docs source lives in a repo's `docs/` folder, previewed with `mint dev`.
- **Publishing is via the Mintlify GitHub App**, which watches a deploy branch (`main`) and redeploys on merge.
  There is no CI workflow that publishes — `.github/workflows/docs.yml` only checks for broken links.
- `mint export` (a static build) is **Enterprise-gated** and not usable on the current plan; GitHub Pages is a
  dead end for the same reason (relative asset paths break under a subpath).
- The org has **one existing Mintlify deployment**, named `exegia`, currently pointed at the Corpora platform
  docs. Repointing it would replace those docs rather than add a section.
- As of the last check, **the Mintlify GitHub App was not connected for `exegia/corpora-auth`** — nothing
  publishes from that repo until a Mintlify project is created for it (monorepo mode, path `/docs`).

## What's NOT confirmed / not yet designed

- There is **no single named "central docs registry repo"** visible in project knowledge. `exegia/docs` is a
  guess based on naming convention, not a verified repo.
- There is **no existing mechanism** in this org for one Mintlify site to aggregate `docs/` content pulled in
  from multiple separate repos as distinct "sections" — Mintlify's own multi-repo support (if used) would need
  to be configured by whoever owns the `exegia` deployment.
- It is not decided whether "sections" map to: (a) separate Mintlify *projects* stitched together, (b) one
  project with `docs.json` `navigation` entries pointing at synced/mirrored content, or (c) git submodules pulled
  into one docs repo at build time.

## Why the skill is designed the way it is

Given the above is unresolved, `mintlify-section-request` deliberately stops at **filing a structured request**
(local manifest + a PR adding one file to a registry repo) rather than attempting to directly rewrite a live
`docs.json` it doesn't have visibility into. This keeps the skill useful today and forward-compatible with
whichever aggregation approach the org eventually picks — the `sections/*.yml` files are a clean input to any of
options (a)/(b)/(c) above.

## Suggested follow-up (separate from this skill, worth its own GitHub issue)

**Title:** Define multi-repo Mintlify section aggregation strategy + connect the GitHub App for repos beyond
the platform docs

**Body outline:**
- Decide the aggregation mechanism (submodule sync vs. multi-project stitch vs. `docs.json` includes)
- Name and create the central registry repo (or confirm `exegia/docs` if that's the intent)
- Connect/verify the Mintlify GitHub App for each repo that files a section request
- Build (or manually run, initially) the reconciliation step that turns `sections/*.yml` → live `docs.json`
  navigation entries
- Confirm whether `mint export`/Enterprise plan is needed for the chosen approach

This is infrastructure/process work, independent of the skill itself — the skill can ship and start collecting
requests before this is resolved; requests just sit as `status: pending` PRs until someone builds the reconciler.
