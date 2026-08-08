# Corpora — Codebase Guide

## Purpose

This repo contains two products:

1. **Supabase local development** — edge functions, database migrations, seeds, and config for the Supabase backend. Connects to the remote production project for deploys.
2. **macOS app (`macOS/`)** — *Corpora*, a native macOS app for managing and uploading corpus datasets to the database.

---

## Repository Structure

```text
exegia-backend/
├── macOS/                        # Swift macOS app (XcodeGen-managed)
│   ├── Sources/Corpora/          # All app source code
│   │   ├── Features/             # Feature modules (one folder per feature)
│   │   │   └── Project/
│   │   │       ├── Create/       # Create project feature
│   │   │       └── Upload/       # Upload corpus feature
│   │   ├── Models/               # Shared data models (FabricDataset, etc.)
│   │   ├── Services/             # Supabase service layer
│   │   ├── ViewModels/           # Shared view models
│   │   ├── Views/                # Shared views and reusable components
│   │   │   └── Components/       # Reusable UI components
│   │   ├── Config/               # App config and secrets
│   │   └── Python/               # Embedded Python bridge
│   ├── Tests/Corpora/            # Unit tests (mirrors Features/ structure)
│   ├── project.yml               # XcodeGen spec — source of truth for .xcodeproj
│   ├── Makefile                  # Build automation
│   └── Scripts/                  # Pre/post generation scripts
├── supabase/
│   ├── functions/                # Deno edge functions (one folder per function)
│   │   ├── convert-corpus/       # ZIP → .exg conversion
│   │   ├── enrich-metadata/      # AI metadata enrichment
│   │   ├── generate-cover/       # AI cover image generation
│   │   └── generate-description/ # AI description generation
│   ├── migrations/               # Ordered SQL migrations
│   ├── seeds/                    # Seed data
│   └── config.toml               # Supabase local config (project: ivaecofevxactmmupvyp)
├── deno.json                     # Task runner for all dev workflows
├── .env                          # Dev secrets (encrypted via dotenvx)
└── .env.production               # Production secrets (encrypted via dotenvx)
```

---

## macOS App

### Tech Stack

| Concern | Library |
| --- | --- |
| UI | SwiftUI (macOS 15+) |
| State | `@Observable` / `@Bindable` (Swift 5.9 Observation) |
| Backend | [supabase-swift](https://github.com/supabase/supabase-swift) v2.5+ |
| ZIP I/O | [ZIPFoundation](https://github.com/weichsel/ZipFoundation) |
| MIME detection | [MimeTypeEnum](https://github.com/emotiveapps/MimeTypeEnum) |
| EPUB parsing | [EPUBKit](https://github.com/witekbobrowski/EPUBKit) |
| Python embed | [PythonKit](https://github.com/pvieito/PythonKit) + Python.xcframework |
| Code generation | [XCResource](https://github.com/nearfri/XCResource) |

Deployment target: **macOS 15.0**. Bundle ID: `com.exegia.Corpora`.

### Project Generation

The `.xcodeproj` is **generated** from `project.yml` via XcodeGen — never hand-edit it.

```bash
make generate     # regenerate .xcodeproj (run after editing project.yml)
make open         # generate + open in Xcode
make bootstrap    # download Python.xcframework (first-time setup)
make build        # xcodebuild Debug
make run          # build + launch Corpora.app
make clean        # remove build artifacts
make clear-cache  # remove DerivedData + caches
```

Equivalent Deno tasks (from repo root):

```bash
deno task xcode:dev       # bootstrap + generate + open Xcode
deno task xcode:generate  # regenerate only
deno task xcode:build     # build
deno task xcode:run       # build + run
```

When you add a new Swift file anywhere under `Sources/Corpora/`, XcodeGen picks it up automatically on the next `make generate` — no need to touch `project.yml` unless you're adding a package, target, scheme, or build setting.

### Xcode Project: Folders, not Groups

XcodeGen reflects the filesystem directory structure as Xcode groups. **All organisation happens on disk**, not inside Xcode:

- Create directories in the filesystem first, then add `.swift` files inside them.
- Run `make generate` — the new folder/files appear as a group in Xcode automatically.
- Never drag-and-drop to reorganize inside Xcode; do it on disk and regenerate.
- The `.xcodeproj` is in `.gitignore`-friendly territory: diffs are minimal because the project is rebuilt from `project.yml`.

### Architecture

```text
ContentView (NavigationSplitView)
├── Sidebar: NavigationItem list
└── Detail: view-per-NavigationItem
    ├── DashboardView         → EmptyCorpusView | corpus overview
    ├── MarketplaceView
    ├── MetadataEditorView
    ├── DigitizationLabView
    └── ArchivalLedgerView
```

#### State flow

- `DatasetListViewModel` — owned by `ContentView`, passed down where needed.
- Feature ViewModels are `@Observable` classes, owned by the view that needs them via `@State`.
- Service calls go through `DatasetService.shared` (singleton wrapping `SupabaseService.shared.client`).

---

## Supabase Backend

### Backend Tech Stack

| Concern | Detail |
| --- | --- |
| Runtime | Deno (edge functions) |
| Database | PostgreSQL 17 (local port 54322, API port 54321) |
| Auth | Supabase Auth |
| Storage | `to-be-converted` bucket (raw uploads), `corpus` bucket (converted .exg), `dataset-covers` bucket |
| Realtime | Postgres changes on `fabric_dataset` |

### Edge Functions

| Function | Trigger | Purpose |
| --- | --- | --- |
| `convert-corpus` | POST `{ dataset_id }` | Converts uploaded ZIP → `.exg` archive in `corpus` bucket |
| `enrich-metadata` | POST `{ dataset_id }` | AI enrichment of dataset metadata |
| `generate-description` | POST `{ dataset_id }` | Generates description via AI |
| `generate-cover` | POST `{ dataset_id }` | Generates cover image via AI |

### Database Migrations

Migrations live in `supabase/migrations/`, named `YYYYMMDDHHMMSS_description.sql`.

### Local Development Commands

```bash
deno task supabase:start    # start local Supabase stack (uses dotenvx for secrets)
deno task status            # show local service URLs and keys
deno task db:reset          # reset DB and re-run all migrations + seeds
deno task db:migrate        # create a new migration file
deno task db:push           # push migrations to production
deno task functions:serve   # serve all functions locally
deno task functions:deploy  # deploy functions to production
deno task functions:check   # type-check all function index.ts files
deno task start             # start Supabase + open Xcode (full dev environment)
```

Secrets are managed with **dotenvx** — all values in `.env` and `.env.production` are encrypted at rest and safe to commit. The decryption keys live in `.env.keys`, which must **never** be committed. Add `.env.keys` to `.gitignore` and keep it out of version control.

---

## Code Practices

### Feature-Based Structure

Every new feature lives in its own folder under `Features/`:

```text
Features/
└── <Domain>/
    └── <FeatureName>/
        ├── <FeatureName>View.swift
        ├── <FeatureName>ViewModel.swift
        └── CLAUDE.md                  ← required (see below)
```

Example: `Features/Project/Create/`, `Features/Project/Upload/`.

Keep the View, ViewModel, and any feature-private types in the same folder. Do not scatter them across `Views/` or `ViewModels/`.

### Shared Folder

Any type used across **two or more features** — views, components, models, enums, utilities — belongs in the appropriate shared directory, not inside a feature folder:

| Type | Location |
| --- | --- |
| Data models | `Models/` |
| Service layer | `Services/` |
| Reusable views / components | `Views/Components/` |
| Shared view models | `ViewModels/` |

### Adding a New Package (SPM)

1. Add the package entry to `project.yml` under `packages:`.
2. Add the product to the `Corpora` target's `dependencies:` list.
3. Add a matching `.package(url:from:)` + `.product(name:package:)` entry in `Package.swift` (kept in sync for IDE resolution).
4. Run `make generate` to regenerate the `.xcodeproj`.
5. Run `xcodebuild -resolvePackageDependencies` if the build fails with a missing product.

### Unit Tests

- Tests mirror the `Features/` folder structure under `Tests/Corpora/Features/`.
- Each feature must have at least one test file: `Tests/Corpora/Features/<Domain>/<Feature>/<FeatureName>Tests.swift`.
- Test targets use **Swift Testing** (`import Testing`, `@Suite`, `@Test`, `#expect`).
- The `CorporaTests` target is configured in `project.yml` — it compiles ViewModel source files directly (no `@testable import`) to avoid sandbox injection issues.
- Run tests: **Xcode → Product → Test** or `xcodebuild test -scheme "Corpora (Dev)"`.
- Every feature PR must pass all tests before merge.

### Feature CLAUDE.md

Every feature folder must contain a `CLAUDE.md` file with:

```markdown
# <FeatureName>

## Purpose
One paragraph describing what this feature does and why it exists.

## Architecture
Key types (View, ViewModel, helpers) and how they interact.

## Iterations
Chronological log of significant changes, each with a date and summary.

## Lessons Learned
Non-obvious constraints, API quirks, or decisions worth remembering.
```

This file is the living documentation for the feature. Update it whenever the feature changes significantly.

---

## Environment Variables

### dotenvx encryption

This project uses [dotenvx](https://dotenvx.com) to encrypt secrets at rest.

| File | Committed? | Purpose |
| --- | --- | --- |
| `.env` | ✅ yes — encrypted | Dev secrets (local Supabase, Apple team ID, OpenAI) |
| `.env.production` | ✅ yes — encrypted | Production secrets |
| `.env.keys` | ❌ **never** — plaintext keys | Private decryption keys for both files |

**Workflow:**

1. Edit a value in `.env` or `.env.production` in plaintext.
2. Run `dotenvx encrypt` to re-encrypt the file before committing.
3. The decryption key stays in `.env.keys` locally — never push it.

All `deno task` commands run through `dotenvx run --` which decrypts values at process start using the key in `.env.keys`.

### macOS app

`Scripts/pre-gen.sh` runs before XcodeGen and writes `Configs/Debug.xcconfig` (from `.env`) and `Configs/Release.xcconfig` (from `.env.production`). Xcode build settings and scheme environment variables reference these xcconfig files via `$(VAR_NAME)` — secrets are never hardcoded.

Key variables:

| Variable | Purpose |
| --- | --- |
| `DEVELOPMENT_TEAM` | Apple Developer team ID for code signing |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_PUBLISHABLE_KEY` | Anon/publishable key for client-side auth |
| `SUPABASE_SECRET_KEY` | Service role key (server/functions only) |
| `SUPABASE_STORAGE_BUCKET` | Primary corpus storage bucket name |
| `SUPABASE_DB_URL` | Direct database connection URL |
| `OPENAI_AI_KEY` | OpenAI API key (for AI features) |

Never hardcode secrets in source files. Never commit `.env.keys`.
