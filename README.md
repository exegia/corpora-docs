# Exegia Backend

<div align="center">

> 🔷 **Supabase-powered backend for academic corpus management**

Convert, store, and serve 30+ pre-loaded text corpora with a REST API

![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Deno](https://img.shields.io/badge/Deno-000000?style=for-the-badge&logo=deno&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)

</div>

---

## ✨ Features

| 🚀 Edge Functions       | 🗄️ PostgreSQL Database | 📦 Storage            | 🔒 Security           |
| ----------------------- | ---------------------- | --------------------- | --------------------- |
| Async corpus conversion | 30+ pre-loaded corpora | S3-compatible storage | Row-level security    |
| Background processing   | Full-text search       | .exg format support   | Public read access    |
| REST API endpoints      | Type-safe schema       | Automatic backups     | Auth-protected writes |

**Supported Languages:** Hebrew • Greek • Syriac • Arabic • Aramaic • Latin • English + more

**Corpus Types:** Biblical texts • Commentaries • Lexicons • Historical manuscripts

---

> **Note:** This project uses **Deno exclusively** for all TypeScript code and Edge Functions. No Node.js or Bun required.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend  │────────▶│   Supabase   │────────▶│  PostgreSQL  │
│  (React)    │  REST   │ Edge Function│   SQL   │   Database   │
└─────────────┘         └──────────────┘         └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   Storage    │
                        │  (.exg files)│
                        └──────────────┘
```

### 📤 Corpus Conversion Flow

```
1. Upload
   │
   ├─▶ POST /functions/v1/convert-corpus
   │   └─ multipart/form-data (corpus.zip + metadata)
   │
   ▼
2. Edge Function Receives Request
   │
   ├─▶ Validate: file type, metadata, size
   ├─▶ Generate job_id (UUID)
   ├─▶ Write to /tmp/job_id.zip (ephemeral)
   ├─▶ Upload to Storage: uploads/job_id.zip
   │
   ├─▶ Return 202 Accepted + job_id ✅
   │
   ▼
3. Background Processing (EdgeRuntime.waitUntil)
   │
   ├─▶ Read zip from /tmp
   ├─▶ Detect format (epub, pdf, tei, xml, text)
   │
   ├─▶ Build .exg envelope:
   │   ├─ manifest.json (metadata, node types)
   │   ├─ index.json (file listing)
   │   └─ corpus.exgc (compressed source)
   │
   ├─▶ Upload to Storage: datasets/{name}.exg
   ├─▶ Delete uploads/job_id.zip
   ├─▶ Insert row into corpora table
   │
   ▼
4. Complete ✨
   │
   └─▶ Corpus available via:
       ├─ REST API: /rest/v1/corpora
       └─ Storage: /storage/v1/object/public/corpora/datasets/{name}.exg
```

## Quick Start

### Prerequisites

```bash
# Install Supabase CLI
brew install supabase/tap/supabase

# Install Deno (only runtime needed)
brew install deno

# Docker Desktop (required for Supabase local dev)
# Download from https://www.docker.com/products/docker-desktop
```

### Setup

```bash
# Start Supabase
supabase start

# Get your API keys
supabase status
```

### Local Development

```bash
# Serve Edge Functions
supabase functions serve

# Open Studio
open http://localhost:54323

# Run dev server (optional)
deno run --allow-net --allow-env index.ts
```

## Project Structure

```
exegia-backend/
├── supabase/
│   ├── functions/          # Edge Functions (Deno)
│   │   └── convert-corpus/ # Corpus conversion API
│   ├── migrations/         # Database schema
│   └── seeds/              # 30+ pre-loaded corpora
└── index.ts                # Local dev server
```

## Screenshots

### 📊 Supabase Studio

> Open at http://localhost:54323 to manage your database

![Supabase Studio](https://supabase.com/dashboard/img/supabase-studio.png)

### 🗂️ Database Explorer

> View and edit your corpus data

<!-- Add screenshot: ./docs/images/database-view.png -->

### 🚀 Edge Functions

> Monitor function logs and deployments

<!-- Add screenshot: ./docs/images/functions-view.png -->

## API

### Upload & Convert Corpus

```bash
curl -X POST http://localhost:54321/functions/v1/convert-corpus \
  -F "file=@corpus.zip" \
  -F "name=my-corpus" \
  -F "type=bible" \
  -F "language=hebrew" \
  -F "period=Biblical" \
  -F "repository=https://github.com/..." \
  -F "category=biblical"
```

**Response:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

### Query Corpora

```bash
# Get all corpora
curl http://localhost:54321/rest/v1/corpora \
  -H "apikey: YOUR_ANON_KEY"

# Filter by language
curl "http://localhost:54321/rest/v1/corpora?language=eq.hebrew" \
  -H "apikey: YOUR_ANON_KEY"
```

## Database Schema

**`corpora` table:**

| Column       | Type   | Description                |
| ------------ | ------ | -------------------------- |
| id           | uuid   | Primary key                |
| name         | text   | Unique identifier          |
| type         | text   | bible, commentary, lexicon |
| language     | text   | hebrew, greek, arabic, etc |
| period       | text   | Historical period          |
| repository   | text   | Source URL                 |
| category     | text[] | biblical, religious, etc   |
| download_uri | text   | Storage URL                |

## Common Commands

### Using Deno Tasks

```bash
# Quick shortcuts (defined in deno.json)
deno task start             # Start Supabase
deno task stop              # Stop Supabase
deno task restart           # Restart Supabase
deno task status            # Show Supabase status

# Database
deno task db:reset          # Reset database (migrations + seeds)
deno task db:migrate        # Create new migration
deno task db:seed           # Apply seed data
deno task db:push           # Push migrations to remote

# Functions
deno task functions:serve   # Serve all functions
deno task functions:check   # Type check all functions
deno task functions:deploy  # Deploy functions
deno task functions:new     # Create new function

# Development
deno task dev               # Run dev server with --watch
deno task studio            # Open Studio UI
deno task logs              # Watch function logs (debug mode)
deno task test              # Run Deno tests
```

### Direct Supabase CLI

```bash
# Database
supabase db reset           # Reset database (migrations + seeds)
supabase migration new <name>  # Create new migration

# Functions
supabase functions serve    # Serve all functions
deno check supabase/functions/*/index.ts  # Type check
supabase functions deploy <name>  # Deploy specific function

# Utilities
supabase start              # Start Supabase
supabase stop               # Stop Supabase
supabase status             # Show service URLs and keys
```

## Environment Variables

Edge Functions automatically load environment variables from `.env.local`:

```bash
cp .env.example .env.local
```

Get keys from `supabase status`:

```env
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## Local Services

| Service    | URL                          |
| ---------- | ---------------------------- |
| API        | http://localhost:54321       |
| Studio     | http://localhost:54323       |
| Database   | postgresql://localhost:54322 |
| Dev Server | http://localhost:3000        |

## Deployment

```bash
# Link to remote project
supabase link --project-ref <your-ref>

# Push migrations
supabase db push

# Deploy functions
supabase functions deploy convert-corpus
```

## Troubleshooting

**Supabase won't start?**

- Ensure Docker is running
- Check ports: `lsof -i :54321,54322,54323`
- Reset: `supabase stop && supabase start`

**Function errors?**

- Check logs: `supabase functions serve --debug`
- Verify env vars: `cat .env.local`

**Database issues?**

- Reset: `supabase db reset`
- Connect: `psql postgresql://postgres:postgres@localhost:54322/postgres`

## Resources

- [Supabase Docs](https://supabase.com/docs)
- [Deno Manual](https://docs.deno.com)
- [Text-Fabric Docs](https://annotation.github.io/text-fabric/)

## Development Screenshots

### Local Dev Server

Visit `http://localhost:3000` for service overview:

```
🔷 Exegia Backend - Development Server

Server running at:    http://localhost:3000
Supabase API:         http://localhost:54321
Supabase Studio:      http://localhost:54323
```

### Database Structure

```sql
-- Example: Query corpora by language
SELECT name, type, language, period
FROM corpora
WHERE language = 'hebrew'
ORDER BY created_at DESC;
```

---

**Built with [Supabase](https://supabase.com) • [Deno](https://deno.com) • [PostgreSQL](https://www.postgresql.org)**
