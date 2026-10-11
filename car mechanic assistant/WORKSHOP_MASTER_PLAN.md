# Workshop job-sheet project — master plan and implementation ledger

**Last updated:** 11 October 2026. **Current phase:** F01–F05 verified. Manual capture, confirmation, history and corrections work at `/workshop`; next is F06 demonstration CSV. Export/AI remain pending.

This is the authoritative implementation/handoff document for the workshop administrative project. Every contributor, including Codex and Claude, must update it for **every feature or implementation part**, including partial work, fixes, migrations, tests, configuration and changed decisions. Do not rely on chat history to resume the work.

The first product is a small local application that turns a permitted paper sheet or manual entry into a reviewed job record and a reusable output. AI may draft fields; staff confirm their meaning. A confirmed record is not automatically a completed repair, final invoice, paid transaction or imported accounting entry.

## 1. Start here: the actual next task

**Next ready task: F06 — reproducible demonstration CSV.** F01–F05 schemas, drafts, images, manual screen and reviewed history are verified. Implement F06 to finish the first complete manual workflow before adding AI. The user explicitly selected job-sheet capture/review; public-reference RAG remains separate research.

Do not start by scanning an archive, training a model, building a vector database or integrating the accounting system. None is required to demonstrate the core review workflow.

The first working milestone is:

> Open a fictional job sheet → enter a draft beside its image → correct an ambiguous value → confirm the record → download a clearly labelled demonstration CSV → reopen the same record and see what was confirmed.

This milestone is a local demonstration. It does not claim company deployment, real handwriting accuracy, accounting integration or reduced staff time.

### First actions for the next implementer

1. Read this file, root `AGENTS.md`, root `CLAUDE.md`, [BUILD_STATUS.md](BUILD_STATUS.md) and [the repository README](../README.md).
2. Run `git status --short` and identify unrelated user work. On 11 October, `PROJECT_SUMMARY.md` is modified and `SYSTEM_DESIGN.md` is untracked; preserve both unless the user explicitly includes them in the task.
3. Read the existing schema/session/router/test fixtures listed in section 5. Confirm actual paths before adding code.
4. Check whether the private visit files exist locally. Their absence does not block a synthetic/manual prototype. Do not obtain company files from public search as replacements for actual evidence.
5. Mark the next ready feature (currently F06) `IN_PROGRESS` and state the exact scope in the ledger below.
6. Reuse reviewed revisions and private storage for deterministic demo CSV, a unique export identity and per-version download controls. Keep destination compatibility and reviewer self-reporting limits explicit.
7. Update the ledger, verification table, next task and work log **before** committing. Commit only the intended files, then push as previously authorised by the user.

## 2. Business problem and scope

The reviewed visit material supports investigating repeated transcription of workshop job information. A useful product must make the record clearer and/or remove an existing copying step. If it produces an additional record but staff still retype every destination, it may increase work.

The initial scope is one job-sheet capture/review flow, one reviewed record, and one demonstration output. It should remain usable without an AI key. Later, confirm a real output mapping and measure the complete task with an actual operator.

**Initial exclusions:** automatic repair diagnosis, automatic pricing, liability/claim decisions, tax/accounting treatment decisions, live financial-system writes, bulk archive scanning, supplier integrations and a new repair-manual RAG system. These are not dependencies of this project. Add them only when the user chooses a concrete new scope supported by evidence.

The existing automotive API and manual assistant remain separate capabilities in this repository. Do not rename their historical development as this new workflow or claim that new work happened during the internship.

## 3. Evidence available and what is still missing

The private sources are in local `company visit/`. The key private documents are `COMPANY_VISIT_REVIEW.md`, `COMPANY_WORKFLOWS_AND_AI_PLAN.md` and `IMAGE_REVIEW.md`. They contain detailed observations and company-answer fields. They are intentionally not published with this master plan.

| Evidence | Available now | What it allows | What remains unknown |
|---|---|---|---|
| Blank administrative PDF forms | Yes | Understand layouts and candidate fields | Actual use, approved version and processing authority |
| Five populated job-sheet photos | Yes, local/private | Real handwriting/annotation development examples | Intended meaning, record stage, full header and independent labels |
| Six illustrated component-reference photos | Yes, local/private | Basic component vocabulary discussion | Vehicle-specific repair instructions or extensive manuals |
| Two text transcripts | Yes, local/private | Identify themes and workflow questions | Original audio, unclear terms and precise roles/rules |
| Final invoice/accounting entry/spreadsheet chain | No | Would specify real reuse | Destination schema and approved field mappings |
| Independent expected extraction values | No | Would support accuracy evaluation | Correct interpretation of ambiguous notes/marks |
| Operator baseline and pilot owner | No | Would establish usefulness and ownership | Whether a new workflow will actually be adopted |
| Permission for future provider processing | Not confirmed | Would allow the selected real-data extraction path | Permitted provider/storage/retention for customer records |

Having uploaded photos available for this review is not blanket approval to send them to any external model or publish them. Synthetic examples may be used freely for development when clearly labelled. Actual company records remain private.

### Work that can proceed without company answers

- Data contract and validation.
- Local storage/migration with a dedicated development database.
- Source preview, manual entry, correction and confirmation.
- Explicit missing/ambiguous states, revision handling and duplicate warning.
- A demonstration CSV with a fictional schema.
- Basic search over synthetic/confirmed development records.
- Tests of failure handling and calculation consistency.
- Extraction integration tests using mocked responses.

### Work whose result depends on answers

- Meaning of real shorthand and diagram marks: company reviewer needed.
- Real extraction accuracy: independent labels and permitted processing needed.
- Company-compatible export: target schema and rules needed.
- Automated imports/ledger changes: separate integration scope and operating authority needed.
- Staff time-saving/adoption: actual task baseline and operator needed.
- Workshop deployment beyond the local demonstration: access/hosting/record-handling decisions needed.

Keep pending questions recorded. Continue independent ready work without repeatedly interrupting the user.

## 4. What the operator should experience

### A. Begin a record

The operator opens `/workshop`, chooses **New record**, and either attaches an allowed image or enters the information directly. The screen clearly identifies a development/demo mode when fictional data or outputs are in use.

The image stays visible beside the draft. Controls support zoom and view rotation without changing the original bytes. The initial scope accepts JPEG/PNG images only; PDFs, HEIC and multi-page bundles require an explicit later scope rather than an unsupported upload that appears to succeed.

### B. Enter or review draft fields

The operator enters visible values, preserving the raw note. Empty means unknown, not zero. An unclear field is marked unclear; a crossed-out value is not accepted automatically. Unknown customer/vehicle details can remain empty because some sources are cropped.

A suggested interpretation belongs beside the literal text. Example: a fictional handwritten abbreviation is saved verbatim; the operator supplies a confirmed expanded description. A model suggestion alone does not become confirmed work.

### C. Confirm a version

The operator selects the record stage and confirms that entered values match the source or a stated manual clarification. The initial **review-complete** record must have a meaningful job reference, at least one confirmed item/description, reviewer identity and explicit resolution of fields selected as required for that demonstration output.

The UI can save incomplete drafts. It cannot present an incomplete record as reviewed merely because it exists. If the source is not visible, a manual record still needs an explicit manual provenance entry. No fake source image is generated to support it.

### D. Reuse the record

The first downloadable output is explicitly **demo CSV — not mapped to company software**. It contains the stable job/version reference and reviewed values. Producing the file records a generated output; it does not mark an external system as imported.

After a real mapping is supplied, a specific approved export replaces the demo mapping. Export format checks and operator confirmation are required before calling it compatible. Repeated downloads of an identical immutable export are allowed; they must not silently create new transaction records or new export versions.

### E. Correct and find it again

An operator can reopen a draft, create a correction to a reviewed version and look up confirmed records. Earlier reviewed/exported versions remain identifiable. Customer names alone do not merge records. A corrected version is not silently resubmitted to an external destination.

## 5. Architecture and places the work reaches

### Selected approach

Extend the existing **FastAPI app** with a small workshop router and static HTML/CSS/JavaScript page. Reuse SQLAlchemy, the database session, Alembic and pytest. Use PostgreSQL for actual migration/integration checks; existing SQLite fixtures may test ordinary service logic when appropriate.

Do not create a third server or install a frontend framework. The existing separate Flask/Gemini/Chroma application is not the host for this workflow. Its Gemini dependency/patterns may be consulted later; extraction is not retrieval and should not import the full RAG application just to call a model.

### Existing files to inspect before implementation

| Path | Existing purpose | Proposed relationship |
|---|---|---|
| `app/main.py` | FastAPI app, routers, static mount, root/health | Register the workshop router and a separate `/workshop` page; preserve existing routes |
| `app/db/models.py` | Shared SQLAlchemy `Base`, automotive and three workshop models | F02 added workshop document/job/revision tables to shared metadata |
| `app/db/session.py` | Engine, `SessionLocal`, `get_db` | Reuse sessions/transactions; no second connection layer |
| `alembic/env.py` | Migration metadata/settings | Ensure workshop tables enter `Base.metadata`; no startup `create_all` |
| `alembic/versions/` | Existing migration chain | Add a new revision after the actual current head; do not rewrite old revisions |
| `app/core/config.py` | Settings/environment loading | Add only storage/feature settings actually required by implemented features |
| `app/core/logging.py` | Structured logging | Log event IDs/status/counts; do not log raw customer text/images |
| `app/static/index.html` | Current automotive UI | Keep existing behaviour; add a workshop link once its route works |
| `tests/conftest.py` | Isolated DB/client/provider fixtures | Reuse; extend only for workshop-specific isolation/storage |
| `requirements.txt` | Root application dependencies | Change only for a real import used by the workshop implementation |
| `requirements-dev.txt` | Combined development dependencies | Keep reproducible test setup; fictional image fixtures may use installed tools |
| `car mechanic assistant/src/rag_system.py` | Existing Gemini manual assistant | Reference SDK patterns if needed; do not couple workshop records to vector collections |

The existing `Vehicle` model expects fields not necessarily present in a job sheet and serves a different purpose. Do not force an administrative job to create a VIN/specification vehicle record. A minimal reviewed vehicle reference can live in the workshop payload.

### Proposed new code files

F01–F04 schema/test/fixture/router/service/UI paths below now exist. Extraction and later export paths remain proposed. If existing code offers a smaller correct arrangement, change the list and explain the decision in this master file before continuing.

| Path | Purpose | First feature |
|---|---|---|
| `app/schemas/workshop.py` | F01 record/review validation plus F02 draft-update/job-response contracts; export schemas deferred until F06 | F01/F02 |
| `app/services/workshop.py` | F02 draft/source checks plus F03 image storage and F05 confirmation/history; F06 export next | F02/F05/F06 |
| `app/api/v1/workshop.py` | F02 create/read/replace routes and default-disabled demo gate; image routes later | F02/F03 |
| `app/templates/workshop.html` | F04 gated source/draft review page outside static mount; no HTML bypass when disabled | F04 |
| `app/static/workshop.js` | Page actions and accessible feedback | F04 |
| `app/static/workshop.css` | Necessary page styles; reuse existing styles where practical | F04 |
| `app/services/workshop_extraction.py` | One optional image-to-draft integration, added only when justified | F07 |
| `tests/unit/test_workshop.py` | Draft/review/export/identity failure checks | F01 onward |
| `tests/integration/test_workshop_postgres.py` | F02 real migrations, reopen, concurrent saves, rollback and revision constraints; review/export checks later | F02/F05/F06 |
| `tests/fixtures/workshop/` | Clearly labelled fictional inputs and expected records | F01 |

No generic provider/plugin/agent abstraction is required. Add one integration when it is chosen, with a testable call boundary and validated results.

### Proposed private storage

Store permitted source files and trial artifacts under ignored `car mechanic assistant/runtime/workshop/`, outside `app/static/`. A minimal `WORKSHOP_STORAGE_DIR` setting may override it when necessary. Server-generated file IDs map to storage paths; original filenames are display metadata, never trusted filesystem paths.

Use a dedicated development database, not an existing company database. Confirm `DATABASE_URL` resolves to the intended environment before running migrations. Do not print credentials or inspect environment-file contents into tool output. Do not expose the local demonstration on a public interface.

## 6. Data contract and record lifecycle

### Fields in the first contract

| Field | Draft behaviour | Reviewed behaviour |
|---|---|---|
| `job_id` | Server-generated stable identifier | Preserved through corrections and output |
| `source_document_id` | Optional for manual entry | Source link or explicit manual provenance |
| `record_stage` | `unknown`, `quote`, `approved_scope`, `completed_work` | Explicitly selected; review state is a separate concept |
| `job_reference` | Optional internal/customer-supplied reference | Required for the first reusable demo record; not an invented invoice number |
| `customer_reference` | Optional literal value | Reviewer-confirmed if supplied; no automatic identity merge |
| `vehicle_reference`, `make`, `model` | Optional | Retain unknowns; do not infer year/VIN |
| Date fields and `date_note_raw` | Raw note plus optional parsed date | Partial dates stay partial unless reviewer supplies missing information |
| `items` | Raw descriptions, proposed interpretation, amount text/value and review status | Every exported item has a confirmed description; uncertain amounts are not zero |
| `diagram_notes` | Literal notes/unknown annotations | Confirmed meanings separate from raw observations |
| Written totals/adjustments | Optional source values, with raw text | Preserve what is written; no default tax treatment |
| `currency` | Unknown unless supplied | Explicit for an output requiring currency; never guessed from model context |
| `reviewer`, `reviewed_at` | Empty | Required on immutable reviewed revision |
| `data_origin` | `synthetic_demo` or `private_source` | Preserved; never count demo records as company use |

For unknown values, use null/explicit status rather than a fabricated empty success. Preserve raw text and separate clarified values. Validation rejects unsupported enum values, impossible numeric formats and oversized fields without rejecting ordinary bilingual text.

Amounts use `Decimal`, not binary floating-point arithmetic. Use an explicitly documented decimal string representation in JSON if needed. Do not infer per-unit quantity, tax rate, account code or currency from a related blank template.

### Missing, unclear and confirmed

Use a small documented set of field states: `missing`, `unclear`, `proposed`, `confirmed`. A manual entry can be confirmed by the reviewer; a model-generated value starts proposed. The application should not require a complex field-object wrapper around every scalar if a compact payload plus review metadata expresses the same rules reliably. Choose and test the simplest representation during F01.

Do not treat a language model's self-reported confidence as a calibrated probability. Source availability, parse validity and explicit review are the usable controls initially.

### Implemented F01 payload rules

Code: [workshop schemas](../app/schemas/workshop.py). Examples: [five fictional JSON records](../tests/fixtures/workshop/examples.json) and [printed demo sheet](../tests/fixtures/workshop/synthetic-sheet.png). Checks: [schema tests](../tests/unit/test_workshop.py). No company image or wording is used in the fixture image. It matches `clean_manual_quote`; it is not a handwriting benchmark.

- `WorkshopItem` separates literal description/amount text from interpreted values, has explicit description/amount states and retains a `cancelled` flag. Active reviewed items need confirmed descriptions; any supplied amount must be confirmed. Cancelled rows are retained and excluded from active-work requirements; later exports must apply the same rule.
- `WorkshopDraft` holds the fields above and a compact `field_states` map for interpreted scalar fields. An omitted scalar state resolves to `missing` for null, otherwise `proposed`. Item states default to `missing`, so supplied item values must also include their state. `missing` cannot accompany a value; `proposed`/`confirmed` require one. `unclear` may retain a candidate or null.
- `WorkshopReviewedDraft` validates a chosen stage, job reference, source UUID or explicit manual provenance, at least one active confirmed description and resolution of every interpreted scalar/active-item amount. Optional genuinely missing values stay null. Raw notes remain literal and do not create interpreted dates, diagram actions, tax rules or amounts. Currency is required when active/written amounts exist.
- `WorkshopReviewedRevision` adds a job UUID, positive strict integer version, nonblank reviewer and timezone-aware review timestamp. F02/F05 must generate/check identities/timestamps, verify source ownership/existence and enforce version immutability in persistence. A UUID or typed reviewer in F01 is only a validated shape.
- Money accepts decimal strings, `Decimal` or whole integers, rejecting float/bool, nonfinite values and more than two decimal places. JSON serialises supplied money as fixed two-decimal strings. Values are bounded to ten integer digits plus two decimals (absolute value below 10,000,000,000); ordinary amounts/totals are nonnegative, written adjustments may be signed. No totals are inferred or reconciled yet.
- Currency is three uppercase letters, not a verified currency-registry membership check. Interpreted references cap at 200 characters, descriptions/manual provenance at 2,000, raw notes at 10,000, raw amount text at 200 and items at 50. Unknown keys and unsupported states/stages/origins are rejected; bilingual strings remain intact.

F01 schemas have no routes, database models, uploads, authentication or provider calls. They do not prove a source was consulted or a reviewer was authorised. Future extraction must set generated values to proposed rather than trusting a provider-supplied confirmed state.

### Persistence design

Start with three narrowly scoped tables:

1. **WorkshopDocument:** generated ID, content checksum, stored file key, detected media type, byte size, data origin and creation time. Do not expose the filesystem path through the API.
2. **WorkshopJob:** stable job ID, current draft payload, draft version and timestamps. A document reference may be null for explicit manual entry.
3. **WorkshopJobRevision:** immutable reviewed snapshot, job ID, version, reviewer and review time. Apply a unique constraint to `(job_id, version)`.

The draft payload can use SQLAlchemy's portable JSON type. Do not normalise each possible document field into a new table before the real mapping is known. When modifying JSON, explicitly assign the updated object so the ORM persists it reliably.

Add **WorkshopExport** in F06 when export exists: job/revision, format/mapping version, checksum/output key, generation status/time. Use a unique export identity for the same reviewed revision and mapping. This records file generation, not external delivery/import. Do not implement payment, customer-master, supplier, claim or accounting tables in this scope.

### Version and correction rules

- A draft edit carries the version the operator loaded; stale updates return a conflict rather than overwrite newer work.
- Confirmation checks that version, validates required fields and writes a snapshot atomically.
- Repeated confirmation of an unchanged version must not create duplicate reviewed revisions.
- Editing after confirmation creates a newer draft and preserves the earlier snapshot.
- Exports refer to a specific reviewed revision, never the mutable draft.
- An output already generated remains reproducible from its snapshot. New corrections require a new reviewed version, not alteration of old export evidence.
- Keep review state distinct from repair stage. A reviewed quote remains a quote.

### Implemented F02 persistence and API

[Models](../app/db/models.py) now include `WorkshopDocument`, `WorkshopJob` and `WorkshopJobRevision`. [Migration](../alembic/versions/20261011_workshop_drafts.py) is additive; timestamps use timezone-aware PostgreSQL columns, IDs are ORM-generated UUIDs, jobs persist an entire JSON-safe draft plus nullable source FK and version. A written Decimal is stored as its fixed two-decimal string. Assign/replace the JSON payload instead of mutating it in place.

Revision storage has job/source FKs, a positive version check and unique `(job_id, version)`. F05 adds the confirmation writer and PostgreSQL UPDATE/DELETE rejection trigger; F12 still supplies real user access controls. F03 supplies actual source storage. Historical F02 checks alone did not establish these later features.

The [router](../app/api/v1/workshop.py) uses the shared `get_db` session and [service](../app/services/workshop.py), gated by `WORKSHOP_ENABLED=false` by default. Disabled routes return 404. Enable only in a local isolated demonstration; the flag is not authentication.

| Operation now | Actual route | Input/result |
|---|---|---|
| Create editable draft | `POST /api/v1/workshop/jobs` | Full `WorkshopDraft` body → 201 with generated `id`, `draft`, `draft_version=1`, `created_at`, `updated_at` |
| Reopen editable draft | `GET /api/v1/workshop/jobs/{job_id}` | UUID → current draft/version/timestamps; missing ID 404, malformed UUID 422 |
| Replace editable draft | `PATCH /api/v1/workshop/jobs/{job_id}` | `{ "expected_version": 1, "draft": { ...full draft... } }` → new version; stale save 409 |

PATCH replaces the entire draft, not selected fields. Read the latest version, edit its full payload and send the version that was loaded. Every successful save advances the version, including unchanged saves; stale/repeated saves conflict and must reload. SQL updates match both job ID and expected version atomically. Drafts may remain incomplete, with stage unknown and no source/provenance; they are never presented as reviewed by this API.

A supplied source UUID must exist in `workshop_documents` and match draft origin. Source FK and payload are saved together. `data_origin` cannot change once a job exists; clearing an attachment does not let a private job become a synthetic job. Jobs sharing customer/reference text remain distinct UUIDs. F03 will add actual file handling; F12 must additionally verify source ownership/access for real users.

Database write failures rollback and use the existing sanitised DB error handler; request logging records route/status/type without the draft contents. F02 performs no model calls, arithmetic, confirmation, automatic record merge, export or external writes.

### Implemented F03 sources

`POST /api/v1/workshop/documents` accepts multipart `file` and explicit `data_origin`; returns opaque UUID, media type, byte size, origin and `duplicate`. `GET /api/v1/workshop/documents/{document_id}/preview` returns unchanged bytes with `Cache-Control: no-store` and `nosniff`. Both use the default-disabled workshop gate. The original filename is not retained or used as a path.

JPEG/PNG only, single frame, decoded content/MIME/suffix agreement, 1 byte–8 MiB file size, 6,000 pixels per side and 20,000,000 pixels total. The ASGI upload middleware buffers at most 8 MiB + 64 KiB of multipart input and rejects overflow before parsing/spooling, including requests without Content-Length. Inner request logging still assigns request IDs to limit responses. Empty/corrupt/mismatched/unsupported/oversized input fails visibly, not as a saved attachment.

`WORKSHOP_STORAGE_DIR` defaults to ignored `car mechanic assistant/runtime/workshop/`, resolved outside `app/static`. Files use generated UUID keys, exclusive creation and private permissions; raw bytes are fsynced before DB commit. Duplicate checksums reuse the existing source only when origin matches and its file passes size/SHA-256 verification; concurrent duplicates retain one row/file. No job merge occurs. Database/write errors rollback and remove newly created files where cleanup succeeds. Missing/altered/unsafe stored paths fail preview/reuse with 503, without exposing a disk path.

Known limit: a process crash between file creation and DB commit can leave an unreferenced file; F12 storage reconciliation/backup work must handle it. Byte deduplication does not detect a different photograph of the same sheet. Pillow 12.3.0 is declared in the root host requirements; no company images were used for checks.

### Implemented F05 review and correction

`POST /api/v1/workshop/jobs/{id}/confirm` requires strict positive `expected_version`, a nonblank self-reported `reviewer` and strict `acknowledged: true`; client timestamps/extra properties are rejected. It locks and refreshes the persisted job, rejects stale versions with 409, validates the full reviewed contract and verifies an attached source's hash/availability. It writes one snapshot with a server UTC timestamp. Repeat confirmation returns the original snapshot/reviewer/time. Confirmation does not increment the draft version or convert a quote to completed work.

`GET /jobs/{id}/revisions` returns newest-first snapshots with default 20, maximum 100 and nonnegative offset. The UI shows read-only records, literal/cancelled rows and original-source links, with older-history pagination. Edits invalidate interpreted confirmation state, require saving a new draft version and then rereview; previous records remain unchanged. Failed validation/confirmation keeps the draft; a history read failure after a successful save is reported separately from the known save result.

Additive revision `20261011_review_guard` follows `20261011_workshop`: source FK/backfill plus a PostgreSQL trigger rejecting snapshot UPDATE/DELETE. This source link prevents deleting the source row even after a newer draft detaches it. SQLite unit tests do not provide that DB trigger guarantee; actual PostgreSQL integration verifies it. A privileged DB administrator can change schema/disable triggers; local reviewer names are not authenticated identities. No production audit/adoption claim follows from these controls.

### Suggested API boundaries

The implementer may simplify route naming, but must document the final contract here. All are under `/api/v1/workshop`; the HTML page is `/workshop`.

| Operation | Proposed route | Expected behaviour |
|---|---|---|
| Attach source | `POST /documents` | Validate/store an allowed image; return opaque ID and possible duplicate reference |
| Preview source | `GET /documents/{id}/preview` | Resolve server-side ID; never accept arbitrary disk paths |
| Create draft | `POST /jobs` | Create synthetic/manual/source-linked draft |
| Read draft/history | `GET /jobs/{id}` | Return current draft and reviewed-version references |
| Edit draft | `PATCH /jobs/{id}` | Validate and reject stale version |
| Confirm | `POST /jobs/{id}/confirm` | Create an immutable reviewed snapshot after checks |
| Generate output | `POST /jobs/{id}/exports` | Generate/reuse output for requested reviewed revision |
| Download output | `GET /exports/{id}/download` | Serve recorded output safely; no implication of import |
| AI draft, later | `POST /jobs/{id}/extract` | Explicit permitted request; validate result; no auto-confirm |
| Find records, later | `GET /jobs` | Bounded search over reviewed records; explicit mode for drafts |

The first build should not add background workers. A bounded synchronous extraction request is sufficient for a local demo if its latency/failure behaviour is acceptable. Reconsider only after real use shows a queue is needed.

## 7. Implementation ledger — update every row as work happens

Allowed statuses: `READY`, `IN_PROGRESS`, `IMPLEMENTED_UNVERIFIED`, `VERIFIED`, `WAITING_COMPANY`, `DEFERRED`. Dependencies can leave a READY item not yet executable. A feature is VERIFIED only when its acceptance checks have actually run. Describe scope rather than claiming production readiness.

| ID | Part | Status now | Dependencies | Evidence / next action |
|---|---|---|---|---|
| F00 | Master plan, handoff and private-source boundary | VERIFIED | None | Documentation/link/exclusion/staged-scope checks for this change; no app implementation |
| F01 | Draft/review contract and fictional fixtures | VERIFIED | F00 | Four record/review schemas, five fictional JSON cases and one printed demo PNG; 45 targeted checks passed |
| F02 | Workshop storage, models and migration | VERIFIED | F01 | Three tables, migration 20261011_workshop and create/read/replace routes; 133 total tests passed with real PostgreSQL; live app restart preserved draft |
| F03 | Safe image attach/preview and duplicate warning | VERIFIED | F02 | 16 new cases plus live upload/preview/duplicate/chunked-limit checks; full suite 149 passed |
| F04 | Manual source/draft review screen | VERIFIED | F01–F03 | Gated page/ordinary JS/CSS; Chrome browser flow and failure retention passed; Python suite 150 passed |
| F05 | Confirmation, immutable revisions and conflict handling | VERIFIED | F02/F04 | Atomic/idempotent confirmation, bounded read-only history, corrections, source FK and PG mutation guard; local self-reported reviewer |
| F06 | Reproducible demonstration CSV output | READY | F05 | Demo-only mapping; deterministic output/export identity |
| F07 | Optional AI image-to-draft extraction | READY for mocks; real source use conditional | F03–F06 | Provider/permission checks before real uploaded records |
| F08 | Reviewed diagram/shorthand interpretation | WAITING_COMPANY for real labels | F04/F07 | Manual annotation can work now; meaning cannot be fabricated |
| F09 | Actual destination mapping and export | WAITING_COMPANY | F06 | One destination schema plus checked record chain needed |
| F10 | Basic lookup of confirmed records | READY | F05 | Filters/keywords first; no vector database |
| F11 | Extraction and end-to-end evaluation | READY for synthetic harness; real metrics conditional | F06/F07/F09 | Independent labels and operator baseline needed for company results |
| F12 | Workshop pilot access, backup and operating guide | WAITING_COMPANY for deployment | Demonstrated useful flow | Authentication/storage/retention/host/operator decisions required |

If a feature takes several turns, add subrows such as `F03.a upload validation` and `F03.b preview route`. Each subrow needs its own status and verification notes. Do not wait until the parent feature is finished to record partial work.

## 8. Feature specifications and acceptance checks

### F01 — contract and fictional examples

**Purpose:** agree what a draft/confirmed record means before coupling it to UI, storage or AI.

**Implementation:** add Pydantic schemas and a small number of synthetic JSON/image fixtures with explicit fictional provenance. Cover a clean job, unclear/cancelled amount, missing description, mixed-language text and same-name distinct records. Use authored fictional content; do not copy private sheets into tracked fixtures.

**Checks:** decimal values round-trip; missing amount stays null; unclear descriptions cannot pass required confirmation; unknown stage cannot become completed work; invalid/oversized fields fail predictably; Unicode text is preserved.

**Completion:** documented payload examples and passing schema tests. Update section 6 with the actual representation and section 13 with exact commands/results.

**Delivered:** VERIFIED on 11 October 2026. The four schema classes, five JSON cases and labelled PNG listed in section 6 exist. All 45 targeted checks passed; broader regression results are in section 13. No persistence/review endpoint or UI has been implemented.

### F02 — persistence and migration

**Purpose:** preserve drafts and reviewed history without disturbing current automotive data.

**Implementation:** add the three initial models to shared metadata; create one new additive Alembic revision; use `get_db` and transactions. Keep generated-source paths private. Do not call `init_db/create_all` on application startup.

**Checks:** new database upgrades to head; a database at the previous head upgrades while preserving a seeded existing row; schema and models align; draft survives process/reopen; rollback leaves no partial reviewed state. Run these on an isolated PostgreSQL database, not only SQLite.

**Completion:** draft create/read/update service or routes working, migration tests/evidence recorded, actual new revision documented. Downstream feature blockers are explicit if PostgreSQL is unavailable.

**Delivered:** VERIFIED on 11 October 2026. Three tables are registered in shared metadata. Revision `20261011_workshop` follows `20261009_complete`; no historical migration is rewritten. Three local draft routes, source/origin checks and atomic version-checked saves work. Fifteen new F02 cases pass within the 133-test suite. Fresh/previous-head migrations, model alignment, concurrent saves, rollback, constraints and a live process restart were checked on PostgreSQL 14.20. Review confirmation/immutable snapshots belong to F05; their table alone is not that feature.

### F03 — attach and preview an image

**Purpose:** give the operator a reliable source beside the draft.

**Implementation:** accept bounded JPEG/PNG uploads; validate decoded content, dimensions/pixel count and byte size; reject mismatched/unsupported files. Reuse Pillow if installed and declare it in the actual host requirements when imported. Write generated file keys under private storage; store SHA-256 and return an ID. No raw upload directory under the static mount.

**Checks:** valid upload/preview; corrupt input; fake extension/MIME; over-limit input; unsafe original filename; unknown source ID; duplicate bytes; database/file failure without a falsely saved attachment. Check limits in the running app, not just a helper.

**Duplicate behaviour:** warn/reuse the source reference when the same bytes already exist; do not merge job records or assume a new photo of the same sheet is unrelated. Byte checksums do not detect all semantic duplicates. Document this limit.

**Completion:** UI can display the stored original by opaque ID; originals unchanged; limits and storage path documented. Real-world remote access is not approved by this local feature.

**Delivered:** VERIFIED for attach/preview service and routes. Sixteen new synthetic cases include live-limit/failure checks and a real PostgreSQL duplicate race. Browser display is exercised by F04; the API already returns the original image. Full suite: 149 passed, 101 warnings, no skips. Live HTTP upload, unchanged preview, duplicate reuse and a chunked oversized request passed.

### F04 — manual source/draft review UI

**Purpose:** make the complete task usable before depending on AI.

**Implementation:** a separate static page with source preview, zoom/view rotation, editable fields, item rows, raw notes, unknown/unclear indicators and save feedback. Use escaped text/safe DOM APIs for source/model/user strings. Provide labels, keyboard access and visible failure feedback. Preserve unsaved edits if a request fails; do not show success before persistence succeeds.

**Checks:** enter a fictional job with image; save/reload preserves values; blank/unclear states remain visible; bilingual text displays; failed save retains entered values; keyboard users can reach controls; long notes do not hide confirmation; existing root/API still works.

**Completion:** one manually entered draft works through browser UI, without provider keys. Record actual browser checks separately from automated tests.

**Delivered:** VERIFIED manual draft workflow at `/workshop`. HTML is outside the static mount so its default-disabled gate cannot be bypassed through `/static/workshop.html`. Source zoom/rotation, scalar/item/raw fields, cancellation, explicit review states, save/reopen and dirty/error retention work. Optional details are collapsed so references/items remain prominent. Browser checks include keyboard focus, mobile width, literal HTML-like notes and original-image identity. Confirmation/history controls are added/verified in F05, not claimed here.

### F05 — reviewed snapshots and corrections

**Purpose:** stop provisional interpretations from silently becoming authoritative outputs.

**Implementation:** validate required fields; require explicit stage/reviewer; save immutable revision in one transaction. Guard loaded draft version. Show reviewed snapshot history and create a new draft when correcting a reviewed record.

**Checks:** incomplete draft can save but cannot confirm; repeated unchanged confirmation does not duplicate; stale edit/confirm returns conflict; two concurrent confirmations produce one correct result; old snapshot survives correction; reviewed quote stays a quote. Usernames typed into a local demo are self-reported reviewers, not authenticated identities; label that limitation until F12.

**Completion:** draft → review → correction → rereview is demonstrable; immutable versions and conflict behaviour verified. Do not claim a compliance-grade audit trail from a local self-reported reviewer.

**Delivered:** VERIFIED on 11 October 2026. API, row locking/idempotence, source retention, PG guard, bounded history and manual correction/rereview UI tested using fictional records. See register/work log for exact checks and limits.

### F06 — demo CSV and export identity

**Purpose:** finish the vertical slice and show how reviewed values could be reused.

**Implementation:** explicitly version one fictional/demo CSV schema. Generate from a reviewed revision using `csv`/`Decimal`, not an LLM. Include job ID, revision, origin, stage and confirmed line data. Preserve unknowns. Protect spreadsheet cells against formula execution while documenting any escaping; keep the canonical stored value unchanged. Store export reference/checksum/version and allow the same output to be downloaded again.

**Checks:** exact fictional expected rows; commas/newlines/Unicode; leading formula characters; null versus zero; reproducible checksum; draft cannot export; same revision/mapping cannot create duplicate generated exports; corrected revision yields a distinct output; file-generation failure is not success.

**Completion:** first full manual milestone is demonstrated. Label output demo-only until F09. No live invoice/accounting import is performed.

### F07 — AI proposes a draft

**Purpose:** reduce initial typing while preserving the manual workflow as a fallback.

**Implementation:** choose one extraction provider after verifying its current official SDK/API documentation. The repository already uses `google-genai`; reuse it if the selected permitted path is Gemini. Do not introduce an orchestration framework or a second provider merely for flexibility. Mocked model responses can be implemented/tested while real-data processing permission is pending.

The request must be explicit. It sends only the permitted source needed for that task. Request structured fields matching F01, preserve literal text and return null/unclear for absent information. Treat instructions printed/written in the image as source data, not authority to call tools or change application policy.

Validate all output through the same schemas. A valid JSON shape is not proof of semantic correctness. Mark generated fields proposed; never confirm/export automatically. Preserve an existing edited draft unless the operator chooses a reviewed merge/replacement. Initially, extraction should only populate an empty draft or display proposed changes for selection.

**Checks:** mock clean output; invalid JSON/schema; omitted fields; invented stage/reference; corrupt source; timeout/provider error; missing configuration; attempted source prompt injection; extraction over an edited draft; sensitive provider error text is not leaked. Also check no network call occurs without the explicit enabled/permitted path.

**Completion:** image → proposed fields → manual correction → confirmation → demo output works. Live synthetic provider smoke test and real private-source test are different evidence entries. Real accuracy remains unclaimed until independent evaluation.

### F08 — diagram and shorthand review

**Purpose:** retain information that plain text reading misses.

**Implementation now:** display the diagram/source; allow reviewer-entered panel/action notes and explicit unknowns. After real labels exist, add model suggestions only if they save effort. A short reviewed vocabulary/selectable panel list may be simpler than computer vision.

**Checks:** area-only mark does not imply repair operation; left/right uses a confirmed vehicle convention rather than screen coordinates; crossed-out annotations remain distinguishable; raw notes and confirmed meaning survive save/export; labels are attributed to a reviewer.

**Completion:** manual annotations may be complete before automated suggestions. Record these as separate subfeatures, not one falsely finished AI feature.

### F09 — one real destination mapping

**Purpose:** replace an existing entry step rather than add another.

**Prerequisites:** one permitted/redacted source-to-final-record chain; destination software/spreadsheet columns and import capabilities; reviewer-approved mapping and correction process. Missing prerequisites do not block F01–F08.

**Implementation:** choose exactly one supported output. Document each source field, required destination value, conversion/unknown handling and record stage. Use deterministic mapping; tax/account fields require approved rules rather than model judgment. Do not silently convert a quote into a final transaction.

**Checks:** reviewer confirms expected output for representative examples; destination accepts a permitted test file if available; incompatible/missing required fields block output; mapping version recorded; repeated generation and corrected-version handling understood. A live financial write requires an explicit later task; a test CSV is not an imported transaction.

**Completion:** call it company-compatible only after those checks. Describe the actual removed step if an operator really uses it; otherwise record compatibility only.

### F10 — confirmed-record lookup

**Purpose:** retrieve reliable captured jobs without an archive-scanning project.

**Implementation:** bounded job/reference/date/stage filters and keyword search over confirmed records. Show source/revision and distinguish draft results if draft search is separately requested. No automatic merging by customer name. Defer embeddings/RAG until an observed query requires more than structured lookup.

**Checks:** same-name customers remain separate; one vehicle can have multiple jobs; missing identifiers stay visible; draft data is not shown as confirmed; pagination/limits work; corrected record links to version history; untrusted search text cannot execute SQL/HTML.

**Completion:** an operator can find and reopen the intended fictional reviewed job. This does not prove fast lookup over the actual storeroom archive.

### F11 — evaluation and baseline comparison

**Purpose:** establish whether AI and the overall workflow are useful.

**Implementation now:** a small evaluation script or existing-test extension reading fictional/privately labelled examples. Report sample/field counts and missing/unclear cases. Keep expected labels independent of the model output. Store real results privately and public synthetic outputs clearly labelled.

**Real trial later:** company reviewer independently labels permitted examples; reserve held-out cases; compare current copying, direct digital entry and AI draft/review. Time the whole routine: photograph, wait, review, clarify, output, remaining entry and corrections. Record how many entry destinations genuinely stopped requiring manual copying.

**Checks:** evaluator rejects missing labels/empty sample; denominators and skipped fields visible; cancelled/unknown values not counted as correctly invented; critical identity/amount/description errors reported separately; synthetic tests excluded from company accuracy/adoption statistics.

**Completion:** a reproducible development report first; a company outcome only when actual observation exists. Document dates, method, sample limits and human-reviewed residual errors. Document-capture field accuracy is not retrieval precision.

### F12 — permitted pilot operation

**Purpose:** support an actual operator safely after the local workflow proves useful.

**Prerequisites:** named operator/owner, permitted host/storage/provider path, data retention/access decisions and selected scope. Local demo completion does not imply these approvals.

**Implementation when selected:** real authentication and identity on the workshop routes, protected source/export access, appropriate origin/CSRF handling, nonpublic storage, backup/restore and a short operating guide. Existing broad CORS and placeholder security settings are not a production boundary. Protect page, API, previews and downloads; do not assume hiding the page protects the endpoints.

**Checks:** unauthorised source/export reads and writes fail; no static bypass; forged origin/session requests are handled appropriately; sensitive values not logged; backup restores reviewed records and corresponding source/output references; deleting records follows the agreed scope without orphaned private files.

**Completion:** record exactly what environment/access was tested and who approved actual use. Do not infer 24 users, six months' adoption or production deployment from a local trial.

## 9. Build order and checkpoints

| Milestone | Deliverable | Ready now? | Decision after demonstration |
|---|---|---|---|
| M1: manual vertical slice | F01–F06; fictional source → review → version → demo CSV | Yes, with isolated development environment | Is the review UI understandable and the record lifecycle correct? |
| M2: AI drafting | F07 plus manual F08 | Mocks yes; real source use conditional | Does extraction reduce complete entry/review effort versus direct form? |
| M3: real reuse | F09 plus selected F10 | Needs company mapping | Can one existing copying destination be removed? |
| M4: measured local trial | Real portion of F11 | Needs labels, operator and baseline | Is it useful enough to maintain? |
| M5: permitted workshop pilot | F12 and agreed scope | Needs operating decisions | Is actual use authorised and supportable? |

There is no honest fixed completion date for company-dependent milestones. Code estimates should be revised after M1; provider/integration/approval delays are not coding effort.

If M2 loses to direct entry, keep the simpler form. If M3 cannot remove entry, do not expand the system to justify its existence. If no operator wants it, leave an accurate local prototype and record that result.

## 10. Configuration, dependencies and operating boundaries

The manual milestone requires no search, marketplace or AI credentials. Provider failures must not prevent manual entry/review. Inspect existing settings loading before adding new environment handling.

**Implemented setting:** `WORKSHOP_ENABLED` defaults to false in Settings and `.env.example`. The workshop endpoints are local demo operations without authentication; keep them disabled in any existing shared/public host. Enabling them does not install tables. Run Alembic explicitly against the intended isolated DB first; startup does not call `create_all` or migrate.

### Manual screen and browser verification

Open `/workshop` after local startup. Attach the fictional PNG from `tests/fixtures/workshop/`, enter a job reference/stage and items, choose states deliberately and save. Copy the generated job ID, reopen it or revisit the resulting `?job=` URL. Existing records cannot change origin. Manual drafts need no model key.

All edited interpreted values become proposed again; raw notes remain literal. Enter decimal text without binary float conversion. Missing values remain null. Save errors/conflicts keep current controls and dirty status. Unsaved navigation/new/open/remove actions require an explicit discard choice; no saved job or stored source is deleted by those UI actions. Source rotation/zoom are view-only. Dynamic content uses text/value APIs, not HTML insertion.

Python route/asset gate test: `tests/unit/test_workshop_page.py`. Repeatable browser scenario: [tests/browser/workshop.cjs](../tests/browser/workshop.cjs). It creates fictional records on the supplied **isolated local** demo server. Verified with Playwright 1.64.0 and installed headless Chrome, an isolated browser context (no user's browser profile). Setup/run:

```sh
npm install --prefix 'car mechanic assistant/runtime/workshop-browser-tests' playwright@1.64.0
node tests/browser/workshop.cjs 'car mechanic assistant/runtime/workshop-browser-tests/node_modules/playwright' http://127.0.0.1:8000
```

Node/Chrome are test tools, not application dependencies. The library supports the installed Chrome channel and file-input actions; see official [browser](https://playwright.dev/docs/browsers) and [input](https://playwright.dev/docs/input) documentation. Desktop/mobile screenshots stay ignored under runtime. Native computer-use access timed out without a state result, so it was not counted as a successful visual check. Playwright-rendered screenshots were inspected locally instead.

### Run the current draft/source API

From the repository root, use the existing Python environment and a separately provisioned local development PostgreSQL database. Set the actual connection through your private environment/config; do not copy a company database URL into this example.

```sh
export DATABASE_URL='postgresql://YOUR_LOCAL_ROLE@127.0.0.1:5432/yap_test_workshop'
export WORKSHOP_ENABLED=true
export USE_GOOGLE_CSE=false
export USE_EBAY_API=false
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The role/database placeholder must be replaced with an existing isolated local target. `/docs` describes the draft/source operations; `/workshop` opens the manual screen. The root automotive UI also links to it. In a second terminal, this sends the authored fixture only:

```python
import json
from pathlib import Path
import httpx

record = json.loads(Path("tests/fixtures/workshop/examples.json").read_text())["examples"][0]["record"]
with httpx.Client(base_url="http://127.0.0.1:8000") as client:
    response = client.post("/api/v1/workshop/jobs", json=record)
    response.raise_for_status()
    job = response.json()
    job["draft"]["diagram_notes_raw"] = "Fictional clarified note"
    saved = client.patch("/api/v1/workshop/jobs/" + job["id"], json={
        "expected_version": job["draft_version"], "draft": job["draft"],
    })
    saved.raise_for_status()
    print(saved.json()["draft_version"])
```

F02 verification used a task-created PostgreSQL 14.20 cluster under ignored `runtime/workshop-f02-tests/`, listening on `127.0.0.1:55441`, database `yap_test_workshop_f02`. Tests use random disposable schemas and an explicitly supplied local `YAP_TEST_POSTGRES_URL`; the migration tests accept a caller-provided connection via Alembic config attributes so they cannot fall back to the application DB. A normal CLI migration/check and live Uvicorn on `127.0.0.1:18041` were also tested against that same isolated database. Two app processes and the test PostgreSQL process were stopped after verification. The ignored cluster/synthetic restart artifact remain local; no company data was used.


Implemented private storage setting: `WORKSHOP_STORAGE_DIR`. Override only with a nonpublic directory; the service rejects the static mount. Example synthetic upload after local startup:

```sh
curl -f -F data_origin=synthetic_demo -F file=@tests/fixtures/workshop/synthetic-sheet.png http://127.0.0.1:8000/api/v1/workshop/documents
```

Possible later settings, added only when needed:

- `WORKSHOP_STORAGE_DIR`: nonpublic directory for source/output files.
- A minimal upload size/pixel limit: choose sensible bounded development limits, then document their actual values rather than promising unsupported formats.
- `WORKSHOP_EXTRACTION_ENABLED`: default disabled so uploaded private files are not unexpectedly sent to a provider.
- Selected provider model/key settings: reuse documented existing configuration where safe; no key in code, fixtures, chat or Markdown.

A general queue, Redis, Neo4j, model-training pipeline or provider registry is not required. Existing configuration names for those systems are not an instruction to install or use them.

When adding Pillow or an extraction SDK to the root application, ensure the dependency is declared for that host rather than merely relying on the separate assistant's environment. Use current installed/repository versions as the starting point; verify compatibility before changing pins.

## 11. Private/public file rules and Git procedure

### Public repository may contain

Code, migrations, clearly synthetic fixtures, generic design/implementation notes, test results with sensitive content removed, this master ledger and general build status.

### Keep private

Visit recordings/transcripts, photos, customer particulars, scanned forms from the company, filled company-answer documents, source-to-invoice record pairs, provider payloads/responses containing company data, real evaluation labels/results and generated private outputs. Do not place them in tracked test fixtures or copy their content into this public plan.

Root ignore rules must protect `company visit/` for future clones, not only this machine's `.git/info/exclude`. The existing ignored `runtime/` is the home for private working artifacts. Ignored paths are not protection if files were already tracked; inspect staged/tracked scope before every commit.

### After every implementation part

1. Update this master file: feature/subfeature status, actual files/routes/schema, checks, remaining limits, next step and work-log entry.
2. Update relevant run instructions/examples when behaviour changed. Add a short [BUILD_STATUS.md](BUILD_STATUS.md) entry for the delivered increment, linking back here.
3. Run targeted verification appropriate to the changed logic and record actual results. If shared schema/router/dependencies changed, run the relevant existing suite too.
4. Inspect `git diff`, `git diff --check` and staged filenames. Preserve unrelated user files.
5. Stage explicit intended paths. Never use `git add .` for this workspace and never force-add private sources.
6. Commit code, meaningful tests and updated master together with a message describing the actual increment.
7. Push the intended branch as authorised; record push failures/remaining work. Do not claim pushed without checking.

A commit cannot contain its own final hash. Use a descriptive work-log entry in that commit, then record its hash in the next update or report it to the user. Read `git log` to identify the latest actual delivery when resuming.

## 12. Required documentation update format

For **each part** implemented, append an entry like this and update the ledger row. Use actual values; do not copy the placeholder result as evidence.

```text
Date / contributor:
Feature/subfeature ID:
Status: IN_PROGRESS | IMPLEMENTED_UNVERIFIED | VERIFIED | WAITING_COMPANY | DEFERRED
Behaviour delivered:
Files/routes/schema/config changed:
Verification commands and actual results:
Manual checks and actual results:
Evidence origin: synthetic | real private development | independent real evaluation
Known limitations / failed checks:
Company questions still needed:
Commit / push status:
Next smallest ready task:
```

If interrupted mid-feature, record what exists, what is broken/unverified, the last command and how to resume. Do not leave the next agent guessing whether a migration ran or a test passed. If an approach is abandoned, explain the relevant reason and update the selected design; do not keep contradictory instructions active.

## 13. Verification and result register

| Date | Scope | Command/check | Actual result | Limits |
|---|---|---|---|---|
| Previous audit, 9 October 2026 | Existing automotive API/RAG | See BUILD_STATUS audit entries | Previously recorded 73 tests passed with PostgreSQL integration and additional live checks | Historical baseline; not rerun for this plan and not a job-sheet test result |
| 11 October 2026 | F00 documentation | Local links, feature-ledger coverage, handoff/ignore scope and Markdown whitespace | Checked for this documentation change | No workshop application feature exists yet |
| 11 October 2026 | Pre-F01 application baseline | `.venv/bin/python -m pytest -q tests` | 72 passed, 1 skipped, 76 warnings | PostgreSQL test skipped: no disposable test URL; mocked/local fixtures only |
| 11 October 2026 | F01 schema/review rules | `.venv/bin/python -m pytest -q tests/unit/test_workshop.py --disable-warnings` | 45 passed, 7 warnings | Fictional contracts only; initial large-integer boundary failure fixed and retested |
| 11 October 2026 | F01 broader regression | `.venv/bin/python -m pytest -q tests` | 117 passed, 1 skipped, 76 warnings | Existing PostgreSQL integration skipped without `YAP_TEST_POSTGRES_URL`; dependency/deprecation warnings remain |
| 11 October 2026 | Fictional image and public/private boundary | Visual PNG inspection, fixture decode/record check, document links, original checksums, ignore/staged scope and `git diff --check` | Checked; image labelled fictional, 18 original source hashes unchanged | No browser UI, provider processing, handwriting or company-outcome test |
| 11 October 2026 | Initial F02 API/migration checks | Explicit local test URL + `pytest -q tests/unit/test_workshop_api.py tests/integration/test_workshop_postgres.py --disable-warnings` | Initial 14 cases passed, 18 warnings; one later constraint case verified by full suite | SQLite API boundary plus actual PostgreSQL migrations/transactions; all fictional |
| 11 October 2026 | F02 full regression with real DB | Explicit local `YAP_TEST_POSTGRES_URL` + `.venv/bin/python -m pytest -q tests` | **133 passed, 0 skipped, 100 warnings** | PostgreSQL 14.20; 15 new F02 cases. Existing dependency/deprecation warnings remain; no business outcome claims |
| 11 October 2026 | Normal migration/environment path | Isolated `DATABASE_URL` + `alembic upgrade head` and `alembic check` | All revisions upgraded to 20261011_workshop; no new upgrade operations detected | Disposable task DB only; production migration/deployment not run |
| 11 October 2026 | Live F02 HTTP/restart | Local Uvicorn: health/create/update/stale save; stop/restart and GET/OpenAPI | 200/201/200/409; second process returned identical draft/version/timestamps | Synthetic example only; no browser UI or authentication test |
| 11 October 2026 | F02 delivery boundaries | Local links, private exclusions, unchanged 18 original hashes, explicit staged scope and whitespace | Checked; only intended code/tests/docs/config included | Company questions remain pending |

| 11 October 2026 | F03 source/API/PG regression | Local test URL + `.venv/bin/python -m pytest -q tests --disable-warnings` | 149 passed, no skips, 101 warnings | Synthetic sources only; real PG deduplication race |
| 11 October 2026 | Clean API host environment | Install root requirements; clean pip check; workshop unit/integration tests | No broken requirements; 76 passed, 20 warnings | Isolated runtime venv; shared environment has unrelated conflicts; Docker unchecked |

| 11 October 2026 | F04 Python regression | Explicit local test URL + pytest tests | 150 passed, no skips, 101 warnings | One new page/gate/assets check; DB checks still enabled |
| 11 October 2026 | F04 rendered manual workflow | `node tests/browser/workshop.cjs ...` against task server | Attach, validation retention, save/reload, Unicode/Decimal text, unchanged rotated/zoomed source, keyboard, stale/503 retention, mobile width, untrusted note rendering passed | Chrome desktop/390px viewport only; no operator usability/baseline measurement |

| 11 October 2026 | F05 review/source-retention regression | Explicit local PG URL + `.venv/bin/python -m pytest -q --disable-warnings` | **167 passed, no skips, 115 warnings** | 17 F05 cases added; fictional inputs; dependency/deprecation warnings remain |
| 11 October 2026 | F05 isolated API environment | Clean root requirements env + workshop unit/integration pytest | **94 passed, 34 warnings** | No assistant/RAG dependencies in this environment |
| 11 October 2026 | F05 migration/browser/privacy | CLI upgrade/head alignment; isolated Chrome harness; original hashes/ignore/whitespace | No new Alembic operations; confirmation/correction/history/idempotence browser checks passed; 18 originals unchanged/ignored | PG14.20 task DB only; no authenticated identity or company trial |

Replace vague “tests pass” with the command, counts, skipped checks and test environment. PostgreSQL integration is skipped without its explicit disposable test URL; do not present a skipped test as passed.

### Commands to adapt during implementation

Run from the repository root using the actual Python 3.12 environment. The checked workspace has `.venv/bin/python`, but a different machine may need its own environment.

```sh
git status --short
.venv/bin/python --version
.venv/bin/python -m pytest -q tests/unit/test_workshop.py
```

`test_workshop.py` covers 45 F01 schema cases. F02 adds `tests/unit/test_workshop_api.py` and `tests/integration/test_workshop_postgres.py`; run those too when changing persistence/routes. PostgreSQL checks require the explicit disposable test URL.

After changes to shared routes/models/dependencies:

```sh
.venv/bin/python -m pytest -q tests
```

For actual DB/migration checks, use a disposable database whose name begins `yap_test` and the established `YAP_TEST_POSTGRES_URL` integration convention. Provide connection settings via a permitted local environment/config path. Never reuse a live company DB or remove its volumes. Setting the integration URL alone does not change Alembic's `DATABASE_URL`; explicitly confirm the migration target separately.

For a manual local server, after environment/migrations are ready:

```sh
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Do not start this against an unintended default database. Stop only processes started for this task. Record the exact startup/migration/browser steps actually used in the operating guide once F02/F04 exist.

## 14. Company question ledger

Keep actual answers and documents in the private visit files. Here, record generic prerequisites and whether they have been resolved without publishing identifying content.

| ID | Needed answer/evidence | Blocks | Status |
|---|---|---|---|
| Q01 | One reviewer explains raw notes, abbreviations, panel convention and amounts on a sheet | Real F08 labels/semantic evaluation | Pending |
| Q02 | Confirm whether source is quote, approved scope or completed work | Real stage/output correctness | Pending |
| Q03 | One redacted sheet → final invoice/software record → spreadsheet chain | F09 mapping | Pending |
| Q04 | Destination name, columns/import format and approved mapping | F09 real compatibility | Pending |
| Q05 | Which existing entry step should disappear | Business usefulness | Pending |
| Q06 | Real user/reviewer and pilot decision owner | Real F11/F12 | Pending |
| Q07 | Permitted source storage and selected external-provider processing | Real F07/F12 | Pending |
| Q08 | Baseline task time and independently checked expected values | Real measured results | Pending |
| Q09 | Access/retention/backup/hosting decisions | F12 | Pending |
| Q10 | What happens when a record already reused downstream is corrected | F09 correction handling | Pending |

Record a question as resolved only when there is an actual answer. An elapsed wait, a synthetic sample or a plausible inference is not an answer. Continue ready tasks while these are pending.

## 15. Current handoff snapshot

- **Branch/repository:** `main`, remote `origin` is the user's existing GitHub repository. Verify actual remote before pushing on a different machine.
- **Previous delivery before F05:** `e99e054`, verified manual screen. Read Git history for the final F05 commit hash.
- **What exists:** current automotive API/RAG, visit review/planning material, F01 schemas/fictional fixtures and F02 workshop models/migration/draft service/API/tests.
- **Latest implementation:** F05 adds atomic confirmation, immutable reviewed snapshots, read-only history and correction/rereview. Review source links survive detachment from later drafts; the PG guard rejects mutation. Browser confirmation/correction checks passed; see verification register for final test counts.
- **What does not exist:** output/search/AI extraction, real benchmark/mapping or permitted company pilot.
- **Next ready feature:** F06 demonstration CSV; then optional mocked extraction and confirmed-record lookup.
- **Independent work available:** safe source attach/preview, local manual UI, confirmation, demo output and later mocked extraction; lack of company access does not block these.
- **Unrelated changes to preserve:** root `PROJECT_SUMMARY.md` and `SYSTEM_DESIGN.md` as seen on this machine; verify current status rather than assuming it remains identical.
- **Open decisions:** real output mapping, model-processing path, operator and expected labels. None should be fabricated.

### Copyable Claude handoff prompt

```text
Continue the workshop job-sheet project in this repository. Read AGENTS.md,
CLAUDE.md and car mechanic assistant/WORKSHOP_MASTER_PLAN.md first.
Treat the master plan as the current implementation ledger. Inspect Git status
and preserve unrelated user work. F01–F05 are verified. Start with F06
reproducible demo CSV from reviewed snapshots. Use synthetic examples until
real-data prerequisites are met. Keep company visit files and runtime artifacts
private. After every implementation part, update the master with actual files,
behaviour, tests, limitations and next task; commit the intended changes and
push as authorised. Do not claim planned features or synthetic results as
company deployment/evidence. Continue independent work while company questions
remain recorded and unanswered.
```

## 16. Work log

### 11 October 2026 — F00, project plan and handoff

- Created this master specification with the first manual milestone, optional AI path, feature acceptance checks, implementation/result ledgers and company prerequisites.
- Selected extension of the existing FastAPI/PostgreSQL application, with static UI and ordinary structured records; no new vector database/server/framework required.
- Added persistent Codex/Claude instructions and a README link so the next contributor can find the plan.
- Made private-source exclusions portable through root Git ignore rules; retained local/private visit detail separately.
- Verification: document structure/links/feature coverage, ignore behaviour, source integrity and explicit staged scope checked. No application code changed; no application tests rerun.
- Next task: F01 schemas/fictional fixtures/validation tests. Implement the manual workflow before extracting real sheets or integrating a destination.

Unverified: new application behaviour, real extraction accuracy, destination compatibility, staff time savings and company deployment.
Main risk: capture/review adds work unless a reviewed record replaces an existing entry step; missing facts and unconfirmed shorthand cannot be repaired by confident generation.

### 11 October 2026 — public automotive corpus feasibility research

The user asked whether public automotive parts information could supply 500+ pages for a separate retrieval project. This is research, not a replacement of the selected workshop workflow or an implemented ingestion feature. **Next ready task remains F01** unless the user chooses a different project direction.

| Candidate | Source checked | Actual verification | Limits |
|---|---|---|---|
| MANN-FILTER cars/transporters catalogue, 2024–2026 | [Official PDF](https://www.mann-filter.com/content/dam/mann-filter/communication-media/brochures-catalogs/mann-filter-catalog-cars-transporters-2024-26-interactive.pdf), linked from the manufacturer's [download hub](https://www.mann-filter.com/de-de/service/download-hub.html) | Downloaded; pypdf/PyMuPDF both count **513 pages**; full text-presence/exact-duplicate checks and local parser dry run complete | Parts catalogue; 2,523 candidate chunks default to unknown scope; semantic quality/relevance and serving ingestion unverified |
| DENSO spark-plug technical manual | [Official PDF](https://assets.denso-am.eu/staging/attachments/1663942351%20EN_Spark%20Plug%20Manual.pdf) | Downloaded; pypdf/PyMuPDF both count **68 pages**; full text-presence/exact-duplicate checks and local parser dry run complete | 271 candidate chunks default to unknown scope; workshop tasks, permitted hosted use and serving ingestion unverified |
| Other manufacturer references | [DENSO downloads](https://www.denso-am.eu/downloads), [Bosch download centre](https://ap.boschaftermarket.com/in/en/news/download-centre/browse-all-downloads) | Official reference/download entry points found | Individual documents, editions, applicability and use conditions need review |

Private research download/inventory: `runtime/public-corpus-research-20261011/mann-filter-cars-transporters-2024-26.pdf` and `mann-filter-inventory.json` under this assistant directory. Inventory records source URL, byte size, SHA-256, physical PDF page count and sample extraction lengths. The file has **not** been embedded or added to any Chroma collection. The PDF is not committed or redistributed.

Initial Python urllib download encountered a local certificate-store error; retry with the installed certifi CA bundle succeeded with certificate verification enabled. Browser retrieval of the large catalogue exceeded that tool's size limit; local download/page counting supplied the result. Neither failure was counted as successful ingestion.

If a public-reference RAG direction is selected, first review permitted use/processing, relevance and unique accepted content. Record publisher, edition, region, document type, source hash and original page IDs; separate tabular fitment retrieval from narrative technical passages. Count accepted source pages separately from downloaded pages and chunk counts. Test model/engine/year matching, tables, missing context, citations and unsupported-query abstention using independently labelled questions. A corpus with 513 physical pages does not automatically contain 513 useful ingested pages or demonstrate retrieval accuracy.

A future résumé may describe a public manufacturer-document corpus after it is actually processed and tested. Public pages found now do not establish Yap Motor ownership/use, internship timing, multilingual EN/CN/JP coverage, 24 mechanics, 90% precision or six-month adoption. Parts catalogues must not be labelled repair manuals.

Status: **research verified; ingestion not implemented**. No application code or provider/model calls changed. Current decision: public sources are available; business usefulness and the chosen project direction remain distinct questions.

### 11 October 2026 — résumé/corpus sufficiency double-check

Created [RAG_CORPUS_RESUME_ASSESSMENT.md](RAG_CORPUS_RESUME_ASSESSMENT.md) as the detailed companion verdict for the RAG résumé wording. Downloaded the second PDF and independently verified 581 physical pages with pypdf and PyMuPDF. Both full-document text scans and exact-normalised-text deduplication completed; the unmodified document processor produced 2,794 candidate chunks in a local dry run. All default to unknown applicability scope, which current retrieval rejects; source language metadata is also too coarse for mixed-language content. No embeddings, model calls, new serving collection or application changes were made.

The assessment separates physical/parsable/quality-approved/indexed pages, classifies source types, evaluates each résumé assertion, records parser/filter/evaluator limitations, links publisher terms and gives conditional build/evidence gates and accurate wording. Source availability is verified; the original production/user/precision/multilingual/history claims remain unsupported. Raw files/page metrics/renders stay ignored in runtime storage. This is completed assessment work, not a new implemented corpus feature or scope change; F01 remains the next workshop task.


### 11 October 2026 — F01, job-sheet schemas and fictional fixtures

- **Status:** VERIFIED for the data contract/fixtures only. User selected job-sheet capture/review over the separate public-reference RAG direction.
- **Delivered:** `WorkshopItem`, `WorkshopDraft`, `WorkshopReviewedDraft` and `WorkshopReviewedRevision`; explicit raw/parsed values and field states, cancelled-row preservation, review validation, literal stage/origin/provenance and decimal-string JSON amounts. Missing amounts stay null. No automatic calculation, pricing or transaction-stage inference.
- **Files:** `app/schemas/workshop.py`, `tests/unit/test_workshop.py`, `tests/fixtures/workshop/examples.json`, `tests/fixtures/workshop/synthetic-sheet.png`; this master, README and BUILD_STATUS updated together. No routes, database tables, migration, dependency or config changes. No existing caller imports these schemas yet.
- **Fixture origin:** five authored fictional cases covering clean quote, cancelled/unclear amounts, missing description, bilingual/unknown-date notes and distinct jobs sharing customer text. One printed demo PNG matches the clean example and is visibly labelled synthetic; it does not imitate or reuse private company sheets.
- **Verification:** targeted 45 passed/7 warnings; full existing/new suite 117 passed/1 skipped/76 warnings. Commands/results and skipped PostgreSQL prerequisite are in section 13. Initial whole-number money-bound failure was fixed with explicit signed bounds; boundary, source-linked and mutated-instance checks pass. No further failing checks remain in this scope.
- **Manual/static checks:** PNG visually inspected; fixture image decodes and matches its example labels; links and whitespace checked; private-source checksums/exclusions/staged scope checked. No UI/server/provider operation was exercised for F01.
- **Limits:** schema validation cannot authenticate a reviewer, prove a source exists, freeze a persisted revision or establish semantic correctness. DB concurrency/immutability belongs to F02/F05. Currency syntax is validated but registry membership is not. Raw unknown notes can remain uninterpreted; an operator must not claim that review resolved their meaning.
- **Company prerequisites:** Q01–Q10 remain pending for real interpretation, mapping, evaluation and pilot use. No company answer is needed to implement F02 in isolated storage.
- **Commit/push:** intended code/tests/fixtures/docs form one increment on `main`; read Git history/remote for its final hash and delivery status. Unrelated PROJECT_SUMMARY.md and SYSTEM_DESIGN.md are preserved.
- **Next smallest ready task:** F02: add three workshop models and one additive Alembic migration; implement draft persistence/version checks and verify both fresh/previous-head upgrade on a disposable PostgreSQL database. Then F03–F06 complete the manual workflow. Do not mark the application usable based on schema tests alone.


### 11 October 2026 — F02, local draft persistence and migration

- **Status:** VERIFIED for draft storage/API and schema migration. F03 is next; no complete workshop UI/review/output workflow exists yet.
- **Behaviour:** create and reopen incomplete drafts; replace a whole draft with an expected version; stale/concurrent writes fail with 409 instead of overwriting. Validate source existence/origin; keep origin immutable and jobs distinct. Persist literal Unicode/null/Decimal-string values. SQL failures rollback and return sanitised errors.
- **Files/schema/routes/config:** three workshop models in `app/db/models.py`; additive `alembic/versions/20261011_workshop_drafts.py`, head `20261011_workshop` after `20261009_complete`; Alembic env accepts an explicit connection for isolated tests. New `app/services/workshop.py` and `app/api/v1/workshop.py`; two F02 schema classes added. Main registers three operations under `/api/v1/workshop/jobs`; Settings/`.env.example` add default-false `WORKSHOP_ENABLED`. Existing dependencies/session/error handling reused. README/build status/master updated.
- **Tests:** new `tests/unit/test_workshop_api.py` (9 cases) and `tests/integration/test_workshop_postgres.py` (6 cases); original automotive routing test now checks the seven original paths explicitly while allowing workshop additions. Initial collection used a pytest-reserved parameter name, fixed before checks passed; full-suite route-count assumption also corrected and retested. Final full run: 133 passed, no skips, 100 warnings, with actual disposable PostgreSQL.
- **DB evidence:** fresh migration and upgrade from previous head with a retained vehicle; metadata comparison and CLI Alembic check show alignment. New-session persistence, timezone-aware DB timestamps, simultaneous saves, transaction rollback, revision uniqueness and job FK enforced. Failed transaction leaves no partial draft/revision changes. Constraint fixtures are not reviewed company records.
- **Live/manual evidence:** normal migration on the task DB; synthetic draft create/update/stale rejection over local HTTP; stop/restart app and reopen identical record/version/timestamps; OpenAPI methods checked. No provider calls or company-data processing. Task-owned app and PostgreSQL processes stopped; local test artifacts ignored.
- **Limits:** no attach/preview route, source-file storage, UI, confirmation writer, enforced snapshot immutability, CSV/search/extraction or access-control implementation. The feature flag is a local-demo gate, not authentication; keep it disabled on shared/public hosts until F12. PATCH is full replacement and advances version on every successful save. No business accuracy/usefulness result.
- **Company questions:** Q01–Q10 remain pending; no company answer is needed for the next synthetic/local F03 increment.
- **Commit/push:** implementation, tests, configuration and master updates form one intended `main` increment; check Git history/remote for the final delivery hash. Preserve unrelated PROJECT_SUMMARY.md/SYSTEM_DESIGN.md; private visit/runtime files excluded.
- **Next smallest ready task:** F03 bounded JPEG/PNG attach/preview, decoded-content checks, opaque IDs, private storage and duplicate-byte warning/reuse. Then F04–F06 deliver the manual workflow before optional AI.


### 11 October 2026 — F03, safe source attach/preview

- **Status:** VERIFIED for upload/private storage/preview/duplicate reuse. Next: F04 browser manual review.
- **Files/routes/config:** root Pillow dependency; Settings storage path; shared workshop schema/service/router; narrowly scoped upload-body middleware and main registration. Added `tests/unit/test_workshop_documents.py` (15 cases) and one PostgreSQL duplicate-race case. No new migration/table. Master/build status/README updated together.
- **Verification:** targeted source + workshop PG checks: 22 passed/16 warnings. Final full suite with explicit local PostgreSQL URL: 149 passed/101 warnings/no skips. Live local HTTP: 201 upload, 200 byte-identical preview, duplicate UUID reuse, chunked over-limit 413. Corrupt, empty, mismatched, animated, over-size/dimension/pixel, unsafe filename/path, missing/corrupt stored source, storage/DB failure and disabled-route checks passed. Shared request-ID/routing checks passed.
- **Failure resolved:** raising a receive-time exception through the multipart/error stack produced 400; bounded buffering/replay now returns 413 before parsing. An initial live probe ran before server startup and was retried against the same confirmed process after startup; final checks passed.
- **Origin/manual checks:** only the authored PNG and generated JPEG/GIF/APNG fixtures; original company sources remain private/unchanged. Source previews do not rewrite/rotate originals. No provider call.
- **Environment:** shared `.venv` pip check reported unrelated audio/telemetry dependency conflicts. A clean root-requirements-only environment at ignored `runtime/workshop-api-venv/` installed successfully, passed pip check and 76 workshop cases (20 warnings); do not call the shared environment dependency-consistent. Docker execution remains unavailable/unverified.
- **Limits/prerequisites:** no browser UI/confirmation/export yet. No authenticated source access; local gated demo only. Crash-orphan and semantic-duplicate limits are documented above. Q01–Q10 remain pending for real mapping/labels/pilot, not for F04.
- **Commit/push:** intended feature/code/tests/docs increment on main; consult Git history for hash. Unrelated user files excluded.
- **Next:** F04 manual form/source viewer/save/reopen, then F05 confirmation/history and F06 demo CSV.


### 11 October 2026 — F04, manual source/draft screen

- **Status:** VERIFIED for manual draft entry/save/reopen; F05 confirmation/history next.
- **Files/routes:** `app/templates/workshop.html`, `app/static/workshop.js`, `app/static/workshop.css`; gated `/workshop` HTMLResponse and root UI link; escaped API-prefix metadata follows the configured namespace. HTML placement deliberately differs from the original proposed static path to prevent a gate bypass. Existing APIs/session/error contracts reused; no dependency or migration change.
- **Behaviour:** source beside draft, view-only zoom/rotation, origin/stage/provenance, main references/items and collapsible optional dates/vehicle/notes/totals. Explicit per-field/item states, retained raw/cancelled values, decimal text/null, save/reopen/bookmark, dirty indicators and validation/stale/server failure retention. Value edits invalidate old confirmation; destructive draft UI actions ask before discarding. Busy requests disable controls to avoid overwriting concurrent unsaved typing.
- **Verification:** page/assets/disabled/static-bypass check passed; full suite 150 passed/no skips/101 warnings with PostgreSQL. `node --check` passed. Isolated Chrome/Playwright scenario passed after correcting review-state accessible names. Browser checks cover attachment, invalid amount retained, money/Unicode save/reload, keyboard focus, view transforms with original-byte comparison, 409/503 retention, mobile no-horizontal-overflow and literal rendering of HTML-like server text. Desktop/mobile screenshot artifacts visually inspected. Native browser tool timeout was bypassed using a separate test browser; no existing user browser session was controlled.
- **Origin:** fictional PNG/generated records only; screenshots/private runtime ignored. No company-source/provider processing or staff feedback claimed.
- **Limits:** self-reported local demo; no confirmation writer, review history/export/AI/authentication yet. Browser checks are Chrome/desktop+390px, not all browsers, real phones, assistive technologies or workshop usability. The page supplies its escaped configured API prefix; the client does not hard-code v1.
- **Company questions:** pending Q01–Q10 recorded; no answer blocks F05/F06 development.
- **Commit/push:** intended code/browser/route tests and documentation increment; read Git history for delivery hash. User's unrelated files preserved.
- **Next:** F05 atomic confirmation/history/correction UI and concurrency/idempotence checks; F06 deterministic demo CSV afterward.


### 11 October 2026 — F05, reviewed snapshots and corrections

- **Status:** VERIFIED; F06 demo CSV next.
- **Files/routes:** schemas/service/router, revision model plus additive `20261011_review_guard`, manual HTML/JS/CSS, `tests/unit/test_workshop_review.py`, PostgreSQL tests and browser harness. POST confirm and GET bounded revision history; no new runtime dependency/config.
- **Behaviour:** explicit acknowledgement/reviewer/version, locked fresh persisted draft, reviewed-contract/source integrity checks, server UTC time and repeat-confirm identity. Source FK/backfill prevents deleting a reviewed source after draft detachment. PostgreSQL rejects reviewed-row UPDATE/DELETE. Read-only paginated history includes original sources/literal/cancelled rows; corrections create newer drafts and require rereview. Known successful saves are distinguished from failed history reads.
- **Verification:** final whole suite **167 passed/no skips/115 warnings** with PostgreSQL; clean API-only environment **94 passed/34 warnings**. Actual concurrent confirmations, stale cached ORM state, correction history, mutation guard, source FK and old-schema source backfill checked. Normal Alembic head/check aligned. Isolated Chrome flow passed acknowledgement, unresolved-field rejection, version 2 → corrected version 4 history preservation and repeat confirmation; reviewed-history screenshot inspected. Original 18 source hashes unchanged/ignored; intended diff whitespace checked.
- **Failure resolved:** migration preservation test initially called current ORM against a pre-column schema. It now inserts through reflected historical table shape and verifies actual source backfill plus unchanged snapshot/reviewer/time; final rerun passed.
- **Limits:** demo-only reviewer self-report and no authentication, CSV/lookup/AI or company semantic evaluation yet. PG trigger is not enforced by SQLite and does not resist a privileged schema administrator. No tax/total inference, accounting write or stage promotion. Company questions Q01–Q10 remain pending without blocking F06.
- **Commit/push:** intended implementation/tests/master/build/readme increment on main; read Git history for hash. Unrelated `PROJECT_SUMMARY.md`/`SYSTEM_DESIGN.md` preserved.
- **Next:** F06 deterministic demo CSV from a specific reviewed revision, private reproducible output identity/checksum, formula-safe cells and per-version downloads; complete manual milestone using fictional sources.
