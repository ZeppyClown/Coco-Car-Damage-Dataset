# Yap Motor project: implementation and evidence plan

Prepared: 9 October 2026. Planning baseline: source inspection, existing summaries, and official provider documentation. No application tests or live provider calls were run for this plan.

The user confirmed that **24 mechanics, 500+ pages, 90% retrieval precision, one month of mechanic feedback, and six-month adoption are targets until evidence is available**. This document specifies how to earn those claims. It does not report them as achieved.

## 1. Outcome and boundaries

Deliver two demonstrable results:

1. A reproducible FastAPI/PostgreSQL automotive service with seven explicitly counted routes, working retrieval adapters, typed entity extraction, migrations, structured logs, and Docker Compose startup.
2. A workshop document assistant using Gemini and ChromaDB, able to ingest real English, Chinese, and Japanese repair material, retrieve applicable passages with sources, and support a measured workshop pilot.

Keep the existing systems separate for this work. The FastAPI application is the earlier structured-service prototype; the Flask application is the document assistant. Neither résumé requires merging them. Reuse their existing services, processor, vector store, interface, and ranking code.

Technical completion, workshop adoption, and historical attribution are separate gates. New code can demonstrate current capabilities. It cannot establish that they existed during the December 2025–January 2026 internship. Preserve commit history, original test reports, and original dates. Record new repairs and evaluations with their actual dates.

The first résumé's description of a stalled replacement can coexist with a later successful RAG assistant if the chronology is explicit: image experiment → structured API prototype constrained by data → document RAG prototype → later repairs and workshop rollout. Do not describe the entire project as both stalled and operational without naming the stage.

### Working assumptions

- One developer; no workshop records or authorised manual corpus supplied yet.
- Existing 14 Markdown notes remain development fixtures pending a mechanic's review; they are not counted as 500 manual pages.
- The initial shared rollout is a small internal workshop service. Retain Flask and local ChromaDB persistence behind one application process; avoid a distributed redesign until measured concurrency requires it.
- Proposed categories, evaluation sizes, and operating thresholds below are planning decisions, not existing results.
- Preserve the existing uncommitted `.gitignore`, `PROJECT_SUMMARY.md`, `SYSTEM_DESIGN.md`, and assistant folder changes. This planning task adds only this document.

## 2. Claim-by-claim baseline and completion evidence

| Résumé claim | Repository evidence inspected | Work or evidence still needed | Completion gate |
|---|---|---|---|
| FastAPI + PostgreSQL | FastAPI routes, SQLAlchemy models and sessions exist | Reproduce installation, clean database setup and successful route requests | Clean-checkout run with actual PostgreSQL |
| Seven automotive endpoints | Six domain/router routes are registered; compatibility checker exists as a service | Add one compatibility route and count query routing explicitly | OpenAPI lists the seven routes in section 4 |
| Alembic migrations | Three revisions exist for parts tables | Resolve complete-schema creation versus startup `create_all`; verify fresh and existing databases | `alembic upgrade head` produces the required schema without startup repairing it |
| Structured logging | `structlog` configuration and event calls exist | Correlate requests and verify failure events without secrets | Successful and failed requests produce parseable, attributable events |
| Docker orchestration | Dockerfile and Compose exist | Dockerfile copies missing `config/`; image omits migrations; unused Redis/Neo4j are required | Compose builds, migrates and starts from empty volumes |
| PostgreSQL + Google hybrid retrieval | Full-text SQL, fallback, storage and cache are written | Constructor contract broken; filtering/cache behaviour needs tests; Google account eligibility unknown | Local and external paths demonstrated separately; live Google result requires eligible access |
| eBay adapter uses same contract | Adapter inherits base but targets retired Finding API | Align contract; use Browse API for current live work | Both adapters pass the same contract tests; live eBay evidence is recorded separately |
| Free-text extraction and routing | Regex/word lists extract fields; classifier loading exists | Year is a string; lowercase codes and mileage shorthand are limited; parts/specs routing returns placeholders | Held-out parsing cases and end-to-end route cases pass |
| CV failure and pivot | Commits show image work and December 30 pivot; January 1 commit mentions static information | Obtain original experimental evidence or describe abandonment and observed limits accurately | Dated chronology distinguishes observed failure, hypothesis and decision |
| Gemini + ChromaDB RAG | Embeddings, retrieval, reranking, generation and Flask interface exist | Supported SDK, reproducible startup, error handling, source fidelity and deployment | Real document question produces a source-supported answer on the deployed version |
| Folder scoring + regex + filters + reranking | Those stages exist in source | Validate distance metric, canonical metadata and applicability; remove generic-document exclusion | Trace shows each stage before generation and regression tests pass |
| Multilingual PDF/Word ingestion | Markdown reader exists; PDF and DOCX libraries are declared | Implement extraction, page provenance, structure handling and scan handling | EN/CN/JP PDF/DOCX matrix passes on representative real files |
| Chroma schema and case-filter blockers debugged | Sanitiser and case-preserving extraction code exist | Reproduce each failure, fix at the common boundary, retain regression cases | Before/after reproductions and passing tests; production label only if incident records exist |
| 500+ pages | Existing library is 14 Markdown files; summaries report 108 chunks | Acquire authorised manuals; verify usable, unique physical pages | Auditable corpus manifest shows at least 500 accepted unique pages |
| 90% across eight diagnostic categories | Eight smoke questions check keywords and source folders | Independent retrieval labels, fixed metric, development experiments and held-out run | Predeclared metric reaches target on the frozen test set; failures remain reported |
| Month of live mechanic feedback | No evidence inspected | Run actual pilot and retain feedback tied to query/version | At least 30 calendar days of structured, attributable live feedback |
| Used by 24 mechanics | No evidence inspected | Real onboarding and actual usage by distinct people | 24 verified mechanic identities each complete at least one real repair query |
| Company's first AI system | Cannot be established from source | Authorised supervisor confirms scope and prior systems | Written, dated confirmation; otherwise omit “first” |
| Still used six months after internship | No evidence inspected | Historical workshop records around July 2026, or a newly dated adoption claim | Historical evidence for the exact original claim; a new rollout uses its own six-month date |

## 3. Scope map and implementation order

Read every caller before modifying a shared function. Re-run only the affected checks plus the release gates. Proposed new test files below are small regression suites, not a new framework.

| Work area | Existing code/callers to reach | Tests/fixtures/config/docs to reach |
|---|---|---|
| API routes | `app/main.py`, `app/api/v1/parts.py`, `query.py`, `specifications.py`, existing compatibility service | `app/schemas/parts.py`, endpoint fixtures, OpenAPI assertions, `app/static/index.html` if result shape changes, README examples |
| Retrieval adapters | `base_adapter.py`, `google_cse_adapter.py`, `ebay_adapter.py`, `parts_search.py` | `test_hybrid_system.py`, `test_google_cse.py`, provider-response fixtures, `app/core/config.py`, `.env.example` |
| Entity parsing/routing | `entity_extractor.py`, `query_service.py`, route dispatch and valuation/paint consumers | `test_entity_extractor.py`, `test_query_routing.py`, generated training-data scripts and model build instructions |
| Database/release | `app/db/models.py`, `session.py`, `alembic/env.py`, all existing revisions, seed/init scripts | `tests/conftest.py`, specifications fixtures, PostgreSQL integration tests, Dockerfile, Compose, root requirements |
| RAG startup/models | assistant `src/config.py`, `embeddings.py`, `rag_system.py`, `vector_store.py`, `app.py`, `web_app.py`, `setup.py` | Assistant requirements, `.env.example`, startup and embedding failure tests, quickstart |
| Ingestion | `src/document_processor.py`, `DocumentChunk`, vector-store writes, source formatting | Small EN/CN/JP fixtures, metadata/chunking tests, corpus manifest, PDF/DOCX/OCR requirements as justified |
| RAG retrieval/evaluation | `extract_vehicle_info`, `query_with_reranking`, `_calculate_relevance_score`, rule inclusion | Filter regression tests, retrieval-only evaluator, frozen questions/labels, experiment records |
| Workshop rollout | Flask query handling, template/source display, operational configuration | Identity and feedback records, one deployment recipe, backup/restore check, health and concurrency smoke checks |

Use development fixtures and a disposable PostgreSQL database. The current specifications tests create rows using the application's global `SessionLocal`, while the client dependency uses a different SQLite database. Repair that isolation before running those tests against a machine with real data. Never let a fixture truncate or drop workshop tables.

## 4. Phase A — make the structured service demonstrable

### A1. Fix adapter contracts and hybrid search

Estimated effort: 3–5 working days. Dependencies: none for fixture tests; real credentials for live checks.

1. Standardise `BasePartsAdapter`, Google and eBay on the same constructor and signatures. The base currently accepts a config dictionary, but both subclasses pass `name` and `rate_limit`. The base declares async operations while the current subclasses and search engine use synchronous calls. Prefer the existing synchronous search path for the smallest complete repair; update the base and its callers consistently.
2. Keep blocking search/HTTP/database work in a synchronous route or a helper dispatched once to a worker. Do not block an async event loop or concurrently share a SQLAlchemy session across workers. Preserve awaited NHTSA calls on their existing async path.
3. Define the shared result fields using the existing normalisation/persistence shape: source, source ID, name, description, part number if known, source URL, seller, price and currency if known, retrieval timestamp, and shipping/fit evidence. Unknown price stays unknown; unknown shipping or fit must not become a verified fact.
4. Prove fallback triggers after vehicle, price and shipping eligibility are considered. Twenty unusable local results must not suppress web retrieval.
5. Repair cache identity to include every result-affecting input: query, vehicle, filters, limit and Singapore-only setting. Prevent cross-filter cache reuse. Keep the existing expiry mechanism.
6. Preserve independent provider failure handling: one timeout must not stop the other provider or discard valid local results. Record attempted sources and failed sources separately from successful sources.
7. Make external writes idempotent by source/source ID. Save listing URLs and refresh timestamps; update prices on refresh. Maintain explicit synthetic versus external provenance.
8. Retain rollback on persistence failure. Do not hide a failed database operation behind a successful empty response without a logged error.
9. Google: repair the existing adapter and demonstrate it with recorded provider fixtures. Check whether an existing eligible account can make a live call before claiming live operation. Google Custom Search is closed to new customers and existing access ends January 1, 2027. A fixture proves the adapter contract, not a current live integration. [Google documentation](https://developers.google.com/custom-search/v1/overview).
10. eBay: retain the original Finding adapter in the historical record; replace its current network implementation with supported Browse API calls, OAuth and a documented supported marketplace/delivery setting. Finding API was decommissioned February 4, 2025. Do not infer Singapore support from the old `EBAY_SG` setting. [eBay deprecation record](https://developer.ebay.com/develop/get-started/api-deprecation-status), [Browse API](https://www.developer.ebay.com/api-docs/buy/static/api-browse.html).

Tests: both adapter constructors; same arguments/result shape; malformed provider data; absent price; timeout and rate-limit responses; no-key disabled providers; local-only hit; local scarcity; local hits eliminated by fit filters; independent provider failures; deduplication; cache separation; database rollback. Full-text tests use PostgreSQL, not SQLite.

Done: a demonstration can show a local catalogue hit, an external fallback, a repeated cached request and a provider failure without losing local results. Record whether each demonstration used fixtures or a live provider. If Google live access is unavailable, keep that precise claim blocked and use a supported current supplier source for deployment rather than inventing successful Google access.

### A2. Complete seven routes and query execution

Estimated effort: 3–4 days. Dependency: A1 for parts execution.

Count these seven automotive routes. Health, documentation and the homepage do not count.

| # | Method | Route | Required demonstration |
|---|---|---|---|
| 1 | POST | `/api/v1/query` | Free text returns typed entities and executes a service |
| 2 | POST | `/api/v1/parts/identify` | Text search returns catalogue or provider results |
| 3 | POST | `/api/v1/diagnostics/troubleshoot` | Known code returns existing diagnostic guidance; unknown code is explicit |
| 4 | POST | `/api/v1/valuation/estimate` | Valid vehicle and mileage produce a reproducible estimate with assumptions |
| 5 | POST | `/api/v1/paint-code/lookup` | Existing guidance identifies verification steps and uncertainty |
| 6 | GET | `/api/v1/specifications/{vin}` | Valid VIN retrieves/cache-reads real specifications; unsupported VIN is explicit |
| 7 | POST | `/api/v1/parts/compatibility` | Thin route calls existing `CompatibilityChecker` for a catalogue part and vehicle |

Tasks:

1. Add route 7 to the existing parts router and reuse the compatibility service. Validate part existence and vehicle fields. Make incomplete fit information explicit, including engine/trim constraints. A confidence score is not proof of physical fit.
2. Return integer year and mileage from the extraction boundary; keep make/model canonical. Handle lowercase VINs/codes, multiple codes, `75,000 km`, `75000km`, `75k km`, and explicit miles. Convert explicit miles to kilometres once and label the unit; bare `75k` requests clarification rather than guessing. Do not treat an engine/part number as mileage or year merely because digits match.
3. Preserve multiword makes and model boundaries; test Mercedes-Benz, Land Rover and common workshop aliases. Reject malformed VIN characters at the API boundary. Do not demand a North American checksum for every market's VIN.
4. Replace the parts/specifications placeholder handlers with calls to existing shared services. Supply an isolated DB session to the parts operation. Extract a small shared VIN lookup only if needed to avoid duplicating the existing endpoint's cache/decoder logic.
5. Reproduce the current valuation string-year failure; fix it once at the typed extraction boundary and verify all consumers. Use missing-value checks that accept zero mileage.
6. Reproduce training with existing scripts. Ship/build the intent artifact reproducibly rather than returning unknown for every query because a git-ignored model was absent. Preserve existing intent labels; document uncertainty and missing-data responses.
7. Preserve HTTP errors such as unsupported image search as their intended status instead of converting every exception to a 500. Update form-versus-JSON examples to the actual contract.
8. Clearly label valuation as a rule-based estimate. Remove fabricated comparable listings or mark them as synthetic examples. Neither this claim nor the plan requires inventing market coverage.

Tests: parser table with at least 40 independently written boundary cases; one complete routed request per supported intent; missing data; invalid VIN; zero mileage; known/missing part; unknown fit; year range boundaries; actual payload/output shapes. Assert that parts/specification handlers no longer return placeholder execution messages. Stub outbound APIs for normal tests and keep live demonstrations separate.

Done: OpenAPI has exactly the seven listed routes, each passes a success and validation/failure example, and representative free-text questions actually call the intended service. Diagnostic and paint coverage limits remain documented.

### A3. Make migrations, Docker and logging reproducible

Estimated effort: 2–4 days. Dependencies: A1–A2.

1. Compare all ORM tables to Alembic revisions. Existing revisions cover the enhanced parts schema, while startup calls `create_all` for the broader application. Ensure a new empty PostgreSQL database can reach the full required schema through Alembic alone.
2. Preserve published revisions unless confirmed unused; add the minimum missing migration. For an existing unmanaged database, compare the exact schema and back it up before any baseline stamping. Stamping is only appropriate when schema equivalence is established. Never use a blanket stamp to hide drift.
3. Verify upgrades on an empty database and a disposable copy of an existing schema. Check foreign keys, nullable external-price fields and the full-text GIN index. Do not test destructive downgrades on real data.
4. Remove the missing `COPY ./config` step. Include `alembic.ini` and revision files in the image. Choose one documented startup sequence: PostgreSQL health → one migration step → API. Remove runtime `create_all` as a substitute for migrations.
5. Remove unused Redis/Neo4j requirements from the minimal Compose startup. Keep persistent PostgreSQL storage. Supply actual secrets through environment configuration; distinguish sample credentials from production configuration.
6. Ensure the classifier is generated or supplied inside the release and the API process can read it. Remove unused heavyweight image/ML dependencies only after checking imports and surviving training scripts. Do not simultaneously rewrite the ML stack.
7. Verify structured success/failure events, request IDs, elapsed time, selected service and provider status. Redact keys and avoid logging raw customer identifiers or entire provider payloads unnecessarily.
8. Correct README setup and request examples so a fresh checkout reproduces the tested release.

Release check, on disposable volumes: `docker compose build`; start PostgreSQL; run `alembic upgrade head`; start API; exercise all seven routes; restart; verify retained records; verify a new request has attributable logs. Do not run `docker compose down -v` on workshop volumes.

Done: reproducible release evidence includes OpenAPI, migration output, representative requests, a Compose smoke report and redacted JSON log events.

## 5. Phase B — make the manual assistant dependable

### B1. Stabilise startup, SDK and index writes

Estimated effort: 2–3 days. No real manuals needed for unit work.

1. Migrate `google-generativeai` calls in embeddings and generation together to `google-genai`. Verify a currently supported embedding and generation model with official docs and a small live request when credentials are available. Pin tested versions; do not rely on preview names or model defaults inherited from January. [Google SDK guidance](https://ai.google.dev/gemini-api/docs/libraries).
2. Load the assistant's own environment file deterministically from its project directory. Move live-key validation to live-client startup so document-processing and mocked tests do not need API credentials.
3. Fix imports consistently for Flask, CLI, processor and index-builder entrypoints. Verify startup from both repository root and assistant directory.
4. Remove zero-vector substitution on embedding failure. The code currently substitutes 768 zeros even though the summary describes a rebuilt index with 3,072-dimensional embeddings. Validate dimensions, finite values and nonzero norms; fail or retry visibly.
5. Retry only transient errors with a bounded attempt/time budget. Authentication/schema errors fail immediately. Record failed documents so no successful ingest report silently skips them.
6. Record model ID, embedding dimensions, distance metric, corpus manifest hash and chunk settings beside each index release. Query/index settings must match.
7. Build a new index in a separate directory, validate it, then switch releases while query workers are stopped. Preserve the previous index for rollback. Do not reset the serving collection to rebuild it.
8. Make unchanged ingestion idempotent and remove obsolete chunks when a source changes or is withdrawn. Use IDs based on relative source path/hash and chunk location; file stems alone can collide across folders.

Tests: offline imports; invalid config; embedding failure produces no fake vector; dimensions mismatch; same-name files in different folders; repeated ingestion; replacement/removal; interrupted build leaves serving index intact; release manifest mismatch is detected.

Done: a fresh installation can build an index from fixtures and launch the assistant through documented commands; provider failure cannot silently poison the index.

### B2. Implement real PDF, Word and multilingual ingestion

Estimated effort: 5–8 days, plus corpus acquisition/review. B1 precedes indexing; extraction work can start immediately.

1. Extend the existing `DocumentProcessor` and `DocumentChunk`; retain Markdown. Add digital PDF via already-declared `pypdf` and DOCX via already-declared `python-docx`. Avoid a new ingestion framework.
2. Enumerate source types, languages, page counts and extraction outcomes into one manifest. Each document records ID, relative path, file hash, origin/licence approval, language, make/model/engine applicability, edition, physical page count, accepted/rejected pages and extraction method.
3. Extract PDF page by page and preserve physical page number plus printed page labels where available. Handle mixed pages independently. Empty/image-heavy or obviously broken text is flagged rather than embedded as usable text.
4. Read DOCX paragraphs and tables in document order. Preserve headings, row/column relationships, notes and units. DOCX lacks reliable physical page numbers; cite heading/table/paragraph IDs. Count it toward “pages” only using a recorded approved PDF rendering, with the rendering hash and tool version retained.
5. For scanned pages, use one OCR path supporting the actual EN/CN/JP corpus and verify all needed language packs. Add the OCR dependency only when scans require it. If OCR is deferred, explicitly exclude those pages and narrow the claim to text-based documents. This plan's full PDF goal includes scanning support if the acquired corpus contains scans.
6. Test simplified/traditional Chinese, Japanese mixed scripts, Latin engine codes, unusual Unicode spaces, multi-column text, rotated pages, merged tables, units, torque ranges and footnotes. Keep original-language text; do not translate entire manuals merely to make them count.
7. Preserve display text while normalising only retrieval keys. Never modify technical numbers or translate part identifiers during normalisation. Require mechanic review for low-confidence OCR of specifications; quarantine unresolved pages.
8. Chunk along headings and procedures, keeping numbered steps and table headers with their contents. Split oversized sections and enforce overlap smaller than chunk size. Starting experiments use the existing character-based units so comparisons are explicit; do not call character counts tokens.
9. Attach chunk provenance: source ID, document hash, page/paragraph span, heading, language, canonical applicability, folder, chunk index and stable ID. Keep legal/access metadata in the manifest, outside the generation prompt unless relevant.
10. Count **accepted, unique physical manual pages**, not chunks, overlapping windows, translated copies or duplicate editions of identical pages. Use automated duplicate flags and manifest review; do not pad the corpus with generated notes.

Minimum fixture matrix: each of PDF and DOCX in EN/CN/JP; PDF scans in each language if scanned manuals are supported; one table-rich document; one two-column/rotated PDF; one corrupted/encrypted file; two sources with the same basename. Every fixture has expected text, identifiers and provenance assertions. Public/owned fixture documents can be small; authorised workshop manuals remain outside the public repository.

Done: at least 500 accepted unique pages from authorised real repair sources are searchable; failed pages are accounted for; every result links back to a readable source location. If 500 pages are not available, ship the real smaller corpus and state its actual size.

### B3. Correct metadata, filters and reranking

Estimated effort: 3–5 days. Dependencies: B1; B2 fixtures for provenance.

1. Define one schema at the processor/vector-store boundary. Use scalar strings/numbers/booleans for portability across the tested pinned Chroma version. Omit unsupported nulls; do not turn missing values into fake strings. Keep raw complex metadata separately in the manifest.
2. Canonicalise query and indexed applicability identically: trimmed/casefolded make/model/engine keys, explicit aliases, integer year ranges and explicit applicability scope. Preserve readable original names separately. Arrays converted to comma-separated strings must not be treated as exact-match scalar makes.
3. Reproduce the case bug with the actual stored key variants (`BMW`, `bmw`, `Bmw`) and demonstrate they retrieve the same applicable source after rebuilding. Index migration and query normalisation must change together.
4. Build filter expressions supported by the pinned Chroma version. Avoid empty operators and invalid single-child compound expressions. Equality, range and logical behaviour need direct tests. Current documentation describes `$and`/`$or`; verify the installed version rather than assuming every current feature existed in the older index. [Chroma filters](https://docs.trychroma.com/docs/querying-collections/metadata-filtering).
5. Replace the current broad OR of make/model/year/engine. Matching the year alone must not admit a different vehicle make. For known vehicle details, combine applicable constraints; where details are absent, apply only confident constraints and return uncertainty.
6. Include generic documents explicitly. Use a vehicle-specific candidate query and a generic candidate query, combine/deduplicate, then rerank. Do not label documents with unknown applicability as universal. When Toyota has no vehicle-specific manual, return applicable general guidance with a coverage warning rather than a BMW-only answer.
7. Keep multilingual text in retrieval using a verified cross-language embedding setup. Test EN questions retrieving CN/JP passages and vice versa. No promise of multilingual quality follows merely from successful text extraction.
8. Set/record the vector distance metric. Validate its score conversion with known close/far examples instead of assuming `100 - distance * 100` yields a calibrated similarity. Expose scores as ranking scores, never diagnostic probabilities.
9. Retain existing folder priorities as a starting point. Generalise exact-code extraction instead of checking only four hard-coded codes. Apply make/model/engine bonuses using extracted canonical fields. Prevent folder priority from overriding conflicting applicability.
10. Begin with 15 candidates and top five context passages as the current code does. Deduplicate materially overlapping passages. Increase candidate count or cap repeated source passages only when development evaluation justifies it.
11. Include the complete concise workshop policy, independently of retrieved candidates. The current rule lookup takes just one chunk. Policy injection never counts toward retrieval precision.

Regression examples: `P0300 on Honda Accord` still retrieves the generic P0300 guide; lowercase `bmw` matches BMW metadata; two 2007 manuals for different makes do not cross-match; conflicting engine excludes a passage; unknown make produces a coverage limit; generic documents remain eligible; zero/one/multiple filter clauses validate; all rule sections are loaded; reranking is deterministic on tied scores.

Done: an inspectable query trace contains parsed fields, validated filters, retrieved candidate IDs/distances, score components, selected passage IDs and policy version before generation. The two blocker reproductions are saved with dates. Only call them production incidents if an actual deployed incident has supporting records.

### B4. Ground answers and expose usable sources

Estimated effort: 2–3 days. Dependencies: B2–B3.

1. Update the existing prompt to use supplied sources for factual repair details. If a torque value, part number or diagnostic conclusion is unsupported, ask for the required vehicle/source information or state the coverage limit. Remove instructions that encourage inventing common defaults for vehicle-critical specifications.
2. Require source IDs/page or section citations for technical statements. Include manual edition and applicability where needed. A general source list alone does not establish which statement it supports.
3. Display source location, short supporting excerpt and retrieval rank in the existing template. Keep the interface simple and usable on workshop phones: keyboard access, readable labels, loading/error states and feedback controls.
4. Treat document content as evidence rather than instructions. Include one malicious-document test so manual text cannot override application rules or extract secrets. Restrict source-file links to approved paths and enforce user access.
5. Handle unknown vehicles, contradictory manuals, no results, unsupported languages and unavailable Gemini with explicit responses. Preserve authoritative edition/applicability distinctions instead of averaging conflicting specifications.
6. Keep image features outside this claim's critical path. If left exposed, validate upload size/type and ensure the image answer is labelled approximate. Do not imply image recognition contributed to document retrieval when it did not.

Tests: known source-supported question; absent torque number; out-of-corpus question; conflicting applicability; provider timeout; citation/source mapping; injected instructions in a source; invalid/oversized request. Mechanic review separately evaluates correctness and dangerous omissions.

Done: answers can be checked against the exact retrieved manual passages; unsupported requests receive useful limits and next questions.

## 6. Phase C — earn a defined retrieval result

Estimated effort: 4–7 developer days for evaluator/experiments, plus mechanic labelling time. Target attainment is uncertain; the honest outcome may be below 90%.

### C1. Freeze the measurement before tuning

Use **passage Precision@5** as the proposed headline metric because the current assistant retrieves five context passages. For each answerable query, count relevant, distinct passages in the first five ranks and divide by five. Missing ranks count as zero. Remove exact/materially overlapping duplicate passages before choosing ranks. A relevant passage must help answer the question and apply to the vehicle/edition; a shared keyword or folder is insufficient.

Relevance is adjudicated by a mechanic against source content. Do not count injected workshop rules as retrieved passages. Do not equate answer keyword tests, Hit@5, Recall@5 or answer accuracy with Precision@5.

Predeclare eight diagnostic categories, with one primary category per question:

1. Crank/no-start and starting systems.
2. Rough idle and stalling.
3. Misfire and ignition.
4. Fuel delivery and pressure.
5. Cooling and overheating.
6. Electrical supply and charging.
7. Sensor, emissions and drivability faults.
8. Mechanical noise and known failure patterns.

Record assignment rules for overlaps before labelling. These are proposed categories, not the existing smoke test's eight unrelated questions. If the available manuals do not cover a category, record the coverage gap; do not replace it after seeing test scores.

Proposed answerable set: 480 independent questions, split into 240 development and 240 held-out. Each split contains 30 per category and, where realistic for the workshop, 10 EN/10 CN/10 JP per category. A question and its translations/paraphrases stay in the same split. Record departures from this balanced design if real query availability differs.

Add a separate 48-question negative set for unsupported vehicle details, missing manuals, malformed codes, conflicts and uncertain specifications. Score correct abstention separately, not as additional precision successes. Retain realistic questions with sparse evidence; do not select only questions that happen to have five relevant chunks.

Question records: query ID, original language/text, primary category, vehicle fields, real versus independently authored provenance, source locations, expected applicability and split. Candidate labels: passage/source ID, relevant/irrelevant, reason, reviewer, date and adjudication. Relevance can be judged across pooled candidates from the compared systems; reviewers do not see system identity, rank or generated answer. The frozen test pool must be reviewed before final scoring, including new final candidates, without changing the model based on test results.

A second mechanic independently reviews a stratified subset, including disagreements and high-consequence specifications. Retain disagreement rates and final decisions. Gold references must be traceable to manuals rather than generated by the assistant being tested.

### C2. Compare a bounded sequence of experiments

1. Baseline: repaired vector-only retrieval with valid embeddings and current source provenance.
2. Chunk experiments: 800/1,200/1,600 characters; 10%/20% overlap; preserve section/table rules. Six initial configurations, keeping model and corpus constant.
3. Choose the best development configuration using the predeclared metric and latency/coverage constraints.
4. Embedding experiments: compare the baseline verified model setup with one officially supported alternative model or output-dimension/task configuration. Model availability is checked at execution time. Changing dimension alone is labelled dimension tuning rather than a new model. If no meaningful alternative is available, record that limit and describe the actual strategy experiments precisely.
5. Retrieval ablations: vector only → applicability plus generic candidates → folder priority → exact entity/code bonuses → final deduplication/reranking. Report individual additions so “multi-stage” has evidence.
6. Record corpus/index hash, model/dimensions/metric, chunk size/overlap, filter/rerank settings, commit, date, latency, errors and all query-level ranks for every experiment.
7. Freeze the selected release, run held-out evaluation once, and retain the full result. If later tuning uses this test set, obtain a new held-out set before describing the next result as independent.

Required report: overall and per-category Precision@5; per-language values; Hit@5 and recall against labelled references as secondary measures; number of evaluated/skipped/failed queries; uncertainty with query-level bootstrap intervals; coverage; retrieval latency. Do not treat five passages from one query as five independent statistical samples. A high point estimate on a small sample does not prove an equally high population minimum.

Target gate: observed held-out macro Precision@5 at least 0.90 across the eight frozen categories. Report each category even when the aggregate passes. Saying “90% in each of eight categories” additionally requires each category to meet 0.90; the aggregate does not establish that. At 240 questions with five ranks each, 1,080 relevant ranks out of 1,200 gives 90% in the equal-weight design.

If Precision@5 plateaus because a real query has only one useful passage, report that limitation and the actual score. A future metric can be predeclared for another study, but do not rename a retrospective Hit@5 success as the original precision result.

### C3. Keep answer correctness separate

Mechanics review a stratified subset of generated answers for factual support, applicability, useful next checks, source-citation fidelity and unsupported specifications. Maintain a separate list of consequential errors and rollout blockers. Retrieval precision is not diagnostic accuracy and is not proof that a repair recommendation is safe.

Done: a reproducible retrieval-only evaluator, frozen labels, raw ranked results, experiment comparison, held-out report and separate answer review exist. The résumé uses the measured metric and actual value, including its evaluation context.

## 7. Phase D — production pilot, feedback and adoption

### D1. Prepare one internal deployment

Estimated effort: 3–5 days. Dependencies: B release and a reviewed corpus; deploy a limited pilot while C develops, but retain version boundaries.

1. Choose one company-controlled host and one documented release method. Retain one Flask application process with bounded request handling initially; run it with a production WSGI server and debug disabled. Test the selected Gemini client and Chroma access under concurrent requests; serialize unsafe shared-client access if needed. Load-test realistic overlapping queries before deciding a Chroma server is necessary.
2. Put the service behind HTTPS and existing company identity/access controls. Prefer identity supplied by an established proxy/provider over building authentication. Distinct identity is needed to substantiate the 24-person claim; anonymous browser sessions cannot prove distinct mechanics.
3. Keep manuals private; restrict source viewing to authorised users. Store secrets outside the image and repo. Avoid customer names, registration plates and VINs in evaluation exports unless required and appropriately restricted.
4. Add bounded query size, image limits if relevant, request deadlines and per-user request limits. Separate liveness from readiness; readiness verifies the loaded index/release without making a paid generation call on every probe.
5. Persist manual originals, manifest, index release and feedback records. Keep one backup and a tested restore procedure. Index switching is an offline operation with an old release available for rollback.
6. Log release/index/model version, request ID, pseudonymous mechanic identity, timing, provider errors and chosen source IDs. Define retention and who may export raw questions. Use aggregate evidence publicly; keep identities in an authorised private record.
7. Measure p50/p95 latency, failure rate and cost per query. Provisional pilot thresholds: p95 under 15 seconds for text queries under measured pilot load, at least 98% completed requests excluding deliberate input rejection, no known unresolved critical answer-support errors. These are proposed launch thresholds; revise before launch based on actual workshop needs and retain the decision.
8. Provide a one-page operator guide: start/restart, health, model/index version, credentials update, manual refresh, backup/restore and rollback. Give a mechanic guide for questions, citations, uncertainty and feedback.

Done: a real internal URL, recorded release, access control, successful restore, concurrent-use smoke check and named company operator. A laptop demo or Docker build alone does not establish production use.

### D2. Run 30 calendar days of structured feedback

Estimated effort: 1–2 days to instrument, then 30 elapsed days with brief weekly reviews. Company participation required.

Use an existing PostgreSQL table or a small private feedback store; avoid an analytics platform. The UI adds useful/partly useful/not useful plus a short reason. Every record stores feedback ID, query ID/time, mechanic pseudonym, category, language, release/index version, retrieved source IDs, relevance assessment, correction and resolution. Record source relevance separately from answer usefulness; thumbs-up alone cannot validate precision.

Rollout:

1. Start with 3–5 mechanics and a constrained approved corpus for several workshop days.
2. Review failures daily at first. Fix source extraction, applicability or unsupported-answer defects before inviting the full group.
3. Expand to the actual available mechanics, targeting 24. Invite and train them in person or through company-authorised channels. This plan does not send messages or assume participation.
4. Track invited, activated and active users separately. Define active as at least one real repair query in the reporting window; additionally report repeated weekly use. Do not count load-test accounts, developer tests or shared terminals as unique mechanics.
5. During the 30-day window, aim to review at least 80 real repair queries spanning the eight categories. Label this a pilot sample, report actual coverage, and do not pad missing categories with synthetic live feedback.
6. Review weekly: source relevance, missing manuals, error trends, usage, latency and cost. Log fixes and version changes. Keep final validation distinct from feedback used to tune the system.
7. At the end, have the designated mechanic/supervisor review the aggregate report and confirm its scope. Do not claim all 24 used it if fewer actually did; report the verified count.

Done: 30 actual calendar days of attributable feedback, the real number of participating mechanics, source-relevance judgements, dated corrections and a reviewed report. A retrospective summary cannot replace missing raw feedback.

### D3. Establish sustained adoption and “first AI” separately

1. Ask the company operator for a factual record of whether an earlier comparable AI system existed and what “first” means. Without confirmation, use “built a workshop RAG assistant.”
2. For the exact “still in use six months after the internship” claim, inspect historical deployment/use records around July 2026 and evidence tying that deployed version to internship work. Current code and new logs do not prove that historical statement.
3. If no historical evidence exists, start adoption evidence at the real new deployment date. Review actual use in the sixth month after rollout, including number of active mechanics, example redacted queries, operator confirmation and maintenance handover.
4. A rollout beginning after October 9, 2026 cannot earn six months of new adoption before April 2027, and any later launch moves that date later. State “six months after rollout” for that evidence; do not silently retain “after the internship.”

Done: actual month-six use evidence and the correct time reference. Inviting 24 users, leaving a server running or waiting six months does not establish continued use.

## 8. Historical retrospective and interview evidence

Estimated effort: 1–2 days using available evidence; company records can extend it.

Existing Git history provides these leads:

- December 19–20, 2025: initial repository/image work.
- December 30, 2025: `c6d427f`, “redoing, now its google car parts engine”.
- January 1, 2026: `aecf02a`, “problems faced, as lack of actual information and static information”.
- January 1, 2026: `c0bb2d3`, secrets-removal commit.
- The existing assistant summary describes files dated January 2, 2026; it also states that the folder was moved here in October and is not committed. File dates are supporting clues, not proof of workshop deployment.

Write a short retrospective preserving these distinctions:

1. Original CV objective and available dataset. Obtain original training/annotation/benchmark records if they exist; otherwise say the approach was explored/abandoned and identify documented constraints. Deleted image files alone do not prove a model failed an evaluation.
2. Why the structured prototype was chosen, what worked in the source, and the specific data bottleneck: synthetic catalogue, five fault codes, small static pricing/paint coverage and unsupported live providers.
3. Why retrieval over manuals was a later direction, what source material was actually available at that time, and what remained a prototype.
4. New engineering repairs and adoption work, dated as current follow-up. Include migration/SDK/provider changes so interview answers do not imply they were already present in January.

Public evidence pack: architecture diagram, seven-route table, representative redacted requests, clean-install instructions, ingestion fixtures, retrieval evaluator, aggregate results and incident regression tests. Private company pack: authorised corpus manifest, manual pages, raw mechanic identities/feedback, live provider evidence, deployment records and supervisor confirmations. Do not publish company manuals merely to prove the résumé.

## 9. Schedule, dependencies and actions while the user is unavailable

Effort is an estimate, not a promise. For one developer, the listed development tasks total roughly **29–48 working days**; allow another **4–6 days** for labelling coordination and evidence review. Budget **7–11 engineering weeks** before all technical and evidence reports are complete. Real data access, review availability, scan complexity and provider eligibility can extend that. A limited pilot may begin earlier and overlap the later evaluation; one month of actual feedback and six months of adoption remain elapsed-time gates.

| Order | Deliverable | Dependencies | Can progress without another answer? |
|---|---|---|---|
| 1 | Claim ledger, historical chronology, code baseline | Existing repository | Yes |
| 2 | Isolated tests and API adapter/parser repairs | Existing code and fixtures | Yes when implementation is requested |
| 3 | Seven working routes, clean migrations/Compose | Steps 1–2 | Yes with local PostgreSQL/Docker availability |
| 4 | RAG SDK/import/index failure repairs | Existing code, mocked calls | Yes; live model check needs valid credentials |
| 5 | EN/CN/JP PDF/DOCX fixtures and ingestion | Step 4 for indexing | Yes with owned/public fixtures |
| 6 | Applicability/filter/reranking regressions | Steps 4–5 | Yes |
| 7 | Evaluator, frozen protocol, baseline reports | Steps 5–6 | Code/protocol yes; mechanic labels need participation |
| 8 | Authorised 500-page corpus and quality review | Company sources/access | No; templates and fixture pipeline can be completed |
| 9 | Real held-out benchmark and final report | Steps 7–8 plus reviewers | No for claimed results; development evaluation can continue |
| 10 | Internal deployment and pilot | Reviewed release, company host/access | Deployment recipe/local checks yes; company rollout needs access |
| 11 | 24 real participants and 30-day feedback | Real deployment and mechanics | Instrumentation yes; participation/time cannot be simulated |
| 12 | Month-six adoption and first-AI confirmation | Actual workshop records | Evidence checklist yes; outcome cannot be created locally |

Next independent implementation batch, once implementation is requested: fix test DB isolation; reproduce/fix adapter constructors and signatures; add constructor/result contract tests; reproduce/fix typed year extraction and its valuation caller; add parsing edge cases; wire parts/specs dispatch and compatibility route; complete migration/Docker smoke setup. In parallel as ordinary work scheduling, prepare RAG fixtures and the evaluation schema; no sub-agents or company communication are required.

Dependency gates:

- Without authorised manuals, complete the ingestion engine using fixtures but do not claim 500 pages or manual coverage.
- Without provider access, complete adapter contract checks but label live calls pending.
- Without mechanic labels, complete the evaluator and publish no invented precision result.
- Without company host/access, complete a local deployment rehearsal but keep production blocked.
- Without participant records, report no user count.
- Without historical evidence, use current-project dates and new rollout timing.

## 10. Résumé wording unlocked by actual evidence

Do not put unfinished targets into past-tense achievements. Use the smallest verified claim at each stage, replacing bracketed fields only from retained results.

**Current source-backed prototype, pending runtime verification:**

> Developed an automotive assistant prototype with FastAPI, PostgreSQL and rule-based query extraction; explored local catalogue retrieval and external-search adapters, then documented limitations caused by sparse static data.

> Prototyped a Gemini/ChromaDB assistant over a small Markdown knowledge base with vehicle metadata filters, folder priority scoring and passage reranking.

These still need correct authorship/employment attribution. Code existence establishes implementation, not runtime reliability or business deployment.

**After structured-service completion, with the new work correctly dated:**

> Built and verified a FastAPI/PostgreSQL service with seven routes covering free-text routing, parts search, diagnostics, valuation, paint guidance, VIN specifications and compatibility; packaged it with Alembic migrations, structured logging and Docker Compose.

> Implemented PostgreSQL full-text retrieval with external-search fallback behind a shared adapter contract, and parsed vehicle queries into typed VIN, fault-code, year, mileage, make and model fields.

Name Google only when the relevant implementation/test/live scope is accurate; name Browse API for the new eBay implementation. Do not describe rule-based valuation as validated market pricing.

**After corpus and benchmark completion:**

> Built a Gemini/ChromaDB RAG assistant over [actual accepted page count] pages of authorised EN/CN/JP repair material, with PDF/DOCX extraction, source citations and applicability-aware retrieval.

> Achieved [actual score]% passage Precision@5 on [actual held-out count] independently labelled diagnostic queries across eight categories, after chunking, embedding and reranking experiments.

If the score is below 90%, state the actual value or omit the figure. If only Hit@5 was measured, call it Hit@5. State a different category count if coverage differs.

**After the real workshop pilot:**

> Deployed the assistant for [verified active mechanic count] mechanics and iterated using [actual elapsed period] of structured feedback on live repair queries.

Add “first AI system” only after company confirmation. Add “still in use six months after rollout” only after month-six evidence. Keep “six months after the internship” only if the historical July 2026 statement is verified. New accomplishments belong under a dated follow-up project or a clearly identified post-internship continuation.

## 11. Final acceptance checklist

- [ ] Historical statements are tied to contemporaneous evidence or explicitly qualified.
- [ ] Seven named domain/router routes work; compatibility is actually exposed.
- [ ] Typed extraction and real parts/specs routing pass regressions.
- [ ] Google/eBay contract tests pass; live operation is identified separately.
- [ ] Fresh/existing-schema migration checks and Compose smoke checks pass in disposable environments.
- [ ] Request logs demonstrate attribution and error handling without exposing secrets.
- [ ] Supported Gemini SDK/model setup and compatible Chroma release are recorded.
- [ ] Failed embeddings cannot silently enter the index; rebuild and rollback are tested.
- [ ] EN/CN/JP PDF/DOCX extraction and any claimed OCR pass representative fixtures.
- [ ] At least 500 unique usable authorised manual pages are accounted for, if that figure is claimed.
- [ ] Metadata/case/filter/generic-source bugs have reproductions and regression checks.
- [ ] Reranking and technical claims can be traced to their sources and score components.
- [ ] Precision metric, categories, labels and splits were frozen before final testing.
- [ ] Raw results support the reported score; all categories, languages and failures remain visible.
- [ ] Live feedback ran for the actual stated period and reviewed source relevance.
- [ ] User count measures distinct real mechanics; active use is separated from invitation/access.
- [ ] Company confirms any “first AI” claim.
- [ ] Month-six adoption has actual usage evidence and the correct time reference.
- [ ] Final résumé distinguishes internship work from subsequent reconstruction and improvements.

Skipped scope: merging both applications, a new agent framework, fine-tuning, a vector database redesign, a new frontend, Kubernetes, extra supplier adapters and image recognition. None is necessary to substantiate these claims.

Remaining risk: code can be completed locally; corpus rights/access, independent mechanic review, provider eligibility and actual adoption require external evidence. Neither 90% retrieval nor 24-person usage nor six-month retention is guaranteed by implementing this plan.

## 12. Implementation update — 9 October 2026

Implementation is now authorised and the first build has been completed locally. The complete per-feature record, verification commands and remaining limits are maintained in [BUILD_STATUS.md](BUILD_STATUS.md). Update that record for every new feature and commit/push the implementation and Markdown together as requested.

Completed in this batch:

- [x] Isolated tests, typed extraction, actual parts/specifications dispatch and the seventh compatibility route.
- [x] PostgreSQL full-text retrieval, shared Google/eBay Browse contract, independent fallback, honest null/currency/shipping data, persisted listing provenance and complete search-cache inputs.
- [x] Compatibility case/engine/trim checks, validation/request IDs, sanitised failures and removal of fabricated valuation comparables.
- [x] New migration retaining existing catalogue data, model/schema alignment, minimal pinned dependencies and migration-first Docker recipes. Docker execution remains pending.
- [x] Supported Gemini SDK, embedding integrity/pacing/retry and generation retry/timeout handling.
- [x] EN/CN/JP text PDF/DOCX fixtures, bounded chunks, source locations/IDs, manifest/page accounting and explicit rejection of scans needing OCR.
- [x] Canonical Chroma metadata, dynamic applicability filters preserving generic passages, folder/code reranking, separated policy and model-aware index releases preserving the legacy index.
- [x] Local web validation/source display, provenance-backed anonymous feedback and independent-label Precision@5 evaluation infrastructure.
- [x] Actual live Gemini embedding build: 138 chunks from the existing 14-note library. This is zero accepted PDF manual pages, not 500 pages.
- [x] Automated suite (53 passing tests), actual PostgreSQL/HTTP migration and seven-route API checks recorded in BUILD_STATUS.md. Live Gemini/Chroma generation succeeded with five cited passages using `gemini-3.1-flash-lite`; earlier provider errors are retained in the record and are not treated as successes.

Still pending: Docker runtime checks; live marketplace checks; OCR; authorised manual corpus; mechanic labels and measured precision; authenticated workshop deployment and distinct participant accounting; real 30-day feedback; historical confirmation and six-month adoption. No company participation or elapsed time is simulated, and no October work is backdated into the internship.
