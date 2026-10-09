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

## Verification record

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

Current guides are README.md, QUICKSTART.md and this file. Older assistant summaries are marked as historical snapshots. The old keyword smoke runner remains a development aid; its success percentage is not retrieval precision.
