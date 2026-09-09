---
title: Corpora Admin MVP
description: Product brief, epics, tasks, and release plan for the Corpora Admin desktop app (Tauri) that manages linguistic corpus projects and converts datasets to .corpus format.
tags:
  - project
  - corpora-admin
  - mvp
  - tauri
---

* **Description**: Desktop application for managing linguistic corpus projects and datasets with conversion to .corpus format
* **Version**: 1.0.0
* **Location**: [mannydefreitas7/corpora-tauri/apps/admin](https://www.github.com/mannydefreitas7/corpora-tauri/apps/admin)
* **Platform**: macOS, Windows (Tauri)
* **Status**: In Development

## Project Brief

**Goal**: Enable corpus administrators to create, manage, and publish linguistic projects and datasets through an intuitive desktop application.
**Scope**: MVP includes project CRUD operations, dataset upload/conversion to .corpus format, and basic workflow management (draft → review → published).
**Not Included**: Multi-user collaboration, version branches, account linking.
**Personas**:

* 👤 **Superadmin**: Full system access, project approval, user management
* 📚 **Scholar/Researcher**: Create/manage own projects, upload datasets
* 👨‍💼 **Theologian**: Contribute datasets to collaborative projects
* 👨‍🎓 **Student**: Read-only access to published datasets

⠀

## Epics & Features

### 🔐 EPIC: User Authentication & Access Control

Enable secure user identification and role-based access to the application.
**Rationale**: Users must be identified to associate projects/datasets with creators and enforce permission boundaries.
**Feature: Social Provider Authentication
User Story**: As a desktop user, I want to authenticate using secure, passwordless methods so that I don't need to manage passwords.
**Acceptance Criteria**:

* Users can authenticate via Apple Sign-In (macOS only)
* Users can authenticate via Google Sign-In (all platforms)
* Apple Passkeys are offered as primary option when available
* Authentication tokens are securely stored
* Session persists across app restarts
* Users can manually sign out

⠀**Tasks**:

* AUTH-1: Set up OAuth2 flow for Apple and Google providers
* AUTH-2: Implement platform-specific Passkey detection
* AUTH-3: Build secure token storage using system keychain
* AUTH-4: Create login UI component
* AUTH-5: Implement session/token refresh logic
* AUTH-6: Add sign-out functionality

⠀**Complexity**: 5 points | **Priority**: High | **Dependencies**: None

**Feature: Biometric Authentication
User Story**: As a macOS/Windows user, I want to unlock the app using biometrics so that I can quickly regain access.
**Acceptance Criteria**:

* macOS: Touch ID is offered when available
* Windows: Windows Hello is offered when available
* Biometric unlock is optional (fallback to social auth)
* Biometric failures gracefully fall back to social re-authentication
* System shows clear status of biometric capability

⠀**Tasks**:

* AUTH-7: Integrate Touch ID on macOS
* AUTH-8: Integrate Windows Hello on Windows
* AUTH-9: Build biometric fallback flow
* AUTH-10: Create biometric settings UI

⠀**Complexity**: 5 points | **Priority**: Medium | **Dependencies**: AUTH-1 complete

**Feature: User Signup (QA/Testing Only)
User Story**: As a QA tester, I want to create new test accounts so that I can test multi-user scenarios.
**Acceptance Criteria**:

* Signup flow is accessible via special test mode only
* Minimal UI effort (basic form)
* Creates user record in test database
* Newly created users can log in
* Not exposed in production builds

⠀**Tasks**:

* AUTH-11: Build basic signup form UI
* AUTH-12: Create user creation API endpoint
* AUTH-13: Gate signup behind test mode flag
* AUTH-14: Document QA signup procedure

⠀**Complexity**: 2 points | **Priority**: Low | **Dependencies**: AUTH-1 complete

### 📁 EPIC: Project Management

Enable creation, organization, and lifecycle management of corpus projects.
**Rationale**: Projects are the top-level container for datasets. Admins need CRUD capabilities with role-based access and workflow states.
**Feature: Project CRUD Operations
User Story**: As a corpus admin, I want to create, read, update, and delete projects so that I can organize my corpus work.
**Acceptance Criteria - Create**:

* Admins can create a new project with required metadata
* Created project defaults to draft status
* Non-superadmin projects require superadmin approval to publish
* Creator is automatically set as project owner

⠀**Acceptance Criteria - Read**:

* Users can browse all published projects
* Project owners can see their own draft/in-review projects
* Superadmin can see all projects regardless of status
* Project list is searchable and filterable

⠀**Acceptance Criteria - Update**:

* Project owners can edit their own draft projects
* Metadata changes on published projects trigger status change to draft
* All project fields except ID can be updated
* Change history is tracked

⠀**Acceptance Criteria - Delete**:

* Project owners can soft-delete their own draft projects
* Superadmin can soft-delete any project
* Deleted projects are not visible to regular users
* Deletion is reversible for audit purposes

⠀**Tasks**:

* PROJ-1: Design project data model and database schema
* PROJ-2: Implement project creation API endpoint
* PROJ-3: Implement project read/list API endpoints
* PROJ-4: Implement project update API endpoint
* PROJ-5: Implement project soft-delete API endpoint
* PROJ-6: Build project form UI (create/edit)
* PROJ-7: Build project list/browser UI
* PROJ-8: Build project detail view UI
* PROJ-9: Implement permission checks for all operations

⠀**Complexity**: 8 points | **Priority**: High | **Dependencies**: AUTH complete

**Feature: Project Metadata Management
User Story**: As a project creator, I want to store comprehensive project information so that other users understand its scope and purpose.
**Acceptance Criteria**:

* All metadata fields can be set during creation and updated later
* Image upload works for project thumbnail/cover
* Language selection includes common ISO 639-1/639-3 codes
* Semantic version validation enforces correct format
* License selection includes common open-source licenses
* Optional fields are truly optional
* Metadata is indexed for search/filter

⠀**Metadata Fields**:

* Short title (required)
* Language (required) + language code
* Version (required) - semantic version
* Description (optional)
* Image/Cover (optional)
* Owner (auto-populated)
* License (optional)
* Created/Updated dates (auto)

⠀**Tasks**:

* PROJ-10: Build project metadata form component
* PROJ-11: Implement image upload/storage
* PROJ-12: Build language selector dropdown
* PROJ-13: Implement version format validation
* PROJ-14: Build license selector
* PROJ-15: Add metadata display in project detail view

⠀**Complexity**: 5 points | **Priority**: High | **Dependencies**: PROJ-1 complete

**Feature: Project Status Workflow
User Story**: As a superadmin, I want to manage project approval workflows so that only verified projects are published.
**Acceptance Criteria**:

* Project can transition: draft → review → approved or rejected
* Superadmin can approve/reject projects in review status
* Rejection includes mandatory reason and location fields
* Owner is notified of approval/rejection decisions
* Approved projects transition to published status
* Any metadata change on published project reverts to draft
* Published and archived projects are read-only
* Status history is visible to owner

⠀**Status States**:

* draft: Initial state, owner can edit, not visible to others
* review: Awaiting superadmin review, owner cannot edit
* approved: Ready to publish by superadmin
* published: Live, read-only, visible to all admins
* rejected: Rejected with feedback, owner can revise and resubmit
* archived: End-of-life, read-only, hidden from browsing

⠀**Tasks**:

* PROJ-16: Implement status transition logic
* PROJ-17: Build status change API endpoints
* PROJ-18: Create approval/rejection form UI
* PROJ-19: Build status history display
* PROJ-20: Implement notification system (UI alerts)
* PROJ-21: Add status badge to project list/detail views

⠀**Complexity**: 6 points | **Priority**: High | **Dependencies**: PROJ-1, AUTH complete

### 📤 EPIC: Dataset Management & Upload

Enable users to upload and manage datasets within projects, with conversion to .corpus format.
**Rationale**: Datasets are the core content. MVP focuses on upload, validation, and async conversion workflow.
**Feature: Dataset Upload
User Story**: As a project owner, I want to upload files in various formats so that I can convert them to .corpus format.
**Acceptance Criteria**:

* Upload UI supports drag-and-drop
* Supported formats: Text Fabric, EPUB, PDF, Plain text, XML, TEI, HTML
* File size limits are enforced and user-friendly error shown
* Upload progress is displayed
* Failed uploads provide clear error messages
* Uploaded files are associated with the correct project
* Only project owners/collaborators can upload to a project
* Dataset is marked draft upon successful upload

⠀**Supported Formats**:

* .tf - Text Fabric
* .epub - EPUB ebooks
* .pdf - PDF documents
* .txt - Plain text
* .xml, .tei - XML/TEI markup
* .html - HTML documents

⠀**Tasks**:

* DSET-1: Design dataset data model and schema
* DSET-2: Build file upload API endpoint with validation
* DSET-3: Implement file storage backend
* DSET-4: Build drag-and-drop file upload UI
* DSET-5: Implement upload progress tracking
* DSET-6: Add format detection/validation
* DSET-7: Implement file size limit checks
* DSET-8: Create error handling and messaging

⠀**Complexity**: 6 points | **Priority**: High | **Dependencies**: AUTH, PROJ complete

**Feature: Dataset Preview
User Story**: As an uploader, I want to preview my dataset before conversion so that I can verify content and catch issues early.
**Acceptance Criteria**:

* Preview shows sample of original file content
* Detected format is displayed with confidence level
* Extracted metadata is shown (language, sections, features)
* Potential data loss warnings are highlighted
* Preview available for draft and ready datasets
* Preview UI is responsive and handles large files gracefully
* Users can dismiss preview and proceed to conversion

⠀**Preview Information**:

* File format detection result
* Detected language
* Number of sections/chapters
* Node count estimate
* Feature list preview
* Encoding detection
* Potential issues/warnings

⠀**Tasks**:

* DSET-9: Build file analysis/inspection module
* DSET-10: Implement format-specific preview logic
* DSET-11: Create preview UI component
* DSET-12: Build metadata extraction for each format
* DSET-13: Implement warning/issue detection
* DSET-14: Add preview caching for performance

⠀**Complexity**: 5 points | **Priority**: Medium | **Dependencies**: DSET-1 complete

**Feature: Dataset Conversion to .corpus
User Story**: As a data manager, I want to convert my uploaded dataset to .corpus format so that it can be published and distributed.
**Acceptance Criteria**:

* Conversion is triggered by user action
* Conversion runs asynchronously with progress updates
* Conversion status shows in UI (pending → in-progress → completed/failed)
* Failed conversions show detailed error messages and logs
* Successful conversion updates dataset status to ready
* Conversion can be retried after failure
* Non-superadmin cannot publish; awaits superadmin review
* Conversion results in valid .corpus archive
* Conversion time is tracked and displayed

⠀**Conversion Pipeline**:

1. Detect/validate input format
2. Convert to Text-Fabric intermediate format
3. Validate TF structure
4. Compile to CFM binary format
5. Generate manifest.yml and toc.yml
6. Package into .corpus zip
7. Store in repository

⠀**Tasks**:

* DSET-15: Design conversion task queue system
* DSET-16: Implement async job processing (background tasks)
* DSET-17: Build format-specific converter modules (TF, EPUB, PDF, etc.)
* DSET-18: Implement TF validation logic
* DSET-19: Integrate CFM compilation (Python backend or external service)
* DSET-20: Build manifest.yml and toc.yml generation
* DSET-21: Implement .corpus packaging
* DSET-22: Build conversion UI with progress tracking
* DSET-23: Create error logging and debugging tools
* DSET-24: Implement conversion retry logic

⠀**Complexity**: 13 points | **Priority**: High | **Dependencies**: DSET-1, schema definitions

**Feature: Dataset CRUD & Lifecycle
User Story**: As a dataset owner, I want to manage my datasets so that I can update metadata, re-convert, or remove datasets.
**Acceptance Criteria - Create**:

* Dataset creation is part of upload flow
* Required fields are enforced
* Non-superadmin can only create in own projects

⠀**Acceptance Criteria - Read**:

* Owners can see all their datasets
* Superadmin can see all datasets
* Published projects show published datasets to all admins
* Dataset list is searchable and filterable

⠀**Acceptance Criteria - Update**:

* Owners can update metadata of draft datasets
* Re-upload of source file triggers new conversion
* Cannot update published datasets directly

⠀**Acceptance Criteria - Delete**:

* Soft delete only (preserve history)
* Owners can delete own draft datasets
* Superadmin can delete any dataset
* Deleted datasets hidden from browse

⠀**Tasks**:

* DSET-25: Implement dataset read/list endpoints
* DSET-26: Implement dataset update endpoint
* DSET-27: Implement dataset soft-delete endpoint
* DSET-28: Build dataset list/browser UI
* DSET-29: Build dataset detail view UI
* DSET-30: Build dataset edit form UI
* DSET-31: Implement permission checks

⠀**Complexity**: 7 points | **Priority**: High | **Dependencies**: DSET-1 complete

### 🎨 EPIC: User Interface & UX

Create an intuitive desktop interface for managing projects and datasets.
**Rationale**: Good UX is critical for adoption; this epic ensures consistent, usable UI across all features.
**Feature: Application Shell & Navigation
User Story**: As a user, I want a clear navigation structure so that I can easily access different sections of the app.
**Acceptance Criteria**:

* Main navigation includes: Dashboard, Projects, Datasets, Settings
* Current section is clearly indicated
* Navigation works with keyboard shortcuts
* Responsive layout adapts to window resizing
* Dark/light theme toggle is available
* User profile menu accessible from header
* Help/documentation links visible

⠀**UI Structure**:

* Header: Logo, search, theme toggle, user menu
* Sidebar: Main navigation
* Main content area: Feature-specific views
* Footer: Version info, status

⠀**Tasks**:

* UI-1: Design app shell layout and components
* UI-2: Build main navigation component
* UI-3: Build header component with search
* UI-4: Build user profile menu
* UI-5: Implement theme toggle (dark/light)
* UI-6: Build responsive layout
* UI-7: Implement keyboard navigation shortcuts

⠀**Complexity**: 5 points | **Priority**: High | **Dependencies**: None

**Feature: Dashboard
User Story**: As a returning user, I want to see a dashboard on startup so that I can quickly access recent projects and status.
**Acceptance Criteria**:

* Dashboard shows recent projects (last 5)
* Dashboard shows conversion jobs status (pending/in-progress)
* Dashboard shows pending approvals (superadmin only)
* Quick-create project button is prominent
* Statistics visible (total projects, published datasets, etc.)
* Welcome message for first-time users

⠀**Dashboard Sections**:

* Quick actions (create project, upload dataset)
* Recent activity
* Pending approvals (superadmin)
* System status
* Statistics widget

⠀**Tasks**:

* UI-8: Design dashboard layout
* UI-9: Build dashboard component
* UI-10: Implement recent projects feed
* UI-11: Build job status indicator
* UI-12: Build pending approvals widget
* UI-13: Build statistics widget
* UI-14: Implement quick-action buttons

⠀**Complexity**: 4 points | **Priority**: Medium | **Dependencies**: UI-1, PROJ complete

**Feature: Forms & Input Validation
User Story**: As a user, I want helpful form feedback so that I can quickly correct errors and complete tasks.
**Acceptance Criteria**:

* All forms have real-time validation
* Error messages are specific and actionable
* Required fields are clearly marked
* Optional fields are marked or implied
* Form submit button is disabled until valid
* Success messages confirm actions
* Unsaved changes trigger warnings
* Form state is preserved on validation error

⠀**Form Components**:

* Text inputs with validation
* Dropdowns/selects
* File inputs
* Checkboxes/toggles
* Rich text editor
* Version input with format validation
* Language selector

⠀**Tasks**:

* UI-15: Build form component library
* UI-16: Implement validation utilities
* UI-17: Build error message display
* UI-18: Implement unsaved changes warning
* UI-19: Create form input components (text, select, file, etc.)
* UI-20: Build language selector component
* UI-21: Build version validator

⠀**Complexity**: 5 points | **Priority**: Medium | **Dependencies**: UI-1

### 🔧 EPIC: Backend Infrastructure & APIs

Build robust backend systems for data persistence and async processing.
**Rationale**: Backend APIs power all frontend features; this epic ensures scalable, reliable infrastructure.
**Feature: Project API Endpoints
User Story**: As a frontend, I need well-designed APIs so that I can reliably manage project data.
**API Endpoints**:

```text
POST   /api/v1/projects              # Create project
GET    /api/v1/projects              # List projects
GET    /api/v1/projects/:id          # Get project detail
PUT    /api/v1/projects/:id          # Update project
DELETE /api/v1/projects/:id          # Soft delete project
POST   /api/v1/projects/:id/status   # Change status
GET    /api/v1/projects/:id/datasets # List project datasets
```

**Tasks**:

* API-1: Design project API schema
* API-2: Implement project create endpoint
* API-3: Implement project list/read endpoints
* API-4: Implement project update endpoint
* API-5: Implement project delete endpoint
* API-6: Implement status change endpoint
* API-7: Add request validation
* API-8: Add permission/auth checks
* API-9: Write API documentation

⠀**Complexity**: 6 points | **Priority**: High | **Dependencies**: AUTH complete

**Feature: Dataset API Endpoints & File Handling
User Story**: As a frontend, I need dataset APIs and file handling so that I can manage uploads and conversions.
**API Endpoints**:

```text
POST   /api/v1/datasets               # Create dataset
GET    /api/v1/datasets               # List datasets
GET    /api/v1/datasets/:id           # Get dataset detail
PUT    /api/v1/datasets/:id           # Update dataset
DELETE /api/v1/datasets/:id           # Soft delete dataset
POST   /api/v1/datasets/:id/upload    # Upload file
GET    /api/v1/datasets/:id/preview   # Get preview data
POST   /api/v1/datasets/:id/convert   # Trigger conversion
GET    /api/v1/datasets/:id/status    # Get conversion status
GET    /api/v1/datasets/:id/download  # Download .corpus
```

**Tasks**:

* API-10: Design dataset API schema
* API-11: Implement dataset CRUD endpoints
* API-12: Implement file upload endpoint
* API-13: Implement preview data endpoint
* API-14: Implement conversion trigger endpoint
* API-15: Implement status polling endpoint
* API-16: Implement download endpoint
* API-17: Add request validation
* API-18: Add permission/auth checks

⠀**Complexity**: 8 points | **Priority**: High | **Dependencies**: AUTH, DSET-1 complete

**Feature: Job Queue & Async Conversion Processing
User Story**: As a system, I need to process conversions asynchronously so that the app stays responsive and handles multiple jobs.
**Acceptance Criteria**:

* Conversion jobs are queued and processed sequentially
* Job status updates are pushed to frontend
* Failed jobs are logged with details
* Jobs can be retried from failed state
* Job history is preserved
* Large file processing doesn't block app

⠀**Tasks**:

* INFRA-1: Select/setup job queue system (Bull, Celery, etc.)
* INFRA-2: Implement job submission API
* INFRA-3: Implement job worker
* INFRA-4: Build job status tracking
* INFRA-5: Implement WebSocket push updates for job status
* INFRA-6: Build job retry logic
* INFRA-7: Implement job logging
* INFRA-8: Create job monitoring dashboard (admin)

⠀**Complexity**: 8 points | **Priority**: High | **Dependencies**: API-10 complete

### ✅ EPIC: Testing & Quality Assurance

Ensure application reliability and user-facing quality.
**Note**: Quality gates should be applied throughout development, not left for end.
**Feature: Automated Testing
User Story**: As a developer, I want automated tests so that I can catch bugs early and refactor confidently.
**Testing Coverage**:

* Unit tests: All utilities, validators, API logic
* Integration tests: API endpoints with database
* E2E tests: Critical user workflows (create project, upload dataset, convert)
* UI tests: Component rendering and interactions

⠀**Tasks**:

* TEST-1: Set up test framework and runners
* TEST-2: Write unit tests for validators
* TEST-3: Write unit tests for API logic
* TEST-4: Write integration tests for API endpoints
* TEST-5: Write E2E tests for critical flows
* TEST-6: Set up CI/CD pipeline for tests
* TEST-7: Achieve 70%+ code coverage target

⠀**Complexity**: 8 points | **Priority**: Medium | **Dependencies**: API complete

**Feature: Error Handling & Logging
User Story**: As a developer/admin, I want comprehensive logging so that I can debug issues and monitor system health.
**Acceptance Criteria**:

* All errors are logged with context
* Sensitive data is not logged
* Logs are aggregated and searchable
* User-facing errors have helpful messages
* Admin can view error logs in UI
* System health metrics are available

⠀**Tasks**:

* QUAL-1: Implement centralized logging
* QUAL-2: Add error handling middleware
* QUAL-3: Create error code documentation
* QUAL-4: Build error log viewer (admin)
* QUAL-5: Implement health check endpoint
* QUAL-6: Build metrics dashboard

⠀**Complexity**: 5 points | **Priority**: Medium | **Dependencies**: API complete

## Release Planning

### MVP (v1.0.0) - Core Workflows

**Timeline**: 8-12 weeks
**Must Have**:

* ✅ Authentication (Social + Biometric)
* ✅ Project CRUD + Status Workflow
* ✅ Dataset Upload + Preview
* ✅ Basic Dataset Conversion (.corpus format)
* ✅ App Shell & Dashboard
* ✅ Core APIs
* ✅ Basic Testing

⠀**Total Story Points**: \~110 points

### Post-MVP Ideas (v1.1+)

* Multi-user project collaboration
* Dataset versioning and branching
* Advanced conversion options (format-specific settings)
* Dataset diffing and history comparison
* Batch operations
* Scheduled conversions
* Dataset duplication/templates
* Advanced search and filtering
* Export project metadata
* API keys for third-party integrations

⠀

## Dependency Map

```text
AUTH (Foundation)
├── PROJ (depends on AUTH)
│   ├── PROJ Metadata
│   └── PROJ Status Workflow
├── DSET (depends on AUTH + PROJ)
│   ├── DSET Upload
│   ├── DSET Preview
│   ├── DSET Convert
│   └── DSET CRUD
├── UI (parallel with APIs)
│   ├── App Shell
│   ├── Dashboard
│   └── Forms
├── API (depends on AUTH)
│   ├── Project APIs
│   ├── Dataset APIs
│   └── Job Queue
└── QUALITY (continuous)
    ├── Testing
    └── Logging
```

## Success Metrics

* ✅ All projects creatable, editable, publishable
* ✅ All supported formats convertible to .corpus
* ✅ Conversion success rate > 95%
* ✅ App responsive and performant
* ✅ Zero authentication failures
* ✅ User can complete basic workflow in < 2 minutes
* ✅ Test coverage > 70%
* ✅ No critical bugs at release
