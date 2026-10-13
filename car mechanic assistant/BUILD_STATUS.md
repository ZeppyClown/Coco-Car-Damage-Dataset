# Build status and feature record

Updated: 9 October 2026. This records a new implementation and verification batch after the internship. It does not establish what was deployed in December 2025–January 2026. Business figures in the résumé are targets until independently evidenced.

## Verified implementation

### Structured automotive service

| Feature | Implementation and limits | Verification |
|---|---|---|
| Seven automotive routes | Query routing, parts identification, diagnostics, valuation, paint guidance, VIN specifications and the newly exposed compatibility check. OpenAPI supplies actual request schemas. | All seven returned HTTP 200 in a live local smoke check; route/validation regressions pass. |
| Typed vehicle extraction | Case-insensitive VIN and OBD codes, integer year, kilometre mileage including `75k km`, comma/decimal values, miles conversion and zero mileage; existing make/model vocabulary. | Parser edge-case tests; valuation accepts zero mileage. Vocabulary coverage remains limited. |
| Real query dispatch | Parts requests call the search engine; VIN specifications call the existing specifications endpoint. Classification model paths resolve from repository root. | Mocked dispatch regressions plus a live query through the trained classifier and PostgreSQL search. Template training accuracy is not workshop accuracy. |
| PostgreSQL retrieval | Parameterised full-text search ranks names/descriptions; fit, shipping and price eligibility are applied before fallback. | Actual PostgreSQL integration test exercises retrieval, incompatible vehicles, price filtering, cache hits and empty results. |
| Common provider contract | Google Custom Search and eBay Browse accept the same query, vehicle, limit and filters arguments. eBay obtains OAuth application tokens and caches them until expiry. Provider failures are independent. | Contract/normalisation tests; failure of one provider does not suppress the other. Live marketplace access remains unchecked. |
| Honest listing provenance | Stable external listing IDs, source URLs and refreshed persisted listings; a URL hash is never a manufacturer part number. Unknown price/shipping/condition stay unknown. Google prices require explicit SGD; eBay USD is not relabelled SGD. Marketplace hostname checks reject lookalike domains. | Normalisation, currency, idempotent refresh and hostname tests. Listings without fit or Singapore delivery evidence cannot satisfy strict requests. |
| Catalogue compatibility | New `POST /api/v1/parts/compatibility`; case-insensitive make/model and engine/trim selection; missing or mismatched constrained fields return unconfirmed fit. | Route, missing-part and engine/case regressions. Catalogue claims still require installation verification. |
| Search cache | Hash covers query, vehicle, filters, limit, Singapore restriction and synthetic-data setting; expired entries refresh and responses identify hits. Failed-provider results are not cached. | Unit cache/key tests and real PostgreSQL cache round-trip. Cross-worker cache contention remains a later load check. |
| Null prices and valuation transparency | Parts can return null price ranges; valuation returns no invented comparable listings. | API/schema regressions. Valuation is rule based, not verified market pricing. |
| Errors and request attribution | Structured logs and generated request IDs; HTTP error details preserve intended validation/501 responses; unexpected failures do not expose raw provider or database exceptions to clients. Validation logs retain counts rather than complete submitted input. | Request ID/validation tests, secret-redaction regression and live response-header smoke check. |
| Complete migration chain | New `20261009_complete` revision adds six legacy model tables without rewriting earlier migrations. Startup no longer performs schema creation. ORM indexes/timestamps align with migration history. | Clean PostgreSQL upgrade, prior-revision upgrade retaining an existing catalogue row, and `alembic check` with no new operations. |
| Container recipes | Python 3.12 API image rebuilds the intent model; Compose runs PostgreSQL, migrations once, then API. Host ports bind localhost. Unused Redis/Neo4j orchestration and heavy unused dependencies removed. Safe provider toggles are passed through Compose. | YAML/service dependency checks and dependency resolution pass. Docker execution is not verified because Docker is absent on this machine. |

### Manual retrieval assistant

| Feature | Implementation and limits | Verification |
|---|---|---|
| Supported Gemini client | Replaced the legacy SDK with `google-genai`; configurable models and dimensions. New generation default is `gemini-3.1-flash-lite`; embedding default is `gemini-embedding-001`, 3,072 dimensions. | Dependency imports, live embedding calls, and current official model documentation. Existing private `.env` overrides are preserved; choose a currently available model explicitly. |
| Embedding integrity | Batch length, dimensions, finite values and nonzero norm must pass before indexing. Failed calls never become zero vectors. Free-tier batches are paced; transient API failures have bounded retries, authentication failures are not retried. SDK automatic retries are disabled to keep retry counts explicit. | Failure/invalid-vector, pacing, bounded-retry and authentication tests; actual 138-chunk Gemini embedding build. |
| Generation failure handling | Low thinking setting, 60-second request timeout and at most three attempts for transient failures; empty answers fail. Web callers receive a sanitised 503. | Retry/empty-answer and web error-redaction regressions. Live end-to-end generation succeeded on the smaller default model; correctness still requires independent review. |
| Multilingual extraction | Markdown, text PDFs and DOCX; PDF physical pages retained, DOCX paragraphs/tables kept in order with block references. EN/CN/JP extraction and numerical units tested. | Six authored language/file-format fixtures using actual PDF/DOCX readers. This does not verify arbitrary workshop documents. |
| Bounded chunks and stable IDs | Section-aware size/overlap bounds; IDs use relative source path, content hash and location; duplicate filenames in different folders remain distinct. | Bounded-chunk, stable-identity and source replacement regressions. Chunking quality still needs a real benchmark. |
| Corpus manifest | Records source hash, format, status, language, accepted/rejected pages and extraction errors. Counts unique accepted PDF page text; DOCX and Markdown are not converted into fictional page counts. CLI creates output parents. | Extraction/manifest tests and actual release manifest. Current library has 14 Markdown notes and zero accepted PDF manual pages. |
| Scanned PDF rejection | Image-only pages fail explicitly with an OCR requirement. | Representative blank/image-only PDF test. OCR itself is pending. |
| Chroma metadata repair | Scalar metadata only, no `None`; canonical make/model/engine values and explicit year bounds; JSON blocks or adjacent metadata sidecars. Unknown scope stays unknown. | Metadata type and case regressions using actual Chroma storage. |
| Applicability filters | AND vehicle constraints; explicit generic passages are retrieved alongside eligible vehicle passages. Wrong makes and years are excluded. | Actual Chroma make/case/year/generic tests. Alias/model vocabulary remains deliberately small. |
| Retrieval scoring | Cosine similarity plus folder priority, exact fault-code matches and metadata match bonuses; deterministic ranking and exact-text deduplication. | Chroma/retrieval regressions. Overlapping-passage adjudication and tuning ablations remain pending. |
| Workshop policy separation | Full policy is loaded separately and never counted as a retrieved diagnostic hit. Source text cannot override application rules. Missing specifications must not be assumed. | Policy-loading and vehicle parsing regressions. A prompt rule does not guarantee clinical or repair accuracy. |
| Source provenance | Answers return chunk IDs, source files, physical page/block locations, excerpts and model/index identity; prompts reference the same IDs. | Source-payload regression. Mechanic verification of citations remains pending. |
| Safe index release | Legacy Chroma files are rejected without resetting them; model/dimension/schema identity must match. Builder uses a new staging directory, validates document count and publishes to a new release path. Failed builds remain separate. | Legacy byte-preservation, schema mismatch, incremental replacement tests; live successful release after a failed quota-limited staging build. |
| Local web application | Lazy client creation, loopback development server, Gunicorn recipe, serialised shared assistant, 1–4,000 character questions, 5 MB upload cap, image validation, escaped answer/source display and no-store headers. | Flask input/error tests; web HTTP functionality check recorded below. Shared production access needs an authenticated HTTPS proxy. |
| Feedback collection | Query IDs are retained privately with source/model/index provenance; ratings and comments attach only to recorded queries. UI feedback controls added. | Valid feedback, invalid rating and unknown-query tests. Anonymous IDs do not measure distinct mechanics or elapsed review time. |
| Retrieval evaluation | Independent JSONL labels, eight explicit diagnostic categories, fixed-denominator distinct-passage Precision@5, separate Hit@5, category/language results, missing-query counts and duplicate/unlabelled-query rejection. | Evaluator regression proving a single hit earns 20% P@5, not 100%. No real precision result exists yet. |
| Reproducible entrypoints | Package imports, module CLI builders/evaluator/smoke runner, safe environment example, minimal pinned requirements and assistant Docker recipe. | Imports/dependency resolution and automated suite. Container runtime remains unchecked. |

## First-build verification record (before the later audit)

Environment: Python 3.12.5 on macOS; PostgreSQL 14 in a disposable cluster on localhost port 55439. Compose specifies PostgreSQL 16; that image is not runtime-tested here. Existing system PostgreSQL and original Chroma data were preserved.

1. Automated suite, including real PostgreSQL integration: **53 passed**. Run from repository root:

   ```sh
   YAP_TEST_POSTGRES_URL=postgresql://yap_build@127.0.0.1:55439/yap_test_build python -m pytest -q tests --disable-warnings
   ```

   Use your own disposable local database with a `yap_test` prefix. Unit tests isolate sessions/providers/vector directories. Without the environment variable the PostgreSQL integration test is skipped. Framework deprecation warnings remain; they are not test failures.

2. Dependency resolution: both pinned application requirement sets install together under Python 3.12; `uv pip check` reports compatible installed packages.
3. Migration verification: clean database to head, existing database from revision `204dc0248bfb` to head retaining the `PRESERVE-ME` catalogue record, and `alembic check` without model drift.
4. Actual local HTTP smoke: seven automotive routes returned 200 with `success=true` and request IDs. Fixtures establish functionality, not market-value or repair-answer accuracy.
5. Live Gemini embedding release: **138 chunks from 14 existing Markdown notes** built at private `runtime/releases/build-20261009`. No 500-page corpus is implied. The first staging build failed on rate limits; batch pacing/retry was added and the new build succeeded without touching the old database.
6. Live generation: initial configured preview returned 503; `gemini-2.5-flash` returned 404 for this account; `gemini-3.8-flash` exceeded the deadline, including a minimal control request. After switching to `gemini-3.1-flash-lite`, the full P0300 query succeeded with **five cited source passages and 2,744 answer characters**. IDs and locations were asserted in the returned payload. This confirms functionality, not mechanic-approved correctness or precision. The client uses explicit retries, a 60-second deadline and low thinking.
7. Live query embedding plus Chroma retrieval independently passed: five passages including the P0300 note, with source IDs and locations. Gunicorn HTTP checks passed for home/health, invalid input (400), unknown feedback query (404), and no-store headers. A live web query also returned 200 with five complete source records, followed by a successful feedback write and initialised health state. Its automated feedback is explicitly test input and cannot count as mechanic feedback.
8. Private verification artefacts are retained under `runtime/verification/`; keys, vector databases and feedback are excluded from git. Public Markdown records the check scope and result.

## Remaining evidence and release gates

- Authorised repair originals and independently reviewed applicability; at least 500 unique usable pages if that number is claimed.
- OCR, scanned-table/numerical accuracy review, and representative mixed-layout manuals.
- Held-out query labels, frozen experiment protocol, ablations and confidence intervals; 90% passage P@5 across eight categories remains a target.
- Live Google/eBay eligibility, real fitment/delivery data, provider expiry/timeout exercises and load testing. The quota limiter is per process; use central accounting before multiple workers.
- Authenticated HTTPS deployment, access controls, backup/restore and a workshop pilot. Local liveness is not production readiness.
- 24 real participating mechanics, an actual month of structured feedback, company confirmation of first-AI status, and real month-six adoption records.
- Historical attribution for internship dates, computer-vision failure and original pivot. This new October build cannot create historical adoption evidence.

Google Custom Search is closed to new customers and existing customers must migrate by 1 January 2027 ([official notice](https://developers.google.com/custom-search/v1/overview)). The updated generation default follows the current stable [Gemini 3.1 Flash-Lite model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite); model access and quota remain account dependent.

## Documentation and git workflow

Every subsequent feature must update this file and the relevant quickstart or design guide in the same change. Record actual checks, known limits and evidence gates. Commit that implementation and its Markdown together, then push to the authorised GitHub repository. Exclude secrets, manual originals, private feedback and built indexes. Preserve unrelated user changes.

Current guides include README.md, QUICKSTART.md, RESUME_VERIFICATION.md, COMPANY_QUESTIONS.md, PUBLIC_REFERENCE_RESEARCH.md and this file. Older assistant summaries are marked as historical snapshots. The old keyword smoke runner remains a development aid; its success percentage is not retrieval precision.


## Verification audit and corrective batch — 9 October 2026

This later batch supersedes the first-build counts and the first-build confidence in retrieval. See [RESUME_VERIFICATION.md](RESUME_VERIFICATION.md) for each résumé claim, exact checked scope and unresolved content risk. Company questions are retained in [COMPANY_QUESTIONS.md](COMPANY_QUESTIONS.md); industry examples/search alternatives are in [PUBLIC_REFERENCE_RESEARCH.md](PUBLIC_REFERENCE_RESEARCH.md).

| New or corrected feature | Verification and limit |
|---|---|
| Strict generic/vehicle applicability | Contradictory generic make/year tags now rejected. Missing required model/engine/year, wrong make and unknown scope cannot qualify vehicle-specific material. Regression tests reproduced the original leakage first. |
| Engine-option metadata | Multiple engines such as `K20_K24`, scalar engine descriptions and `affected_engines` lists normalise into Chroma-compatible JSON options with exact applicability checks. Honda K20 VTC and exact BMW N52B30 probes now find their expected notes. |
| Similarity gate and visible scores | Raw cosine threshold precedes folder/fault bonuses; source payloads show similarity and individual score components. Development cutoff defaults to 0.65; it is uncalibrated and bounded candidate pools may miss relevant material. Four unsupported/unrelated probes abstained; this is not a precision benchmark. |
| Schema-3 release provenance | Metadata and sidecar hashes enter the corpus manifest; release policy is snapshotted/checksummed; collection identity/name checked. Old schema-2 and legacy releases are preserved and rejected by new code until a fresh build is selected. Actual repair rebuild: 138 chunks/14 English notes/zero PDF pages at private `runtime/releases/audit-20261009`. |
| Citation-ID enforcement | Text/image answers require known passage IDs; no passages skips generation. Wrong/absent citations raise a sanitised failure. Prompt no longer labels sources by ordinal numbers after a live Japanese ordinal-citation failure. All six final live answer checks passed; earlier failure report retained. This checks IDs, not sentence-level entailment or factual repair correctness. |
| Safe evidence policy | Replaced mutable default workshop assumptions with `workshop_policy.md`, clearly marked application policy rather than company approval. Unsupported diagnostic percentages prohibited in generation. Old notes still contain questionable details and require original-source/mechanic review. |
| Evaluator input validation | Passage-ID arrays, query identity, reviewer, language and review date required; malformed string IDs cannot generate meaningless precision. No independent labels or 90% result supplied. |
| Reviewable feedback records | Private query records include question/answer/source/model/release evidence for later review; synthetic test feedback cannot count as workshop feedback. Authentication, retention and distinct identities pending. |
| Public industry demo | 12 authored EN/CN/JP summaries with primary source URLs, provenance and placeholder labels. Separate `public_reference_demo` collection and checked `public-reference-demo-20261009-v2` release: 12 chunks, zero PDF pages. Three live answers and inventory regression passed; no vehicle repair procedures or company statistics supplied. |
| Source provenance display | Text/image source payloads now include URL, language and corpus kind; escaped UI shows provenance and a prototype/review banner. Source payload regression passed. |
| Supported recall lookup | Replaced the failing vPIC VIN-recall URL with make/model/year campaigns; failures return 502/unknown. Scope and missing VIN-completion check are explicit. Live fresh VIN decode returned 200 with 24 model-year campaigns; this is US data, not Singapore recall clearance. |
| Idempotent specifications refresh | Fresh decode updates vehicle identity and replaces engine/transmission/safety/vehicle-info groups in one transaction, preserving unrelated groups. Regression confirms repeated refresh does not duplicate fields and safety remains cached. |
| Eligible offer pricing and provider-aware cache | Parts price range excludes known non-Singapore-shipping offers. Cache identity includes enabled Google/eBay choices. Both regressions pass. |
| Search migration research | Brave recommended for direct URL/snippet replacement; Tavily and Gemini grounding documented alternatives. No new adapter/account added without provider choice/access; provider storage rights need checking before persistence. |

Current final checks: **73 passed** with the actual PostgreSQL integration enabled; all seven live API routes returned 200; fresh/older-schema migrations and Alembic alignment passed; dependency consistency and Linux-target resolution passed; 11 live retrieval development probes, six Gemini answer checks, three public-demo answers and live web query/feedback checks completed. Warnings remain from dependencies/deprecated APIs. Docker/Compose execution and live search/marketplace providers remain unchecked.

The résumé is still unverified for employment/first AI/production, 24 mechanics, 500 pages, 90% precision, real month of feedback and historical six-month use. No statistics or deployment evidence were fabricated. The current corpus is not an expert-approved repair library; known problematic note content is documented in the verification report.

Observed platform limit: macOS Gunicorn HUP reload caused an Objective-C fork-initialisation worker crash. The operator guide now uses full stop/start on this host; a fresh process passed the final web query/feedback check. No unsafe fork override was introduced. Linux/container reload and concurrency remain unchecked.

## Workshop interview workbook — 10 October 2026

Added [WORKSHOP_VISIT_WORKBOOK.md](WORKSHOP_VISIT_WORKBOOK.md), an extensive blank fill-in document for the company visit. It prioritises one real task, authorised manuals, one observed workflow, five real questions/source references and a mechanic reviewer. Detailed forms cover separate document/cloud/storage permissions, manual editions and extraction/page checks, vehicle vocabulary, operational data, synthetic-fixture provenance, independent evaluation, pilot feedback, supplier/hosting requirements, historical résumé claims and evidence/action handover. The company question ledger and repository README link to it.

The workbook distinguishes initial build needs from pilot prerequisites and résumé evidence. It includes instructions for a private ignored copy; no company answers, approvals, records or outcome figures are prefilled. Verification for this documentation-only change: local links/contents anchors, five case forms, required section coverage, Markdown whitespace and staged-file scope checked. Application tests were not rerun because executable code is unchanged; the prior 73-test result remains the latest code verification.

## Private visit-material review — 11 October 2026

Reviewed two user-supplied text transcripts and four unique scanned PDF forms (six pages) locally, including visual inspection of every page. A fifth PDF was an exact duplicate and was retained separately. Seven filenames were made descriptive with byte checksums preserved; original transcript wording was kept intact and separate reading copies were produced. Uploaded originals, detailed observations, the filename manifest and the completed visit-workbook update remain private and locally excluded from Git. No material was sent to a model provider or published as company evidence.

The supplied forms define administrative layouts; they are not a repair-manual corpus or completed extraction benchmark. A document-capture/review/reuse workflow is a candidate for further validation, not an implemented feature or approved company pilot. The private assessment separates directly inspected content, noisy transcript accounts and design inferences. Completed reviewed examples, actual source-to-software mappings, an operator and appropriate processing permissions remain necessary before measuring usefulness.

Checks for this review: PDF page inventory and duplicate checksum, rename content integrity, full transcript/page coverage, private-file exclusions and review-document links. No application code changed and no application tests were rerun. Original audio, real handwriting extraction accuracy, software integration, legal/tax applicability and business outcomes remain unverified.

## Private workflow and software/AI plan — 11 October 2026

Created a detailed private Markdown document mapping 15 workflows from the reviewed visit material. Each process distinguishes reported or observed practices from proposed software/AI changes, explains the recommendation, identifies human review boundaries and lists missing facts. The document includes source references, a document inventory, proposed record lifecycle and field rules, priorities, baseline/development/evaluation steps and company-answer fields. The existing private review and completed workbook link to it.

The plan remains a draft for company correction, not an approved operating procedure, implemented feature or pilot result. Detailed observations and uploads remain locally excluded from Git; this general status entry is the only public change. Verification covers Markdown structure/local links, source checksum integrity, private-file exclusions and staged-file scope. No application code changed or application tests were rerun; no new accuracy, adoption or business outcome is claimed.

## Additional private image review — 11 October 2026

Visually inspected 11 subsequently supplied images: five populated administrative sheet photographs and six illustrated component-reference pages. Added a private image assessment and updated the private workflow plan/review to distinguish newly available examples from independently labelled records, complete record chains and repair procedures. The review notes partial framing, handwriting/diagram ambiguity and template variation. The images and detailed findings remain excluded from Git. No extraction pipeline was implemented or benchmarked; no accuracy, integration or time-saving result is claimed. Checks cover document links/structure, unchanged image checksums, exclusions and staged scope; application code is unchanged.

## Workshop master implementation plan — 11 October 2026

Added [WORKSHOP_MASTER_PLAN.md](WORKSHOP_MASTER_PLAN.md) as the authoritative specification and per-part implementation ledger for the proposed job-sheet workflow. It defines a manual source/draft/review/version/demo-output milestone in the existing FastAPI/PostgreSQL app, followed by optional AI drafting, conditional real destination mapping, lookup, evaluation and permitted pilot operation. Every feature has dependencies, acceptance checks and an explicit current status; no new application feature is marked implemented. Company-dependent work is distinguished from independent synthetic/manual development.

Root AGENTS.md and CLAUDE.md persist the user's requirement to update the master for every implementation part and commit/push intended increments. README links to the master. Root ignore rules now protect private visit sources across clones rather than relying only on this machine's local exclusions. Checks for this documentation/configuration change cover local links/structure, feature and handoff coverage, private-file exclusions/source checksums and staged-file scope. No application code changed and application tests were not rerun.

## Public automotive reference feasibility — 11 October 2026

Researched official manufacturer downloads in response to the user's corpus question. Locally downloaded MANN-FILTER's 2024–2026 cars/transporters catalogue and counted 513 physical PDF pages with pypdf; sampled text extraction on three pages. The browser PDF parser also reports 68 pages for an official DENSO spark-plug technical manual. Sources, download inventory location and scope limits are recorded in [the master plan](WORKSHOP_MASTER_PLAN.md). The catalogue remains ignored in private runtime storage and has not been ingested/embedded. A parts catalogue is not a repair-manual corpus or company-adoption evidence. No project scope change, application implementation, model call or new accuracy result is claimed; workshop F01 remains the next ready task.

## RAG résumé corpus sufficiency assessment — 11 October 2026

Added [RAG_CORPUS_RESUME_ASSESSMENT.md](RAG_CORPUS_RESUME_ASSESSMENT.md) and updated the master ledger with a deeper local audit: two official PDFs, 581 pages independently counted by pypdf/PyMuPDF, full nonempty-text/script/exact-duplicate checks and 2,794 in-memory chunks from the unmodified document processor. Default scope remains unknown and the current applicability filter rejects it; no source was embedded or added to a serving release. Five representative renders were visually inspected. Publisher terms, source types, language limits, current ingestion/applicability/evaluation code and every RAG résumé assertion are assessed separately. Evidence artifacts remain private/ignored. No application changes, model-provider calls or new retrieval-performance results; application regression tests were not rerun.


## Workshop F01 — verified schemas and fictional fixtures, 11 October 2026

The user selected the job-sheet capture/review project. Implemented four Pydantic schemas for raw/parsed item values, editable drafts, review validation and revision metadata. Review requires an explicit stage/reference/provenance and confirmed active descriptions; supplied interpreted values must be resolved, while genuinely missing amounts stay null. Decimal-string amounts reject floats, invalid precision and out-of-range/nonfinite values. Cancelled rows and bilingual raw notes remain available. Five fictional JSON cases and one visibly labelled printed demo PNG contain no company data.

Verification: `.venv/bin/python -m pytest -q tests/unit/test_workshop.py --disable-warnings` returned **45 passed, 7 warnings**. The broader `.venv/bin/python -m pytest -q tests` returned **117 passed, 1 skipped, 76 warnings**; the existing PostgreSQL integration was skipped because no disposable `YAP_TEST_POSTGRES_URL` is configured. An initial whole-number amount-bound issue was fixed and the checks passed afterward. Fixture image, links, private exclusions/source integrity and Git scope/whitespace were checked.

[WORKSHOP_MASTER_PLAN.md](WORKSHOP_MASTER_PLAN.md) records the exact fields, limits and handoff. **F02 persistence/migration is next.** No workshop routes, UI, database models, uploads, persisted immutable revisions, CSV output or AI extraction exist yet. These schema checks do not establish handwriting accuracy, company compatibility, reviewer identity or staff adoption.


## Workshop F02 — local draft persistence/API verified, 11 October 2026

Added document/job/revision models and additive migration `20261011_workshop` after `20261009_complete`. Three operations now create, reopen and replace draft records under `/api/v1/workshop/jobs`. Full-draft saves carry `expected_version` and atomically reject stale writes with 409. Source references must exist/match origin; job origin cannot be relabelled. Incomplete drafts remain drafts. Database errors rollback and are sanitised by the existing handler. `WORKSHOP_ENABLED=false` is the default; enable only for a local isolated demo. No new dependency was added.

Verification: **133 passed, 0 skipped, 100 warnings** using `.venv/bin/python -m pytest -q tests` with an explicitly supplied local disposable PostgreSQL 14.20 database. Fifteen F02 cases cover API validation/failure handling, fresh/previous-head migrations preserving a vehicle, model alignment, reopen, concurrent save conflicts, rollback and revision/FK constraints. The original automotive routing test now explicitly checks its seven original paths while allowing workshop additions. Normal CLI `alembic upgrade head`/`alembic check` passed; a synthetic HTTP create/update/stale-save and app restart/reopen passed. Task-owned servers stopped afterward. Private sources stayed unchanged/ignored; no provider calls or company data used.

The [master plan](WORKSHOP_MASTER_PLAN.md) records exact API payloads, local run instructions, results and handoff. **F03 image attach/preview is next.** A revision table is not a confirmation service or immutable audit history. The UI, confirmation, export, AI and pilot access controls remain pending; keep the demo off public/shared hosts. No company accuracy/adoption or résumé outcome is established.


## Workshop F03 — safe image sources, 11 October 2026

Added bounded JPEG/PNG attach and checksum-verified original preview, private UUID-key storage, explicit origin and duplicate-byte reuse without merging jobs. Upload limits are 8 MiB, 6,000 pixels per side, 20 megapixels and one frame; streamed multipart requests are bounded before parsing. Corrupt/mismatched/oversized input and missing/altered files fail visibly. Write/DB failures rollback and clean newly created files; a process crash may leave an unreferenced file for later reconciliation. Pillow is declared for the root API host.

Verification: 22 targeted source/PG cases passed; full suite **149 passed, no skips, 101 warnings** with actual PostgreSQL. Live HTTP upload, byte-identical preview, duplicate reuse and chunked-body 413 passed. Sixteen new cases cover validation, static/path boundary, disabled routes, failure cleanup and concurrent deduplication. Shared-environment pip check found unrelated audio/telemetry conflicts; a clean root-requirements environment passed pip check and all 76 workshop tests (20 warnings). Details are in the master. No company source/model processing or business metrics. F04 manual UI is next; source access remains local/demo-gated without authentication.


## Workshop F04 — manual screen verified, 11 October 2026

Added gated `/workshop` manual entry/save/reopen with source preview/zoom/rotation, explicit raw/interpreted fields and states, cancellation, Decimal-text/null handling and unsaved/error retention. HTML lives outside the static mount; disabled access has no HTML bypass. Main references/items stay visible while optional fields collapse. Root automotive UI links to the local demo. No model/provider or new app dependency.

Verification: **150 Python tests passed, no skips, 101 warnings**, including PostgreSQL; the new page/gate/assets case passed. Repeatable isolated Chrome/Playwright browser checks passed for attachment, invalid-amount retention, save/reload, Unicode/money, source byte identity after view transforms, keyboard focus, stale/503 retention, mobile width and escaped HTML-like notes. Accessible select names were corrected after the browser check caught ambiguity. Desktop/mobile renders were inspected; native computer-use timed out and was not treated as a pass. Screenshots/test browser environment remain ignored; sources and records are fictional. The master records repeatable commands and limits. F05 reviewed snapshots/history is next; company use/accuracy/usability and authentication remain unverified.


## Workshop F05 — reviewed versions verified, 11 October 2026

Added atomic/idempotent confirmation with explicit acknowledgement, self-reported reviewer, version checks and server UTC timestamp; bounded read-only history and correction/rereview UI. Additive `20261011_review_guard` adds/backfills revision source FK and a PostgreSQL UPDATE/DELETE rejection trigger. Detaching a newer draft cannot remove the reviewed source's database link. Existing quote stage remains quote. No new dependency or provider call.

Verification: **167 tests passed, no skips, 115 warnings** with PostgreSQL14.20, including concurrent confirmation, stale cached state, immutable snapshots, source FK and old-schema backfill. The initial historical migration test used the current ORM prematurely; it was corrected to insert the old table shape and the final suite passed. Clean API-only environment: **94 passed, 34 warnings**. CLI Alembic check aligned; isolated Chrome confirmation/correction/history/idempotence checks passed. Original18 sources remained unchanged/ignored. No authenticated identities/company accuracy/pilot result; F06 demo CSV is next. See master for full commands, boundaries and handoff.


## Workshop F06 — manual milestone verified, 11 October 2026

Added fixed `workshop-demo-v1` CSV from reviewed snapshots, private output identities/checksums, additive `20261011_exports` and per-version downloads. Null remains empty, zero remains0.00; cancelled literal rows survive without interpreted values. Formula-like cells are escaped without changing records. Simultaneous generation reuses one output; file/DB failures leave no success row; original output survives later correction. No provider/new app dependency/accounting write.

Verification: **184 passed, no skips, 117 warnings** including PostgreSQL14.20; clean API-only **111 passed,36 warnings**. Exact demo rows, CSV/Unicode/formula/null/cancelled handling, failures/corruption/gates and concurrency checked. CLI Alembic aligned. Isolated Chrome completed source→draft→review→correction→CSV/download/checksum→reopen with repeat identity and older output preserved; render inspected. This completes M1 local fictional manual demonstration. Company destination compatibility, semantic accuracy, authentication and pilot use remain unverified; F07 optional drafting/F10 lookup are ready next. Master records full contract/commands/limits.


## Workshop F07 — mocked AI proposal path verified, live use unverified, 11 October 2026

Added explicit fictional-image Gemini proposal with strict acknowledgement, default-off enable flag and explicit model/key. Private-source processing returns403 until company permission is resolved. One closed SDK client, JSON schema,60-second timeout/one attempt, no tools; server-owned stage/source/origin and proposed-only values. Bad response/provider failure is sanitized and no draft is saved. UI refuses overwriting entered/saved work, then supports manual correction/review/output. Initial-source/model/prompt/time provenance survives reopen; no migration/CSV mapping change.

Verification:24 mocked API/SDK cases; full **208 passed/no skips/119 warnings** with PostgreSQL; clean API **135 passed/38 warnings**, updated requirements install and pip check clean. Browser intercepted mock proposal passed acknowledgement/states/overwrite refusal/correction/review/CSV/provenance-reopen. No live Gemini/model-schema acceptance or handwriting/accuracy result. Company AI permission/labels/baseline unresolved. F10 lookup is next; master describes provider docs, boundaries, configuration and handoff.


## Workshop F10 — reviewed lookup verified,11October2026

Added bounded latest-reviewed-per-job lookup, literal customer/vehicle/reference/keyword filters, stage/UTC review dates and pagination. Draft-only jobs stay excluded; newer unreviewed drafts are explicitly flagged. JSON item values are searched rather than property names. Same-name customers/vehicles stay distinct UUID jobs. UI opens the current draft/history with reviewed source links and labels previous results if a search fails. No migration/dependency/config.

Verification: **227 passed/no skips/127 warnings** with PostgreSQL14.20; clean API **154 passed/46 warnings**.19 new cases cover latest/draft/null/filter/date/limit/literal/injection boundaries. Browser full flow plus lookup/newer-draft/open/history/503-labelled retention passed after correcting an async test wait; initial serialized-item underscore false match fixed using value extraction. No actual archive performance/company semantic/staff-use evidence. F11 synthetic harness is next; company mapping/pilot and live Gemini remain conditional. Master updated with exact behaviour/commands/limits.


## Workshop F11 — synthetic evaluator verified, real measurement pending,11October2026

Added no-network field comparison with separately supplied labels/predictions and declared prediction kind, exact canonical values, visible unknown/cancelled/failure/row/critical-error counts and separate origins. Proposed gold labels, empty/missing/duplicate/unmatched inputs fail; failed responses cannot earn abstention. Aggregate output omits identifying values/IDs. Evaluation guide documents held-out independent company labels and complete current/manual/AI task timing; those observations do not exist yet.

Verification:17 targeted evaluator/CLI checks; final **244 passed/no skips/127 warnings** with PostgreSQL; clean API **171 passed/46 warnings**. CLI ran on3 deliberately imperfect authored contract cases with22 resolved values,1 simulated timeout,3 unknown-value candidates and2 cancelled exclusions. Empty literal/missing-row denominator handling corrected before final run. No live model/handwriting/company accuracy or business/adoption result. Next manual F08 provenance boundary then local F12 guide/recovery rehearsal; master and README updated.


## Workshop F08 — manual clarification boundary verified,11October2026

New confirmations with interpreted diagram notes now require stated clarification context; UI requests speaker/established meaning/vehicle direction convention. Area-only marks cannot become active work. Literal/cancelled/context/reviewer data survive history/demo output with stage unchanged. Earlier immutable snapshots remain readable/exportable and get a missing-context history notice; the stronger rule applies at new confirmation, not retroactive DTO validation.

Verification: **248 passed/no skips/127 warnings** with PostgreSQL; clean API **175 passed/46 warnings**.4 new fictional boundary/preservation/legacy cases; browser full regression plus missing-context422 retained values and successful clarification/rereview passed. No actual company panel vocabulary/shorthand semantic validation or automated diagram recognition; Q01/Q02 pending. F12 local guide/recovery rehearsal is next.


## Workshop F12 local operation/recovery verified; company pilot pending,11October2026

Added an operating guide and actual custom-format PostgreSQL dump/restore test in an owned disposable namespace, with fictional source/two reviewed versions/two outputs and fresh file storage. DB-only restore correctly lacked source bytes; full restore preserved drafts/history/UTC metadata/repeat output identity/checksum, migration/model alignment and immutability/source-FK guards. No public/company schema restore/overwrite or new runtime dependency.

Verification: recovery **1 passed/9 warnings**; final **249 passed/no skips/129 warnings** with PG14.20; clean API **176 passed/48 warnings**. All14 workshop PG cases ran. Last browser F08 complete flow remains verified, no UI code changed here.18 original hashes remain unchanged/ignored. Root Gemini key and workshop model checked by presence only: absent; no live call. Tests use quiescent same-host temporary namespace/private fictional files, not production/offsite/encrypted backup evidence.

Local manual workflow/lookup/mocked AI/synthetic evaluator/guide/recovery work is delivered and committed. Full company project remains unfinished: live Gemini, actual semantics/independent labels/baseline, accepted mapping, real authentication/access/host/retention/reconciliation/pilot. Q01–Q10 master questions remain pending; no independently ready feature under agreed scope remains. Resume adoption/precision/history claims remain unverified. Next work needs an actual prerequisite, not more unchanged regression reruns.

## Workshop F12 local authentication prototype,11October2026

Added one configured operator account with a salted standard-library scrypt hash, native HTTP Basic challenge, exact host/origin checks and cross-site rejection before multipart parsing. Page, API, previews, extraction and CSV downloads are protected; default-disabled and misconfigured enabled routes fail closed. Protected responses and generic unexpected failures are not cached. Password setup reads hidden terminal input; account/hash/origin setup is documented in [the operating guide](WORKSHOP_OPERATING_GUIDE.md). No new dependency.

New review attribution comes from the verified account; client reviewer text cannot impersonate another identity. The readonly UI/history distinguishes authenticated accounts from legacy self-reported names. Additive `20261011_auth` preserves immutable old snapshots and existing demo CSV bytes/checksums/identities. Direct service callers default to self-reported attribution. Existing automotive endpoints remain outside the workshop boundary.

Verification:35 added checks, including old-schema review/CSV preservation on PostgreSQL. Final full **284 passed/no skips/132 warnings**; clean API-only **211 passed/no skips/51 warnings**; all15 workshop PG cases ran, including actual dump/restore. An extra legacy reconfirmation assertion passed in a targeted PG run. Full authenticated Chrome workflow and anonymous page/upload rejection passed; the restarted loopback server verified authenticated200/no-store, anonymous401, cross-origin403 and static-bypass404. Alembic upgraded/aligned and clean requirements pip check passed.18 original private sources unchanged/ignored; fictional credential/config files private0600/ignored. Exact scope/commands and the generic-error cache/logging boundary are recorded in the master.

This is a single local account with access to all workshop records. No real company access policy, TLS/proxy/rate limiting, retention/deletion/reconciliation or permitted pilot is supplied. Live Gemini/model acceptance, actual semantics/independent labels/baseline and destination mapping still need inputs. Q01–Q10 remain in the master; no company statistics or internship history was inferred. The master is the next-contributor handoff, and this implementation/docs increment is committed/pushed together.

## Workshop F07 live printed-fictional integration verified,11October2026

Reinspection found the separate assistant's existing local Gemini key. It was explicitly supplied to a temporary authenticated localhost process; root workshop configuration does not automatically load that file. Model metadata and current official documentation verified `gemini-3.1-flash-lite` support. Actual generation exposed a provider-schema incompatibility hidden by SDK mocks: nested `maxItems:50` returned400, while the same item schema without that cap succeeded. The provider copy now omits this cap; the shared validator still accepts50 and rejects51. Typed money serializers produce accurate string/null schemas without changing input rules or actual output bytes. No new dependency/migration/provider/framework.

Final live source→unsaved proposed draft→source-checked manual quote review→demo CSV/repeat identity/provenance passed at2026-10-11T10:14:47UTC using SDK2.29.0. The proposal took3.871s, matched4 known printed headers and the description/25.10, and wrote no draft/review/output automatically. The unresolved version failed confirmation; the checked version2 used authenticated attribution and preserved initial AI provenance. Chrome reopened that real live-created record/source/history/provenance with no page errors or extra provider call. Explicit schema diagnostics preceded acceptance;17 generation requests total,7 accepted/10 rejected, all on the same public fictional PNG, one SDK attempt per call. Failed extractions preserved counts and returned generic errors.

Verification: **75 targeted passed/9 warnings;290 full passed/no skips/132 warnings;217 clean API passed/no skips/51 warnings** with PostgreSQL14.20, including all15 workshop PG cases/recovery. Six added schema/row-bound cases. Private config/proposal/report/screenshot/harness remain ignored under runtime; original company sources unchanged. The temporary AI process is stopped after verification; normal demo AI stays off. Full privacy/source/Git scope checks are recorded in the master and this code/tests/docs increment is committed/pushed together.

The single author-known printed fixture proves integration, not handwriting/independent accuracy, time savings, real mapping, company processing permission/pilot use or résumé history. Q01–Q10 remain the required next-input ledger. Existing RAG and new image-to-draft workflow remain separate capabilities.

## Workshop usefulness assumption,12October2026

The user instructed us to assume the project is useful to its customer. Demand interviews, workflow baselines, time-saving/adoption studies and proof of removed copying are now optional rather than build/completion gates. Q05 records the user assumption; Q08 independent expected labels remain needed for real accuracy, while its baseline-time portion is optional. No measured benefit or company answer is inferred.

Updated the master F11/F12 dependencies, M2–M4 checks, current question/handoff entries and companion validation/evaluation/operating/README guidance. The worksheet's timing section can be skipped while building. Source meanings, destination schema/correction rules, independent quality evidence and selected processing/operation remain technical requirements. No runtime/code/config/schema change or provider call; application tests are not rerun for this documentation increment. Scope consistency, 24 contract fields/all stages and 51 local links passed; the unchanged blank private copy was updated without overwriting answers and retained mode0600/ignored status. Whitespace/staged scope checked; intended documentation committed/pushed together.

## Workshop captured record/export and fresh verification,12October2026

User requested actual artifacts/direct software verification and assumes the old financial/GST software gone. Target standalone workshop records/history/export; external mapping F09 is deferred. Invoicing/GST/accounting is a separate conditional extension. No existing import schema is required for the current app.

Added [WORKSHOP_VERIFICATION_REPORT.md](WORKSHOP_VERIFICATION_REPORT.md) with the actual saved fictional quote/version2/25.10 JSON, unchanged32-column CSV and inspected Chrome screenshot. Source preview matches the authored fixture; CSV matches the reviewed record and original checksum/repeated identity. No new model call or real-company record processing.

Fresh live HTTP checks passed saving/reopen, authored manual amount correction25.10→30.10, stale save/confirm409, preserved original snapshots/CSV, new authenticated review/repeat export identity, anonymous/wrong-password401/cross-origin403/static404/no-store. Fresh Chrome reopened stored source/quote/25.10/history with readonly account/no page errors. Fresh clean API workshop suite: **217 passed/no skips/51 warnings in146.30s**, all15 PostgreSQL14.20 cases including actual disposable `pg_dump`/`pg_restore` plus source/output-file recovery. Local/quiescent fictional recovery is not production/offsite/concurrent-write evidence.

Master/companions updated with actual results and revised scope; no application code/schema/config changes. Real source meaning/handwriting quality, actual hosting/pilot and historical résumé figures remain unverified. Keep private run report/credentials/visit sources and unrelated root documents out of the commit; publish only intended documentation and authored-fictional showcase.

## 12 October 2026 — F13 standalone invoicing/GST verified locally

User explicitly selected GST/invoicing and supplied GST-registered/inclusive pricing. Added strict supplier/customer/billing contracts, deterministic SGD Decimal subtotal rounding, inclusive/exclusive GST and explicit discount, completed-work/confirmed-price eligibility, immutable issued snapshot/HTML/checksum and job-level duplicate prevention. New additive migration `20261012_invoices` preserves all old reviews/record CSVs. Existing protected UI/API now supports billing preview, explicit issue acknowledgement, saved invoice reopening and browser Print/Save as PDF. No new dependency, AI or accounting service.

Final full regression after UTC normalisation: **326 passed/no skips/137 warnings in136.34s**, including all18 workshop PG cases/actual invoice dump-restore. Initial money/API33 passed and PG18 passed. Fresh Chrome passed existing workflows and invoice basis/discount/invalidation/unsaved-discard/failure retry/issuance/reopen/HTML escaping/print-PDF/anonymous checks. Dev-only migration/check passed. Fresh restarted HTTP reread/retry JSON is equal; original issued HTML unchanged. Initial CSV browser timing and timezone serialization failures were corrected and retained in the master log.

[Actual fictional invoice PDF/HTML/JSON and results](WORKSHOP_VERIFICATION_REPORT.md) show inclusive109.00 = net100.00 + GST9.00. [Billing guide](WORKSHOP_INVOICING_GUIDE.md) documents every route/config/rule and Q11 company questions. Master/operating/README/blank worksheet updated; unchanged private blank copy kept ignored/0600. Real issuance defaults off, supplier unset, AI off. Exact billing name/address/GST number and InvoiceNow implementation date remain pending; no credit notes/payments/GST returns/general ledger/InvoiceNow submission or company deployment claimed. Intended code/tests/docs/artifacts are committed/pushed together, preserving unrelated user files and original private sources.

## 13 October 2026 — F14 paper-layout job sheet and before/after slides

Reviewed records can now be printed onto the workshop's own blank job sheet (`GET /api/v1/workshop/revisions/{id}/sheet`, linked from each reviewed version in `/workshop`). Set `WORKSHOP_SHEET_TEMPLATE` to a private image of the blank form; without it the values print with a notice. 5 new cases pass; full suite **312 passed, 19 skipped (PostgreSQL URL unset), 0 failed**; a fictional record rendered on the real form was inspected. Positions fit the supplied blank quotation form only; the sheet version photographed in use differs. Knock/spray/servicing, fuel gauge and contact are not captured. The invoice layout is unchanged pending a company invoice sample. The Slidev deck now shows the collected paper documents first, then the web app, then the pipeline. Details: [master section 16](WORKSHOP_MASTER_PLAN.md#16-work-log).

### F14.b — invoice on the workshop form, 13 October 2026

Issued invoices can also be printed on the same form (`GET /api/v1/workshop/invoices/{id}/sheet`, linked from the issued-invoice panel): work lines in the numbered rows, Total / GST 9% / Grand total in the last rows, invoice number and date beside the car outline. The stored immutable invoice and its plain `/print` view are unchanged. `tests/unit/test_workshop_sheet.py` **8 passed**; full suite **315 passed, 19 skipped (PostgreSQL URL unset), 0 failed**; a fictional invoice rendered on the real form was inspected. The three added cases were written after the code. Tax-invoice content rules, a PostgreSQL run, a live click-through and staff review are not checked.

### F15 — step-by-step job-sheet screen, 13 October 2026

`/workshop` was rebuilt: a top bar with six numbered steps (Car & customer, Knock, Repair & parts, Spray, Check & save, Print & invoice), numbered work lines like the paper sheet, a car outline staff click to mark damage, fuel gauge and contact, and a built-in “How to use” page. Print-outs now circle knock/spray/servicing and fuel level and show the car marks. Full suite **318 passed, 19 skipped (PostgreSQL URL unset), 0 failed**; a whole fictional job was run through the live app in Chrome and every screenshot inspected. One confirmation tick now sets all typed values to confirmed, replacing per-value review states on screen; this needs a decision. The old ignored browser suite no longer matches the screen. Details: [master section 16](WORKSHOP_MASTER_PLAN.md#16-work-log).

### F16 — books, payments, car history, quick lines and pop-up guide, 13 October 2026

`/workshop` now has a **Books** page (every invoice in a month with GST, paid and balance, plus a download for Excel), payment and refund entries against invoices, vehicle-number matching that fills in a returning car's details and lists its earlier jobs, one-click common lines, and a **Paper guide** pop-up showing private reference pictures. New table `workshop_payments` (migration `20261013_payments`). Full suite **322 passed, 19 skipped (PostgreSQL URL unset), 0 failed**; checked end to end in Chrome on a scratch SQLite instance. The migration was later applied to the demo PostgreSQL database by hand and Books, a payment and the Excel download were checked there in Chrome. This is a sales and collections book, not full accounts. Details: [master section 16](WORKSHOP_MASTER_PLAN.md#16-work-log).

### F17 — setup, real-looking invoices, expenses and profit, accident jobs, 13 October 2026

`/workshop` now opens on a first-time welcome where the workshop's own details are typed once; invoices use them, are numbered `INV-2026-0001` onwards and no longer carry any DEMO label. **Books** gained expenses and a monthly profit and loss. Step 1 gained accident and insurance details. Two jobs can no longer share a job number (database rule). One click adds three months of made-up example jobs. New tables `workshop_company` and `workshop_expenses` and column `workshop_jobs.job_number` (migration `20261014_company_expenses`). Full suite **328 passed, 19 skipped (PostgreSQL URL unset), 0 failed**; checked end to end in Chrome on a SQLite scratch instance. The new PostgreSQL database for the real-looking copy has not had its tables built yet. Details: [master section 16](WORKSHOP_MASTER_PLAN.md#16-work-log).

### F18 — profit per job, invoice counter, old jobs checked, 14 October 2026

Books now shows the profit on each job (what was charged less the expenses recorded with that job no.). Invoice numbers come from a locked counter in the database, so two invoices issued together get consecutive numbers. The migration gives earlier jobs their job number so the no-duplicates rule covers them too. Demo labels were removed from the slide deck and the per-job download. Full suite with PostgreSQL **349 passed, 0 skipped, 0 failed**. Details: [master section 16](WORKSHOP_MASTER_PLAN.md#16-work-log).
