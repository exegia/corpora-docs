# `.mintlify/section-request.yml` schema

Written into the *requesting* repo (the one that wants to become a docs section). This file is the durable,
human-readable record — commit it, don't gitignore it.

```yaml
apiVersion: v1
kind: MintlifySectionRequest

metadata:
  repo: exegia/corpora-auth       # owner/name, auto-detected from `git remote get-url origin`
  requestedAt: 2026-08-08T18:40:00Z
  requestedBy: jane@exegia.dev    # from `git config user.email`, or CI actor
  status: pending                  # pending | approved | rejected | live — set by the registry side, not locally

section:
  title: Corpora Auth
  slug: corpora-auth               # kebab-case; becomes the nav path segment and the registry filename
  description: Auth plugin + hooks for Supabase, Tauri-first.
  icon: lock                       # optional, any Mintlify icon name
  docsPath: docs                   # path within THIS repo containing the Mintlify-compatible docs source
  navigation:                      # optional — omit to let the registry maintainer derive it from docs/docs.json
    - group: Guides
      pages:
        - docs/quickstart
        - docs/configuration

owner: "@exegia/platform-team"     # required — who to ping if something breaks
tags: [auth, plugin, tauri]
```

## Field notes

- **`section.slug`** must be unique across the whole org's docs site. The submit script checks for a collision
  against existing `sections/*.yml` filenames in the central registry repo before opening a PR, and stops if one
  exists (does not silently overwrite).
- **`section.docsPath`** doesn't need to exist yet at request time (see SKILL.md prerequisites) — but the PR
  description must say so plainly if it doesn't, so reviewers aren't surprised.
- **`metadata.status`** is set to `pending` by the requesting repo and only ever changed by the registry
  side (a maintainer merging the PR, or later automation) — this skill never writes anything other than `pending`
  locally.
- This schema deliberately mirrors the `title` / `description` / `tags` shape already used by this org's
  `.ok/frontmatter.yml` folder-metadata convention, so it should feel familiar rather than inventing new
  vocabulary.

## Central registry repo layout (proposed)

```
<central-docs-repo>/
├── docs.json                # the live Mintlify nav — hand-reconciled or automated from sections/
└── sections/
    ├── corpora-auth.yml     # == a copy of the requesting repo's section-request.yml, plus status
    ├── corpora-ui.yml
    └── ...
```

One file per repo avoids merge conflicts when multiple repos file requests around the same time — the alternative
(every repo PRing directly into a shared `docs.json`) is exactly the failure mode this design avoids.
