# CORPORA – Claude Project Instruction

## PROJECT OVERVIEW

- **Project Name:** Corpora
- **Type:** Full-stack application with dual-stack architecture
- **Status:** MVP (Minimum Viable Product)
- **Primary Goal:** Provide a secure local development environment and admin interface for managing scholarly text corpora (manuscripts, biblical texts, Quranic texts, lexical data, etc.)

---

## PROJECT PURPOSE & VISION

- **Core Mission:** Create an accessible platform for scholars, researchers, and language enthusiasts to work with, analyze, and manage large text corpora in a secure, offline-first sandbox environment
- **Value Proposition:** Combines local-first development infrastructure with a native macOS management interface for seamless corpus curation and research
- **Key Philosophy:** Safe, isolated sandbox for experimenting with text data without affecting production systems

---

## ARCHITECTURE OVERVIEW

### Stack 1: TypeScript/Deno Local Development Sandbox

- **Purpose:** Local, safe development environment mirroring Supabase functionality
- **Technology:**
  - **Language:** TypeScript
  - **Runtime:** Deno JS
  - **Primary Function:** Map remote database storage, authentication, and edge functions locally
- **Responsibilities:**
  - Abstract Supabase interactions
  - Provide local authentication sandbox
  - Enable offline edge function development and testing
  - Serve as development proxy for database operations
- **Scope:** MVP phase focuses on core connectivity and basic CRUD operations

### Stack 2: macOS SwiftUI Admin Application

- **Purpose:** Native admin interface for corpus management and data curation
- **Technology:**
  - **Language:** Swift
  - **Framework:** SwiftUI
  - **Platform:** macOS (native application)
- **Core Features (MVP):**
  - **Upload:** Ingest new datasets, manuscripts, PDFs (Bible, Quran, etc.)
  - **View:** Browse and inspect corpus content with metadata
  - **Edit:** Modify, annotate, or correct text data
  - **Update:** Manage versions and revisions of corpora
  - **Delete:** Remove or archive datasets safely
- **Scope:** Focus on admin operations; not a user-facing research interface (yet)

---

## TARGET USERS & AUDIENCE

### Primary Audience

- Scholars and academic researchers working with manuscripts
- Linguists analyzing lexicons and language data
- Biblical/religious studies researchers (Bible, Quran, etc.)
- Manuscript enthusiasts and paleography students
- Language learners interested in text fabric research

### Secondary Audience

- Researchers preparing publications or thesis work
- Digital humanities projects requiring text corpora
- Theological and historical research initiatives

### Use Cases

- Offline scholarly research on sacred texts
- Corpus preparation for NLP or computational linguistics
- Manuscript digitization and cataloging
- Lexical analysis and linguistic research

---

## KEY FEATURES & DELIVERABLES

### MVP Deliverables

**Supabase Local Sandbox (TypeScript/Deno)**
- Local mirror of Supabase database schema
- Authentication simulation (API key, session management)
- Edge function emulation
- Simple CLI or dev-server interface for local testing

**macOS Admin App (SwiftUI)**
- Clean, native macOS UI for corpus management
- File upload interface (PDF, text, structured data)
- Search/browse functionality for existing corpora
- Edit interface for text annotation and metadata
- Update/version control for datasets
- Basic authentication (local or synced)

---

## PROJECT SCOPE & BOUNDARIES

### In Scope (MVP)

- Local Supabase sandbox environment (TypeScript/Deno)
- macOS SwiftUI admin application
- Core CRUD operations (Create, Read, Update, Delete) for corpora
- Basic authentication and access control
- File upload and ingestion pipeline
- Metadata management (title, source, language, etc.)

### Out of Scope (Future Phases)

- Web-based UI for corpus access
- Multi-platform support (Windows, Linux, iOS)
- Advanced research analytics or visualizations
- Collaborative/multi-user features
- Public sharing or distribution features
- AI-powered analysis tools

---

## TECHNICAL SPECIFICATIONS

### Stack 1: TypeScript/Deno Sandbox

- **File Structure:** TBD (recommend modular function-based organization)
- **Key Modules:**
  - Database connection/schema mapper
  - Authentication service
  - Edge function router
  - File storage abstraction
- **Integration Point:** macOS app communicates via local HTTP API or direct IPC

### Stack 2: macOS SwiftUI App

- **Architecture:** MVVM or MVC (recommend MVVM for SwiftUI)
- **Data Persistence:** Core Data or SQLite (local)
- **Networking:** URLSession connecting to local Deno server
- **UI Components:**
  - Document/corpus browser (list or table view)
  - Upload interface (drag-and-drop, file picker)
  - Text editor/viewer
  - Metadata editor
  - Search/filter controls

---

## SUCCESS CRITERIA (MVP)

- ✅ Local Supabase sandbox runs without errors
- ✅ macOS app successfully connects to local sandbox
- ✅ Users can upload PDF/text files to the sandbox
- ✅ Users can view, edit, and delete corpus entries
- ✅ Metadata (title, language, source) is persisted and retrievable
- ✅ App is performant with 100+ corpus entries
- ✅ All operations work offline (no internet required)

---

## DEPENDENCIES & INTEGRATIONS

- **Supabase (Reference):** The local sandbox mimics Supabase API/schema
- **Deno Runtime:** Required for TypeScript sandbox execution
- **macOS SDK:** SwiftUI (iOS 14+/macOS 11+)
- **File System:** OS-level file handling for PDF/text ingestion
- **No External APIs:** MVP is fully offline and self-contained

---

## TIMELINE & PHASING

### Phase 1 (MVP): Local Deno Sandbox + Basic macOS App

- **Week 1-2:** Deno sandbox scaffolding, database schema
- **Week 2-3:** SwiftUI app UI and basic file upload
- **Week 3-4:** Integration, testing, polish

### Future Phases (Post-MVP)

- **Phase 2:** Advanced editing and annotation tools
- **Phase 3:** Research/analysis dashboard
- **Phase 4:** Web interface or collaborative features

---

## DEVELOPMENT NOTES

- **Language Priorities:** TypeScript (full-stack consistency) + Swift (native performance)
- **Code Quality:** Modular, well-documented, testable architecture
- **Offline-First:** All critical features work without network connectivity
- **Data Safety:** Local encryption option for sensitive manuscripts (future)
- **Extensibility:** Design for future corpus types and metadata schemas

---

## PROJECT CONSTRAINTS & CONSIDERATIONS

- **MVP Focus:** Prioritize functional core over feature completeness
- **macOS-Only (MVP):** No web, Windows, or cross-platform concerns for initial release
- **Local Data Storage:** Avoid cloud sync initially; keep all data on local file system
- **Performance:** Handle corpus files efficiently (PDFs can be large)
- **UX Priority:** Admin app should be intuitive for non-technical scholars

---

## Next Steps

1. **Backend Setup:** Initialize Deno project with TypeScript configuration
2. **Database Schema:** Design corpus metadata schema (mirror Supabase structure)
3. **macOS Project:** Create SwiftUI project with basic MVVM structure
4. **API Definition:** Document local sandbox HTTP API endpoints
5. **Integration Testing:** Establish communication between Deno and macOS app
6. **UI Implementation:** Build macOS interface with upload, view, edit workflows

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-01  
**Project Status:** Planning & Design Phase