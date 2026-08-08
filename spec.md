# Feature Specification: Corpora MVP

**Feature Branch**: `001-corpora-mvp`
**Created**: 2026-05-01
**Status**: Draft
**Input**: User description: "see @PROJECT.md for project scope."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload New Corpus Dataset (Priority: P1)

A researcher has a corpus file (PDF, plain text, or structured XML/TEI) they want
to ingest into the system. They open the Corpora admin app, trigger the upload
workflow, provide metadata (title, language, source, corpus type), and submit the
file. The system ingests the file, converts it to the internal storage format, and
makes it available in the corpus library.

**Why this priority**: Without upload, no data exists in the system. All other
operations depend on having corpora available. This is the foundational capability
the entire MVP builds on.

**Independent Test**: Can be fully tested by uploading a PDF or text file, entering
metadata, and confirming the new entry appears in the corpus library with correct
metadata and accessible content.

**Acceptance Scenarios**:

1. **Given** a researcher has a PDF file of a biblical text, **When** they upload
   the file and supply title, language, and source metadata, **Then** the corpus
   appears in the library with all supplied metadata and the file content is
   accessible for viewing.
2. **Given** a researcher submits an unsupported file format, **When** the upload
   is attempted, **Then** the system displays a clear error message listing
   accepted formats without corrupting existing data.
3. **Given** a researcher submits a file without required metadata fields,
   **When** they attempt to save, **Then** the system highlights missing fields
   and prevents submission until all required fields are populated.

---

### User Story 2 - Browse and View Corpus Library (Priority: P2)

A researcher opens the Corpora app and sees a list of all available corpora. They
can browse the list, apply filters (by language or corpus type), and select an
entry to view its full content and metadata.

**Why this priority**: Read access is the most common operation for scholars. Once
data exists, they need to navigate and read it efficiently before editing or
managing entries.

**Independent Test**: Can be fully tested with pre-loaded seed data — confirm the
list renders, filters work, and selecting an entry shows content and metadata
without errors.

**Acceptance Scenarios**:

1. **Given** the corpus library contains 50+ entries, **When** the researcher
   opens the library view, **Then** all entries are displayed with title, language,
   and corpus type visible, and the interface remains responsive.
2. **Given** the library contains corpora in multiple languages, **When** the
   researcher filters by "Hebrew", **Then** only Hebrew corpora are shown and the
   count updates accordingly.
3. **Given** the researcher selects a corpus entry, **When** the detail view
   opens, **Then** the full metadata and corpus content are displayed clearly and
   the researcher can scroll through the text.

---

### User Story 3 - Edit Corpus Metadata and Content (Priority: P3)

A researcher finds an error in a corpus entry's metadata or text content. They
select the entry, enter edit mode, make corrections, and save the updated version.
The system preserves the previous state so the change can be tracked.

**Why this priority**: Data quality is critical for scholarly work. Researchers
must be able to correct errors and annotate content, but this depends on Story 2
(viewing) being in place first.

**Independent Test**: Can be fully tested by selecting an existing entry, changing
its title and one text annotation, saving, and confirming the changes persist
across app restarts.

**Acceptance Scenarios**:

1. **Given** a researcher is viewing a corpus entry, **When** they enter edit mode
   and update the title and language, **Then** the changes are saved and reflected
   immediately in the library list.
2. **Given** a researcher edits a corpus entry and closes the app without saving,
   **When** the app is reopened, **Then** the original entry is unchanged and the
   researcher is prompted about unsaved changes before closing.

---

### User Story 4 - Delete or Archive Corpus Entry (Priority: P4)

A researcher identifies a duplicate or deprecated corpus entry and wants to remove
it. They select the entry, choose to delete or archive it, confirm the action, and
the entry is removed from the active library.

**Why this priority**: Data hygiene is important but not blocking for initial
research workflows. Stories 1–3 provide the full read/write MVP; deletion is a
clean-up capability.

**Independent Test**: Can be fully tested by deleting a test entry and confirming
it no longer appears in the library, and that other entries are unaffected.

**Acceptance Scenarios**:

1. **Given** a researcher selects a corpus entry, **When** they choose Delete and
   confirm the action, **Then** the entry is removed from the library and a
   confirmation is shown.
2. **Given** a researcher initiates deletion, **When** they cancel the confirmation
   dialog, **Then** the entry remains in the library unchanged.

---

### Edge Cases

- What happens when a corpus file exceeds available local storage space?
- How does the system behave if the local database becomes corrupted?
- What happens if a researcher uploads a duplicate corpus (same title and source)?
- How are very large files (100MB+ PDFs) handled during upload and display?
- What happens when the app is force-quit during an active upload?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow users to upload corpus files in PDF, plain
  text (.txt), and TEI/XML formats.
- **FR-002**: The system MUST require title, language, and source metadata fields
  before saving a corpus entry.
- **FR-003**: The system MUST display all corpus entries in a browsable list with
  title, language, and corpus type visible.
- **FR-004**: Users MUST be able to filter the corpus library by language and by
  corpus type.
- **FR-005**: The system MUST allow users to view the full content and metadata of
  any corpus entry.
- **FR-006**: Users MUST be able to edit the metadata and text content of any
  existing corpus entry.
- **FR-007**: The system MUST persist all edits so they survive app restarts.
- **FR-008**: Users MUST be able to delete or archive a corpus entry with a
  confirmation step.
- **FR-009**: The system MUST warn users about unsaved changes before closing the
  editor.
- **FR-010**: The system MUST operate fully offline — no internet connection
  required for any core operation.
- **FR-011**: The system MUST remain responsive with 100+ corpus entries in the
  library.
- **FR-012**: The system MUST display actionable error messages for unsupported
  file formats, missing metadata, and storage failures.
- **FR-013**: The system MUST support corpus languages including Hebrew, Greek,
  Syriac, Arabic, Aramaic, Latin, and English.

### Key Entities *(include if feature involves data)*

- **Corpus Dataset**: Represents a single ingested corpus. Key attributes: title,
  language, source, corpus type (manuscript, biblical text, lexicon, commentary),
  content, created date, last modified date.
- **Metadata Record**: Descriptive information attached to a Corpus Dataset.
  Attributes: title, author/source, language, corpus type, notes/annotations.
- **Upload Job**: Tracks a file ingestion in progress. Attributes: file name,
  file type, status (pending, processing, complete, failed), error message.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A researcher can upload a corpus file and have it appear in the
  library, fully searchable, in under 30 seconds for files up to 50 MB.
- **SC-002**: The corpus library loads and displays 100+ entries in under 2
  seconds.
- **SC-003**: A researcher can complete the full upload-to-view workflow (upload,
  enter metadata, confirm, view) in under 3 minutes on first use without
  instruction.
- **SC-004**: All core operations (upload, browse, edit, delete) function correctly
  with no internet connection 100% of the time.
- **SC-005**: Search/filter results are returned in under 1 second for a library
  of 500 entries.
- **SC-006**: Zero data loss occurs during normal CRUD operations; edits persist
  across app restarts with 100% fidelity.

## Assumptions

- The primary user is a single researcher or administrator operating locally on
  their own macOS machine; multi-user or concurrent access is out of scope for MVP.
- Authentication is not required for local-only MVP use; access control will be
  added in a future phase.
- Corpus files are provided by the user from their local file system; remote URL
  ingestion is out of scope for MVP.
- The accepted file size limit is 200 MB per upload; larger files are out of scope
  for MVP.
- "Archive" is treated as a soft-delete (entry hidden from active library but data
  retained); permanent deletion destroys the record entirely.
- Corpus type taxonomy for MVP: biblical text, manuscript, lexicon, commentary,
  historical text. Additional types can be added post-MVP.
- The system stores corpora in the internal `.exg` envelope format; direct
  access to raw source files is not exposed in the UI.
- Version history beyond "last saved" state is out of scope for MVP; full
  versioning is a Phase 2 feature.
- Seed data (30+ pre-loaded corpora) is present in the development environment
  for testing Story 2 independently.
