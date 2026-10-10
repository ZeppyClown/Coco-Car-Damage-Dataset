# Yap Motor workshop visit — interview and evidence workbook

Blank template prepared 10 October 2026. Fill this in during the company visit. This document contains questions and proposed collection forms, not company answers, approval or proof of résumé outcomes.

**The first goal is to obtain authorised documents, understand one real repair workflow, collect five useful real questions and identify a mechanic who can review the prototype.** A large database is not necessary to start a manual-based RAG prototype. The PDFs themselves provide its main knowledge data.

The existing project is a locally tested prototype. Its current repair library is 14 English Markdown notes, 138 chunks and zero accepted PDF manual pages. A separate 12-summary public EN/CN/JP demo is a placeholder. The figures 24 mechanics, 500+ pages, 90% precision, a month of mechanic feedback and six-month adoption are targets until supported by actual evidence.

## How to use this workbook

1. Make a **private copy** before writing company answers. This blank template is tracked in a public GitHub repository. Filled copies, company documents, names, records and screenshots belong in an authorised private location.
2. Complete sections 1–5 first. If time is short, use the five-question script in section 2 and the departure checklist in section 18.
3. Write `unknown`, `not available`, `not applicable` or `follow-up needed` rather than guessing. An empty cell means unanswered, not approved.
4. Record whether an answer is a direct observation, a remembered account, a proposal or a documented fact. Link an evidence ID whenever possible.
5. Ask to see one actual workflow and an actual information lookup. Demonstrated behaviour is more useful than an idealised process description.
6. Keep real cases separate from fictional examples. Record dates accurately; do not backdate new work or reconstruct missing usage records as facts.
7. The collection suggestions below are starting points, not mandatory company policies or completed agreements. Permission may be granted, refused or conditional; record the actual decision.

From the assistant directory, an optional private local copy can be created with:

```sh
mkdir -p runtime
cp WORKSHOP_VISIT_WORKBOOK.md runtime/workshop-visit-20261010.md
```

The repository currently ignores `runtime/`. Do not move the completed copy into a tracked directory or commit it. If the company requires a different approved location, use that location instead. Do not paste credentials into any version of this workbook; record the private file path or account owner.

## Contents

- [1. Meeting record and priority checklist](#1-meeting-record-and-priority-checklist)
- [2. Five-question opening script](#2-five-question-opening-script)
- [3. Choose the first useful problem](#3-choose-the-first-useful-problem)
- [4. Document access and permissions](#4-document-access-and-permissions)
- [5. One actual job from arrival to completion](#5-one-actual-job-from-arrival-to-completion)
- [6. Five real query capture forms](#6-five-real-query-capture-forms)
- [7. Manual inventory and extraction checks](#7-manual-inventory-and-extraction-checks)
- [8. Vehicle applicability and workshop vocabulary](#8-vehicle-applicability-and-workshop-vocabulary)
- [9. Available operational data](#9-available-operational-data)
- [10. Synthetic development data agreement](#10-synthetic-development-data-agreement)
- [11. Retrieval and answer evaluation](#11-retrieval-and-answer-evaluation)
- [12. Pilot and feedback workflow](#12-pilot-and-feedback-workflow)
- [13. Parts search and supplier workflow](#13-parts-search-and-supplier-workflow)
- [14. Hosting and operating the prototype](#14-hosting-and-operating-the-prototype)
- [15. Historical and résumé evidence](#15-historical-and-résumé-evidence)
- [16. File handover and evidence register](#16-file-handover-and-evidence-register)
- [17. Decisions and follow-up actions](#17-decisions-and-follow-up-actions)
- [18. Departure checklist and implementation handoff](#18-departure-checklist-and-implementation-handoff)

## 1. Meeting record and priority checklist

### 1.1 Visit details

| Field | Fill in |
|---|---|
| Actual visit date and time | |
| Workshop/site | |
| Interviewer | |
| Respondent role; use an ID in any public summary | |
| Who understands the day-to-day repair workflow? | |
| Who can authorise documents and cloud processing? | |
| Who can review diagnostic answers? | |
| Who operates the company’s computers/accounts? | |
| Language used for the interview | |
| Time available | |
| Private location for these completed notes | |
| Permission to take notes/screenshots or record a demonstration; conditions | |
| Topics or documents the respondent cannot authorise | |

### 1.2 Essential before building against company material

These are separate decisions. Possession of a PDF does not establish permission for every use.

- [ ] One priority use case has been selected in section 3.
- [ ] At least one useful original manual/document has been identified.
- [ ] Extraction, storage, cloud processing and staff access decisions are recorded in section 4.
- [ ] A mechanic has demonstrated one actual workflow in section 5.
- [ ] Five real questions or a smaller actual available number are recorded in section 6, with expected answers or reference pages.
- [ ] One reviewer has agreed to review a defined sample and has a next review date.

Missing item / owner / next action:

>

### 1.3 Needed before a real workshop pilot

- [ ] Corpus extraction and vehicle applicability have been reviewed.
- [ ] The company has agreed what the tool may answer and when a mechanic must take over.
- [ ] A host, account/access method and operator are identified.
- [ ] Questions, answers and feedback have agreed access and retention rules.
- [ ] A small pilot group and feedback/review routine are agreed.
- [ ] Provider access, cost limits, backups and restart procedures are understood.

These can be follow-up decisions. They do not all have to be resolved during the first interview.

### 1.4 Evidence required only for specific résumé claims

- [ ] Employment/dates/authorship confirmed.
- [ ] Historical pivot and data limitations documented.
- [ ] “First AI system” scope confirmed.
- [ ] Actual manual page/language counts retained.
- [ ] Independent retrieval evaluation and raw results retained.
- [ ] Actual participant/feedback/adoption records retained.
- [ ] Historical production incidents substantiated.

A useful prototype can be built before these claims are verified. Keep unsupported claims out of past-tense achievements.

## 2. Five-question opening script

Use this if you only have 10–15 minutes. Ask in your own words and record the respondent’s answers without suggesting the résumé numbers as facts.

### Question A — the useful task

> “What is one question or information lookup mechanics repeat that is slow or difficult today? Can you show me a recent example?”

Exact answer:

>

Observed example / evidence ID:

>

### Question B — the actual source material

> “Which manuals or documents do you trust for that task? Can we obtain the original files, and who can approve extracting them and using them with Gemini?”

Document names / location / approver / conditions:

>

### Question C — the real workflow

> “Can you walk me through one job, from the customer’s complaint to diagnosis and repair, including where you look up information and how you check that it applies to this vehicle?”

Summary:

>

### Question D — the first test cases

> “Can you give me five questions mechanics actually ask, including the vehicle details and the correct answer or manual page?”

Number available / where recorded / remaining cases to collect:

>

### Question E — the reviewer

> “Who can review the prototype’s answers, tell us when they are wrong, and decide whether a small workshop trial is useful?”

Reviewer ID / role / review date / preferred review method:

>

### One-minute read-back before leaving

> “My understanding is that the first task is ______. The permitted source files are ______. We may use them for ______ under these conditions: ______. Our initial examples are ______. The reviewer is ______, and the next step is ______ by ______. Have I understood that correctly?”

Corrections to the read-back:

>

## 3. Choose the first useful problem

### 3.1 What mechanics need

Ask for actual examples rather than every possible feature.

| Candidate task | Done today? How? | Frequency and basis of estimate | Current difficulty | Useful first pilot? |
|---|---|---|---|---|
| Find a fault-code explanation and the next documented checks | | | | |
| Find an applicable diagnostic procedure | | | | |
| Find a manufacturer specification or torque value | | | | |
| Find an installation/removal procedure | | | | |
| Locate a wiring diagram or connector information | | | | |
| Find a part number and confirm variant/fit | | | | |
| Compare supplier stock, price and delivery | | | | |
| Find technical bulletins or known repair cases | | | | |
| Translate or search a manual in another language | | | | |
| Find paint-code information | | | | |
| Other actual task | | | | |

### 3.2 Select one first task

| Question | Answer |
|---|---|
| First task to support | |
| Why is it more useful than the other tasks? | |
| Who performs it? | |
| At what point in a repair job? | |
| What information does the mechanic already have? | |
| What information is frequently missing? | |
| Which documents contain the answer? | |
| What should the assistant return: excerpt, page link, checklist, explanation or another format? | |
| What action would the mechanic take after reading it? | |
| How will the mechanic check it before acting? | |
| What should the assistant ask before answering? | |
| What would make the response unusable? | |
| What would make it useful enough to try again? | |
| Which tasks should wait until a later phase? | |

### 3.3 Success measure for the first pilot

Record a proposed measure, its baseline and how it will actually be observed. Do not invent a baseline.

| Measure | Current observed value or “unknown” | Desired result | How/when measured | Reviewer |
|---|---|---|---|---|
| Time to find the correct source | | | | |
| Correct vehicle-specific source located | | | | |
| Answer supported by cited passages | | | | |
| Mechanic finds the result useful | | | | |
| Incorrect or unsupported details | | | | |
| Missing-document questions correctly declined | | | | |

What must be true before moving from demonstration to a pilot?

>

## 4. Document access and permissions

### 4.1 Decision authority

| Field | Answer |
|---|---|
| Decision-maker role/ID | |
| What documents can this person approve? | |
| Are any documents supplied under a third-party subscription/licence? | |
| Who can resolve unclear rights or licence restrictions? | |
| Date of decision | |
| Supporting message, policy or confirmation reference | |
| Conditions or expiry/review date | |

### 4.2 Separate decisions for each use

Use `approved`, `refused`, `conditional`, `unknown` or `not applicable`. A blank cell does not mean approval. Ask for a document-specific decision if different files have different restrictions.

| Proposed use | Actual decision | Applies to which files? | Conditions / approver / evidence |
|---|---|---|---|
| Obtain a private development copy | | | |
| Extract text and tables locally | | | |
| Store originals and extracted text | | | |
| Send document text to Gemini for embeddings | | | |
| Send selected excerpts and user questions to Gemini for answer generation | | | |
| Store embeddings in a private Chroma index | | | |
| Display excerpts/source pages to authorised workshop staff | | | |
| Store questions and generated answers for review | | | |
| Store mechanic ratings/comments | | | |
| Share redacted examples privately with a reviewer | | | |
| Use aggregate results in a résumé/interview | | | |
| Publish any excerpt, screenshot or example externally | | | |
| Retain backups and prior index releases | | | |
| Use photos or scanned diagrams if image processing is later enabled | | | |

### 4.3 Access and retention

| Question | Answer |
|---|---|
| Where may originals and indexes be stored? | |
| Which staff may access the tool and its source excerpts? | |
| May staff download originals? | |
| Who may see raw questions/answers and feedback? | |
| How long may each type of data be retained? | |
| Who can request deletion or revoke access? | |
| What information must be removed from examples? | |
| Are registration plates, VINs, customer names, contact details or invoices unnecessary for the selected task? | |
| What must never be entered into an external model? | |
| Who owns the approved provider account and its cost limit? | |
| What must happen if cloud processing is not approved? | |

If permission is unclear, retain the question and use the separate public/synthetic demonstration material. Do not import the company files until the relevant use is authorised.

## 5. One actual job from arrival to completion

Use an anonymised case ID. Customer names, phone numbers and registration plates are usually unnecessary for this engineering interview. Record only the vehicle/context details needed for the selected task and permitted by the company.

### 5.1 Case overview

| Field | Fill in |
|---|---|
| Case ID | |
| Job date or approximate period; mark estimates | |
| Evidence type: observed job / completed record / respondent recollection | |
| Staff role(s) involved | |
| Vehicle make/model/year/engine/variant | |
| Relevant market/region or import variant | |
| Mileage and unit, if relevant | |
| Customer’s original symptom wording | |
| Mechanic’s technical interpretation | |
| OBD/fault codes, if available | |
| Conditions when symptom appears | |
| Prior repairs/modifications relevant to the issue | |
| Source/job-record evidence ID | |

### 5.2 Walk through the actual steps

| Stage | What actually happened? | Information used / tool / source | Person responsible | Delay, uncertainty or rework |
|---|---|---|---|---|
| Customer arrival and complaint capture | | | | |
| Initial vehicle identification | | | | |
| Preliminary inspection | | | | |
| Scan/read fault codes | | | | |
| Interpret codes and symptoms | | | | |
| Form possible causes | | | | |
| Choose and perform diagnostic checks | | | | |
| Look up a procedure/specification | | | | |
| Confirm document applicability | | | | |
| Identify parts or materials | | | | |
| Confirm fit, availability and quote | | | | |
| Obtain any required approval | | | | |
| Complete the repair | | | | |
| Verify result and check for remaining faults | | | | |
| Record outcome and hand over vehicle | | | | |
| Retain knowledge for a similar future job | | | | |

### 5.3 Information lookup demonstration

Ask: “Please show me exactly how you find the information for this job.”

| Question | Answer |
|---|---|
| What words did the mechanic type or ask? | |
| Where did they search first? | |
| Which website, software, manual folder or person was consulted next? | |
| Which result was selected, and why? | |
| How was the make/model/year/engine/edition checked? | |
| Exact document and page/section used | |
| Did information conflict across sources? How was it resolved? | |
| Was translation needed? Which terms were difficult? | |
| Time spent, with observation/estimate clearly identified | |
| What did the mechanic do when no applicable answer was found? | |
| What should the prototype do at that same point? | |
| Permitted screenshot/recording reference, if any | |

### 5.4 Outcome and what is known

| Field | Answer |
|---|---|
| Final diagnosis | |
| How was the diagnosis confirmed? | |
| Repair performed | |
| Post-repair verification | |
| Unresolved issue or uncertainty | |
| What was learned or documented? | |
| Which part of this case may be used in development/evaluation? | |
| Which part needs redaction or permission? | |

An observed repair outcome is useful evidence, but it does not automatically establish that every statement in a generated answer is correct.

## 6. Five real query capture forms

Try to collect five actual questions. A smaller genuine set is better than padding it with invented “real” jobs. These first examples are for development and understanding; final precision evaluation needs additional independently reviewed questions kept separate from tuning.

Ask for the original wording, necessary vehicle context, a source page and what a useful answer would look like. If the mechanic knows an answer from experience but no source is available, record that distinction.

### Case 01

| Field | Fill in |
|---|---|
| Query ID | QRY-01 |
| Origin: actual question / observed job / recalled case / proposed example | |
| Actual date or approximate period | |
| Question exactly as the mechanic would ask it | |
| Language and abbreviations used | |
| Make/model/year/engine/trim/region needed | |
| Mileage/unit, if relevant | |
| Symptoms, conditions and fault codes | |
| Details the assistant must ask for before answering | |
| Correct answer or acceptable answer elements, in mechanic’s words | |
| Required original manual/file and edition | |
| PDF page number and printed page number, if different | |
| Section heading / table / diagram reference | |
| How does the source support the answer? | |
| What would be an incorrect or misleading answer? | |
| What must not be guessed? | |
| When should the assistant say it lacks coverage? | |
| Reviewer ID and actual review date | |
| Permission/redaction conditions | |
| Evidence IDs | |
| Open question / next action | |

### Case 02

| Field | Fill in |
|---|---|
| Query ID | QRY-02 |
| Origin: actual question / observed job / recalled case / proposed example | |
| Actual date or approximate period | |
| Question exactly as the mechanic would ask it | |
| Language and abbreviations used | |
| Make/model/year/engine/trim/region needed | |
| Mileage/unit, if relevant | |
| Symptoms, conditions and fault codes | |
| Details the assistant must ask for before answering | |
| Correct answer or acceptable answer elements, in mechanic’s words | |
| Required original manual/file and edition | |
| PDF page number and printed page number, if different | |
| Section heading / table / diagram reference | |
| How does the source support the answer? | |
| What would be an incorrect or misleading answer? | |
| What must not be guessed? | |
| When should the assistant say it lacks coverage? | |
| Reviewer ID and actual review date | |
| Permission/redaction conditions | |
| Evidence IDs | |
| Open question / next action | |

### Case 03

| Field | Fill in |
|---|---|
| Query ID | QRY-03 |
| Origin: actual question / observed job / recalled case / proposed example | |
| Actual date or approximate period | |
| Question exactly as the mechanic would ask it | |
| Language and abbreviations used | |
| Make/model/year/engine/trim/region needed | |
| Mileage/unit, if relevant | |
| Symptoms, conditions and fault codes | |
| Details the assistant must ask for before answering | |
| Correct answer or acceptable answer elements, in mechanic’s words | |
| Required original manual/file and edition | |
| PDF page number and printed page number, if different | |
| Section heading / table / diagram reference | |
| How does the source support the answer? | |
| What would be an incorrect or misleading answer? | |
| What must not be guessed? | |
| When should the assistant say it lacks coverage? | |
| Reviewer ID and actual review date | |
| Permission/redaction conditions | |
| Evidence IDs | |
| Open question / next action | |

### Case 04

| Field | Fill in |
|---|---|
| Query ID | QRY-04 |
| Origin: actual question / observed job / recalled case / proposed example | |
| Actual date or approximate period | |
| Question exactly as the mechanic would ask it | |
| Language and abbreviations used | |
| Make/model/year/engine/trim/region needed | |
| Mileage/unit, if relevant | |
| Symptoms, conditions and fault codes | |
| Details the assistant must ask for before answering | |
| Correct answer or acceptable answer elements, in mechanic’s words | |
| Required original manual/file and edition | |
| PDF page number and printed page number, if different | |
| Section heading / table / diagram reference | |
| How does the source support the answer? | |
| What would be an incorrect or misleading answer? | |
| What must not be guessed? | |
| When should the assistant say it lacks coverage? | |
| Reviewer ID and actual review date | |
| Permission/redaction conditions | |
| Evidence IDs | |
| Open question / next action | |

### Case 05

| Field | Fill in |
|---|---|
| Query ID | QRY-05 |
| Origin: actual question / observed job / recalled case / proposed example | |
| Actual date or approximate period | |
| Question exactly as the mechanic would ask it | |
| Language and abbreviations used | |
| Make/model/year/engine/trim/region needed | |
| Mileage/unit, if relevant | |
| Symptoms, conditions and fault codes | |
| Details the assistant must ask for before answering | |
| Correct answer or acceptable answer elements, in mechanic’s words | |
| Required original manual/file and edition | |
| PDF page number and printed page number, if different | |
| Section heading / table / diagram reference | |
| How does the source support the answer? | |
| What would be an incorrect or misleading answer? | |
| What must not be guessed? | |
| When should the assistant say it lacks coverage? | |
| Reviewer ID and actual review date | |
| Permission/redaction conditions | |
| Evidence IDs | |
| Open question / next action | |

### 6.1 Additional question register

Copy a case form above for each extra example.

| Query ID | Original question or private reference | Vehicle context | Source/page | Reviewer/status | Development or held-out? |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

### 6.2 Missing-answer examples

Ask for questions the existing library cannot answer. Useful negative cases include an unsupported vehicle/edition, missing engine details, conflicting sources or an unrelated question. These evaluate whether the assistant declines or asks for context appropriately.

| Query/context | Why the answer is unavailable or ambiguous | Correct action: decline / clarify / refer | Reviewer |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

## 7. Manual inventory and extraction checks

### 7.1 Inventory overview

| Document ID | Original title/file; private location | Language | Edition/date/region | Applicable vehicles | Permission evidence | Ready / needs review / unavailable |
|---|---|---|---|---|---|---|
| DOC-01 | | | | | | |
| DOC-02 | | | | | | |
| DOC-03 | | | | | | |
| DOC-04 | | | | | | |
| DOC-05 | | | | | | |
| DOC-06 | | | | | | |
| DOC-07 | | | | | | |
| DOC-08 | | | | | | |
| DOC-09 | | | | | | |
| DOC-10 | | | | | | |

### 7.2 Detailed document form

Copy this form for each important document or document family. Human interview notes need not match the ingestion schema exactly; a developer will map reviewed applicability into the supported metadata format later.

| Field | Fill in |
|---|---|
| Document ID | |
| Exact original filename and title | |
| Original source/publisher | |
| Company owner/contact role | |
| File format: PDF / DOCX / other | |
| Native language(s); separate original from translation | |
| Edition, revision and publication date | |
| Geographic/market applicability | |
| Makes and models covered | |
| Engine codes, trims and transmissions covered | |
| Year ranges and any chassis/VIN applicability rules | |
| General reference or vehicle-specific material? Why? | |
| Categories/procedures covered | |
| Physical PDF page count, if known | |
| Useful ranges; blank/index/duplicate pages | |
| Printed-page numbering versus PDF-page numbering | |
| Selectable text or scanned images? | |
| Columns, tables, footnotes and diagrams present? | |
| Password/access restrictions; do not record passwords | |
| Superseded/conflicting edition or newer bulletin? | |
| Permission/conditions evidence ID | |
| Approved private storage path/link | |
| Reviewer for extraction and applicability | |
| Current status and outstanding issue | |

### 7.3 Ask the mechanic to identify useful pages

Do not just collect a folder of files without knowing which pages matter.

| Document ID | Page/section | What question does it answer? | Table/diagram needed? | Vehicle/edition restriction | Reviewer |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

### 7.4 Extraction spot check

The current code handles text PDFs and DOCX. Scanned/image-only pages are rejected for OCR; OCR and diagram interpretation are not currently verified. A document can contain both selectable text and essential scanned pages, so inspect representative useful pages.

- [ ] A paragraph from an important page can be copied as sensible text.
- [ ] Chinese/Japanese characters survive extraction where present.
- [ ] Numerical values, decimal points, units and symbols remain intact.
- [ ] Table values remain associated with the correct row/column headings.
- [ ] Vehicle applicability and warnings are not separated from their procedure.
- [ ] The source page/section can be reopened to check the extracted passage.
- [ ] Important diagrams have been identified as a separate review requirement.
- [ ] Scan/OCR needs are recorded rather than silently treating image pages as usable text.

| Page checked | Result | Error or uncertainty | Consequence for use | Follow-up owner |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |

### 7.5 Honest page accounting

Raw PDF length is not the accepted unique repair-manual page count. Keep editions, duplicates, blank/scanned pages and usable extraction distinct. Do not turn DOCX paragraphs or vector chunks into a physical page count.

| Count | Actual value / unknown | Basis/evidence |
|---|---|---|
| Original files supplied | | |
| Total physical PDF pages | | |
| Duplicate pages excluded | | |
| Blank/unusable pages excluded | | |
| Scanned pages awaiting OCR/review | | |
| Unique accepted PDF pages after review | | |
| DOCX files; physical count not established unless rendered/count recorded | | |
| Accepted material by actual language | | |
| Remaining gap to the 500-page target, if still relevant | | |

## 8. Vehicle applicability and workshop vocabulary

### 8.1 Vehicle context used today

| Question | Answer |
|---|---|
| Which makes/models are most common? Actual count or estimate? | |
| Which engines/variants/import regions cause confusion? | |
| How is the exact vehicle/engine identified? | |
| Is VIN decoding used, and which source is trusted? | |
| When are model year and registration year different? | |
| When does trim/transmission/chassis affect the procedure? | |
| How are aftermarket modifications or replaced engines handled? | |
| What vehicle details must be requested before specifications are given? | |
| How is a generic source distinguished from a vehicle-specific one? | |
| What happens when a manual covers several models/engines? | |
| Who can confirm applicability metadata before indexing? | |

### 8.2 Local vocabulary and aliases

Record how mechanics actually speak/type. Include mixed languages, shorthand, spelling variants and local nicknames. Preserve the original wording; do not assume an alias uniquely identifies a vehicle.

| Spoken/typed term | Language | Intended meaning | Canonical make/model/engine/code, if known | Ambiguity / necessary clarification |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

### 8.3 Units and answer presentation

| Item | Actual preferred convention | Where variation causes errors |
|---|---|---|
| Mileage/distance | | |
| Torque | | |
| Pressure | | |
| Temperature | | |
| Fluid volume | | |
| Prices/currency | | |
| Date formats/model years | | |
| English/Chinese/Japanese terminology | | |

Preferred answer language / whether original technical terms should be retained:

>

## 9. Available operational data

**Manual-based RAG does not require customer invoices or a complete job database.** Collect only information needed for the selected task. The minimum useful real evaluation data is a question, relevant vehicle context, expected answer/source reference and reviewer judgement.

### 9.1 Data availability register

| Data type | Exists? Format/location? | Owner and access decision | Useful fields for selected task | Redaction/limits | Next action |
|---|---|---|---|---|---|
| Repair manuals/bulletins | | | | | |
| Actual mechanic questions | | | | | |
| Completed diagnostic cases/job cards | | | | | |
| Scan-tool codes/readings | | | | | |
| Confirmed diagnoses and repair outcomes | | | | | |
| Parts catalogue and manufacturer numbers | | | | | |
| Vehicle-to-part compatibility records | | | | | |
| Supplier quotes/stock/delivery records | | | | | |
| Historical source-relevance reviews | | | | | |
| Historical answer-usefulness feedback | | | | | |
| Historical tool access/query logs | | | | | |
| Deployment/version/handover records | | | | | |
| No existing records; prospective collection needed | | | | | |

### 9.2 Minimal real-case dataset specification

Complete the “available” column. These fields describe evidence we may collect; they are not a request for all customer information.

| Field | Purpose | Available? How obtained? | May be retained? |
|---|---|---|---|
| Pseudonymous case/query ID | Join records without customer identity | | |
| Actual date and origin | Separate real events from examples | | |
| Original mechanic question/language | Test real phrasing | | |
| Relevant make/model/year/engine/variant | Check applicability | | |
| Symptoms and fault codes | Diagnostic context | | |
| Relevant measurements/units, if needed | Interpret the specific case | | |
| Expected answer elements | Review generated content | | |
| Original source/edition/page | Establish answer support | | |
| Confirmed outcome and how verified | Distinguish diagnosis from speculation | | |
| Reviewer ID/date and uncertainties | Independent judgement | | |
| Document/query usage conditions | Keep collection within permission | | |

### 9.3 Export practicalities

| Question | Answer |
|---|---|
| Can a small redacted sample be exported? | |
| Who will export it? | |
| CSV, spreadsheet, JSON, PDF or handwritten notes? | |
| Are fields consistent across records? | |
| Are empty values distinguishable from “not tested” or “normal”? | |
| Can dates, units and source references be preserved? | |
| What must be removed before handover? | |
| Can an export include unrelated/private columns? How will those be excluded? | |
| Approved transfer method and recipient | |
| Sample delivery date | |

If no export is available, record a few permitted anonymised cases manually using section 6. Do not scrape restricted systems or infer absent outcomes.

## 10. Synthetic development data agreement

Here, “synthetic” means generated fictional fixtures used to exercise software. It must be labelled and stored separately from actual company evidence. A real record with identifying fields removed remains a real anonymised record; it is not synthetic.

Questions derived from real manuals are another category: they are source-derived drafts. Their answers and relevance labels still require independent review before a final benchmark.

### 10.1 What can be generated

| Development material | Valid use | What it cannot establish | Needed real input |
|---|---|---|---|
| Fictional symptoms and fault-code queries | Parser/routing and rejection tests | Real repair prevalence or workshop query distribution | Vocabulary/context from observed workflow |
| Dummy vehicle descriptions | Missing-field, alias and applicability tests | Actual vehicle inventory or real VIN identity | Approved variant/field definitions |
| Dummy parts catalogue | Database, search/filter and caching checks | Real part number, fitment or supplier coverage | Actual catalogue/fit source before live use |
| Fictional prices/stock/delivery | API behaviour and unknown-field tests | Market price, current stock or Singapore delivery | Live approved supplier data |
| Dummy compatibility rows | Match/mismatch/missing-context checks | Physical installation fit | Reviewed catalogue/variant records |
| EN/CN/JP sample text documents | Extraction, metadata and display tests | Genuine multilingual manual coverage or translation accuracy | Authorised original manuals and language review |
| Manual-derived draft questions/answers | Retrieval development and review preparation | Independent held-out precision without review/separation | Original pages and mechanic review |
| Fictional users and feedback | Logging, UI and feedback persistence | Distinct mechanics, real usefulness or month-long participation | Actual consenting staff/use records |
| Simulated timestamps/load requests | Timestamp handling/performance rehearsal | Historical adoption, six-month use or real mechanic activity | Real dated deployment/activity records |

Do not generate fictional company approvals, supervisor statements, production incidents, mechanic endorsements or business results and present them as real.

### 10.2 Agree on development fixtures

| Fixture type | Needed now? | Definition or examples permitted | Naming/storage rule | Reviewer, if required |
|---|---|---|---|---|
| Vehicle/parser fixtures | | | | |
| Parts/pricing fixtures | | | | |
| Multilingual extraction fixtures | | | | |
| Source-derived draft queries | | | | |
| Dummy user/feedback events | | | | |
| Missing-source/invalid-input cases | | | | |

### 10.3 Provenance rules for each dataset

| Dataset ID | Origin: real / anonymised real / source-derived draft / synthetic / public summary | Source/evidence | Development or evaluation role | Review status | Private location |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |

- [ ] Synthetic IDs have a visible development prefix or equivalent label.
- [ ] Synthetic records are excluded from workshop-user, feedback-duration and adoption counts.
- [ ] Draft labels are not described as independent mechanic labels before review.
- [ ] Development/tuning examples are separated from final held-out evaluation.
- [ ] Public summaries are not counted as company manual pages or diagnostic evidence.
- [ ] Unknown real price, fit, stock or shipping stays unknown.

## 11. Retrieval and answer evaluation

The first five examples help development. They do not by themselves establish broad diagnostic coverage or the claimed 90% retrieval precision. Select and review a separate evaluation set after the corpus and intended task are understood.

### 11.1 Reviewer arrangement

| Question | Answer |
|---|---|
| Who can review technical source relevance? | |
| Who can review repair-answer correctness? Same person or another? | |
| Languages and vehicle families each reviewer can assess | |
| Who reviews disagreements or high-consequence errors? | |
| Time available per review session | |
| First review date and method | |
| What documents will reviewers have access to? | |
| Who records source IDs/pages and decisions? | |
| May review results be retained/exported? Conditions? | |

### 11.2 Category coverage planning

The current evaluator supports these eight categories. Actual workshop scope may cover fewer; record that honestly. Do not pad absent categories with invented live cases.

| Category ID | Plain-language meaning | Relevant to workshop? | Available real questions | Source coverage / gap | Reviewer |
|---|---|---|---|---|---|
| `starting` | Starting/cranking problems | | | | |
| `idle_stalling` | Idle quality and stalling | | | | |
| `misfire_ignition` | Misfire and ignition | | | | |
| `fuel_pressure` | Fuel supply/pressure | | | | |
| `cooling` | Cooling/temperature issues | | | | |
| `charging` | Battery/charging issues | | | | |
| `sensor_emissions` | Sensors and emissions | | | | |
| `mechanical_noise` | Mechanical noises | | | | |

Other task categories or language groups requiring a different evaluation:

>

### 11.3 Source relevance review form

During the visit, manual pages are enough to identify candidate correct sources. The developer can map them to actual passage IDs after extraction; the mapping should then be checked by a reviewer.

| Field | Fill in |
|---|---|
| Query ID and original question | |
| Vehicle context and missing details | |
| Category/language | |
| Index/corpus release, when available | |
| Applicable original source/edition | |
| Correct page/section or set of pages | |
| What makes each source relevant? | |
| Are multiple sources necessary to answer? | |
| Are nearby/overlapping passages redundant? | |
| Should this query return no passage? Why? | |
| Reviewer/date | |
| Uncertainty/disagreement and resolution | |
| Development or held-out designation | |

### 11.4 Answer review form

A known citation ID proves which passage was referenced, not that the answer is true, complete or safe to act on.

| Check | Reviewer result: yes / no / uncertain / not applicable | Correction/source |
|---|---|---|
| Correct make/model/year/engine/edition | | |
| Needed context was requested before specific advice | | |
| Factual statements are supported by the cited passages | | |
| Numerical values and units match the original | | |
| Warnings/conditions are preserved | | |
| No unsupported part number, torque, interval or diagnostic percentage | | |
| No inapplicable procedure mixed in | | |
| Missing evidence is explained appropriately | | |
| Language is understandable and technical terms are preserved | | |
| Answer is useful for the chosen workflow | | |
| Expert/source verification is still required before action | | |

Query / answer / reviewer / actual date / release reference:

>

Required correction and whether it blocks further pilot use:

>

### 11.5 Metric agreement

Current code reports distinct-passage Precision@5: the number of relevant distinct retrieved passages in the top five divided by five. Missing ranks count as zero. Hit@5 is separate: whether at least one relevant passage appears. Five questions each containing one correct passage do not automatically give 100% Precision@5.

| Decision | Fill in |
|---|---|
| Actual metric to report and why | |
| Meaning of a “relevant passage” for the selected task | |
| How overlapping/duplicate passages are judged | |
| Category/language coverage required | |
| Development examples used for tuning | |
| Separate held-out questions and owner | |
| Who labels relevance independently of generated rankings? | |
| How negative/missing-source queries are assessed separately | |
| How answer correctness is assessed separately | |
| When labels/configuration will be frozen before final testing | |
| Where raw labels, rankings and versions will be retained | |
| What result would prevent a pilot or require a fix? | |

The 90% figure is a target until an actual agreed evaluation produces it. Report the actual score and sample even if the target is missed.

## 12. Pilot and feedback workflow

### 12.1 A small practical trial

| Question | Answer |
|---|---|
| Does the company want a demonstration or an actual pilot? | |
| First task and approved corpus | |
| Staff roles in initial trial | |
| Actual proposed participant count; do not default to 24 | |
| Workstation/phone/tablet and access method | |
| Proposed start/end dates | |
| Who explains how to check sources and report problems? | |
| Where will staff report an incorrect answer? | |
| Who decides whether to pause use after an error? | |
| Who checks feedback and at what frequency? | |
| What would justify expanding the trial? | |
| What would end or narrow the trial? | |

### 12.2 Participation accounting

Invited, trained, activated and active mechanics are different counts. A developer test account or a shared terminal is not proof of a distinct mechanic.

| Measure | Agreed definition | How recorded | Actual value/date, if known |
|---|---|---|---|
| Invited staff | | | |
| Trained staff | | | |
| Activated accounts | | | |
| Distinct active mechanics | | | |
| Repeated weekly use | | | |
| Real repair queries | | | |
| Developer/demo/load-test events excluded | | | |

How can participants be distinguished privately without putting names in public results?

>

### 12.3 Feedback record fields

The current prototype stores questions, answers, sources, model/release identity and anonymous ratings/comments. Company approval and attributable reviewer/participant records are still needed for business claims.

| Field | Needed/agreed? | Who enters or records it? | Access/retention |
|---|---|---|---|
| Query ID and actual timestamp | | | |
| Pseudonymous mechanic ID | | | |
| Query language and category | | | |
| Relevant vehicle context | | | |
| Retrieved source IDs/pages | | | |
| Source relevance judgement | | | |
| Answer usefulness judgement | | | |
| Unsupported/incorrect detail | | | |
| Correct source/answer and reviewer | | | |
| Release/model/index identity | | | |
| Correction status and resolution date | | | |
| Real repair event versus test/demo | | | |

### 12.4 Review calendar

| Event | Proposed date/time | Owner | Evidence to retain |
|---|---|---|---|
| Initial demonstration | | | |
| Corpus/applicability review | | | |
| First supervised pilot session | | | |
| First feedback review | | | |
| Regular feedback review cadence | | | |
| End-of-pilot review | | | |
| Independent held-out evaluation | | | |
| Adoption follow-up, if later agreed | | | |

Thirty days of feedback requires thirty actual calendar days of records. Month-six adoption requires actual use in the relevant month, not just a server that remained online.

## 13. Parts search and supplier workflow

Complete this if parts discovery is selected or likely to be a later requirement. It is not essential to start the manual-search prototype.

### 13.1 Current lookup process

| Question | Answer |
|---|---|
| Which supplier/catalogue/marketplace is searched first? | |
| What query is used: part number, vehicle, description or photo? | |
| How is OEM versus aftermarket distinguished? | |
| How is fit confirmed for engine/trim/year/region? | |
| Are superseded/cross-reference numbers used? | |
| How is Singapore shipping/delivery confirmed? | |
| Are displayed prices inclusive of tax, shipping or other charges? | |
| What currencies appear, and how are conversions handled? | |
| How are stock and price freshness checked? | |
| Which information must be checked with a supplier directly? | |
| What information may be cached, and for how long? | |
| Is any catalogue/API access available to the company? | |

### 13.2 Real part/offer example

| Field | Fill in |
|---|---|
| Example ID and actual date | |
| Vehicle context | |
| Part description and verified number/source | |
| OEM/aftermarket/used condition | |
| Supplier/source URL or private reference | |
| Evidence for fit and any unresolved restriction | |
| Quoted value and original currency | |
| Tax/shipping inclusion or unknown | |
| Evidence of stock and quoted delivery | |
| Quote validity/last checked date | |
| Permission to retain/use this record | |

### 13.3 Provider choice and access

The researched choices are in [PUBLIC_REFERENCE_RESEARCH.md](PUBLIC_REFERENCE_RESEARCH.md). Brave is the proposed direct web-search replacement; Tavily is another prototype option. Neither is configured as a new adapter yet. A general web result does not establish structured price, fit or delivery.

| Decision | Answer |
|---|---|
| Need general web discovery, structured supplier data, or both? | |
| Preferred provider and reason | |
| Existing account owner/approved purchaser | |
| Permitted domains/suppliers | |
| Provider storage/caching conditions | |
| Monthly cost/request limit agreed | |
| Private environment-file path or credential manager; no keys here | |
| Who can supply access and by when? | |

## 14. Hosting and operating the prototype

This section turns a useful local demonstration into an approved company trial. It is a follow-up if the visit is focused only on workflow/documents.

### 14.1 Operating environment

| Question | Answer |
|---|---|
| Company-controlled host or other approved location | |
| Operating system and hardware | |
| Existing browser/device and network access | |
| Docker available? Version/host, if known | |
| Who has access to install/run/update services? | |
| Approved internal URL and HTTPS/access arrangement | |
| Staff identity/sign-in mechanism | |
| Approved Gemini/provider account owner | |
| Billing/quota owner and spending limit | |
| Can the host reach the external API? | |
| Where are manuals, indexes and feedback stored privately? | |
| Existing databases/volumes that must be preserved | |
| Backup location, owner and restore procedure | |
| Who will restart it or handle failures? | |
| Who will refresh manuals and approve new editions? | |

### 14.2 Failure and handover expectations

| Situation | Expected behaviour | Responsible person/role |
|---|---|---|
| No applicable manual/source found | | |
| Required vehicle details missing | | |
| Model/API unavailable or quota exceeded | | |
| Generated answer has invalid/unsupported citations | | |
| Mechanic finds an incorrect answer | | |
| Conflicting or superseded source found | | |
| New manual edition arrives | | |
| Host restarts or index becomes unavailable | | |
| Access must be revoked or records deleted | | |

### 14.3 Pilot access decision

| Field | Actual decision |
|---|---|
| Demonstration approved? Scope/conditions | |
| Pilot approved? Scope/conditions | |
| Technical checks still required before access | |
| Corpus/answer review still required | |
| Decision-maker/evidence/date | |
| Next operational review date | |

Do not mark the project “production” solely because it runs locally or has Docker configuration. Docker runtime, company hosting, access controls, restore and realistic concurrent use still need their own verification.

## 15. Historical and résumé evidence

Keep this separate from the forward-looking workflow interview. Ask neutral questions, record disagreement/unknowns and request evidence. Do not seek confirmation of figures merely because they appear in a résumé draft.

For the existing question IDs and technical verdicts, see [COMPANY_QUESTIONS.md](COMPANY_QUESTIONS.md) and [RESUME_VERIFICATION.md](RESUME_VERIFICATION.md).

### 15.1 Claim register

| Claim / question IDs | Ask neutrally | Actual answer / uncertainty | Evidence ID / date / owner | Wording supported? |
|---|---|---|---|---|
| Employment, role and dates — Q01 | What were the exact internship dates, job title and responsibilities? | | | |
| Original versus later work — Q02 | Which deliverables existed during the internship, and which were added later? | | | |
| Computer-vision approach — Q03 | What was attempted, what results existed, and why was it abandoned or changed? | | | |
| Static-data limitation — Q04 | What parts data was available, and what actual queries could not be answered? | | | |
| First AI system — Q05 | Were earlier comparable AI tools used, and what would “first” mean here? | | | |
| Authorised corpus — Q06–Q09 | Which originals were used, with what rights, languages, editions and counted usable pages? | | | |
| User count — Q10 | How many distinct mechanics actually used the system for repairs, and over which dates? | | | |
| Month of feedback — Q11 | What dated source-relevance and answer-usefulness records exist? | | | |
| Retrieval score — Q12 | Was precision measured? Which metric, sample, labels and raw results produced it? | | | |
| Eight categories — Q13 | Which diagnostic categories/languages were actually tested? | | | |
| Tuning experiments — Q14 | What chunk/overlap/embedding comparisons were run, and was final validation separate? | | | |
| Production deployment — Q15 | Where/when was it deployed, which version, and who operated it? | | | |
| Six-month adoption — Q16 | What evidence exists of continued use around July 2026 of the internship version? | | | |
| Production blockers — Q17 | What actual schema/filter incidents occurred, when and in which release? | | | |

### 15.2 Historical timeline

Git history is supporting evidence for code activity, not proof of employment or business use. The October rebuild must remain dated as later work.

| Actual date/period | Event/deliverable | Source: record / observation / recollection | Version/file/evidence | Who can confirm? |
|---|---|---|---|---|
| Internship start | | | | |
| CV exploration | | | | |
| Decision to pivot | | | | |
| Parts-search prototype | | | | |
| Manual/RAG work, if any at the time | | | | |
| Any original workshop deployment | | | | |
| Internship end | | | | |
| July 2026 usage, if recorded | | | | |
| October 2026 follow-up/rebuild | | | | |

### 15.3 Production incident capture

Copy for each actual incident. A regression fixed in October is not automatically a historical production incident.

| Field | Fill in |
|---|---|
| Incident ID / actual date | |
| Original release and environment | |
| What operation failed? | |
| User impact and how observed | |
| Relevant sanitised error/log reference | |
| Confirmed root cause versus hypothesis | |
| Fix/version/date | |
| Regression check or restoration evidence | |
| Who confirmed resolution? | |
| What can be disclosed externally? | |

### 15.4 Factual confirmation summary

This is a record of an actual confirmation only after the respondent reviews it. It is not a pre-written endorsement.

| Field | Fill in |
|---|---|
| Facts the respondent explicitly confirmed | |
| Facts they disputed or could not confirm | |
| Contemporaneous evidence provided | |
| Recollections without supporting records | |
| Proposed future work, clearly separated | |
| Permitted public wording or restrictions | |
| Respondent role/ID and actual confirmation date | |
| Confirmation evidence reference | |

If historical records do not exist, use accurately dated current-project wording and prospective measurements. A new October 2026 rollout can establish six months after rollout only in April 2027 or later, depending on the actual launch date; it cannot prove six months after a January 2026 internship.

## 16. File handover and evidence register

### 16.1 Before transfer

- [ ] Each supplied file has an owner/source and permission status.
- [ ] Originals are preserved rather than overwritten during extraction.
- [ ] Sensitive fields have been removed where unnecessary.
- [ ] Transfer and private storage location are agreed.
- [ ] No provider password, token or secret key is included in the notes.
- [ ] Files received are distinguished from files merely promised.
- [ ] Developer will compute hashes and extraction/page counts after receipt.

### 16.2 File handover log

| Item ID | Original file/title | Received or promised? | Actual received date | Private location | Permission evidence | Remaining condition |
|---|---|---|---|---|---|---|
| FILE-01 | | | | | | |
| FILE-02 | | | | | | |
| FILE-03 | | | | | | |
| FILE-04 | | | | | | |
| FILE-05 | | | | | | |
| FILE-06 | | | | | | |
| FILE-07 | | | | | | |
| FILE-08 | | | | | | |

### 16.3 Evidence register

Use short IDs such as EVID-01 in earlier sections. Keep access links private when they contain company information.

| Evidence ID | What it supports | Type/origin | Actual date/period | Private location | Owner/access conditions | Verified by / open issue |
|---|---|---|---|---|---|---|
| EVID-01 | | | | | | |
| EVID-02 | | | | | | |
| EVID-03 | | | | | | |
| EVID-04 | | | | | | |
| EVID-05 | | | | | | |
| EVID-06 | | | | | | |
| EVID-07 | | | | | | |
| EVID-08 | | | | | | |
| EVID-09 | | | | | | |
| EVID-10 | | | | | | |

### 16.4 Public/private summary boundary

| May be shared publicly, if actually authorised | Must remain private / undecided |
|---|---|
| | |
| | |
| | |

What may be shared with the developer, through which authorised method?

>

## 17. Decisions and follow-up actions

### 17.1 Decision log

Record what was decided, by whom and for which scope. Discussion does not imply approval.

| Decision ID | Question | Actual decision | Scope/conditions | Decision-maker/date | Evidence |
|---|---|---|---|---|---|
| DEC-01 | First task | | | | |
| DEC-02 | Documents and permitted use | | | | |
| DEC-03 | First real questions and reviewer | | | | |
| DEC-04 | Synthetic development fixtures | | | | |
| DEC-05 | Pilot/access/retention | | | | |
| DEC-06 | Provider/hosting, if discussed | | | | |
| DEC-07 | Historical facts/public wording | | | | |

### 17.2 Follow-up queue

| Action ID | Exact deliverable/question | Owner | Due date or next contact | Dependency | Status | Evidence/result |
|---|---|---|---|---|---|---|
| ACT-01 | | | | | | |
| ACT-02 | | | | | | |
| ACT-03 | | | | | | |
| ACT-04 | | | | | | |
| ACT-05 | | | | | | |
| ACT-06 | | | | | | |
| ACT-07 | | | | | | |
| ACT-08 | | | | | | |
| ACT-09 | | | | | | |
| ACT-10 | | | | | | |

### 17.3 Unanswered items

| Question/section | Why unresolved? | Who can answer? | Next step | Does it block company ingestion, evaluation, pilot or only a résumé claim? |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

Next agreed meeting/review and expected deliverable:

>

## 18. Departure checklist and implementation handoff

### 18.1 Minimum useful outcome today

- [ ] I know the first real task and what a useful answer should contain.
- [ ] I have seen one actual workflow or recorded an honest account of it.
- [ ] I have useful original documents or a clear owner/date for obtaining them.
- [ ] I know exactly which processing/storage uses are approved, conditional or unresolved.
- [ ] I have five real questions, or the actual smaller number, with vehicle context and answer/source references.
- [ ] A named reviewer role/ID and first review date are recorded.
- [ ] Files/answers received are separated from promises and proposals.
- [ ] Sensitive answers are in a private copy, not this public template.
- [ ] I have read back the decisions and recorded corrections.

### 18.2 What to give the developer after the visit

1. The private completed workbook or a permitted redacted summary.
2. The approved private manual-folder path and file permission conditions.
3. Actual source editions, vehicle applicability and scanned-page/diagram issues.
4. The real case/query forms with expected answers or original source pages.
5. The reviewer arrangement, task priorities and agreed next action/date.
6. Provider/host settings only if available; secret values stay in private environment files or an approved credential manager.
7. Historical evidence only where actually supplied; keep it separate from the new prototype requirements.

### 18.3 Fill-in handoff summary

| Item | Final answer |
|---|---|
| First task to build | |
| Workshop user and point in workflow | |
| Required inputs | |
| Required output and source presentation | |
| Approved manuals and private folder | |
| Document/cloud/storage permission decisions | |
| Vehicle scope/languages/editions | |
| Real questions collected and private location | |
| Missing-answer/clarification examples | |
| Reviewer and first review date | |
| Synthetic fixtures permitted for development | |
| Pilot decision or remaining prerequisite | |
| Host/provider owner, if discussed | |
| Data retention/access decisions | |
| Historical résumé facts actually evidenced | |
| Highest-priority unresolved item | |
| Next owner/action/date | |

### 18.4 Readiness decision after the visit

Select only what the collected evidence supports; these are status choices, not automatic approvals.

- [ ] Continue the public/synthetic demonstration: company permission or sources are still unavailable.
- [ ] Prepare company ingestion: originals and the relevant processing permissions are available; extraction/applicability review remains next.
- [ ] Prepare reviewed development evaluation: real questions/source references and a reviewer are available.
- [ ] Prepare a supervised pilot: reviewed sources and the agreed operational prerequisites are satisfied.
- [ ] Update a particular résumé statement: its specific evidence exists and the wording/date match it.

Reason/evidence for the selected next step:

>

## Related project documents

- [Company question ledger](COMPANY_QUESTIONS.md): Q01–Q20 evidence requests.
- [Résumé verification](RESUME_VERIFICATION.md): checked technical claims and unsupported outcomes.
- [Implementation plan](RESUME_DELIVERY_PLAN.md): detailed build/evaluation/adoption milestones.
- [Build status](BUILD_STATUS.md): features, actual checks and remaining limits.
- [Public references and search options](PUBLIC_REFERENCE_RESEARCH.md): separate industry demo and provider alternatives.
- [Quickstart](QUICKSTART.md): ingestion/index and local serving instructions.

Uncompleted in this blank template: company answers, permissions, expert labels and historical confirmations.
Remaining limitation: synthetic fixtures and cited prototype answers cannot establish real workshop performance or adoption.
