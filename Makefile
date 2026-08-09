# corpora-docs — repository task runner.
#
# Every step in .github/workflows/*.yml is one target here, so anything CI does
# can be reproduced locally with the same command. The branch model these
# implement is <type>/<slug> -> release/vX.Y.Z -> main; see
# contributing/multi-repo-docs.mdx and .github/rulesets/.
#
#   make            # list targets
#   make ci         # everything the `check` job runs on a pull request
#   make pr-guard   # the `guard` job (env: BASE, HEAD, TITLE)

SHELL := /bin/bash

# The long-lived branch. Production; protected; PRs only, from release/vX.Y.Z.
TRUNK    ?= main

# Bump used when opening the next release branch.
BUMP     ?= minor

# Commit range for `release-notes`.
RANGE    ?= origin/$(TRUNK)..HEAD

# owner/name. The workflows set this from ${{ github.repository }}; otherwise
# it is derived from the origin remote. `gh` reads this variable natively too.
# (sed uses `,` as its delimiter: a `#` would open a comment, even in $(shell).)
GH_REPO  ?= $(shell git config --get remote.origin.url 2>/dev/null | sed -E 's,.*github\.com[:/],,; s,\.git$$,,')

# Branch and PR-title types accepted by `pr-guard`.
TYPES    := feat|fix|chore|docs|ci|refactor|test|perf|build|style|revert

# This repo publishes a documentation site, not a package, so there is no
# manifest to carry the version — VERSION is that manifest. It is what
# `release-branch` writes, what `pr-guard` cross-checks a release branch
# against, and what `tag-release` turns into the tag.
VERSION_FILE := VERSION
pkg_version   = cat $(VERSION_FILE)

SCRIPTS  := .github/scripts

.DEFAULT_GOAL := help

.PHONY: help ci validate-docs validate-sections pr-guard \
        pkg-version next-version version-set release-notes \
        release-pr release-branch delete-branch tag-release \
        rulesets-diff rulesets-apply

help: ## Show this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── checks ────────────────────────────────────────────────────────────────────
# Deliberately offline. A `mint broken-links` or any npx-shaped check would make
# the required status on every PR depend on a registry and a remote build; the
# same navigation errors are detectable from the tree alone.

ci: validate-docs validate-sections ## Everything CI runs on a pull request.

validate-docs: ## Check docs.json parses and every page it lists exists.
	@python3 $(SCRIPTS)/validate_docs.py

# Needs pyyaml, which the workflows pip-install; the section workflows run this
# same script the same way.
validate-sections: ## Validate the sections/ registry (schema + uniqueness).
	@python3 $(SCRIPTS)/validate_sections.py

# ── pull requests ─────────────────────────────────────────────────────────────

# Dependabot opens `dependabot/<ecosystem>/<dep>-<version>` with a "Bump X from
# A to B" title — neither is expressible in the convention, and neither is
# something we can rename. It also targets the default branch, so the bypass
# has to sit above the base switch rather than inside the release/v* case: a
# bot PR lands on the trunk directly and the next release branch, cut from the
# trunk, picks it up. Waving it through beats a permanently-red bot PR.
pr-guard: ## Validate a PR's base, branch name and title (env: BASE, HEAD, TITLE).
	@set -eu; \
	: "$${BASE:?BASE is required}" "$${HEAD:?HEAD is required}"; \
	case "$$HEAD" in \
	dependabot/*) \
	  echo "guard skipped for dependabot: $$HEAD -> $$BASE"; exit 0;; \
	esac; \
	case "$$BASE" in \
	$(TRUNK)) \
	  echo "$$HEAD" | grep -Eq '^release/v[0-9]+\.[0-9]+\.[0-9]+$$' \
	    || { echo "::error::$(TRUNK) only accepts PRs from release/vX.Y.Z (got '$$HEAD')"; exit 1; }; \
	  want="release/v$$($(pkg_version))"; \
	  [ "$$want" = "$$HEAD" ] \
	    || { echo "::error::$(VERSION_FILE) declares $$want but the branch is $$HEAD"; exit 1; }; \
	  ;; \
	release/v*) \
	  echo "$$HEAD" | grep -Eq '^($(TYPES))/[a-z0-9][a-z0-9._-]*$$' \
	    || { echo "::error::branch must be <type>/<slug> — one of $(TYPES) (got '$$HEAD')"; exit 1; }; \
	  printf '%s' "$${TITLE-}" | grep -Eq '^($(TYPES))(\([a-z0-9._/-]+\))?!?: .+' \
	    || { echo "::error::PR title must read '<type>: summary' (got '$${TITLE-}')"; exit 1; }; \
	  ;; \
	*) \
	  echo "::error::$$BASE is not a valid base — target $(TRUNK) or release/vX.Y.Z"; exit 1;; \
	esac; \
	echo "guard passed: $$HEAD -> $$BASE"

# ── versions ──────────────────────────────────────────────────────────────────

pkg-version: ## Print the version in VERSION.
	@$(pkg_version)

next-version: ## Print the version after the newest vX.Y.Z tag (BUMP=major|minor|patch).
	@git tag -l 'v[0-9]*' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$$' | sed 's/^v//' \
	  | sort -t. -k1,1n -k2,2n -k3,3n | tail -1 \
	  | awk -F. -v b='$(BUMP)' \
	      'BEGIN { maj = 0; min = 0; pat = 0 } { maj = $$1; min = $$2; pat = $$3 } \
	       END { if (b == "major") printf "%d.0.0\n", maj + 1; \
	             else if (b == "patch") printf "%d.%d.%d\n", maj, min, pat + 1; \
	             else printf "%d.%d.0\n", maj, min + 1 }'

version-set: ## Write VERSION into $(VERSION_FILE) (env: VERSION).
	@set -eu; : "$${VERSION:?VERSION is required}"; \
	printf '%s\n' "$$VERSION" > $(VERSION_FILE); \
	echo "  $(VERSION_FILE) is now $$VERSION"

release-notes: ## Print a markdown changelog for RANGE (default origin/$(TRUNK)..HEAD).
	@git log --no-merges --reverse --pretty='- %s' $(RANGE) | grep . \
	  || echo '- _Nothing merged yet._'

# ── release pipeline ──────────────────────────────────────────────────────────

release-pr: ## Open or refresh the draft release PR into $(TRUNK) (env: BRANCH).
	@set -eu; \
	branch="$${BRANCH:-$$(git rev-parse --abbrev-ref HEAD)}"; \
	version="$${branch#release/v}"; \
	git fetch --quiet origin \
	  "$(TRUNK):refs/remotes/origin/$(TRUNK)" "$$branch:refs/remotes/origin/$$branch"; \
	body="$$(mktemp)"; \
	{ printf 'Release **v%s**.\n\n## Changes\n\n' "$$version"; \
	  $(MAKE) -s --no-print-directory release-notes RANGE="origin/$(TRUNK)..origin/$$branch"; \
	  printf '\n---\nRefreshed automatically whenever a PR lands on `%s`.\n' "$$branch"; \
	} > "$$body"; \
	num="$$(gh pr list --base $(TRUNK) --head "$$branch" --state open --json number --jq '.[0].number // empty')"; \
	if [ -n "$$num" ]; then \
	  gh pr edit "$$num" --body-file "$$body"; \
	  echo "refreshed release PR #$$num"; \
	else \
	  gh pr create --draft --base $(TRUNK) --head "$$branch" \
	    --title "release: v$$version" --body-file "$$body"; \
	fi; \
	rm -f "$$body"

release-branch: ## Cut release/v<next> from $(TRUNK) with VERSION bumped (env: VERSION, BUMP).
	@set -eu; \
	git fetch --quiet --force --tags origin "$(TRUNK):refs/remotes/origin/$(TRUNK)"; \
	version="$${VERSION:-$$($(MAKE) -s --no-print-directory next-version)}"; \
	branch="release/v$$version"; \
	if git ls-remote --exit-code --heads origin "$$branch" >/dev/null 2>&1; then \
	  echo "$$branch already exists — nothing to do"; exit 0; \
	fi; \
	git checkout --quiet -B "$$branch" origin/$(TRUNK); \
	$(MAKE) -s --no-print-directory version-set VERSION="$$version"; \
	git add $(VERSION_FILE); \
	git commit --quiet -m "chore(release): open v$$version"; \
	git push --quiet -u origin "$$branch"; \
	echo "opened $$branch"

delete-branch: ## Delete a remote branch, tolerating one already gone (env: BRANCH).
	@set -eu; : "$${BRANCH:?BRANCH is required}"; \
	if gh api -X DELETE "repos/$(GH_REPO)/git/refs/heads/$$BRANCH" >/dev/null 2>&1; then \
	  echo "deleted $$BRANCH"; \
	else \
	  echo "$$BRANCH was already gone"; \
	fi

# Idempotent: a tag already released is skipped, not an error.
#
# Must run with the automation App's token, never GITHUB_TOKEN — events raised
# by GITHUB_TOKEN do not start workflow runs, so anything hanging off this tag
# would go silently dead.
tag-release: ## Tag HEAD as v<VERSION> and publish the GitHub Release.
	@set -eu; \
	tag="v$$($(pkg_version))"; \
	if gh api "repos/$(GH_REPO)/git/ref/tags/$$tag" >/dev/null 2>&1; then \
	  echo "$$tag already exists — skipping"; exit 0; \
	fi; \
	gh release create "$$tag" --target "$$(git rev-parse HEAD)" \
	  --title "$$tag" --generate-notes; \
	echo "released $$tag"

# ── repository settings ───────────────────────────────────────────────────────

rulesets-diff: ## List the rulesets GitHub currently has, by id and name.
	@gh api "repos/$(GH_REPO)/rulesets" --jq '.[] | "\(.id)\t\(.name)"'

# Matched by `.name`, so a file must keep the name of the ruleset already on
# GitHub or a second one is created alongside it.
rulesets-apply: ## Push .github/rulesets/*.json to GitHub (matched by name).
	@set -eu; \
	for f in .github/rulesets/*.json; do \
	  name="$$(jq -r .name "$$f")"; \
	  id="$$(gh api "repos/$(GH_REPO)/rulesets" --jq ".[] | select(.name==\"$$name\") | .id")"; \
	  if [ -n "$$id" ]; then \
	    gh api -X PUT "repos/$(GH_REPO)/rulesets/$$id" --input "$$f" >/dev/null; \
	    echo "updated $$name"; \
	  else \
	    gh api -X POST "repos/$(GH_REPO)/rulesets" --input "$$f" >/dev/null; \
	    echo "created $$name"; \
	  fi; \
	done
