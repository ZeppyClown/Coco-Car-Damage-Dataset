# Workshop job-sheet project — master plan and implementation ledger

**Last updated:** 11 October 2026. **Current phase:** planning complete; new job-sheet application features not implemented.

This is the authoritative implementation/handoff document for the workshop administrative project. Every contributor, including Codex and Claude, must update it for **every feature or implementation part**, including partial work, fixes, migrations, tests, configuration and changed decisions. Do not rely on chat history to resume the work.

The first product is a small local application that turns a permitted paper sheet or manual entry into a reviewed job record and a reusable output. AI may draft fields; staff confirm their meaning. A confirmed record is not automatically a completed repair, final invoice, paid transaction or imported accounting entry.

## 1. Start here: the actual next task

**Next ready task: F01 — define and validate the draft record contract using synthetic examples.** Then implement F02–F06 to produce the first complete manual workflow before adding AI.

Do not start by scanning an archive, training a model, building a vector database or integrating the accounting system. None is required to demonstrate the core review workflow.

The first working milestone is:

> Open a fictional job sheet → enter a draft beside its image → correct an ambiguous value → confirm the record → download a clearly labelled demonstration CSV → reopen the same record and see what was confirmed.

This milestone is a local demonstration. It does not claim company deployment, real handwriting accuracy, accounting integration or reduced staff time.

### First actions for the next implementer

1. Read this file, root `AGENTS.md`, root `CLAUDE.md`, [BUILD_STATUS.md](BUILD_STATUS.md) and [the repository README](../README.md).
2. Run `git status --short` and identify unrelated user work. On 11 October, `PROJECT_SUMMARY.md` is modified and `SYSTEM_DESIGN.md` is untracked; preserve both unless the user explicitly includes them in the task.
3. Read the existing schema/session/router/test fixtures listed in section 5. Confirm actual paths before adding code.
4. Check whether the private visit files exist locally. Their absence does not block a synthetic/manual prototype. Do not obtain company files from public search as replacements for actual evidence.
5. Mark F01 `IN_PROGRESS` and state the exact scope in the ledger below.
6. Implement the draft/confirmed schemas, validation and fictional examples, with the small tests specified for F01.
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
| `app/db/models.py` | Shared SQLAlchemy `Base` and current automotive models | Add workshop models or import their definitions before metadata collection |
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

Paths are proposed, not already implemented. If existing code offers a smaller correct arrangement, change the list and explain the decision in this master file before continuing.

| Path | Purpose | First feature |
|---|---|---|
| `app/schemas/workshop.py` | Draft, reviewed revision, item and export request/response validation | F01 |
| `app/services/workshop.py` | Draft updates, review/version rules and deterministic output logic | F02/F05/F06 |
| `app/api/v1/workshop.py` | HTTP input boundary and workshop operations | F02/F03 |
| `app/static/workshop.html` | Source/draft review page | F04 |
| `app/static/workshop.js` | Page actions and accessible feedback | F04 |
| `app/static/workshop.css` | Necessary page styles; reuse existing styles where practical | F04 |
| `app/services/workshop_extraction.py` | One optional image-to-draft integration, added only when justified | F07 |
| `tests/unit/test_workshop.py` | Draft/review/export/identity failure checks | F01 onward |
| `tests/integration/test_workshop_postgres.py` | Real DB/migration and concurrent version/export checks | F02/F05/F06 |
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
| F01 | Draft/review contract and fictional fixtures | READY | F00 | Next task: schemas, examples and validation tests |
| F02 | Workshop storage, models and migration | READY | F01 | Dedicated development DB; no company writes |
| F03 | Safe image attach/preview and duplicate warning | READY | F02 | JPEG/PNG initially; immutable original bytes |
| F04 | Manual source/draft review screen | READY | F01–F03 | First usable UI; no AI dependency |
| F05 | Confirmation, immutable revisions and conflict handling | READY | F02/F04 | Separate review state from repair stage |
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

### F02 — persistence and migration

**Purpose:** preserve drafts and reviewed history without disturbing current automotive data.

**Implementation:** add the three initial models to shared metadata; create one new additive Alembic revision; use `get_db` and transactions. Keep generated-source paths private. Do not call `init_db/create_all` on application startup.

**Checks:** new database upgrades to head; a database at the previous head upgrades while preserving a seeded existing row; schema and models align; draft survives process/reopen; rollback leaves no partial reviewed state. Run these on an isolated PostgreSQL database, not only SQLite.

**Completion:** draft create/read/update service or routes working, migration tests/evidence recorded, actual new revision documented. Downstream feature blockers are explicit if PostgreSQL is unavailable.

### F03 — attach and preview an image

**Purpose:** give the operator a reliable source beside the draft.

**Implementation:** accept bounded JPEG/PNG uploads; validate decoded content, dimensions/pixel count and byte size; reject mismatched/unsupported files. Reuse Pillow if installed and declare it in the actual host requirements when imported. Write generated file keys under private storage; store SHA-256 and return an ID. No raw upload directory under the static mount.

**Checks:** valid upload/preview; corrupt input; fake extension/MIME; over-limit input; unsafe original filename; unknown source ID; duplicate bytes; database/file failure without a falsely saved attachment. Check limits in the running app, not just a helper.

**Duplicate behaviour:** warn/reuse the source reference when the same bytes already exist; do not merge job records or assume a new photo of the same sheet is unrelated. Byte checksums do not detect all semantic duplicates. Document this limit.

**Completion:** UI can display the stored original by opaque ID; originals unchanged; limits and storage path documented. Real-world remote access is not approved by this local feature.

### F04 — manual source/draft review UI

**Purpose:** make the complete task usable before depending on AI.

**Implementation:** a separate static page with source preview, zoom/view rotation, editable fields, item rows, raw notes, unknown/unclear indicators and save feedback. Use escaped text/safe DOM APIs for source/model/user strings. Provide labels, keyboard access and visible failure feedback. Preserve unsaved edits if a request fails; do not show success before persistence succeeds.

**Checks:** enter a fictional job with image; save/reload preserves values; blank/unclear states remain visible; bilingual text displays; failed save retains entered values; keyboard users can reach controls; long notes do not hide confirmation; existing root/API still works.

**Completion:** one manually entered draft works through browser UI, without provider keys. Record actual browser checks separately from automated tests.

### F05 — reviewed snapshots and corrections

**Purpose:** stop provisional interpretations from silently becoming authoritative outputs.

**Implementation:** validate required fields; require explicit stage/reviewer; save immutable revision in one transaction. Guard loaded draft version. Show reviewed snapshot history and create a new draft when correcting a reviewed record.

**Checks:** incomplete draft can save but cannot confirm; repeated unchanged confirmation does not duplicate; stale edit/confirm returns conflict; two concurrent confirmations produce one correct result; old snapshot survives correction; reviewed quote stays a quote. Usernames typed into a local demo are self-reported reviewers, not authenticated identities; label that limitation until F12.

**Completion:** draft → review → correction → rereview is demonstrable; immutable versions and conflict behaviour verified. Do not claim a compliance-grade audit trail from a local self-reported reviewer.

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

Possible settings, added only when needed:

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

Replace vague “tests pass” with the command, counts, skipped checks and test environment. PostgreSQL integration is skipped without its explicit disposable test URL; do not present a skipped test as passed.

### Commands to adapt during implementation

Run from the repository root using the actual Python 3.12 environment. The checked workspace has `.venv/bin/python`, but a different machine may need its own environment.

```sh
git status --short
.venv/bin/python --version
.venv/bin/python -m pytest -q tests/unit/test_workshop.py
```

`test_workshop.py` is a proposed future file. Do not report this command as executed successfully before it exists.

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
- **Previous delivery before this plan:** `fe3a0ec`, generic status entry for the private image review.
- **What exists:** current automotive API/RAG code, visit review/planning documents and private uploaded examples.
- **What this task adds:** this master plan, persistent contributor instructions, README discovery link, portable ignore rules and a build-status entry.
- **What does not exist:** workshop upload/review/confirmation/export/search application features, real extraction benchmark, real destination mapping or authorised company pilot.
- **Next ready feature:** F01, then the F02–F06 manual milestone.
- **Independent work available:** fictional schemas, fixtures, local UI and mocked extraction; lack of company access is not a reason to stop those.
- **Unrelated changes to preserve:** root `PROJECT_SUMMARY.md` and `SYSTEM_DESIGN.md` as seen on this machine; verify current status rather than assuming it remains identical.
- **Open decisions:** real output mapping, model-processing path, operator and expected labels. None should be fabricated.

### Copyable Claude handoff prompt

```text
Continue the workshop job-sheet project in this repository. Read AGENTS.md,
CLAUDE.md and car mechanic assistant/WORKSHOP_MASTER_PLAN.md first.
Treat the master plan as the current implementation ledger. Inspect Git status
and preserve unrelated user work. Start with the next ready feature; initially
F01 and then the manual F02–F06 vertical slice. Use synthetic examples until
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
