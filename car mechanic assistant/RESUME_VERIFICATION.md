# Résumé verification — 9 October 2026

**The rebuilt technical prototype works in the checked local scenarios. The full résumé is not verified.** Company outcomes remain targets, as instructed. No local engineering change can prove past employment, production usage, independent retrieval precision or elapsed workshop adoption.

This audit follows the first build at `82561fd`. It reproduced defects, fixed the relevant shared paths and reran checks. October work must be dated as an October follow-up, not backdated into December 2025–January 2026.

## Claim-by-claim verdict

| Résumé statement | Verdict | Evidence and limit |
|---|---|---|
| Yap Motor Singapore, Machine Learning Intern, Dec 2025–Jan 2026 | Awaiting company evidence | Git timestamps are not HR records or supervisor confirmation. Q01–Q02 |
| FastAPI/PostgreSQL exposing seven automotive endpoints | Verified current implementation/local execution | Seven HTTP routes returned 200 in a disposable local PostgreSQL rehearsal; query routing is the seventh route alongside the six named domains |
| Alembic, structured logging, Docker orchestration | Partly verified | Fresh/older-schema migrations, preserved catalogue fixture, Alembic model check and structured request logs checked. Docker recipes exist; no Docker runtime is installed, so image/Compose execution is unverified |
| PostgreSQL full-text catalogue retrieval + Google adapter; eBay contract | Verified implementation; live providers pending | Real PostgreSQL FTS/filter/cache integration and mocked provider-contract tests pass. Credentials absent; do not claim observed live Google/eBay results |
| Parse VIN, OBD code, year, mileage, make/model and route | Verified current tested cases | Typed extraction and route dispatch tests plus HTTP query execution. Bounded rule/regex coverage is not universal NLP accuracy |
| Failed CV approach, pivot and sparse-data stall during internship | Partial historical support | Dec 30 `c6d427f` mentions redoing toward Google parts search; Jan 1 `aecf02a` mentions lack of actual/static information. Neither establishes the CV failure metric or supervisor account. Q03–Q04 |
| First AI system; production Gemini + Chroma RAG | Prototype runtime verified; historical/business claim pending | Live Gemini embeddings, Chroma persistence/filter/reranking, Flask/Gunicorn query/feedback checked. No authenticated company deployment or first-system confirmation. Q02/Q05/Q15 |
| 24 mechanics | Unverified target | Anonymous/test feedback is not distinct mechanic adoption. Q10 |
| 500+ multilingual repair-manual pages | Not established by this corpus | Repair release: 14 English Markdown notes, 138 chunks, **zero accepted PDF pages**. Separate public demo: 12 EN/CN/JP summaries, 12 chunks, zero PDF pages. Neither equals 500 manual pages. Q06–Q09 |
| Still in use six months after internship | Unverified historical statement | Need attributable July 2026 usage of the internship release. October rebuild/live tests do not prove this. Q16 |
| 90% retrieval precision across eight categories | Unverified target | Evaluator supports eight category IDs and validates labels; no independent held-out workshop labels or measured 90% report exist. Development probes are not precision data. Q12–Q14 |
| Iterating chunk size, overlap, embeddings; month of mechanic feedback | Infrastructure exists; outcome pending | Configurable bounded chunking and model-aware releases exist. No completed comparative experiments or real month of feedback established. Q11/Q14 |
| Folder scoring, vehicle regex, dynamic Chroma filters and reranking | Verified current implementation | Applicability checks, case normalisation, multiple-engine metadata, source deduplication and inspectable scoring have regression tests and live probes |
| EN/CN/JP PDF and Word ingestion of variable structure | Verified authored fixtures, not company corpus | Text PDFs and DOCX paragraphs/tables checked. Scans rejected for OCR. Japanese/Chinese fixture extraction and public summary retrieval do not prove manual translation or production repair correctness |
| Debugged production schema-validation and case-filter blockers | Current engineering fixes verified; “production” historical wording pending | Canonical scalar metadata, identity validation and applicability regressions pass. Need original incident records for historical production attribution. Q17 |

## Checks and actual results

| Check | Result | Scope |
|---|---|---|
| Automated suite with disposable PostgreSQL integration enabled | **73 passed**, 88 dependency/deprecation warnings | Mocked providers/model calls plus temporary real Chroma; real PostgreSQL FTS integration included |
| Dependency consistency | `uv pip check` passed | Installed Python 3.12 environment |
| Linux dependency resolution | Passed for Python 3.12 x86_64 manylinux target | Resolution only; not an executed container |
| Clean database migration | Upgrade to head passed | Disposable `yap_test_audit_fresh` |
| Older-revision migration | Upgrade from `204dc0248bfb` passed, `AUDIT-PRESERVE` fixture retained | Disposable `yap_test_audit_upgrade_verified`; earlier failed fixture attempt is not counted |
| Alembic schema check | No new upgrade operations | Model/migration alignment in local PostgreSQL |
| Seven-route live HTTP smoke | 7/7 returned 200 | See route table below; synthetic fixture inputs, not workshop ground truth |
| Live fresh VIN specifications + recalls | 200; 24 make/model/year campaigns returned for test VIN | Supported NHTSA endpoints; **not** VIN-specific open/completed recall status or Singapore coverage |
| Live repaired retrieval probes | 11 development queries checked | Relevant expected source present in seven covered probes; four unsupported/unrelated probes returned no passages |
| Live Gemini answers | 6/6 completed with known passage IDs or explicit no-source response | EN P0300, BMW N54 preparation, missing Toyota torque, unrelated booking, CN/JP P0300. No measured repair accuracy |
| Live Gunicorn web checks | Home/health 200, invalid query 400, unknown feedback query 404; answer and feedback 200 | Test feedback explicitly synthetic and excluded from user/adoption statistics |
| Public-reference demo | Live build: 12 chunks; three EN/CN/JP answers passed citation-ID checks | Separate collection; summaries need native-language review |
| Docker/Compose execution | Not checked: runtime unavailable | Recipes are not runtime evidence |
| Google/eBay or replacement search live calls | Not checked: credentials absent | Contract tests only; no new provider account purchased |

### Seven-route smoke results

All paths below have `/api/v1` prefix.

| Route | HTTP result |
|---|---|
| POST `/query` | 200 |
| POST `/parts/identify` | 200 |
| POST `/diagnostics/troubleshoot` | 200 |
| POST `/valuation/estimate` | 200 |
| POST `/paint-code/lookup` | 200 |
| GET `/specifications/1HGCM82633A004352` | 200 |
| POST `/parts/compatibility` | 200 |

## Defects found and repaired

1. **Vehicle leakage/missed engines:** contradictory generic metadata could admit a BMW passage for Honda; missing context admitted specific procedures; K20/K24 and descriptive engine tags failed matching. Ingestion now rejects contradictory generic scope, serialises engine options safely and requires known applicable vehicle fields. Candidate selection retains broadly applicable sources but excludes unknown scope.
2. **Unrelated and unsupported retrieval:** restaurant/capital queries and missing Toyota specifications received unrelated repair passages. Raw cosine similarity is now checked before folder/code bonuses. The provisional `0.65` threshold was selected from these development probes. It is not independently calibrated and may miss useful material on a larger corpus. Post-filter candidate pools are bounded and may also miss relevant documents; evaluate recall with real labels before production.
3. **Incomplete provenance:** sidecar applicability changes did not alter corpus identity; policy was read from mutable notes. Manifests now include metadata/sidecar hashes, schema-3 releases snapshot/checksum application policy, and collection/model/dimension identity is verified. Old releases remain intact and need a fresh build for the new schema.
4. **Answers lacked enforceable citations:** generation now requests full source IDs, rejects absent/unknown citations and exposes cited IDs. A live Japanese answer initially cited ordinal numbers and was rejected. Removing ordinal document labels and clarifying the prompt allowed all six final checks to pass. The prior failure report is retained privately. Invalid future answers still fail closed; formatting checks cannot prove sentence-level entailment or truth.
5. **Malformed evaluation labels:** strings could be mistaken for lists of passage IDs, generating a meaningless score. The evaluator now validates lists, IDs, reviewer, language and date before scoring. Independent labels still have to come from real source review.
6. **Broken recall endpoint/false certainty:** the old VIN recall URL returned 404. Lookup now uses the supported make/model/year endpoint and marks that scope explicitly. Provider failure returns 502/unknown instead of a misleading empty recall list. VIN decoding rejects incomplete/error results.
7. **Stale/duplicated specification cache:** forced refresh previously left vehicle identity stale and appended duplicate/incomplete cached fields. Refresh now replaces NHTSA specification groups transactionally, retains unrelated groups and stores safety data.
8. **Misleading prices/cache:** price range now excludes offers known not to ship to Singapore; cache identity includes enabled provider choices.
9. **Unreviewable feedback:** private query records now retain question, generated answer, sources and release/model metadata alongside feedback. They still lack verified staff identities and must follow company access/retention policy.
10. **Placeholder provenance:** separate public summaries include primary URLs, language, organisation, date and placeholder kind. Answer payloads/UI expose the source distinction, and the UI identifies this application as a prototype requiring mechanic review.

A macOS Gunicorn HUP reload caused an Objective-C fork-initialisation worker crash during the final rehearsal. This platform limitation is recorded rather than counted as a successful reload. Use a full stop/start on this host; fresh startup and query/feedback checks passed. Linux/container reload and concurrency behaviour remain unverified.

## RAG correctness boundary

The checked pipeline successfully extracts fixture text, embeds nonzero finite vectors, loads a matching persistent collection, applies declared metadata, reranks, rejects low-similarity candidates and validates answer citation IDs. This does **not** certify the repair content.

Existing notes contain unsupported diagnostic percentages, broad replacement advice, inconsistent injector details and instructions involving spray near a running engine. Spot inspection of live output showed that a correctly cited answer can repeat an unreviewed note. The prompt prohibits unsupported diagnostic percentages, but prompt rules and citation validation are not a technical-content audit. Do not describe this corpus as a reviewed manufacturer manual or deploy it for unsupervised repair decisions. Replace/review originals and evaluate factual support with mechanics before a workshop pilot. Public industry summaries are workflow examples, not vehicle repair instructions.

The API also retains small static diagnostic/paint libraries, rule-based valuation without verified comparables and catalogue-based compatibility. A successful response does not validate market value, paint correctness or physical fit.

## Reproduce and inspect evidence

From repository root after installing both applications and dev requirements:

```sh
YAP_TEST_POSTGRES_URL=postgresql://USER@127.0.0.1:PORT/yap_test_disposable python -m pytest -q
uv pip check
```

Create a disposable local test database first; the PostgreSQL test requires a localhost URL and a database name starting `yap_test`. Without that variable the integration test is skipped. Use [QUICKSTART.md](QUICKSTART.md) for fresh RAG releases and [PUBLIC_REFERENCE_RESEARCH.md](PUBLIC_REFERENCE_RESEARCH.md) for the separate demo.

Private local runtime evidence is excluded from Git to avoid exposing questions/manual excerpts: `runtime/verification/audit-baseline-probes.json`, `live-audit-pre-fix.json`, `live-audit-post-fix.json`, `live-answer-audit-before-source-header-fix.json`, `live-answer-audit.json`, `audit-migrations.json`, `nhtsa-audit.json`, `specifications-live-fresh.json`, `web-smoke-20261009.json`, `live-web-answer-20261009.json`, `public-reference-demo-audit.json`. Built releases retain `release.json`, `corpus.json` and `policy.md`. These are local execution evidence, not company endorsements. Public regressions and this report are committed.

## Résumé wording supported now

Use under an accurately dated follow-up project, subject to authorship confirmation:

> Built and locally verified a FastAPI/PostgreSQL automotive prototype with seven routes, Alembic migrations, full-text catalogue retrieval and interchangeable Google/eBay search adapters; parsed vehicle queries into typed fields for routing.

> Rebuilt a Gemini/ChromaDB assistant with text PDF/DOCX ingestion, vehicle applicability filters, passage reranking, source provenance and citation-ID validation; checked EN/CN/JP fixtures and documented missing corpus and workshop evidence.

Keep historical pivot wording tied to dated records and supervisor confirmation. Omit production, first AI, 24 mechanics, 500+ pages, 90%, month of mechanic feedback and six-month adoption until the corresponding evidence exists. The company questions are in [COMPANY_QUESTIONS.md](COMPANY_QUESTIONS.md), so no reply is required to continue the independent work.
