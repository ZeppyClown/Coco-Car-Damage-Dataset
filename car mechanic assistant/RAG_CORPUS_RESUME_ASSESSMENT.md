# Public automotive corpus: is it enough for the RAG résumé claims?

Assessment date: 11 October 2026. This document evaluates the publicly available sources identified during research, the existing RAG code and the evidence needed for the user's proposed résumé wording. It is a feasibility/evidence assessment, not a claim that the new corpus has been deployed.

**Verdict: enough source material to investigate a substantial public-reference RAG prototype; not enough to substantiate the original résumé bullets.** The two verified downloads contain 581 physical PDF pages. Their document types, language coverage, extraction quality, applicability, permitted use and evaluation still matter. A page count is one input to the claim, not proof of the whole achievement.

Read [the master implementation ledger](WORKSHOP_MASTER_PLAN.md) for the active workshop project. This assessment does not switch that project's scope; F01 remains its next ready task unless the user chooses a public-reference RAG direction. Read [RESUME_VERIFICATION.md](RESUME_VERIFICATION.md) for the earlier technical/historical audit.

## 1. Exactly which résumé statements are being assessed

The user's RAG résumé version includes these assertions:

1. Yap Motor's first AI system, a production Gemini/ChromaDB pipeline, 24 mechanic users, 500+ pages of multilingual repair manuals and continued use six months after the internship.
2. 90% retrieval precision across eight diagnostic categories, achieved through chunking/overlap/embedding iterations and validated against a month of structured mechanic feedback on live queries.
3. Folder-priority scoring, regex vehicle extraction, dynamic Chroma filters and reranking before generation.
4. EN/CN/JP PDF/Word ingestion and production schema-validation/case-sensitive-filter incidents.

The public-source search addresses **source availability**. It cannot independently establish employer approval, historical dates, users, production operation, measured quality or feedback. Even the source assertion contains separate requirements: at least 500 pages, correct document classification, relevant content, accepted extraction and a truthful description of language coverage.

## 2. Sources double-checked

### A. MANN-FILTER cars and transporters catalogue, 2024–2026

- Publisher's [download hub](https://www.mann-filter.com/de-de/service/download-hub.html) links the [official catalogue PDF](https://www.mann-filter.com/content/dam/mann-filter/communication-media/brochures-catalogs/mann-filter-catalog-cars-transporters-2024-26-interactive.pdf).
- Download: **22,592,119 bytes**. SHA-256: `e36caae552a836a03a676fbc6ff70b06c1f57f5f7533b66beb800d8904aa7a16`.
- Both pypdf and PyMuPDF count **513 physical pages**.
- PyMuPDF finds nonempty text on all 513 pages. Selected visual inspection confirms catalogue/table content and introductory material; this is not a complete vehicle repair manual.

### B. DENSO spark-plug technical manual

- [Official PDF](https://assets.denso-am.eu/staging/attachments/1663942351%20EN_Spark%20Plug%20Manual.pdf) on DENSO's asset domain.
- Download: **7,584,422 bytes**. SHA-256: `6216208f15829a19bd7ae1e99fb51534430696ef884d043ff7745fc8413765a3`.
- Both pypdf and PyMuPDF count **68 physical pages**.
- PyMuPDF finds nonempty text on all 68 pages. Contents/FAQ pages were inspected visually. It is an English component-specific technical reference, rather than comprehensive coverage of every diagnostic category.

### Combined inventory

| Quantity | Verified value | Meaning |
|---|---:|---|
| Downloaded documents | 2 | Two distinct source files, not hundreds of manuals |
| Physical PDF pages | 581 | 513 + 68, including covers/front matter |
| Pages with nonempty PyMuPDF text | 581 | Text exists; layout/meaning still needs review |
| Chinese CJK characters in PyMuPDF-extracted text | None detected | Does not establish Chinese source coverage |
| Japanese kana in PyMuPDF-extracted text | None detected | Does not establish Japanese source coverage |
| Quality-approved relevant source pages | Not yet established | Requires a documented acceptance/relevance review |
| New source pages in a serving vector release | 0 | These downloads have not been embedded or published to a Chroma release |
| Independently measured retrieval precision on these sources | Not measured | No held-out labelled retrieval run performed |

The character scan is an extracted-text check, not a visual audit of every glyph. It is nevertheless no basis for claiming EN/CN/JP document coverage. A Japanese manufacturer name does not make an English PDF a Japanese-language source. Different European-language sections do not establish the specific languages named on the résumé.

## 3. What was checked and what was not

### Completed checks

1. Reopened the publisher download page and followed its catalogue link.
2. Downloaded both PDFs locally with HTTPS certificate verification enabled.
3. Recorded content hashes, byte sizes and independent page counts.
4. Ran a PyMuPDF nonempty-text and CJK/kana scan over every physical page.
5. Inspected five rendered pages: MANN physical pages 1, 25 and 250; DENSO physical pages 3 and 65. Other renders produced by the inventory task are reading artifacts, not automatically reviewed pages.
6. Read the actual PDF ingestion/chunking/applicability/evaluation implementations in this repository.
7. Checked publisher terms relevant to the intended corpus use; unrestricted hosted/commercial/model processing permission is not established.

### Local parser audit

An additional pypdf per-page extraction/exact-text-duplicate inventory and existing `DocumentProcessor` dry run completed and are recorded in local `runtime/public-corpus-research-20261011/corpus-double-check.json`. The dry run produced candidate text chunks in memory only; it did not call an embedding/generation provider or create a serving collection. Its final counts are in section 4.

### Not completed

- Semantic validation of every table row, language section, footnote or technical statement.
- Manual classification/acceptance of 500 relevant content pages.
- A fitment-safe source preparation pipeline and serving index for these downloads.
- EN/CN/JP source ingestion or Word ingestion using these particular documents.
- Independent retrieval labels, chunking/model experiments or live mechanic feedback.
- Company deployment, authenticated staff use, historical adoption or supervisor confirmation.

Existing tests from the previous audit are not new tests of this corpus. No application regression suite was rerun for this documentation task.

## 4. Existing parser dry run: result and interpretation

The local audit completed without PDF rejection. It used the unmodified current `DocumentProcessor` at its default 1,000-character chunk size and 200-character overlap, processing each document separately.

| Document | Physical pages, both parsers | Nonempty pypdf pages | Exact unique nonempty text pages | Current parser chunks | Default scope/language |
|---|---:|---:|---:|---:|---|
| MANN-FILTER | 513 | 513 | 513 | 2,523 | `unknown` / `en` |
| DENSO | 68 | 68 | 68 | 271 | `unknown` / `en` |
| Combined | 581 | 581 | 581 across both documents | 2,794 | No applicability sidecars supplied |

No exact whitespace-normalised duplicate pages were found. DENSO's cover page has fewer than 100 extracted characters; no MANN page falls below that text-length threshold. These are mechanical checks, not approvals of relevance or row fidelity.

All candidate chunks have unknown scope, so the current applicability rule rejects them. The catalogue's `en` tag also fails to represent its mixed-language sections accurately. Both issues need correct source preparation; neither justifies weakening the filter or treating the tag as verified source-language coverage. There are **zero new embedded/serving pages** despite successful local text parsing.

Keep these counts distinct:

- **Physical pages:** pages in the PDF file.
- **Nonempty text pages:** pages for which a parser returns some text.
- **Exact unique text pages:** pages whose whitespace-normalised text hash is distinct.
- **Parser-accepted pages/chunks:** accepted by the current mechanical ingestion rules.
- **Quality-approved relevant pages:** content that retains the information needed for the intended queries.
- **Indexed source pages:** accepted pages represented in the released serving collection.

Exact text deduplication does not detect translated repetitions or semantically repeated content. Nonempty text can be a cover, navigation, advertisement or badly flattened table. A parser acceptance count cannot substitute for source-quality approval.

## 5. Claim-by-claim verdict

| Résumé component | Do these sources establish it? | Evidence still required |
|---|---|---|
| 500+ downloadable automotive-reference pages | **Yes, as a physical source inventory** | Relevant/accepted/indexed count before describing an implemented corpus |
| 500+ repair-manual pages | **No** | Correctly classified repair manuals; this mixed catalogue/component-reference corpus needs different wording |
| Multilingual sources | **Partly, broadly** | Explicit source-language inventory and extraction checks; specific EN/CN/JP coverage is absent |
| Gemini + Chroma RAG implementation | **Earlier prototype exists; new corpus is not built** | New frozen release, embeddings/index counts, retrieval and answer checks |
| Useful to Yap Motor mechanics | **Not established** | Specific workshop questions, qualified review and observed usefulness |
| First company AI system | **No** | Company/supervisor confirmation tied to the actual system/date |
| Production operation | **No** | Deployment/access/operating records for the actual release and environment |
| 24 mechanics | **No** | Genuine distinct users and attributable usage; sample/test IDs are insufficient |
| Six months' continued use | **No** | Dated real usage of the identified earlier release over the claimed period |
| 90% retrieval precision | **No** | Defined metric, independent labels, held-out run and actual result |
| Eight diagnostic categories | **No** | Sources and reviewed queries covering all eight meaningfully; filter/ignition references do not establish that coverage |
| Chunk size/overlap/embedding optimisation | **Not from downloading PDFs** | Comparative experiment records on development data, followed by held-out evaluation |
| Month of structured mechanic feedback | **No** | Actual dated review/feedback records across the claimed period |
| Folder scoring/regex/filtering/reranking | **Existing code supports current prototype** | Verify operation with this corpus and its new applicability representation |
| EN/CN/JP PDF and Word ingestion | **Not established by these two PDFs** | Actual sources or clearly described fixtures in each claimed language/format |
| Production schema/filter incidents | **No historical evidence from these sources** | Original incident evidence; current engineering fixes remain separately describable |
| Dec 2025–Jan 2026 internship attribution | **No** | Dated contribution/history and employment confirmation; October research is October work |

Answer to “is this enough?”: **yes for finding candidate volume; no for the original complete bullet; potentially enough to begin a differently worded public-reference prototype after use/applicability issues are resolved.**

## 6. Why the current code is not automatically ready for this corpus

These findings are from reading current code, not hypothetical claims that a new implementation already works.

### A. Text extraction does not preserve a fitment table by itself

`src/document_processor.py` extracts each PDF page with pypdf, then chunks the page as text. Its oversized-section path uses character windows with overlap. It does not build explicit records for vehicle/application rows, carry row-spanning headers into each record or validate column association.

For a table-heavy source, the information required to answer a question may depend on the correct header, row, year/engine restriction and note. A chunk may contain a part code without all the constraints that make it applicable. A plausible answer is not proof that those relationships survived extraction.

**Needed:** inspect representative rows against the rendered source; preserve the relevant row/header/footnote context. Use structured filtering for fitment where necessary. Do not start with a blanket semantic-search assumption that every row is safely interchangeable.

### B. File-wide vehicle metadata is too coarse for a mixed application catalogue

The processor extracts/accepts file-level applicability metadata. Without suitable metadata, these filenames default to unknown scope. `VectorStore._applicable` rejects unknown scope. That is a useful safeguard, but means naive ingestion does not automatically yield useful retrieval.

Simply labelling the whole catalogue generic would bypass the important distinction between general explanation and specific vehicle fitment. Assigning one make/model to an entire mixed catalogue is also incorrect.

**Needed:** distinguish genuine generic explanatory passages from vehicle/application records. Preserve applicable make/model/engine/year constraints at the correct level. Never relax the current safety filter merely to make more documents show up.

### C. Language defaults are not a multilingual source audit

The current heuristic chooses Japanese for kana, Chinese for CJK and otherwise English. It is not a detector for every language in a multilingual catalogue. A whole mixed-language file may therefore receive a misleading single tag.

**Needed:** explicit section/page language metadata and language-specific checks. Answering an English-source question in Chinese/Japanese is a different capability from ingesting Chinese/Japanese source documents; report them separately.

### D. A successful citation ID is not full answer correctness

Existing generation validates source passage IDs. It does not establish that every sentence follows from the cited passage or that the cited row applies to the user's vehicle.

**Needed:** expected answer/source checks, appropriate vehicle-context requirements and unsupported-query abstention. Track incorrect fitment and unsupported claims separately from citation-format failures.

### E. Existing evaluation categories and metric need an honest fit

`src/evaluate_retrieval.py` currently requires diagnostic categories: starting, idle/stalling, misfire/ignition, fuel pressure, cooling, charging, sensors/emissions and mechanical noise. Parts application/reference tasks should not be forced into those labels simply to preserve the résumé number eight.

The evaluator uses distinct-passage **Precision@5**, dividing the number of relevant retrieved passages by five; missing ranks count as zero. If a query has only one genuinely relevant labelled passage, returning that single correct passage produces 0.2 under this definition. That is not 100% Precision@5, even though the source was found. Conversely, a 90% hit rate is not 90% precision.

**Needed:** define the intended tasks and relevance units first. Report hit rate, precision, recall/abstention or answer correctness under explicit definitions as appropriate. Do not manufacture five labels or relabel a favourable metric to obtain 90%.

## 7. Is the source material sufficiently useful?

Page volume answers a size question. It does not answer the product question.

| Possible product | Current source fit | Remaining requirement |
|---|---|---|
| Public manufacturer-reference search | Reasonable candidate | Source-use path, content preparation and retrieval checks |
| Filter/application lookup | Reasonable candidate, technically demanding | Fitment-preserving extraction, exact applicability and source verification |
| Spark-plug technical-reference assistant | Narrow candidate | Defined questions and independently reviewed supported answers |
| All-purpose mechanical diagnosis | Insufficient scope established | Broader authoritative sources, qualified review and defined coverage |
| Workshop repair-procedure assistant | Insufficient | Approved relevant procedures, vehicle/edition context and actual workshop need |
| Customer job-history/admin tool | Different data/problem | Private reviewed job records and destination mapping; public catalogues do not supply them |

An honest project can be valuable with fewer than 500 carefully selected pages. A catalogue can also be valuable at over 500 pages when its tables are handled correctly. Do not pad the corpus with repeated language sections or unrelated documents to satisfy a headline figure.

## 8. Publisher use conditions: an unresolved feasibility dependency

The publisher download link establishes availability, not every intended processing permission.

- MANN+HUMMEL's [legal notice](https://www.mann-hummel.com/de/rechtlicher-hinweis.html) reserves rights, describes restrictions on commercial/distribution copying and states that the website does not grant intellectual-property licences.
- DENSO's [terms of use](https://www.denso-am.eu/terms-conditions) describe limited personal/non-commercial text use and restrictions on reproduction, transmission, publication and graphical material.

This review does not determine the legal applicability of every clause or exception to a specific implementation. It establishes that **unrestricted hosted/commercial RAG or third-party model processing is not verified**. Do not label these sources openly licensed based on their download buttons. Clarify the intended use or choose sources with explicit compatible rights before that deployment/processing step.

Local PDFs, rendered pages and extracted artifacts stay ignored in runtime storage. This public report contains links, inventories and our assessment; it does not redistribute the source books. No source text was sent to an embedding or generation provider in this task.

## 9. Minimum evidence before claiming a 500-page RAG achievement

### Gate 1 — choose an accurate scope

Write the intended questions and document types. A public parts/reference corpus needs that name; a workshop repair-manual corpus needs actual repair manuals and workshop relevance. Decide which project is being built without changing historical résumé facts.

### Gate 2 — source/use inventory

Record publisher, title, edition, URL, hash, document type, region/applicability, language and intended processing/use basis. Keep excluded sources/pages with reasons. Do not claim a licence that has not been established.

### Gate 3 — accepted content inventory

Check text, row/header/footnote associations, document/page identity and relevance. Identify covers, repeated introductory sections and unusable extraction. Count physical and accepted source pages separately. The accepted count could be lower than 581; it is currently unknown.

### Gate 4 — build a separate frozen release

Keep the public corpus separate from private workshop records and the old unreviewed repair notes. Freeze model/dimensions, chunking settings, source hashes and processing metadata. Build embeddings and a new collection only through the selected permitted path. Confirm its source/page/chunk counts match the release manifest.

### Gate 5 — exercise the actual pipeline

Run factual reference, precise application, partial-context, wrong-vehicle and unsupported queries. Verify cited pages, applicable constraints, retrieval scores and generated answer support. Save actual outcomes; a successful HTTP response alone is insufficient.

### Gate 6 — independent evaluation and experiments

Use reviewed development queries for tuning; reserve held-out questions before selecting settings. Compare a small number of meaningful chunk/context approaches. For table queries, relevance may be a validated row/application record rather than an arbitrary text window. Report dataset size, metric definition, per-task/language results and failure cases.

A proposed starting evaluation might use 30–50 independently reviewed questions for a narrow development exercise. That is a suggested starting scope, not existing evidence or a guarantee of reliable population accuracy. Mechanic review becomes necessary for workshop repair/diagnostic correctness; generic factual labels can be checked against their exact cited source with limitations stated.

### Gate 7 — report only the achieved scope

If accepted/indexed pages exceed 500, that count can enter the accurately dated project description. If there are fewer, use the real count or omit the number. Report measured performance only after evaluation. Keep deployment/user/feedback-duration claims out unless actual records independently support them.

## 10. Résumé wording at different evidence stages

### Current completed work: research only for the new corpus

If useful to mention at all, the accurate statement is:

> Identified and audited two public automotive reference PDFs totalling 581 physical pages, assessing extraction, applicability and evidence gaps for a proposed RAG corpus.

This describes research, not a deployed retrieval achievement. The existing locally verified Gemini/Chroma prototype can be described separately using [the earlier verification report](RESUME_VERIFICATION.md).

### After an actual permitted build and pipeline verification

Possible wording, only if the accepted/indexed count supports it:

> Built a Gemini/ChromaDB retrieval prototype over 500+ accepted pages of public automotive parts catalogues and technical references, preserving source-page citations and application metadata.

If table-aware extraction or vehicle constraints have not actually been implemented, remove those implications from the wording. If fewer than 500 pages are accepted, replace the number with the actual result.

### After a real independent evaluation

Use a measured template with no prefilled score:

> Evaluated retrieval on [N] independently reviewed held-out questions, achieving [measured metric/result] across [actual task categories]; documented unsupported-query and application-matching failures.

### After genuine company use

Only add workshop-user counts, production status, feedback duration and adoption dates if the actual company release/use records support them. Public-source work done in October 2026 cannot prove a system was used after a January 2026 internship. Company-reviewed use of public references is possible in principle, but has not happened merely because the documents were found.

## 11. Work for Claude if this direction is selected

This is a conditional handoff, not an instruction to abandon workshop F01.

1. Read this assessment, `WORKSHOP_MASTER_PLAN.md`, `RESUME_VERIFICATION.md` and the private source inventories if available.
2. Confirm selected corpus/task/use path. Do not assume public sources are unrestricted or send PDFs to a model automatically.
3. Start with a few checked pages and expected queries; resolve table/applicability/language representation before processing the whole file.
4. Preserve the existing restrictive applicability checks. Avoid whole-catalogue generic tags that erase row-specific context.
5. Record each implemented extraction/retrieval/evaluation part in the master ledger, with actual tests and limits.
6. Expand only after the narrow slice retrieves and answers supported questions correctly.
7. Count accepted/indexed pages and conduct held-out evaluation before changing résumé achievement wording.

If this route is selected, add explicit corpus feature rows to the master before implementation. Until then, record it as assessed feasibility and keep the current job-sheet feature statuses unchanged.

## 12. Evidence paths and final decision

Private local artifacts under `runtime/public-corpus-research-20261011/`:

- `mann-filter-inventory.json` and `denso-inventory.json`: source URL, checksum, byte size and physical count.
- `language-and-layout-check.json`: full-document PyMuPDF text/script checks.
- `corpus-double-check.json`: pypdf page metrics/exact deduplication and existing-parser dry run.
- Source PDFs and selected PNG renders: private reading/verification copies, not committed books.

**Decision:** the search has solved the availability question. It has not solved corpus preparation, permission, workshop relevance, multilingual coverage, measured retrieval quality or historical company evidence. The proposed public-reference RAG project is technically plausible; the original résumé wording remains unsupported.

Unverified: semantic quality across all pages, permitted hosted/provider use, serving-index correctness, independent performance and company deployment/history.
Main risk: treating 581 downloaded pages or mechanically accepted chunks as proof of a 500-page production repair-manual system.
