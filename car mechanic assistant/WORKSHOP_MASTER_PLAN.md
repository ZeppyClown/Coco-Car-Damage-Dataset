# Workshop job-sheet project — master plan and implementation ledger

**Last updated:** 12 October 2026. **Current phase:** standalone local capture/review/history/lookup/record export and F13 SGD invoicing/GST delivered; local saving/corrections/access/recovery and billing verified. Usefulness and removal of old financial/GST software are user assumptions. Business-benefit studies/external integrations are optional. F13 invoice/GST workflow is verified locally; real issuance is disabled pending Q11 supplier configuration/operation. Real-source permission/quality/meanings/labels and actual company pilot operation remain unverified. See [actual artifacts and fresh verification](WORKSHOP_VERIFICATION_REPORT.md).

This is the authoritative implementation/handoff document for the workshop administrative project. Every contributor, including Codex and Claude, must update it for **every feature or implementation part**, including partial work, fixes, migrations, tests, configuration and changed decisions. Do not rely on chat history to resume the work.

The first product is a small local application that turns a permitted paper sheet or manual entry into a reviewed job record and a reusable output. AI may draft fields; staff confirm their meaning. A confirmed record is not automatically a completed repair, final invoice, paid transaction or imported accounting entry.

## 1. Start here: the actual next task

**Separate manual-assistant integration, 12 October:** B2.5–B2.7 opt-in offline multilingual PDF OCR/quarantine and the C2 retrieval experiment harness are delivered on `mechanic-integration`; see [BUILD_STATUS.md](BUILD_STATUS.md) and section 16 for actual checks. These are separate from the workshop job-sheet feature ledger. No F-row or company-question status changes and no READY workshop row: workshop work still waits on Q01/Q02, Q06–Q09 and Q11. Remaining buildable manual-assistant work is the applicable work still listed as pending in BUILD_STATUS, subject to its evidence/processing prerequisites; no real retrieval result is supplied.

**Next billing input:** Q11 exact supplier name/address/GST number and InvoiceNow date; user confirmed GST registration and GST-inclusive pricing. Start with the [invoicing guide](WORKSHOP_INVOICING_GUIDE.md) and actual fictional invoice artifacts in [the verification report](WORKSHOP_VERIFICATION_REPORT.md). F13 is implemented and locally verified; normal real issuance remains off.

**Next real-data/operation work depends on technical inputs:** Q01/Q02 meanings/stage, Q06/Q07/Q09 operator/processing/access/operation and independent labels from Q08. Q03/Q04/Q10 external destination mapping is optional under the standalone scope below. F07 has a successful live **printed fictional** Gemini image→unsaved proposed draft→source-checked manual review→demo CSV API smoke. The separate assistant's ignored key was supplied only to an explicitly configured temporary process; workshop credentials are not loaded automatically. Normal demo AI is off, private-source AI blocked and real handwriting accuracy unverified. Job-sheet capture/review is selected; public-reference RAG remains separate research.

**User decision, 12 October:** assume the project is useful to its customer/workshop users. Do not require interviews proving demand, baseline timings, adoption or removed-copying measurements before continuing implementation. Those studies are optional and needed only for actual benefit/outcome claims. This assumption does not establish what a source means, which destination columns exist, extraction accuracy or operating permission. Keep technical correctness and company compatibility checks.

**Further user decision, 12 October:** assume the old financial/GST software is gone. Target a standalone workshop record system; matching the old import format is not a prerequisite. External integration F09 is deferred unless selected later. User requested GST/invoicing on 12 October; F13 is implemented as a separate locally verified billing module, with real issuance off pending company settings. The CSV remains a record/demo export, not a tax invoice. Saving, corrections, access and local recovery are freshly verified: [actual record/export and verification report](WORKSHOP_VERIFICATION_REPORT.md),initial217 tests passed; final F13 full326 passed/no skips plus live HTTP/Chrome billing checks.

Use the [workshop validation worksheet](WORKSHOP_VALIDATION_WORKSHEET.md) for source meaning/independent labels and selected real-data operation. External destination and timing sections are optional. The earlier workbook also covers separate manual-RAG research. No company answer or measured result is prefilled.

Do not start by scanning an archive, training a model, building a vector database or integrating the accounting system. None is required to demonstrate the core review workflow.

The first working milestone is:

> Open a fictional job sheet → enter a draft beside its image → correct an ambiguous value → confirm the record → download a clearly labelled demonstration CSV → reopen the same record and see what was confirmed.

This milestone is a local demonstration. It does not claim company deployment, real handwriting accuracy, accounting integration or reduced staff time.

### First actions for the next implementer

1. Read this file, root `AGENTS.md`, root `CLAUDE.md`, [BUILD_STATUS.md](BUILD_STATUS.md) and [the repository README](../README.md).
2. Run `git status --short` and identify unrelated user work. On 11 October, `PROJECT_SUMMARY.md` is modified and `SYSTEM_DESIGN.md` is untracked; preserve both unless the user explicitly includes them in the task.
3. Read the existing schema/session/router/test fixtures listed in section 5. Confirm actual paths before adding code.
4. Check whether the private visit files exist locally. Their absence does not block a synthetic/manual prototype. Do not obtain company files from public search as replacements for actual evidence.
5. Mark the next branch whose company prerequisite is supplied `IN_PROGRESS` and state its exact scope. Printed-fictional F07 integration is verified; repeated smoke calls are not a substitute for missing company evidence.
6. Choose a branch whose technical prerequisite is available. Real F07/F08/F11 need permitted samples/reviewer labels; real F12 operation needs owner/access/host/retention decisions. F09 is deferred unless an external integration is selected; do not require the old software's schema for this standalone app. Baseline timing, demand/adoption and old-format compatibility are not coding gates. No guessed rules or public/live deployment.
7. Update the ledger, verification table, next task and work log **before** committing. Commit only the intended files, then push as previously authorised by the user.

## 2. Business problem and scope

The reviewed visit material supports investigating repeated transcription of workshop job information. A useful product must make the record clearer and/or remove an existing copying step. If it produces an additional record but staff still retype every destination, it may increase work.

The scope is standalone job-sheet capture/review, reviewed history, lookup and record export, usable without an AI key. External mapping is optional if later selected. F13 adds standalone invoicing/GST as explicitly requested on 12 October; general accounting remains outside scope. Measuring task time/usefulness is optional and not a coding prerequisite.

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
| Optional external invoice/software/spreadsheet chain | No | Would specify a later selected integration | Not required for standalone record export |
| Independent expected extraction values | No | Would support accuracy evaluation | Correct interpretation of ambiguous notes/marks |
| User's usefulness decision | Assumed by user, 12 October | Continue without business-benefit validation | Actual time savings/adoption remain unmeasured |
| Pilot operator and owner | No | Would establish operating responsibility | Who will use/support and approve the selected pilot |
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
- Optional external export/integration: target schema/rules needed only if selected; current standalone record export verified.
- Automated imports/ledger changes: separate integration scope and operating authority needed.
- Optional staff time-saving/adoption claims: actual task baseline and observations needed; not required to continue building.
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

F01–F06 schema/test/fixture/router/service/UI/export paths below now exist. Extraction remains proposed. If existing code offers a smaller correct arrangement, change the list and explain the decision in this master file before continuing.

| Path | Purpose | First feature |
|---|---|---|
| `app/schemas/workshop.py` | F01 validation, F02 draft responses, F05 confirmation/revisions and F06 generated-export response | F01/F02 |
| `app/services/workshop.py` | Draft/source checks, image storage, reviewed history and F06 deterministic CSV/private output identity | F02/F05/F06 |
| `app/api/v1/workshop.py` | Draft/source/review/history/demo-export routes with default-disabled demo gate | F02/F03 |
| `app/templates/workshop.html` | F04 gated source/draft review page outside static mount; no HTML bypass when disabled | F04 |
| `app/static/workshop.js` | Page actions and accessible feedback | F04 |
| `app/static/workshop.css` | Necessary page styles; reuse existing styles where practical | F04 |
| `app/services/workshop_extraction.py` | One optional image-to-draft integration, added only when justified | F07 |
| `tests/unit/test_workshop.py` | Draft/review/export/identity failure checks | F01 onward |
| `tests/integration/test_workshop_postgres.py` | Real migrations, concurrent draft/review/export transactions, rollback and revision/source constraints | F02/F05/F06 |
| `tests/fixtures/workshop/` | Clearly labelled fictional inputs and expected records | F01 |
| `app/schemas/workshop_invoice.py`, `app/services/workshop_invoice.py` | Invoice request/calculation/immutable issue/read/print contract | F13 |
| `alembic/versions/20261012_workshop_invoices.py` | Add invoice table/immutable PG guard after actual prior head | F13 |
| `tests/unit/test_workshop_invoice.py` | Money/API/real-config/access/failure/idempotence tests | F13 |

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

F06 added **WorkshopExport**: reviewed-revision FK, mapping version, checksum/output key and generation time; only successful generated files get a row. Use a unique export identity for the same reviewed revision and mapping. This records file generation, not external delivery/import. Do not implement payment, customer-master, supplier, claim or accounting tables in this scope.

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

The [router](../app/api/v1/workshop.py) uses the shared `get_db` session and [service](../app/services/workshop.py), gated by `WORKSHOP_ENABLED=false` by default. Disabled routes return404. F12 now additionally requires configured account/origin authentication; the flag alone cannot open the workshop. See the operating guide for setup.

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

`POST /api/v1/workshop/jobs/{id}/confirm` requires strict positive `expected_version`, a nonblank `reviewer` compatibility field and strict `acknowledged: true`; client timestamps/extra properties are rejected. The authenticated API replaces that compatibility field with the verified account name. It locks and refreshes the persisted job, rejects stale versions with409, validates the full reviewed contract and verifies an attached source's hash/availability. It writes one snapshot with a server UTC timestamp. Repeat confirmation returns the original snapshot/reviewer/time/identity kind, including legacy reviews. Confirmation does not increment the draft version or convert a quote to completed work.

`GET /jobs/{id}/revisions` returns newest-first snapshots with default 20, maximum 100 and nonnegative offset. The UI shows read-only records, literal/cancelled rows and original-source links, with older-history pagination. Edits invalidate interpreted confirmation state, require saving a new draft version and then rereview; previous records remain unchanged. Failed validation/confirmation keeps the draft; a history read failure after a successful save is reported separately from the known save result.

Additive revision `20261011_review_guard` follows `20261011_workshop`: source FK/backfill plus a PostgreSQL trigger rejecting snapshot UPDATE/DELETE. This source link prevents deleting the source row even after a newer draft detaches it. SQLite unit tests do not provide that DB trigger guarantee; actual PostgreSQL integration verifies it. A privileged DB administrator can change schema/disable triggers. F12 distinguishes new authenticated account attribution from legacy self-reported names; it cannot retroactively authenticate them. No production audit/adoption claim follows from these controls.

### Implemented F06 demo output contract

The single fixed mapping is **`workshop-demo-v1`**, not company-compatible. `POST /api/v1/workshop/revisions/{id}/exports` accepts an existing reviewed revision ID and returns its successful output identity, revision ID, mapping version, SHA-256, byte size, UTC generation time and `status: generated`. A draft ID cannot create output. `GET /exports/{id}/download` serves verified bytes as a CSV attachment with no-store/nosniff. All workshop gates apply.

Additive `20261011_exports` follows `20261011_review_guard` and adds `workshop_exports`: UUID, revision FK, mapping version, checksum, opaque unique storage key, positive byte size and generation time. Unique `(revision_id, mapping_version)` plus a PostgreSQL revision lock prevents duplicate concurrent outputs. Only successful files get committed rows: no external delivery/import status is invented. Repeats return the same identity/time/bytes; a changed mapping must get a new mapping version. Missing/corrupt outputs fail rather than silently rewrite historical output evidence.

The CSV is UTF-8 with BOM and CRLF records, using Python `csv`; comma/quote/newline/Unicode values round-trip. Columns in order: `mapping_version`, `output_kind`, `job_id`, `revision_id`, `revision`, `data_origin`, `record_stage`, `job_reference`, `customer_reference`, `vehicle_reference`, `make`, `model`, `currency`, `line_number`, `cancelled`, `description`, `amount`, `description_raw`, `amount_raw`, `diagram_notes`, `diagram_notes_raw`, `written_total`, `written_adjustment`, `written_grand_total`, `date_note_raw`, `quotation_date`, `date_in`, `date_out`, `reviewer`, `reviewed_at`, `source_document_id`, `manual_provenance`.

Every row includes `output_kind: DEMO_ONLY`. Snapshot-level fields repeat per line. Active lines contain reviewed descriptions/optional amounts; missing values are empty and zero is `0.00`. Cancelled rows remain explicitly marked with literal description/amount text and empty interpreted values, so unreviewed cancelled meanings never become active work. No line sum, tax or inferred total. Formula-like prefixes `= + - @` (including fullwidth equivalents after whitespace) and leading tab/CR/LF get an apostrophe prefix. This also makes signed negative amounts textual in the demo CSV; it is a deliberate demonstration safety rule, not an approved financial import conversion. Canonical snapshot values remain unchanged.

Outputs use opaque filenames in existing private storage, mode0600; write/fsync before DB commit and cleanup on handled file/DB failure. A process crash can still orphan a file and F12 must reconcile/backup storage. A generated row means file generation succeeded, never that staff downloaded/imported/accepted it. The UI downloads each reviewed version from history without saving/confirming the mutable draft or changing its stage.

### Implemented F07 optional proposal boundary (printed fictional live smoke verified)

`POST /api/v1/workshop/documents/{id}/extract` requires strict `send_to_gemini: true`. It reads one registered, checksum-verified source. The source must be declared `synthetic_demo`; `private_source` returns403 before the call and no configuration flag bypasses unresolved Q07. Origin is an operator declaration, not image-content recognition. `WORKSHOP_AI_ENABLED` defaults false; missing `GOOGLE_API_KEY` or explicit nonblank `WORKSHOP_AI_MODEL` returns503. There is no default model or automatic network request. Existing Gemini key/SDK is reused; root requirements now pin `google-genai==2.29.0` like the separate assistant.

One SDK client per request closes in a context manager. GenerateContent receives inline image bytes, a system prompt and JSON schema derived from the F01 serialization contract. Only extractable properties are requested; stage, origins, source IDs, provenance, field states and diagram interpretation remain application/operator decisions. No tools are configured. The prompt treats written instructions as untrusted data, preserves literal/CJK/crossed-out text, keeps uncertainty null and forbids guessed currency, repairs/totals/tax. A60-second timeout, one attempt and8000-token output bound avoid automatic repeated processing. Current official sources checked11October: [SDK JSON schema/inline image support](https://github.com/googleapis/python-genai), [structured output constraints](https://ai.google.dev/gemini-api/docs/generate-content/structured-output), [image input](https://ai.google.dev/gemini-api/docs/image-understanding) and [tested Gemini3.1 Flash-Lite capabilities](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite). Actual provider/schema acceptance is now verified for the printed fictional smoke below; this does not establish real handwriting/semantic accuracy or acceptance for every model/shape.

Explicit `str | None` return types make serialized money schemas accurately describe string/null output without nonstandard decimal constraint keys. Input money validation and actual JSON/CSV bytes remain unchanged. The provider copy omits nested `items.maxItems=50`: the tested Gemini model rejected that grammar with400 while the identical item schema without that cap succeeded. **The application still accepts at most50 items** and rejects51 before saving; response character/token/time bounds remain. This adapts the provider's decoding constraints without weakening the shared draft validator or lowering the supported local row limit. The complete original schema with only this cap omitted passed the live API flow.

Response JSON is bounded 100000 characters and validated using the same `WorkshopDraft`. Reserved/unrecognised top properties, invalid items/money/lengths and bad JSON fail502 without saved data. Supplied scalar values become proposed; item interpretations become proposed regardless of model confirmation claims. Literal ambiguous items with null interpretations become unclear. Stage stays unknown, diagram meaning stays null. Valid structured output may still hallucinate a reference/value; proposed status and required human review are safeguards, not semantic detection. Provider errors return generic502/504 without raw message/keys; no automatic retry.

The route writes no job/revision/export. It returns an unsaved draft with `ai_provenance` (Google Gemini, configured model, `workshop-extract-v1`, server UTC proposal time and initial source UUID). This optional JSON metadata survives manual edits/save/reopen/review; it is local provenance, not signed/authenticated evidence. Demo CSV v1 is unchanged and does not add model columns. UI requires an attached image, explicit external-processing acknowledgement and a new empty unsaved draft (including missing review states); it refuses to replace entered/saved values. The operator corrects fields, chooses stage and resolves states before ordinary confirmation/export. Manual entry works without AI configuration.

### Implemented F10 lookup boundary

`GET /api/v1/workshop/jobs` returns `results`, `limit`, `offset` and `has_more`. Results are the **latest reviewed snapshot per distinct job UUID**, chosen before filtering. Jobs with only drafts are excluded; older revisions remain in history rather than duplicated in search. Each result includes reviewed snapshot identity/source/stage, current `draft_version` and `has_unreviewed_changes`. Draft values never replace reviewed result values.

Parameters: optional `q`, `job_id`, literal substring `customer`, `vehicle`, `reference`, exact `stage`, inclusive UTC review-date `reviewed_from`/`reviewed_to`, default20/max100 `limit`, nonnegative `offset`. Text bounds200 characters; reversed/invalid dates rejected. Keyword checks reference/vehicle/diagram/date-note values and individual item description/literal/amount-text values. Raw/unknown/cancelled text may match, but remains visibly raw/unknown/cancelled when opened; search does not establish its meaning. SQLAlchemy bound parameters and automatic LIKE escaping preserve literal percent/underscore/backslash. PostgreSQL `json_array_elements` and SQLite test `json_each` search item values, excluding JSON property names. Stable order uses review time descending then job UUID; offset pages can move if a new review occurs between requests.

UI under **Find reviewed records** shows unknown identifiers, reviewed version/stage, newer-unreviewed-draft notice, original-source and open-job/history controls. Same customer/vehicle text never merges records. Failed search labels retained previous results and keeps their pagination query. Keyword search is bounded but scans JSON values; no index/RAG/performance claim over an actual archive. PostgreSQL remains the supported runtime; SQLite is unit-test persistence. No schema/dependency/config change.

### Implemented F11 field comparison (real evaluation pending)

[`scripts/evaluate_workshop.py`](../scripts/evaluate_workshop.py), separate authored label/mock-prediction JSONL fixtures and [WORKSHOP_EVALUATION_GUIDE.md](WORKSHOP_EVALUATION_GUIDE.md) provide a no-network comparison. Run `python -m scripts.evaluate_workshop --labels PATH --predictions PATH --prediction-kind mocked|live_model|manual`. Aggregate JSON goes to stdout; no job/file/model write. Unknown/cancelled values never enter resolved-value accuracy, failed cases/missing rows are not credited as abstention, extra/missing rows and critical identity/amount/description/cancellation errors are visible. Empty literals are absent. Decimal strings use canonical two places; Unicode/raw whitespace comparisons remain exact.

Labels/predictions must cover the same unique opaque IDs. Labels carry nonblank labeler/source explanation, origin-matching label-source declaration and resolved or explicitly uncertain interpretations (no proposed gold labels). An explicit failure can stand in for a response, but scheduled cases cannot disappear. Inputs use the shared draft validation; invalid/empty/unmatched/unresolved-only inputs fail with no report. Origin groups never pool synthetic/private cases; `is_company_outcome:false` and unverified label provenance are explicit. No per-case identifiers/values are echoed. Excluded metadata/stage/states and row-order alignment are documented, not silently scored. Actual reviewer independence and authority need evidence outside the file.

Public cases are authored **contract fixtures**, not handwriting/image ground truth or real provider output. The deliberately imperfect mock set includes3 cases, one timeout,22 resolved comparison values (identity5, amount2, description3, date0, literal8, cancellation4),3 proposed values where labels say unknown and2 cancelled interpretations excluded. These counts verify the evaluator, not AI quality. The guide specifies independent company labels/held-out data and complete existing/manual/AI workflow timing, including remaining copying/clarification/rework. No company label set, live model metric or business baseline exists yet.

### Implemented F08 manual annotation boundary (real meanings pending)

Raw diagram/shorthand text is stored/displayed literally; no panel recognition, screen-coordinate left/right conversion or inferred repair operation exists. The AI proposal route cannot supply `diagram_notes`. Manual clarified meaning uses the explicit diagram review state; **new confirmation** additionally requires nonblank `manual_provenance` stating clarification context. The UI asks who clarified meaning, what was established and vehicle convention when relevant. Text presence cannot prove that explanation is correct or enforce a real panel vocabulary; Q01 remains unresolved.

An area-only mark without an active interpreted item cannot confirm as work. Cancelled rows retain raw text but unreviewed interpretations stay out of active CSV values. Reviewer identity/time and clarified/raw/context text survive history/output while the quote stays a quote. Older snapshots lacking context remain readable/exportable and get an explicit history notice; the stronger new-confirmation rule does not rewrite or invalidate immutable historical records. Repeat confirmation of an already-reviewed version still returns its original snapshot. Add context to a new draft/review to supersede it.

### Implemented F12 local operation/recovery evidence (pilot pending)

[WORKSHOP_OPERATING_GUIDE.md](WORKSHOP_OPERATING_GUIDE.md) documents API-only installation, explicit isolated DB migration, localhost startup, manual/AI review/correction/lookup/demo output, errors, tests and operating prerequisites. `test_disposable_dump_restore_recovers_history_sources_outputs_and_guards` performs actual custom-format `pg_dump`/`pg_restore` in a self-created random schema of a permitted local `yap_test` database. It copies the fictional source/two CSVs to backup/fresh restore storage and checks draft/history/time/identity, byte integrity, repeat export identity, migration/model alignment, restored immutability trigger and reviewed-source FK. A DB-only restore correctly fails source availability until files are restored. Only its own schemas are renamed/dropped; the public app/company schema is never restored over.

The drill needs PostgreSQL client tools and its explicit disposable URL; absent tools/URL skip, not pass. Credentials pass in subprocess environment rather than command arguments; dumps/private fixtures use private temporary paths. Pytest may retain fictional temporary files under its normal policy. The fixture has no concurrent writers; this is not evidence of a consistent backup during arbitrary production writes or cross-host/offsite/encrypted recovery. Startup/migration/code versions and actual host test are documented. The drill itself adds no authentication; the configured-account prototype is documented separately below. Production backup scheduling, retention/deletion/orphan reconciliation and deployment remain unimplemented. Q06/Q07/Q09 must select the actual operating path; broad CORS and the feature flag alone are not identity/access controls.

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

### Implemented F12 configured-account prototype (company policy pending)

[WorkshopAccessMiddleware](../app/core/workshop_auth.py) protects `/workshop` and the entire workshop API namespace, including source previews, proposals and CSV downloads, before the upload-limit/multipart parser. It requires one configured printable ASCII operator identifier, a salted hash and exact canonical origin. The native HTTP Basic401 challenge is supported; enabled invalid/missing configuration fails closed503. Configured non-loopback origins require HTTPS. Origin/host mismatches and browser cross-site/same-site requests fail403, even with credentials. No Origin header is required for ordinary authenticated CLI calls. Every protected response uses `Cache-Control: no-store`. Static JS/CSS have no records and remain public; the page is outside the static mount. Existing automotive endpoints are outside this boundary.

The standard-library hash uses scrypt N=16384/r=8/p=5, a random16-byte salt,32-byte digest and constant-time username/digest comparison; bounded input and fixed parameters prevent a malformed configured hash choosing arbitrary work. This parameter tuple is listed by the official [OWASP password-storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html); browser authentication follows [FastAPI HTTP Basic](https://fastapi.tiangolo.com/advanced/security/http-basic-auth/). [scripts/workshop_password.py](../scripts/workshop_password.py) reads a16+ character password twice with hidden terminal input and prints only its salted hash. Password/hash/config/test credentials must remain private/ignored. See [the operating guide](WORKSHOP_OPERATING_GUIDE.md) for repeatable setup and known limits.

New API confirmation binds the reviewer to middleware-verified account state; the existing nonblank `reviewer` request field remains a compatibility field and cannot impersonate another account. The UI account is read-only and history distinguishes identity kind. Additive migration `20261011_auth` follows `20261011_exports`, adds nonnull `reviewer_identity` with a two-value check and `self_reported` default for existing snapshots. It does not UPDATE historical immutable rows. New API snapshots carry `authenticated`; direct service/test callers default to `self_reported`. Existing DTOs remain loadable. Reconfirmation returns original attribution, including an old self-reported review. CSV v1 does not add identity-kind columns, preserving old output checksums/identities; inspect API/history for that distinction.

This is a single configured account with access to all workshop records. Account ownership, real user/role policy, TLS/proxy/rate limiting, credential custody/revocation, retention/deletion/reconciliation and actual pilot remain company-dependent. Basic credentials are cached by the browser; use a dedicated context and close it, or rotate the hash/restart to revoke. No session/logout/user-management system or production/load claim was added. Fictional account verification does not authenticate a company employee or historical internship use. Actual verification results belong in section13 and the latest work log.

## 7. Implementation ledger — update every row as work happens

Allowed statuses: `READY`, `IN_PROGRESS`, `IMPLEMENTED_UNVERIFIED`, `VERIFIED`, `WAITING_COMPANY`, `DEFERRED`. Dependencies can leave a READY item not yet executable. A feature is VERIFIED only when its acceptance checks have actually run. Describe scope rather than claiming production readiness.

| ID | Part | Status now | Dependencies | Evidence / next action |
|---|---|---|---|---|
| F00 | Master plan, handoff, private-source boundary and validation worksheet | VERIFIED | None | Documentation/link/exclusion checks; 12 October worksheet covers 24 contract fields/all stages, 27 local links resolve and blank private copy is 0600/ignored; no company answers or new app feature |
| F01 | Draft/review contract and fictional fixtures | VERIFIED | F00 | Four record/review schemas, five fictional JSON cases and one printed demo PNG; 45 targeted checks passed |
| F02 | Workshop storage, models and migration | VERIFIED | F01 | Three tables, migration 20261011_workshop and create/read/replace routes; 133 total tests passed with real PostgreSQL; live app restart preserved draft |
| F03 | Safe image attach/preview and duplicate warning | VERIFIED | F02 | 16 new cases plus live upload/preview/duplicate/chunked-limit checks; full suite 149 passed |
| F04 | Manual source/draft review screen | VERIFIED | F01–F03 | Gated page/ordinary JS/CSS; Chrome browser flow and failure retention passed; Python suite 150 passed |
| F05 | Confirmation, immutable revisions and conflict handling | VERIFIED | F02/F04 | Atomic/idempotent confirmation, bounded read-only history, corrections, source FK and PG mutation guard; F12 binds new API reviews to its account and preserves legacy attribution |
| F06 | Reproducible demonstration CSV output | VERIFIED | F05 | Fixed demo mapping, private output identity/checksum, concurrent reuse and browser per-version download/reopen passed |
| F07 | Optional AI image-to-draft extraction | IMPLEMENTED_UNVERIFIED for company quality | F03–F06 | Mock boundary and real printed-fictional Gemini3.1 Flash-Lite source→proposal→manual review→CSV flow verified; handwriting/independent semantic accuracy and private-source use remain pending Q07/Q08 |
| F08 | Reviewed diagram/shorthand interpretation | IMPLEMENTED_UNVERIFIED | F04/F07 | Manual clarification/context/raw/cancelled/history/output checks verified; actual company meanings/vocabulary pending Q01 |
| F09 | Optional external destination mapping/integration | DEFERRED | F06; explicit integration scope | Old software assumed gone; standalone record export exists in F06; target schema needed only if integration selected |
| F10 | Basic lookup of confirmed records | VERIFIED | F05 | Latest reviewed per job, literal bounded filters/pagination/newer-draft status; SQLite/PG and Chrome checks passed |
| F11 | Extraction evaluation; optional benefit measurement | IMPLEMENTED_UNVERIFIED for real accuracy | F06/F07; F09 for destination checks | Synthetic evaluator/CLI verified; independent labels/provider quality pending Q08; baseline timing/adoption optional, usefulness assumed |
| F12 | Workshop access/recovery/guide and later pilot | VERIFIED locally; company pilot pending | User-assumed usefulness; selected operating scope | Initial217/final full326-test suites plus live HTTP/Chrome verify access, saving/corrections, invoice output and actual disposable recovery; company operation/retention/pilot pending Q06/Q07/Q09 |
| F13 | Standalone SGD invoicing/GST | VERIFIED locally; real operation pending | F05/F12; explicitly selected12October | Money/API33 passed; PG18 passed including invoice concurrency/recovery; full326 passed; Chrome preview/issue/reopen/print/PDF/access passed; user GST-registered/inclusive answer recorded; Q11 supplier/InvoiceNow pending |

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

**Delivered:** VERIFIED on 11 October 2026. Mapping/CSV failure tests, actual PG concurrent reuse/migration and browser per-version download/checksum/reopen passed. M1 is complete as a local fictional demonstration; the full company project is not complete.

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

**Current status:** DEFERRED under the user's12October standalone decision. Matching the assumed-removed software is not required. The specification below applies only if an external integration is later selected; F06 record export exists now. F13 supplies the separate standalone invoicing/GST feature; general accounting is outside scope.

**Purpose:** replace an existing entry step rather than add another.

**Prerequisites:** one permitted/redacted source-to-final-record chain; destination software/spreadsheet columns and import capabilities; reviewer-approved mapping and correction process. Missing prerequisites do not block F01–F08.

**Implementation:** choose exactly one supported output. Document each source field, required destination value, conversion/unknown handling and record stage. Use deterministic mapping; tax/account fields require approved rules rather than model judgment. Do not silently convert a quote into a final transaction.

**Checks:** reviewer confirms expected output for representative examples; destination accepts a permitted test file if available; incompatible/missing required fields block output; mapping version recorded; repeated generation and corrected-version handling understood. A live financial write requires an explicit later task; a test CSV is not an imported transaction.

**Completion:** call it company-compatible only after those checks. Demonstrating an actually removed copying step is optional under the user's usefulness assumption; only claim that outcome if observed.

### F10 — confirmed-record lookup

**Purpose:** retrieve reliable captured jobs without an archive-scanning project.

**Implementation:** bounded job/reference/date/stage filters and keyword search over confirmed records. Show source/revision and distinguish draft results if draft search is separately requested. No automatic merging by customer name. Defer embeddings/RAG until an observed query requires more than structured lookup.

**Checks:** same-name customers remain separate; one vehicle can have multiple jobs; missing identifiers stay visible; draft data is not shown as confirmed; pagination/limits work; corrected record links to version history; untrusted search text cannot execute SQL/HTML.

**Completion:** an operator can find and reopen the intended fictional reviewed job. This does not prove fast lookup over the actual storeroom archive.

**Delivered:** VERIFIED on11October2026: latest-only/literal filters, same-name separation, UTC dates, pagination and browser search→newer-draft/open/history checked. No archive-speed or staff-acceptance result.

### F11 — extraction correctness and optional benefit measurement

**Purpose:** establish extraction correctness. Usefulness is assumed by the user; measuring business benefit is optional.

**Implementation now:** a small evaluation script or existing-test extension reading fictional/privately labelled examples. Report sample/field counts and missing/unclear cases. Keep expected labels independent of the model output. Store real results privately and public synthetic outputs clearly labelled.

**Real accuracy check later:** company reviewer independently labels permitted examples; reserve held-out cases and retain incorrect/missing values and provider failures. This requires labels and the selected processing path, not a time-saving baseline.

**Optional benefit study:** compare current copying, direct digital entry and AI draft/review. Time the whole routine: photograph, wait, review, clarify, output, remaining entry and corrections. Record how many entry destinations genuinely stopped requiring manual copying. Skip this study while building unless the user requests measured benefit claims.

**Checks:** evaluator rejects missing labels/empty sample; denominators and skipped fields visible; cancelled/unknown values not counted as correctly invented; critical identity/amount/description errors reported separately; synthetic tests excluded from company accuracy/adoption statistics.

**Completion:** a reproducible development report first; real extraction-quality evidence needs independent permitted labels. Benefit/adoption studies are outside required build completion under the user's assumption. Actual outcome claims still need observations. Document dates, method, sample limits and human-reviewed residual errors. Document-capture field accuracy is not retrieval precision.

### F12 — permitted pilot operation

**Purpose:** support an actual operator in the selected operating environment. Usefulness is assumed; no benefit study is required before this work.

**Prerequisites:** named operator/owner, permitted host/storage/provider path, data retention/access decisions and selected scope. Local demo completion does not imply these approvals.

**Implementation when selected:** real authentication and identity on the workshop routes, protected source/export access, appropriate origin/CSRF handling, nonpublic storage, backup/restore and a short operating guide. Existing broad CORS and placeholder security settings are not a production boundary. Protect page, API, previews and downloads; do not assume hiding the page protects the endpoints.

**Checks:** unauthorised source/export reads and writes fail; no static bypass; forged origin/session requests are handled appropriately; sensitive values not logged; backup restores reviewed records and corresponding source/output references; deleting records follows the agreed scope without orphaned private files.

**Completion:** record exactly what environment/access was tested and who approved actual use. Do not infer 24 users, six months' adoption or production deployment from a local trial.

**Delivered local parts:** configured single-account access/origin checks and server-bound attribution, private source/output handling, fictional dump/restore and operating guide are verified. The actual company account policy/hosting/retention/deletion/reconciliation/pilot decisions remain pending; the prototype does not supply approval.

### F13 — standalone SGD invoicing and GST

**Selected:** explicitly requested12October2026. User confirmed GST-registered and prices include GST; exact supplier name/address/GST number and InvoiceNow applicability/date remain Q11. Defaults reflect inclusive pricing; they do not invent company billing identity or prove registration. See [full workflow/rules/questions](WORKSHOP_INVOICING_GUIDE.md).

**Implemented:** separate `InvoiceRequest`/supplier/customer/calculated preview/issued response schemas; money uses the existing strict Decimal boundary. A current reviewed completed-work version, SGD, confirmed prices and full supplier/customer details are required. Sum active line totals, exclude cancelled rows and subtract an explicit discount in the selected price basis. Registered inclusive: GST=round(B×9/109); exclusive: GST=round(B×0.09). Fixed invoice-subtotal rounding uses half-up cents. Non-registered means GST not applicable, distinct from zero-rated. Reject oversized totals/excessive discounts/unknown prices/quotes; issuance uses today's Singapore date. Source written totals/adjustments remain observations and do not silently change billing.

**Persistence/config:** additive `20261012_invoices` after `20261011_auth`; `workshop_invoices` stores job/revision, unique invoice number, immutable calculated/request JSON, exact HTML/SHA-256 and authenticated issuer/server UTC time. Job row lock plus unique job ID allows one invoice per job, with exact-request retries reusing identity/time/bytes and different requests/corrections conflicting409. PG trigger rejects invoice UPDATE/DELETE. Database dump recovers invoice HTML; private source/CSV files still need file backup. No old CSV/review bytes or migration rewritten. Invoice numbers use INV-/DEMO-INV- plus UUID. Settings: `WORKSHOP_REAL_INVOICES_ENABLED=false` and optional validated JSON `WORKSHOP_BILLING_SUPPLIER`; real supplier must match configured profile, missing/disabled configuration fails closed. Synthetic jobs always produce DEMO labels.

**Routes:** protected `GET /billing-settings`; `POST /revisions/{id}/invoice-preview` (no write), `POST /revisions/{id}/invoice` (`invoice` request plus strict true acknowledgement), `GET /jobs/{id}/invoice`, `GET /invoices/{id}`, `GET /invoices/{id}/print`. UI invoice form in completed-work history, preview invalidation, explicit acknowledgement, unsaved-billing retention, immutable invoice reopen and browser Print/Save as PDF. Printable text escaped; no scripts; restrictive CSP/no-store/nosniff and existing account/origin boundary. Exact issued HTML is read rather than regenerated. Responses canonicalise UTC across issue/read/retry/restore.

**Verified locally:**33 money/API tests;18 PG cases including new invoice races/prior-auth-head preservation/immutable guard and extended actual dump/restore;326 full regression tests/no skips; fresh Chrome invoice flow and actual PDF/HTML/reopen/access. The clean fictional artifact has net100.00/GST9.00/payable109.00 inclusive. See [actual artifacts/results](WORKSHOP_VERIFICATION_REPORT.md). Real profile JSON parsing/missing GST number rejection/default-off settings checked; normal demo remains AI-off/real-billing-off/supplier-unset.

**Limits/next:** credit notes/void/replacement billing, payment receipts/receivables, input tax/GST returns/general ledger/InvoiceNow transmission are outside this increment. Issued errors cannot be fixed by editing or duplicate billing; add linked credit notes before those cases. No company deployment, legal certification or representative real-document outcome. Configure Q11 only after actual details/operating decisions arrive; optional external mapping/benefit studies are not gates.

## 9. Build order and checkpoints

| Milestone | Deliverable | Ready now? | Decision after demonstration |
|---|---|---|---|
| M1: manual vertical slice | F01–F06; fictional source → review → version → demo CSV | Yes, with isolated development environment | Is the review UI understandable and the record lifecycle correct? |
| M2: AI drafting | F07 plus manual F08 | Mock and printed-fictional live integration verified; company processing/quality conditional | Are proposed values correct and uncertainty/review preserved? |
| M3: standalone reuse | F06 record export plus F10 lookup; optional F09 later | Current fictional record/CSV/lookup verified; external integration deferred | Does the output match the reviewed record and preserve correction history? |
| M4: independent accuracy check | Real correctness portion of F11 | Needs permitted cases and independent labels; no timing baseline | Which critical errors/failures remain on representative held-out cases? |
| M5: permitted workshop pilot | F12 and agreed scope | Needs operating decisions | Is actual use authorised and supportable? |

There is no honest fixed completion date for company-dependent milestones. Code estimates should be revised after M1; provider/integration/approval delays are not coding effort.

User-assumed usefulness is sufficient to proceed with implementation. Optional timing/adoption studies may later inform product decisions, but do not block coding or replace the correctness checks above.

## 10. Configuration, dependencies and operating boundaries

The manual milestone requires no search, marketplace or AI credentials. Provider failures must not prevent manual entry/review. Inspect existing settings loading before adding new environment handling.

**Implemented settings:** `WORKSHOP_ENABLED=false` plus `WORKSHOP_AUTH_USERNAME`, secret `WORKSHOP_AUTH_PASSWORD_HASH` and `WORKSHOP_ORIGIN`. Enabled workshop requests fail closed503 until the account/hash/origin is valid; unauthenticated requests401 and cross-origin requests403. Enabling does not install tables. Run Alembic explicitly against the intended isolated DB first; startup does not call `create_all` or migrate. See [the operating guide](WORKSHOP_OPERATING_GUIDE.md) for the interactive password-hash helper, private environment setup, exact-origin browser login and single-account limitations. Keep disabled on any existing shared/public host.

### Manual screen and browser verification

Open `/workshop` at the configured origin after local startup and native HTTP Basic login. After saving, check the read-only account, explicitly acknowledge checked values and confirm. Unresolved interpretations block review; optional missing values remain unknown. Expand a reviewed version in history to download its demo CSV. For corrections, edit/save, resolve proposed values and confirm again; earlier CSV/revision stays unchanged.

 Attach the fictional PNG from `tests/fixtures/workshop/`, enter a job reference/stage and items, choose states deliberately and save. Copy the generated job ID, reopen it or revisit the resulting `?job=` URL. Existing records cannot change origin. Manual drafts need no model key.

All edited interpreted values become proposed again; raw notes remain literal. Enter decimal text without binary float conversion. Missing values remain null. Save errors/conflicts keep current controls and dirty status. Unsaved navigation/new/open/remove actions require an explicit discard choice; no saved job or stored source is deleted by those UI actions. Source rotation/zoom are view-only. Dynamic content uses text/value APIs, not HTML insertion.

Python route/asset gate test: `tests/unit/test_workshop_page.py`. Repeatable browser scenario: [tests/browser/workshop.cjs](../tests/browser/workshop.cjs). It creates fictional records on the supplied **isolated local** demo server. Verified with Playwright 1.64.0 and installed headless Chrome, an isolated browser context (no user's browser profile). Setup/run:

```sh
npm install --prefix 'car mechanic assistant/runtime/workshop-browser-tests' playwright@1.64.0
node tests/browser/workshop.cjs 'car mechanic assistant/runtime/workshop-browser-tests/node_modules/playwright' http://127.0.0.1:8000 'PATH_TO_PRIVATE_FICTIONAL_CREDENTIAL_JSON'
```

Node/Chrome are test tools, not application dependencies. The library supports the installed Chrome channel and file-input actions; see official [browser](https://playwright.dev/docs/browsers) and [input](https://playwright.dev/docs/input) documentation. Desktop/mobile screenshots stay ignored under runtime. Native computer-use access timed out without a state result, so it was not counted as a successful visual check. Playwright-rendered screenshots were inspected locally instead.

### Run the current draft/source API

From the repository root, use the existing Python environment and a separately provisioned local development PostgreSQL database. Set the actual connection through your private environment/config; do not copy a company database URL into this example.

```sh
export DATABASE_URL='postgresql://YOUR_LOCAL_ROLE@127.0.0.1:5432/yap_test_workshop'
export WORKSHOP_ENABLED=true
export WORKSHOP_AUTH_USERNAME='fictional-local-operator'
export WORKSHOP_ORIGIN='http://127.0.0.1:8000'
export USE_GOOGLE_CSE=false
export USE_EBAY_API=false
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m scripts.workshop_password
# Store its hash in WORKSHOP_AUTH_PASSWORD_HASH in an ignored private env file.
.venv/bin/python -m uvicorn app.main:app --env-file 'PATH_TO_PRIVATE_ENV_FILE' --host 127.0.0.1 --port 8000
```

The role/database placeholder must be replaced with an existing isolated local target. `/docs` describes the draft/source operations; `/workshop` opens the manual screen. The root automotive UI also links to it. In a second terminal, this sends the authored fixture only:

```python
import json
from pathlib import Path
import httpx
from getpass import getpass

record = json.loads(Path("tests/fixtures/workshop/examples.json").read_text())["examples"][0]["record"]
with httpx.Client(base_url="http://127.0.0.1:8000", auth=("fictional-local-operator", getpass("Local operator password: "))) as client:
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
curl -f --user fictional-local-operator -F data_origin=synthetic_demo -F file=@tests/fixtures/workshop/synthetic-sheet.png http://127.0.0.1:8000/api/v1/workshop/documents
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

| 11 October 2026 | F06 mapping/output/PG regression | Explicit local PG URL + `.venv/bin/python -m pytest -q --disable-warnings` | **184 passed, no skips, 117 warnings** | 17 new F06 cases; fixture correctness, not actual accounting compatibility |
| 11 October 2026 | F06 clean environment/migration/browser | API-only workshop pytest; CLI upgrade/check; isolated Chrome harness | **111 passed, 36 warnings**; head20261011_exports aligned; manual vertical slice including CSV checksum/repeat/old-vs-new/reopen passed | Local fictional data; Chrome only; no company import/provider/pilot |

| 11 October 2026 | F07 regression and clean environment | Explicit local PG URL + full pytest; API-only workshop pytest/pip check | **208 passed/no skips/119 warnings**; clean **135 passed/38 warnings**, no broken requirements | 24 mock extraction cases; no live Gemini call/model-schema acceptance or accuracy measurement |
| 11 October 2026 | F07 mocked browser workflow | Isolated Chrome harness, browser-only intercepted proposal response | External-processing ack, proposed states, edited-draft refusal, correction/review/CSV and provenance reopen passed | API provider/validation separately mocked in unit tests; browser mock is not extraction quality evidence |

| 11 October 2026 | F10 lookup regression | Explicit local PG URL + full pytest; clean API workshop pytest | **227 passed/no skips/127 warnings**; clean **154 passed/46 warnings** | 19 added cases; JSON value/literal escaping/latest snapshot checks run on SQLite and PG14.20 |
| 11 October 2026 | F10 browser lookup/open/error state | Isolated Chrome harness | Reviewed search, unknown refs, newer-draft notice, open/history and labelled previous results on503 passed | First browser assertion ran before history loaded; explicit async wait fixed; no archive performance/operator trial |

| 11 October 2026 | F11 comparison/CLI regression | Targeted evaluator pytest; explicit PG full suite; clean API workshop tests | **17 targeted passed/7 warnings;244 full passed/no skips/127 warnings;171 clean passed/46 warnings** |3 authored contract cases and deliberately bad mock predictions; no live AI/business measurement |
| 11 October 2026 | F11 CLI fixture report | `python -m scripts.evaluate_workshop ... --prediction-kind mocked` |3 cases/22 resolved values; one timeout;3 unknown-value candidates;2 cancelled fields excluded; exact expected error counts checked | Does not validate handwriting, reviewer authority, retrieval precision or actual company outcomes |

| 11 October 2026 | F08 manual annotation regression | Targeted schema/review/diagram checks, PG whole suite, clean API workshop suite | **248 passed/no skips/127 warnings**; clean **175 passed/46 warnings** |4 new area/context/cancelled/provenance/legacy cases; fictional semantics only |
| 11 October 2026 | F08 browser confirmation boundary | Full isolated Chrome harness + missing diagram context, correction/save/rereview | Passed; input retained on422, explicit context allows new review | Does not verify actual workshop conventions or authorised repair meanings |

| 11 October 2026 | F12 actual disposable recovery/full regression | Local PG URL + pg_dump/pg_restore fixture test/full pytest/clean workshop suite | Targeted1 passed/9 warnings; **249 full passed/no skips/129 warnings;176 clean passed/48 warnings** |14 workshop PG cases run; same local server/temporary namespace/private fictional file restore only |
| 11 October 2026 | Final source/privacy/config check | Original SHA256/ignore check, root Settings presence flags, explicit Git scope/whitespace |18 originals unchanged/ignored; root Gemini key absent and workshop model absent; no real source/provider/deployment call | No secret values printed; live smoke and company decisions remain pending |
| 11 October 2026 | F12 account/origin/attribution regression | Explicit PG URL + full pytest; clean API workshop pytest; CLI Alembic upgrade/check and pip check | **284 full passed/no skips/132 warnings;211 clean passed/no skips/51 warnings**;35 added checks;15 workshop PG cases run; schema aligned/requirements clean | Fictional account/records; generic failure no-store/secret logging, pre-parser rejection and old review/CSV migration checked; no company policy/load/TLS/pilot evidence |
| 11 October 2026 | F12 authenticated browser/live restart | Isolated Chrome harness with private fictional credential path; restarted loopback HTTP checks | Full manual/review/correction/history/CSV/mocked AI/diagram/lookup flow passed; anonymous page/upload401; account readonly; authenticated200/no-store, cross-origin403, static-bypass404 | No live provider; credentials/config0600 and ignored;18 originals unchanged/ignored; latest generic-error change additionally verified in Python |
| 11 October 2026 | F07 provider schema/local invariants | Targeted schema/extraction pytest; explicit PG URL + full pytest and clean API workshop pytest | **75 targeted passed/9 warnings;290 full passed/no skips/132 warnings;217 clean passed/no skips/51 warnings** |6 added cases: four accurate money-output schema types and50 accepted/51 rejected proposed rows; no local validator/CSV/migration change |
| 11 October 2026 | F07 actual printed-fictional live flow | Authenticated temporary localhost API with explicit existing assistant key/model; live SDK2.29.0, `gemini-3.1-flash-lite`; actual source-preview bytes/counted tables/review/export/reopen | **Passed** at2026-10-11T10:14:47UTC; extraction3.871s;4 printed headers and description/25.10 matched; no automatic save/confirmation; version2 quote/account/provenance/repeat CSV checksum passed | One authored printed page, no handwriting/held-out/company benchmark. Provider error diagnostics were explicit calls on that same PNG, never automatic retries |
| 11 October 2026 | Live-created record UI reopen | Fresh authenticated Chrome context, no intercepted model response or additional generation | Source image, quote/25.10, readonly account, reviewed history and real initial model provenance displayed; no page errors | Actual generation occurred through API; UI reopen is not a second model/accuracy experiment. Private screenshot/report/config stay ignored |

Replace vague “tests pass” with the command, counts, skipped checks and test environment. PostgreSQL integration is skipped without its explicit disposable test URL; do not present a skipped test as passed.

### 12 October — fresh software verification

| Check | Actual result | Scope |
|---|---|---|
| Clean API workshop suite, explicit PG14.20 URL |217 passed/no skips/51 warnings in146.30s |All15 workshop PG cases, actual DB/file restore, migrations/concurrency/guards |
| Live local HTTP persistence/corrections/export/access |Passed |New fictional manual correction25.10→30.10, stale409, preserved originals/repeat IDs, anonymous/wrong-password401/cross-origin403/static404/no-store |
| Stored record/CSV and Chrome reopen |Passed |Actual earlier fictional quote/version2/25.10/source/history; original CSV checksum matches; screenshot/JSON/CSV published as fictional examples |

Exact artifacts/command/limits are in [WORKSHOP_VERIFICATION_REPORT.md](WORKSHOP_VERIFICATION_REPORT.md). No company accuracy, tax/accounting, remote hosting or adoption result inferred.

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
| Q03 | Optional source→external invoice/software/spreadsheet chain | Selected future F09 only | Deferred under standalone scope |
| Q04 | Optional destination columns/import format and mapping | Selected future F09 only | Deferred under standalone scope |
| Q05 | Usefulness/demand; optional observation of which entry step disappears | No coding blocker; measured benefit claims only | Assumed by user, 12 October; actual benefit unmeasured |
| Q06 | Real user/reviewer and pilot decision owner | Real F11/F12 | Pending |
| Q07 | Permitted source storage and selected external-provider processing | Real F07/F12 | Pending |
| Q08 | Independently checked expected values; optional baseline task time | Real accuracy; optional benefit claims | Labels pending; baseline optional |
| Q09 | Access/retention/backup/hosting decisions | F12 | Pending |
| Q10 | Correction handling in selected external destination | Selected future F09 only | External handling deferred; local correction/history verified |
| Q11 | Exact invoice supplier name/address/GST number and InvoiceNow applicability/date | Real F13 billing configuration/operation | User confirmed GST-registered and inclusive prices; identity/number/date pending; real issuance off |

Record a question as resolved only when there is an actual answer. An elapsed wait, a synthetic sample or a plausible inference is not an answer. Continue ready tasks while these are pending.

The [validation worksheet](WORKSHOP_VALIDATION_WORKSHEET.md) provides the fill-in evidence tables for these questions. Completed answers and attachments remain private; returning a checked mapping or reviewed label set can unlock that branch before every other question is answered.

## 15. Current handoff snapshot

- **Separate manual assistant, 12 October integration:** optional checksum-verified offline OCR with page quarantine and a reviewed C2 retrieval experiment harness now exist. Fictional real-engine OCR and deterministic/mocked retrieval checks are recorded below; real-manual quality, independent results and company approval remain pending. This increment is on `mechanic-integration`, with no push or merge into main. Workshop F-rows/questions remain unchanged and no workshop READY row exists; next workshop work needs Q01/Q02, Q06–Q09 or Q11 inputs. Remaining independently buildable manual-assistant items are those still pending in BUILD_STATUS.

- **Branch/repository:** `main`, remote `origin` is the user's existing GitHub repository. Verify actual remote before pushing on a different machine.
- **Latest committed delivery before F13:** `5a38891`, actual record/export and fresh persistence/access/recovery results, pushed to main. F13 code/tests/docs/artifacts are the current increment; read `git log` for its resulting commit ID.
- **What exists:** existing automotive API/RAG and the separate workshop source/draft/review/history/correction/demo-output/lookup workflow, configured account, optional AI, evaluator, guide/recovery and F13 SGD invoice/GST preview/issue/read/print workflow.
- **Latest implementation:** F13 SGD invoice/GST schemas/service/migration/UI/print output, fixed subtotal Decimal rounding, immutable invoice snapshots, job-level duplicate protection and canonical UTC responses. Final326 passed/no skips/137 warnings in136.34s, all18 workshop PG cases; fresh Chrome invoice/old-flow checks and restarted invoice JSON/HTML/PDF verified. Prior F07 live printed-fictional integration remains separate evidence; no new provider call.
- **What does not exist:** real handwriting/independently labelled benchmark, company account/pilot operating policy, production backup/reconciliation/retention or permitted company deployment. External mapping/general accounting remain future scope. F13 SGD invoicing/GST is implemented and verified locally; credit notes/payments/GST returns/InvoiceNow submission are not implemented. Real issuance remains disabled pending Q11 supplier configuration and actual operation.
- **Latest provider integration:** F07 original schema failed400/endpoint502 without DB writes. Explicit string/null money serialization and provider-only omission of nested maxItems50 retain all local validators. Full printed-fictional live API proposal→source-checked quote review→repeatable CSV/provenance passed on `gemini-3.1-flash-lite`. Final tests/browser/privacy results appear in the newest work-log/result entries.
- **Next conditional work:** Q11 billing supplier and InvoiceNow date; Q01/Q02 meanings/stage; Q06/Q07/Q09 actual operator/provider/access/operation; Q08 independent labels. External mapping Q03/Q04/Q10 is deferred under standalone scope. Saving, corrections, access and local recovery are freshly verified developer checks, not waiting for company validation. Baseline timing/usefulness and old-format compatibility are not required.
- **Usefulness decision:** assumed by user on 12 October. Demand, baseline timing, adoption and removed-copying studies are optional; do not treat them as implementation blockers. Q08 independent labels and the destination/operating rules remain technical inputs.
- **Independent work delivered:** source handling, manual review/version/export, account/origin controls, optional extraction, manual clarification, lookup, evaluator/guide/recovery and F13 deterministic billing/immutable output. New company data/rules/identity/approval must not be fabricated to extend these.
- **Unrelated changes to preserve:** root `PROJECT_SUMMARY.md` and `SYSTEM_DESIGN.md` as seen on this machine; verify current status rather than assuming it remains identical.
- **Open decisions:** Q11 supplier billing identity/number and InvoiceNow date, model-processing path, operator and expected labels. External mapping is optional. None should be fabricated.

### Completion audit and the minimum company handoff

The 11 October completion audit checked the F00–F12 acceptance requirements, M1–M5 milestones, current extraction code/tests, saved live-fictional report and private visit/workbook answer sections. The private workflow-plan correction table and focused image questions are still unanswered; the workbook still lists the missing record chain, mapping, operator and processing decisions. No company-labelled JSONL set or destination CSV/spreadsheet was found in `company visit/`. **The local prototype is delivered; the full company project is incomplete.** That11October audit preceded the new12October F13 request. F13 independent implementation is now delivered; company billing configuration/InvoiceNow applicability and actual operation remain input-dependent.

Bring back these specific artifacts rather than another general interview. Keep the completed answers and records private; section 14 remains the question ledger.

| Remaining work | Minimum input to return | What the next implementer can then do | Evidence needed before completion |
|---|---|---|---|
| F08: actual meanings/stage (Q01/Q02) | A reviewer explains one permitted sheet, each raw note/amount/cancellation/diagram mark and whether it is a quote, approved work or completed work; unresolved values remain unknown | Save independently reviewed expected values and any approved vocabulary without guessing from the photograph | Reviewer checks that captured meaning and stage match that source |
| Optional F09: external destination correctness (Q03/Q04/Q10) | Only if a specific integration is later selected: target schema/conversions/correction procedure | Implement a versioned mapping for that selected destination | Not a current standalone-build requirement; record/CSV match verified |
| Real F07/F11/M4: extraction correctness (Q01/Q02/Q07/Q08) | Permitted processing/storage path and representative source cases with independently checked labels and reviewer explanations | Select the approved extraction path, retain failures and compare held-out values | Recorded sample/denominator/error/failure results; a fictional smoke or developer correction is insufficient; no baseline time required |
| Real F12/M5: workshop operation (Q06/Q07/Q09) | Decision owner and intended users/host; agreed access, provider, retention/deletion, backup and support rules; actual pilot decision | Implement only the selected operational gaps and verify them on the agreed host before any separately authorised deployment | Access and recovery checks in that environment plus actual operating approval; the current single-account local drill is insufficient |

Existing verification remains **290 full tests and 217 clean API tests passed**, plus the recorded live printed-fictional flow/browser reopen. Those are prior implementation results, not new company evidence or a new test run. This documentation-only audit does not change code, models, fixtures, configuration, CSV mapping or runtime. Résumé adoption, retrieval-precision, corpus-size and internship-history claims remain unverified separately.

### Copyable Claude handoff prompt

```text
Continue the workshop job-sheet project in this repository. Read AGENTS.md,
CLAUDE.md and car mechanic assistant/WORKSHOP_MASTER_PLAN.md first.
Treat the master plan as the current implementation ledger. Inspect Git status
and preserve unrelated user work. F01–F06 manual milestone is verified. Start
the next branch whose prerequisite is supplied: real F08/F11 labels/quality or selected F12 access/operation.
Old financial/GST software is assumed gone: target standalone records/export; F09 external mapping is deferred. User requested GST/invoicing on 12 October; F13 is implemented as a separate locally verified billing module, with real issuance off pending company settings.
Usefulness is assumed by the user; baseline timing, demand/adoption and removed-copying studies are optional and must not block coding.
Local account/origin/attribution and guide/recovery are verified. Manual F08 actual meanings remain pending Q01. F11 synthetic
harness/F10 lookup are verified. F07 mock and printed-fictional live API integration
passed after a provider-schema fix; real quality/use remains unverified and private-source AI blocked. Use synthetic examples until
real-data prerequisites are met. Keep company visit files and runtime artifacts
private. After every implementation part, update the master with actual files,
behaviour, tests, limitations and next task; commit the intended changes and
push as authorised. Do not claim planned features or synthetic results as
company deployment/evidence. Continue independent work while company questions
remain recorded and unanswered.
```

## 16. Work log

### 12 October 2026 — separate manual assistant OCR and C2 integration

- **Contributor/scope:** `kobold-bieresel/mechanic-integration`, branch `mechanic-integration`, based on OCR commit `574e0f4`. Merged `mechanic-experiments` (`312dc6e`) with `--no-ff`, merge commit `a175b325d4a368897587b8832f2f92c31e94fe4f`. No rebase, push or main merge. These are separate manual-assistant capabilities; workshop F-rows, company questions and their statuses are unchanged, with no READY workshop row.
- **OCR delivered (B2.5–B2.7):** existing `DocumentProcessor` opt-in page OCR through checksum-verified RapidOCR 3.10.0/PP-OCRv6 small/ONNX Runtime/PDFium. Text pages keep pypdf extraction; image-only pages use local OCR. Physical page/method/engine/confidence/threshold provenance is retained. Low-confidence/unreadable pages keep review text/reason in the manifest, produce no chunks/embeddings and are excluded from accepted page counts. Missing models/dependencies and execution/render-limit failures reject explicitly. Defaults: `OCR_ENABLED=false`, `OCR_MODEL_DIR` unset, `OCR_MIN_CONFIDENCE=0.90`; no runtime fetch, translation or technical-number rewriting.
- **OCR reaches:** `src/document_processor.py`, `src/ocr.py`, `src/config.py`, tracked environment example/pinned assistant requirements, `tests/unit/test_manual_ocr.py`, eight authored fictional raster PDFs/generator and retained `handoff/mechanic-ocr.md`. Local model download followed that handoff into ignored `.context/ocr-models/`; all three pinned SHA-256 checks passed (31,749,509 bytes). Python 3.12.5 worker environment was created with `python3 -m venv .venv-worker` and `.venv-worker/bin/python -m pip install -r 'car mechanic assistant/requirements.txt' -r requirements-dev.txt`; `pip check` reports no broken requirements.
- **C2 delivered:** `src/retrieval_experiments.py`, CLI, fictional corpus/labels under `tests/fixtures/retrieval_experiments/`, expanded `tests/unit/test_retrieval_experiments.py` and retained `handoff/mechanic-experiments.md`. Six actual chunk settings (800/1200/1600 × 10%/20%) and five behaviorally distinct retrieval stages use isolated temporary Chroma indexes and the existing evaluator. Records contain corpus/label hashes, chunk/stage/model/implementation identity, latency, query ranks/components, failures and bootstrap intervals. Every stage sorts deterministically; final dedup suppresses whitespace-identical text, not arbitrary overlapping passages. No new route/schema/migration/serving release or dependency from integration fixes.
- **Failure-first runner fixes:** mixed/missing/unknown origin declarations can no longer inherit the first row; every row must declare one consistent origin and canonical split. Split casing/aliases share one allowance; unknown/renamed splits, corrupt ledgers and reasonless overrides fail clearly. Custom ledger paths must remain in caller output; symlink output artifacts, corpus/index release destinations and unignored repository output paths are rejected. Configured Gemini embeddings were already injectable in Python; the CLI now explicitly selects them with `--embeddings configured`, while default offline records/summaries name the deterministic implementation truthfully, including stable identity under module execution. Hash failures no longer escape/leak a preallocated directory; Chroma clients close before removal, and close/cleanup errors mark the configuration failed. Source-stem relevant IDs no longer truncate after five chunks.
- **Regression evidence:** initial failure-first runner run: **24 failed, 14 passed, 7 warnings in 15.27s**; corrected run: **38 passed, 7 warnings in 13.44s**. Later module-CLI identity reproduction: **1 failed, 38 deselected**, then **1 passed, 38 deselected** after the fix. Controlled candidates prove each ladder step changes ranks; a long fictional source proves each declared size/overlap; injected configuration/hash/cleanup errors remain failed records; success/failure paths remove temporary indexes and preserve the fictional serving sentinel. The Python `GeminiEmbeddings` path uses a mocked client, with actual document/query task settings asserted; no live provider inference.
- **Initial suite results:** from `.context/`, `PYTHONPATH=.. PYTHON_DOTENV_DISABLED=1 OCR_TEST_MODEL_DIR=ocr-models ../.venv-worker/bin/python -m pytest -q ../tests/unit/test_manual_assistant.py ../tests/unit/test_rag_audit.py ../tests/unit/test_manual_ocr.py ../tests/unit/test_retrieval_experiments.py` — **102 passed, no skips/failures, 7 warnings in 93.00s**. All seven model-dependent OCR cases ran. First full scratch-directory run, `env -u YAP_TEST_POSTGRES_URL PYTHONPATH=.. PYTHON_DOTENV_DISABLED=1 OCR_TEST_MODEL_DIR=ocr-models ../.venv-worker/bin/python -m pytest -q ../tests` — **377 passed, 19 skipped, 1 failed, 98 warnings in 247.24s**. Existing `test_storage_failure_and_static_directory_rejected` assumes root-relative `app/static/private`; from scratch it points elsewhere. No production guard change was needed. Root and assistant dotenv files are absent (existence checked only); final reruns use repository root with dotenv disabled and PostgreSQL explicitly unset.
- **Final combined suite (repository root):** `PYTHON_DOTENV_DISABLED=1 OCR_TEST_MODEL_DIR=.context/ocr-models .venv-worker/bin/python -m pytest -q tests/unit/test_manual_assistant.py tests/unit/test_rag_audit.py tests/unit/test_manual_ocr.py tests/unit/test_retrieval_experiments.py` — **103 passed, no skips/failures, 7 warnings in 201.69s**. Includes 33 OCR cases (all seven model-dependent cases ran), 39 runner cases and 31 existing assistant cases. Timing overlaps the separate full regression and is not an OCR throughput measurement.
- **Final full repository suite (repository root):** `env -u YAP_TEST_POSTGRES_URL PYTHON_DOTENV_DISABLED=1 OCR_TEST_MODEL_DIR=.context/ocr-models .venv-worker/bin/python -m pytest -q tests` — **379 passed, 19 skipped, 0 failed, 98 warnings in 331.40s**. All 19 PostgreSQL cases skipped because no test URL was supplied (18 workshop cases, one search case); no database was started. The existing root-relative static-storage test passes from the intended root directory. Final implementation has no unresolved failing checks in this test scope; PostgreSQL/browser/container/live-provider and real-company checks were not run.
- **Actual offline CLI:** `PYTHONPATH='car mechanic assistant' PYTHON_DOTENV_DISABLED=1 .venv-worker/bin/python -m src.retrieval_experiments --corpus tests/fixtures/retrieval_experiments/synthetic_kb --labels tests/fixtures/retrieval_experiments/synthetic_dev_labels.jsonl --output-dir .context/integration-experiments-final` — **11 evaluated, 0 failed**, all records and summary assert `synthetic` and `src.retrieval_experiments.DeterministicTestEmbeddings`. Generated outputs/models/logs remain ignored; neither handoff file is removed. During failure-first checks, task-created fictional output files and the empty hash-failure temp directory were removed; no tracked source/release was overwritten.
- **Limits/prerequisites:** OCR checks cover fictional EN/Simplified ZH/Traditional ZH/JA scans, identifiers/units/numbers, mixed/unreadable quarantine, rotation and a small layout; no real-manual accuracy, calibrated confidence, complex table semantics, handwriting, mechanic use or company approval. The local held-out ledger is single-process and can be reset/moved; self-declared origins/splits do not authenticate independence. It records allowed runs/overrides, not refused attempts, and does not enforce selecting one frozen configuration before held-out use. Complete config/index/manifest hashes, alternative-model comparisons, coverage/recall study and independent real results remain pending. Source-stem fixtures treat every matching source chunk as relevant and may conflate duplicate stems; real studies need passage-level adjudication. Cleanup is attempted on ordinary exceptions; OS cleanup failure is visible, and process termination is outside that guarantee.
- **Git/next task:** intended code/tests/master/build/run/resume/handoff updates commit together with explicit paths only. No PostgreSQL/company database started or touched; tests use isolated in-memory storage. No company/runtime/env/key records or existing serving indexes/feedback read, no live inference, system install, public deployment or push. Pre-existing app `.gitignore` modification is unchanged and excluded. Workshop work still waits on Q01/Q02, Q06–Q09 and Q11; remaining buildable manual-assistant work is the applicable pending work in BUILD_STATUS, without fabricating sources/labels/approval or measured results.
- **Final audit:** 80 local documentation links resolve; exact F/Q rows match the pre-integration master, app `.gitignore` matches its original uncommitted addition, and worker environment/models/generated outputs are ignored. Intended public files contain no API-key/private-key patterns; Git whitespace checks and dependency consistency pass. Commit only the nine intended changed paths; retain `.gitignore` as the sole unrelated modification. No push is requested or performed.

### 12 October 2026 — actual record/export shown; fresh software checks and standalone scope

- User requested the captured record/export and direct saving/corrections/access/recovery verification, and assumes old financial/GST software gone. Target is standalone records/history/export; external mapping F09 deferred. Invoicing/GST/accounting is conditional, with no tax rules/outcomes assumed.
- Read live existing fictional reviewed job/source and downloaded original CSV; verified source bytes, quote/version2/four headers/description/25.10/authenticated attribution, repeat identity and SHA256. Added public fictional JSON/CSV/Chrome screenshot and `WORKSHOP_VERIFICATION_REPORT.md` for direct inspection.
- Live local HTTP check: new fictional manual case saved/reopened; amount25.10→30.10 in new version; stale save/confirm409; original review/CSV unchanged; new authenticated review and repeated output identity correct; fresh-client reopen persisted correction. Anonymous page/job/source/CSV401, wrong password401, cross-origin write403/static bypass404 and no-store passed. Run IDs/report stay ignored/private.
- Fresh Chrome reopened actual earlier stored source/quote/25.10/history, readonly account/no page errors. Screenshot visually inspected. No new model call or company-source processing.
- Fresh clean API suite with explicit local PostgreSQL14.20: **217 passed, no skips,51 warnings in146.30s**. All15 PG cases ran, including actual `pg_dump`/`pg_restore` plus fictional source/output recovery. DB-only restore correctly lacked bytes; full restore preserved records/history/identities/checksums/schema/guards. Scope is local/quiescent, not production/offsite/concurrent-write recovery.
- Delivery checks: exported snapshot passes shared schema;32-column CSV/revision/source/checksum match;63 local links resolve;18 original company hashes unchanged; actual password/hash/provider key absent from intended public files. Screenshot inspected. Updated only unchanged blank private worksheet, mode0600/ignored retained; no filled answers overwritten. Explicit staged-scope/whitespace checks pass.
- Staging exposed Git CRLF→LF normalisation of the exact CSV artifact. Added an exact-path `.gitattributes` rule (`-text`, CR-at-EOL whitespace handling), restaged and checked indexed bytes/checksum equal the downloaded original; no other file's text handling changed.
- Update companions with standalone scope and verified software behavior. No application code/schema/config change. Keep unrelated root docs, company sources and credentials private; commit/push intended documentation and authored-fictional showcase only.

### 12 October 2026 — usefulness assumed; technical checks retained

- User instructed us to assume usefulness to the customer. This changes the build requirements: demand interviews, workflow baselines, time-saving/adoption studies and proof of removed copying are optional, not implementation/completion gates. It does not supply measured outcomes.
- Updated current scope, F11/F12 dependencies, M2–M4 checkpoints, Q05/Q08 and the handoff table/prompt. Independent source meanings/labels, actual destination schema/correction rules and the selected processing/operating path remain technical prerequisites. Do not infer those from the usefulness assumption.
- Updated the evaluation guide, validation worksheet, operating guide and README consistently; preserve prior work-log/results as historical evidence. Real accuracy and résumé outcome/history claims remain unverified. No code/config/schema/provider request changes.
- Verification: scope consistency asserts across six documents, 24 schema fields/all stage values and 51 local links passed. Updated only the private copy that still exactly matched the previous blank template; mode0600 preserved, no answers overwritten, private path remains ignored. Whitespace/explicit staged scope checked. No application tests rerun for this requirements-only increment. Commit/push the intended documentation together, preserving unrelated root documents and private answers.

### 12 October 2026 — focused validation worksheet prepared

- User asked what must be validated, then requested continuation. Rechecked current Git/visit/master state: no new company answers, labelled cases, destination CSV/spreadsheet or operating decisions are supplied. Code remains `f7b2c8c`; master audit increment `a057b79` is pushed. Preserve unrelated root documents.
- Added `WORKSHOP_VALIDATION_WORKSHEET.md`, a blank public template with a non-overwriting private-copy command, one-job record chain, every current interpreted field/raw note/item and independent-review provenance, exact destination mapping/correction checks, separate permission/operation decisions and per-run complete-task timing/results.
- Read the actual draft/evaluator contracts before writing tables. Stage values/field names match the implementation; unknown money/partial dates stay unknown, cancelled rows retain order, uncertain cancellation must not default to false, and gold labels cannot be model-derived. The comparator does not establish stage/permission/company outcomes. Real-source AI remains blocked; no permission, interpretation, mapping or outcome is invented.
- Linked the worksheet from the master/evaluation guide. This supports collecting the missing evidence; it does not implement F09, validate handwriting, establish time savings or complete the company project. No application behavior, schema, fixture, dependency or model request changes.
- Verification for this documentation increment: actual schema/evaluator inspection and asserts confirm 24 contract fields/all stage values and independent/unknown/private-AI boundaries; 27 local links resolve. Created a blank private copy at `runtime/workshop-validation-private.md` using exclusive creation, verified identical template bytes and mode 0600, and confirmed it is ignored. Existing copies would be preserved. Whitespace/staged-scope checks pass. Application tests/browser/provider checks are not rerun because executable behavior is unchanged; prior 290 full/217 clean results remain historical implementation evidence.
- Commit/push only the worksheet and companion master/evaluation links. Next implementation remains the first branch whose real company prerequisite arrives; do not create substitute company labels/mappings or claim a completed validation from a blank form.

### 11 October 2026 — completion audit and company handoff

- Rechecked the entire feature/milestone ledger against the private visit review, workflow-plan answer/correction sections, image-review questions and completed working workbook. Relevant answers remain blank/pending; the visit directory contains the existing review Markdown/transcripts, with no independent label set or destination CSV/spreadsheet.
- Read the actual F07 provider/validation boundary and prior live report: successful printed-fictional proposal did not write a record automatically, and the manually checked review/output is explicitly not a company benchmark. Inspected relevant extraction, evaluator, authentication and PostgreSQL test coverage without rerunning unchanged tests or making another provider request.
- Added the minimum artifact/next-action/completion-evidence table above and pinned the delivered code hash `f7b2c8c`. No independently ready feature remains under the agreed plan; company-dependent F08/F09/F11/F12 and real extraction quality/use remain unfinished. Status documentation is not implementation progress or project completion.
- Documentation-only increment: check Markdown whitespace/local links and explicit staged scope, then commit/push this master update. Preserve unrelated root documents, private answers/sources and runtime artifacts. Application tests and browser/provider checks are not rerun because executable behavior is unchanged.
- Next task: start the first remaining branch whose actual company prerequisite arrives. Do not add guessed mappings, manufacture labels/approval or repeat fictional generation as a substitute for those inputs.

### 11 October 2026 — F07 provider schema fixed and printed-fictional live smoke verified

- Previous goal turn made concrete progress: authentication increment `276579c` committed/pushed and284 tests plus authenticated browser workflow passed.
- Revalidated remaining requirements rather than rerunning unchanged tests. Root Settings still have no Gemini key/model, but the separate assistant's ignored `.env` has a configured key. Presence was checked without printing it. This supplies an independent prerequisite for a fictional smoke; it does not supply company permission or labels.
- Verified current official model/image/structured-output support and executed the full explicitly enabled authenticated local API flow on the public printed `synthetic-sheet.png`. Key/config/provider artifacts stay ignored/private. No company image, live accounting write or public deployment.
- **Verified integration:** real provider/schema acceptance, unsaved proposed draft, manually source-checked stage/review, persisted initial provenance, repeatable demo CSV and UI reopening. A printed one-case smoke is not handwriting accuracy, independent field precision or a company outcome. F07 stays IMPLEMENTED_UNVERIFIED for company quality/use.
- Provider model metadata succeeded. The first harness stopped on an upload DTO checksum assumption before any generation; fixed it to compare actual preview bytes. The first full extraction then returned safe502 with jobs18/revisions23/exports17 unchanged. Direct SDK diagnostics confirmed400; a minimal one-field image schema succeeded, so key/model/image access is available.
- Current serialization schema exposed Pydantic-specific decimal constraint keys on string outputs. Explicit `str | None` serializer return types now describe the actual wire values; input precision/range/non-float validation and JSON/CSV bytes remain unchanged. That fix alone did not resolve the provider400, and its passing local tests were not treated as provider acceptance.
- **Root provider incompatibility:** independent header/date/notes-money projections succeeded; nested items failed. The same simplified item schema succeeded without `maxItems:50` and failed with it. Omitting only that cap from the complete typed provider schema then passed the actual API. The shared validator still accepts50 and rejects51, with no automatic save. No generic schema normalizer, lower row limit, alternate provider, new dependency or migration was added.
- **Calls/failures:**17 explicit generation requests across initial failures, schema diagnostics and final smoke;7 accepted (6 partial diagnostic schemas plus1 complete API flow),10 returned400. One model-metadata check succeeded separately. Every image was the same public printed PNG; each call used one SDK attempt. The checksum-assumption and startup-readiness harness failures occurred before generation; the latter was corrected by checking the live handle/health, not restarting a merely unobserved process. Rejected extraction returned safe502 and left counts unchanged; no raw provider/key value reached the UI/logs.
- **Actual complete case:** requested2026-10-11T10:14:47UTC, `gemini-3.1-flash-lite`, google-genai2.29.0,3.871s extraction observation. SourceSHA256 `a47a2f3ed9d6fe47fde70aa1448a2e6a22bef38dbf8bb858c7f6fe9c73b87d92`. Four printed headers and the description/25.10 matched the author-known reference. Jobs/reviews/outputs stayed18/23/17 after extraction; source-checked correction/save, version2 authenticated quote review and demo output ended19/24/18. Initial source/model/prompt/time provenance survived; repeat generation returned identical export identity/checksum and CSV stayedDEMO_ONLY. Private report contains case IDs; they are not company evidence.
- **Tests/UI:**75 targeted passed/9 warnings; final **290 full passed/no skips/132 warnings**, clean **217 passed/no skips/51 warnings**, all15 workshop PG cases including recovery run. Six added schema/50-vs51 cases. Fresh Chrome reopened the real live-created record/source/quote/25.10/account/history/model provenance with no page errors or additional provider call. Standard UI/provider mock tests remain mocks; no live handwriting benchmark exists.
- **Artifacts/runtime:** private0600 config/report/proposal/screenshot and ignored local harness under `runtime/workshop-ai-smoke/`; temporary AI process is stopped after verification. Normal localhost demo keeps AI disabled; no automatic loading of the other assistant's `.env`. Current migration remains20261011_auth. Company originals and unrelated root docs stay untouched/unpublished.
- **Final privacy/runtime checks:**18 original source hashes unchanged/ignored;5 live artifacts0600/ignored and local harness ignored;33 local guide/master/README links resolve; known actual provider key, operator password and password hash absent from the intended diff. Restarted task-owned normal demo responds200, extraction returns503 disabled and the live-created record still carries its provenance; temporary port18042 is no longer listening. No other host/app/profile was altered.
- **Commit/push increment:** shared serializer types, provider-only schema cap compatibility,6 regression cases and master/build/operating/README evidence together. Stage explicit intended paths; preserve unrelated `PROJECT_SUMMARY.md`/`SYSTEM_DESIGN.md` and all private runtime/company files.
- **Next:** real Q01–Q10 branch once supplied: meanings/stage, checked destination/correction mapping, permitted company processing/operator/access/operation, independent labels/baseline. Do not rerun the same fictional case to manufacture quality/adoption/history evidence. The full company project remains incomplete.

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


### 11 October 2026 — F06, reproducible demonstration CSV

- **Status:** VERIFIED; M1 full manual demonstration complete. Full company project remains conditional.
- **Files/routes/schema:** `WorkshopExport`/response, additive `20261011_exports`, fixed mapper and safe CSV cell helper in existing service; POST reviewed-revision exports and GET output download; per-version UI button. New `test_workshop_export.py`, PG concurrent-generation/migration case and extended browser harness. Standard `csv` only, no app dependency.
- **Behaviour:** UTF8 BOM/CRLF fixed `workshop-demo-v1`, reviewed identity/origin/stage and line values, literal cancelled rows without unconfirmed interpretations, empty unknowns versus0.00, no sums/tax inferred. Apostrophe formula escaping (including negative text) preserves canonical data. Opaque mode0600 private file, checksum, fsync then commit; row lock/unique identity reuses one output for simultaneous requests. Changed revision gives different output; original remains available. Failure/corruption does not become a successful generation/import.
- **Verification:** targeted28 cases passed/25 warnings; final full suite **184 passed/no skips/117 warnings** with PG14.20; clean API-only **111 passed/36 warnings**. Exact authored row, Unicode/CSV delimiters,9 formula cases, null/zero/cancellation, storage/DB rollback/cleanup, gate, corrupt/missing/unsafe path and concurrent reuse checked. Normal migration/check aligned. Browser download filename/checksum, repeat identity, old/new descriptions and reopen history passed; updated history render inspected.
- **Limits:** fictional mapping only, no destination acceptance/import/accounting credentials, no authentication/AI/real baseline. Signed negatives are spreadsheet-safe textual cells under this mapping; real financial types require approved F09 rules. Process crashes can orphan files; F12 reconciliation/backup remains. Questions Q01–Q10 pending.
- **Commit/push:** intended code/migration/tests/master/build/readme increment on main; user source/runtime and unrelated root docs excluded.
- **Next:** F07 one explicit optional image-to-proposed-draft provider path with mock/error/overwrite/permission checks; manual workflow stays primary. F10 lookup is independently ready; F09/company pilot cannot be fabricated.


### 11 October 2026 — F07, optional AI proposal implementation

- **Status:** IMPLEMENTED_UNVERIFIED for live provider; mocked API/SDK/UI scope verified. Next F10 lookup.
- **Files/config:** new `app/services/workshop_extraction.py`, extraction request/AI provenance contracts, router, manual UI, `test_workshop_extraction.py` and browser extension. Root requirements reuse google-genai2.29.0; default-off `WORKSHOP_AI_ENABLED`, explicit `WORKSHOP_AI_MODEL`, existing `GOOGLE_API_KEY`. No migration because optional provenance lives in existing JSON; demo CSV v1 unchanged.
- **Boundary:** explicitly acknowledged single fictional-source request, checksum check, no job writes, no configured tools/retries,60s/8000-token bound. Server assigns unknown stage/source/origin and proposed states; literal ambiguity stays unclear/null. AI cannot assign diagram meanings or provenance/control fields. Private-source403 cannot be enabled by a setting while Q07 is unresolved. Empty-draft UI protects entered/saved values; provenance persists through correction/reopen/review.
- **Verification:**24 mock cases passed/9 warnings including SDK call/close/config, no-call gates, invalid JSON/schema/size/floats/forbidden keys, prompt-injection-shaped payload, sanitised timeout/error, proposal states and no persistence. Final **208 passed/no skips/119 warnings** with PostgreSQL; clean API **135 passed/38 warnings**, requirements install/pip check clean. Chrome browser intercepted only the proposal response: ack, proposed/unclear fields, overwrite refusal, human correction/review/output and provenance reload passed. All existing manual checks rerun by same harness.
- **Evidence limits:** no live provider call or credentials/model configured for a smoke test; SDK schema construction does not prove Gemini accepts this schema or reads handwriting correctly. Valid hallucinated text can pass shape validation but cannot bypass proposed review. Browser/unit mocks are not AI accuracy. Origin is declared by an operator; do not upload real material as fictional. Provenance is not authenticated/signed.
- **Company prerequisites:** Q07 private processing, Q01 shorthand/labels and Q08 evaluation remain pending. These do not block F10/synthetic evaluation.
- **Commit/push:** intended feature/config/dependency/tests/docs increment only; private sources/runtime/unrelated root docs excluded.
- **Next:** F10 bounded latest-reviewed lookup, visible newer-draft status and reopen/history links; F11 synthetic evaluation afterward. Real mapping/pilot remains conditional.


### 11 October 2026 — F10, reviewed-record lookup

- **Status:** VERIFIED; F11 synthetic evaluator next.
- **Files/route:** schema/service/router, manual HTML/JS/CSS, new `test_workshop_lookup.py`, PG keyword/filter/latest case and browser checks. GET jobs lookup; no migration/config/dependency.
- **Behaviour:** latest reviewed snapshot selected before filtering; draft-only jobs excluded; newer draft version flagged but draft values not used in reviewed result. Literal bounded reference/name/vehicle/keyword filters, stage, inclusive UTC review dates, max100/page/offset/has_more; stable ordering. Keywords search individual scalar/item values rather than JSON keys; retained raw/cancelled text can match without claiming interpretation. UI shows unknowns and original source, opens current editable job with history; failed search clearly labels old results and retains their old pagination query.
- **Verification:** targeted31 cases passed/33 warnings; whole suite **227 passed/no skips/127 warnings** with PG14.20; clean API **154 passed/46 warnings**. Same names/vehicles remain separate; draft/correction/latest-stage gates, null refs, dates/limits, Unicode/percent/underscore/backslash/SQL/HTML-like literal text checked. Browser full regression plus reviewed result→newer unreviewed notice→open version5/history,503 retained-results label passed. The first browser assertion checked before async history loaded; it now explicitly waits for final history state.
- **Failures resolved:** initial unknown-reference fixture had invalid confirmed-null states; fixture fixed. Initial serialized-items search matched JSON underscore keys; replaced with value extraction on PG/SQLite and retested literal underscore case.
- **Limits:** JSON substring scan, no indexing/vector search or measured archive performance. Offset pages may move if reviews occur between requests. Local gate/self-reported identity; Q01–Q10 remain pending. F07 live provider still unverified.
- **Commit/push:** intended code/tests/docs only; user private sources/runtime/unrelated changes preserved.
- **Next:** F11 deterministic synthetic evaluator with independently supplied labels/predictions, explicit unknown/cancelled/critical errors and baseline protocol; audit manual F08 coverage separately from unresolved real semantics.


### 11 October 2026 — F11, synthetic field-comparison harness

- **Status:** IMPLEMENTED_UNVERIFIED for real outcome; evaluator/fictional development scope verified. Next manual F08 clarification guard/checks, then local F12 operating/recovery rehearsal.
- **Files:** `scripts/evaluate_workshop.py`, separate authored `evaluation-labels.jsonl`/`evaluation-mocked-predictions.jsonl`,17 meaningful cases in `test_workshop_evaluation.py`, `WORKSHOP_EVALUATION_GUIDE.md`. No API/schema/migration/dependency/provider change.
- **Behaviour:** strict shared-draft labels/predictions and explicit kind/failure, matching unique IDs, no proposed gold values, separate origin groups. Known-value denominators, unknown-kept/proposed/not-observed, exact canonical money/literal comparisons, missing/extra rows, cancelled interpretation exclusion and critical error counts. No metadata/stage/internship metric conflation. Aggregate output omits sensitive IDs/values; invalid CLI input produces no report. Supplied label provenance is not authenticated. The guide specifies held-out independent labelling and whole existing/manual/AI workflow timing, including remaining downstream copying.
- **Verification:**17 evaluator/CLI cases passed/7 warnings; full **244 passed/no skips/127 warnings** with PG14.20; clean API **171 passed/46 warnings**. Actual CLI run on3 authored cases yielded22 resolved values,1 explicit timeout,3 candidates for unknown fields,2 cancelled interpretation exclusions and exact asserted category/error counts. Initial empty raw strings were incorrectly counted as unknown candidates; normalised absent literal comparison and missing-row unknown-not-observed counts before final tests. Whole browser unchanged; last F10 flow remains its latest verification.
- **Limits:** public sources are authored contract cases, not handwriting ground truth; predictions deliberately mocked, not live Gemini results. Zero category denominator returns null. Row order is the alignment rule, no fuzzy merging. Private-source declarations do not prove independent company review. Q01/Q02/Q07/Q08/F09 prerequisites remain pending for real semantic/e2e/business results; no90% retrieval claim or time/adoption inference.
- **Commit/push:** intended evaluator/fixtures/tests/guide/master/build/readme only; private data/runtime and unrelated root docs preserved.
- **Next:** F08 preserve manual clarification context/unknown diagram boundaries and prove cancelled/raw provenance across review/output. F12 local guide and disposable backup/restore rehearsal can then proceed without pretending a company pilot is approved.


### 11 October 2026 — F08, manual clarification context and preservation

- **Status:** IMPLEMENTED_UNVERIFIED for company semantics; manual freeform boundary verified. Next F12 local guide/recovery rehearsal.
- **Files:** confirmation service, manual HTML/JS,4 `test_workshop_diagram.py` cases and browser extension. No new vocabulary/model/schema/migration/dependency.
- **Behaviour:** area-only annotation cannot create active repair work; diagram meaning on a new confirmation needs stated clarification context even with an image. UI requests speaker/established meaning/vehicle direction convention. Raw/cancelled notes, clarified meaning, context and reviewer survive snapshot/output without quote-stage promotion. Older snapshots without the newer context rule remain readable/exportable with a notice; no immutable history mutation/retroactive schema invalidation.
- **Verification:** initial targeted61 cases passed/14 warnings; after legacy-case addition final **248 passed/no skips/127 warnings** with PostgreSQL; clean API **175 passed/46 warnings**.4 boundary/preservation cases include area-only block, image+meaning-without-context block, manual raw/cancelled/reviewer/quote/output retention and previous-shape history/export compatibility. Full Chrome flow passed missing-context422 with value retention, added context→save/rereview. AI still cannot supply diagram meaning.
- **Decision:** apply the stronger rule only at new confirmation rather than the persisted DTO schema, so previously legitimate immutable snapshots continue to load. Existing reviewed-version repeat is still idempotent.
- **Limits/questions:** freeform text cannot validate the truth of a convention/repair action or authenticate its speaker. No real panel glossary, shorthand labels, automated diagram interpretation or company reviewer approval. Q01/Q02 remain pending; no screenshot-coordinate conversion or guessed operation is introduced.
- **Commit/push:** intended small guard/UI/tests/docs increment; public tests fictional, private originals/runtime/unrelated root docs unchanged/excluded.
- **Next:** local F12 operating guide and actual disposable-schema/source/output recovery rehearsal; real access/pilot/retention/mapping still require company answers.


### 11 October 2026 — F12 local guide and disposable recovery rehearsal

- **Status:** local development portion verified; full F12 WAITING_COMPANY. Company-dependent project objective is not marked complete.
- **Files:** `WORKSHOP_OPERATING_GUIDE.md`, existing PG integration module's real dump/restore case, README/master/build updates. Only standard-library/PostgreSQL client test tools; no new runtime dependency/API/auth implementation.
- **Recovery behaviour:** isolated random-schema source→two reviewed versions/CSV exports, custom-format PG dump plus private file copy, own-schema rename/restore into original temporary name, new storage restore. DB-only restore fails preview, full restore reproduces source bytes/draft/history/output identities/checksums and mapping/migration metadata. Restored PG trigger/source FK reject snapshot mutation/source deletion. Own schemas cleaned; fixture files may be retained by pytest. No public/company schema overwrite.
- **Verification:** actual recovery case **1 passed/9 warnings**; final **249 passed/no skips/129 warnings** with PG14.20; clean API **176 passed/48 warnings**. All14 workshop PG cases ran, not skipped. Browser code unchanged since successful full F08 run. Root key/model presence checked without printing secrets: both absent, so no live provider attempt. Final18 original hashes unchanged/ignored; intended staged scope/whitespace checked.
- **Guide:** verified root requirements environment, explicit isolated migration/localhost startup, complete source/manual/AI-proposal/review/correction/lookup/demo output routine, common errors and backup consistency/recovery limits. The fixture is quiescent/same-host namespace recovery, not production/offsite/encrypted backup proof.
- **Unfinished:** real auth/named identity/roles/session-origin protection, permitted hosting/provider/data/retention/delete/reconciliation/backup support and company pilot. Those choices are unresolved Q06/Q07/Q09; no dummy approval/inferred24 users is substituted. Real F08 meaning/F09 mapping/F11 labels/baseline also pending; private-source AI still403. Core manual local milestone is working; full company project remains incomplete.
- **Commit/push:** intended recovery test/guide/README/master/build increment; private visit/runtime and unrelated root docs excluded.
- **Next:** input-dependent branch only: configure permitted key/model for fictional F07 smoke, or provide actual reviewer meanings/labels, one redacted source→invoice/software→spreadsheet chain plus columns, named operator/owner and operating/processing decisions. User asked to retain questions in Markdown; Q01–Q10 remain the durable company checklist rather than repeating chat requests. Do not repeatedly rerun unchanged passing checks while awaiting inputs.


### 11 October 2026 — F12 authentication prototype verified; company pilot pending

- **Status:** IMPLEMENTED_UNVERIFIED for actual company pilot; fictional local account/origin/attribution part verified. Authentication infrastructure was built/tested without inventing a company access policy or approving deployment.
- **Scope:** one configured named account with a salted scrypt password hash, HTTP Basic browser challenge, explicit canonical origin and rejection of cross-origin browser requests before multipart parsing; protect page/API/source/output. Server binds new review attribution to the authenticated account. Existing snapshots remain self-reported and immutable; demo CSV v1 bytes stay reproducible. No user-management framework, sessions/cookies, roles/deletion policy or public deployment.
- **Reaches:** Settings/example config, auth middleware/hash setup helper, router/page/JS reviewer presentation, revision DTO/model/new additive migration, tests/fixtures/browser/run docs. Existing automotive endpoints remain outside the workshop boundary. Existing unrelated root documents stay unstaged.
- **Company decisions:** actual operator/password storage/TLS host/access scope/retention/processing/pilot still need Q06/Q07/Q09. Building a credential boundary does not approve deployment or authenticate historical reviewers.
- **Verification:**35 additional checks, including one real legacy-auth migration/CSV-preservation case. Final full suite **284 passed/no skips/132 warnings** with PostgreSQL14.20; clean API-only **211 passed/no skips/51 warnings**. Earlier targeted49 boundary/review/diagram cases passed; the final suites additionally include the setup-helper and generic-failure checks. All15 workshop PG cases passed, including recovery and unchanged CSV reuse across migration. An extra legacy reconfirmation assertion passed in a targeted PG run. CLI Alembic upgrade/check aligned; isolated API requirements pip check clean. Full authenticated Chrome capture/review/correction/history/CSV, mocked AI, manual diagram context and lookup regression passed, with anonymous page/upload401 and readonly account attribution. Restarted HTTP boundary checks passed;18 originals unchanged/ignored, auth files0600/ignored and33 local documentation links resolve.
- **Final error boundary:** the outer global generic500 response also needs no-store, because it can be generated outside the authentication response wrapper. Added that header and a meaningful injected-exception test checking response/cache/log secrecy; final suites above ran after the fix. OpenAPI advertises Basic authentication for workshop callers.
- **Failures corrected before acceptance:** TestClient does not accept constructor `auth`; set its supported `.auth` property. Historical migration fixtures use reflected old tables rather than querying the new ORM before upgrade. Build a reviewed DTO from the validated draft dictionary, not the distinct draft-model class. These fixture failures were not presented as successful security/migration checks.
- **Local runtime:** only the task-owned API was stopped/restarted and disposable public schema upgraded to `20261011_auth`. Fictional credentials/config live mode0600 under ignored `runtime/workshop-auth/`; values never printed/committed. Demo remains loopback port18041 and requires native Basic login. Password hash setup is interactive in the guide; the test harness accepts a private credential-file path.
- **Next:** conditional F07 key/model smoke or company Q01–Q10 real semantics/labels/mapping/operating path. This increment does not prove real AI accuracy, staff use, public deployment, employee identity, or résumé history.

### 12 October 2026 — F13 GST/invoicing implementation in progress

- **Scope:** add deterministic SGD billing to the existing app, separate from unchanged historical record CSV. No new dependency, model call or accounting integration. Current user answer: GST-registered and prices include GST; registration number, exact supplier/address and InvoiceNow implementation date pending. This is a user-supplied setting, not independently verified registration.
- **Delivered part, not yet verified:** invoice contracts/service/config, additive `20261012_invoices` migration and protected preview/issue/read/print routes. Fixed invoice-subtotal GST rounding, inclusive/exclusive calculation, explicit discount, non-registered treatment, completed-work/confirmed-price checks; immutable DB HTML/snapshot and job-level duplicate protection. Real issuance defaults off.
- **Places reached:** schemas/models/service/router/config/migration; UI, meaningful money/API/PostgreSQL/recovery/browser checks and operating docs next. Old capture/review/export APIs and CSV bytes are preserved. No company documents or user changes staged.
- **Next:** finish UI and tests, run actual isolated migrations and checks, update results, commit/push code and documentation together. Do not treat this entry as a passed financial feature.

### 12 October 2026 — F13 UI and initial verification

- **Delivered part:** completed-work history actions and invoice form, GST-inclusive default from user answer, explicit supplier/customer/address/registration, local Singapore issue date, discount and calculated preview. Changing details invalidates preview/issuance acknowledgement; saved invoices reopen as print/Save-as-PDF links. Real supplier must match server configuration; all endpoints inherit existing account/origin checks.
- **Actual targeted results:** `tests/unit/test_workshop_invoice.py`: **33 passed /8 warnings**; full workshop PostgreSQL integration file: **18 passed /34 warnings**, including new same/different-request concurrency, prior-head preservation, immutable issued HTML/rows and extended actual dump/restore recovering invoice identity/bytes/guards. SQLite does not assert production triggers.
- **Files:** schemas/service/models/config/migration/router plus existing template/JS and new money/API tests; browser harness now includes invoice scenario but has not yet been run against the new server.
- **Next:** full regression, dev-only additive migration/restart, complete actual Chrome scenario/artifacts, review docs/privacy/diff, then commit/push. Production billing remains disabled; missing supplier number/address/name and InvoiceNow date retained as questions.

### 12 October 2026 — F13 regression and development migration

- Full `.venv` regression with explicit disposable PG URL: **326 passed/no skips/137 warnings in158.41s**, including all18 workshop PG cases. Development-only migration to `20261012_invoices` and `alembic check` passed; original local server restarted with existing private account, AI off, real billing disabled/supplier unset. No company/live DB touched.
- Initial Chrome run timed out awaiting the preexisting CSV download after repeat confirmation. A fresh settled-page reproduction downloaded the same new fictional version successfully; history was rendered before its newly added invoice lookup completed, and the harness matched a stale confirmation status. Moved the invoice lookup before history-ready rendering and made the harness await the actual repeat-confirm response and re-enabled control. Expanded UI also protects unsaved invoice details when opening/saving/starting another record or navigating.
- New billing guide documents deterministic rules, routes/settings, real gating, missing Q11 and accounting/credit-note/InvoiceNow limits. Revised Chrome run is pending; do not treat the earlier timeout as a pass. No new provider request.

### 12 October 2026 — F13 Chrome pass and UTC response correction

- Expanded fresh Chrome harness passed old manual/review/history/CSV/mocked-AI/diagram/lookup workflows and new inclusive/exclusive/discount calculations, preview invalidation, cancelled discard retention, mock issuance failure without data loss, deliberate retry, actual saved invoice reopening, literal HTML escaping, anonymous401 and actual browser PDF generation. No provider call.
- A separate clean fictional showcase's fresh HTTP reread exposed a serialization inconsistency: initial issue used UTC `Z`, PostgreSQL reread used Singapore `+08:00`. The timestamp instant was identical but JSON was not. Invoice responses now normalise UTC like existing review/export responses; PG fresh-session and dump/restore assertions compare JSON, not timezone-insensitive Python datetime equality. Rerun final regression and fresh runtime verification before committing.

### 12 October 2026 — F13 final delivery/verification and handoff

- **Status:** VERIFIED locally; company billing configuration/actual operation pending Q11 and existing F12 decisions. User confirmed registered/inclusive pricing. All F13 schemas/service/models/config/migration/router/UI/meaningful tests and master/run/build/README/worksheet/billing guide are delivered together. Source capture/review/CSV APIs and historical artifacts remain unchanged.
- **Final verification:** explicit local `YAP_TEST_POSTGRES_URL` + `.venv/bin/python -m pytest -q --disable-warnings tests`: **326 passed/no skips/137 warnings in136.34s** after UTC response correction; all18 workshop PG cases ran. Earlier initial33 billing unit/API and18 PG passed. Dev-only migration to20261012_invoices and metadata check passed. Invoice supplier environment JSON parsed, missing registered-supplier number rejected, real flag remains default-off.
- **Chrome/runtime:** expanded isolated harness passed old capture/review/history/CSV/mocked-AI/diagram/lookup and invoice inclusive/exclusive/discount/invalidation/unsaved retention/failure-retry/issue/reopen/escaping/print/PDF/anonymous access. Clean fictional completed-work109.00 invoice read/retried after restart with identical canonical UTC JSON and original HTML checksum. Actual one-page Chrome PDF, stored HTML and JSON in `workshop_demo/` are inspectable; all values/company registration placeholder are fictional. No live model call.
- **Artifact:** `DEMO-INVOICE-001`, net100.00/GST9.00/payable109.00; exact HTML SHA256 `48563a7d09b5494ec6b256b2ea0456c8e557a0dfe8385492e2fde7aa4a1cd49a`. PDF is browser output from that stored HTML; do not infer real company invoice/registration/payment/IRAS submission.
- **Limits/next:** exact supplier name/address/GST number and InvoiceNow date Q11 are the next billing inputs. Credit notes/replacement/payment receipts/input tax/GST returns/general ledger/InvoiceNow network submission are not implemented. Current normal localhost server is AI-off/real-issuance-off/supplier-unset; no public/company deployment. No usefulness study or old-software schema required. Independent company quality/meanings and actual operation remain separate pending evidence.
- **Git/privacy:** stage explicit intended files and commit/push existing main after final link/source/secret/diff checks. Preserve unrelated `PROJECT_SUMMARY.md`/`SYSTEM_DESIGN.md` and all private visit/runtime sources. Filled worksheet untouched unless byte-identical to previous public blank; this unfilled copy was safely updated and remains0600/ignored. Final commit hash belongs in chat/next entry, since a commit cannot contain its own hash.

- **Final pre-commit audit:**21 intended public files checked;77 local Markdown links resolve; all18 original company files match recorded SHA256; actual private password/hash/configured-key values absent from intended public bytes. Historical record CSV retains its original SHA256 locally and through the live protected API; invoice HTML retains its recorded SHA256 and fresh JSON equality. JS/harness syntax and intended Git whitespace checks passed. Normal real billing remains disabled/supplier unset.
