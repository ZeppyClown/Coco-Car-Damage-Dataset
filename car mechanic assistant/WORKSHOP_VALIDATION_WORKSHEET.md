# Workshop validation worksheet — one job, checked meaning and actual reuse

Blank template prepared 12 October 2026. This is for the selected **job-sheet capture/review** project. It contains no company answers, permission, labels or measured results. Use the [master plan](WORKSHOP_MASTER_PLAN.md) for implementation status and the [evaluation guide](WORKSHOP_EVALUATION_GUIDE.md) for the comparison protocol.

**User decision, 12 October:** assume the project is useful to its customer. Demand, baseline timing, adoption and removed-copying studies are optional. Fill the technical sections for source meaning, destination correctness and selected operation; section 6 can be skipped while building. This is a user scope assumption, not a company answer or measured result.

**Further scope decision:** old financial/GST software is assumed gone; target standalone workshop records/history/export. Sections2/4 external destination fields are optional and not required to verify this app. Invoicing/GST/accounting is a separate extension if needed. Saving/corrections/access/local recovery are developer checks, now verified in [the actual record/export report](WORKSHOP_VERIFICATION_REPORT.md).

Start with **one permitted job and a person who can explain it**. One case can establish a candidate mapping; it cannot establish representative AI accuracy or time savings. Use more representative cases for those measurements after the company agrees the task and processing path. You do not need to scan the storeroom archive.

## 1. Make a private copy and capture the essential decisions

The blank template is public. Do not put answers, customer information, company files or filled tables in this tracked file. From the repository root, make a private copy without overwriting an existing one:

```sh
umask 077
mkdir -p 'car mechanic assistant/runtime'
cp -n 'car mechanic assistant/WORKSHOP_VALIDATION_WORKSHEET.md' \
  'car mechanic assistant/runtime/workshop-validation-private.md'
git check-ignore 'car mechanic assistant/runtime/workshop-validation-private.md'
```

The ignored path is suitable only if the company permits this local storage. Follow its actual decision. Keep any supplied records/labels in an agreed private location. No passwords or API keys belong in this worksheet. Write `unknown`, `not available`, `not applicable` or `follow-up needed` instead of guessing. A blank cell is unanswered.

If time is short, obtain these technical inputs first:

- One permitted sheet and a reviewer who explains its notes, amounts, cancelled values and stage.
- If an external integration is later selected: corresponding records/columns/import example and approved mapping/correction rules. Otherwise skip those fields.
- A named operator/decision owner and separate local-storage/external-processing decisions.

Current-task timing and evidence that a copying step disappears are optional; collect them later only if measured benefit is wanted.

| Meeting and scope | Fill in privately |
|---|---|
| Actual meeting date and timezone | |
| Person explaining sheet meaning; role/authority | |
| Person entering/checking financial or spreadsheet records | |
| Person who can decide on processing and a pilot | |
| Selected task, in the operator's words | |
| Current entry destinations and why each is used | |
| Optional: exactly which existing step should disappear | |
| Decision/evidence IDs and unresolved questions | |

## 2. Follow one real job through its records — Q02/Q03/Q04/Q10

Use an opaque case ID. Keep any link to identifying details private. Do not invent a missing invoice, spreadsheet or software entry; record its absence. If redaction changes a compared value, document that change privately and use a consistent redacted reference across the chain.

| Case and source | Fill in privately |
|---|---|
| Opaque case ID and actual job/document dates | |
| Source file path/evidence ID; page/image and form version | |
| Source complete or cropped; unreadable/missing areas | |
| Record stage: `unknown` / `quote` / `approved_scope` / `completed_work` | |
| Who established that stage and from what evidence | |
| Final invoice path/evidence ID, or absent/not applicable | |
| Software name/version and corresponding record evidence | |
| Spreadsheet name/tab/row evidence, or absent/not applicable | |
| How the reviewer knows these records are the same job | |
| What changed between quote, approved work and final record | |

Do not call a reviewed quote a completed repair, final invoice or paid transaction. The current application accepts JPEG/PNG source images; a supplied PDF can be recorded as evidence but PDF upload is outside the implemented scope.

## 3. Get expected values before showing AI output — Q01/Q02/Q08

The reviewer reads the source and explains it **without seeing model predictions**. Record whether each value is visible on the sheet or supplied by a stated clarification. Preserve literal text separately from meaning. A developer's guess or corrected model output is not an independent expected label.

For interpreted values, use `confirmed`, `missing` or `unclear`. `confirmed` means the reviewer established the value; `missing` means no value is supplied; `unclear` retains uncertainty and may include a candidate. Do not use `proposed` for expected labels. Missing money is not zero. Dates must not acquire an invented year or month.

| Label provenance | Fill in privately |
|---|---|
| Case ID and label version | |
| Reviewer ID, actual review date and authority to explain this sheet | |
| Did the reviewer see model output first? Explain if yes | |
| Source reviewed and evidence for any oral clarification | |
| Language/legibility/cancellation/diagram characteristics | |
| Development or held-out case; any prior prompt/tuning exposure | |
| Unresolved issues, exclusion reason and follow-up owner | |

### Header, dates, diagram meaning and written totals

| Application field | Literal text/source location | Established value or candidate | State | Explanation/evidence |
|---|---|---|---|---|
| `job_reference` | | | | |
| `customer_reference` | | | | |
| `vehicle_reference` | | | | |
| `make` | | | | |
| `model` | | | | |
| `quotation_date` | | | | |
| `date_in` | | | | |
| `date_out` | | | | |
| `currency` | | | | |
| `diagram_notes` | | | | |
| `written_total` | | | | |
| `written_adjustment` | | | | |
| `written_grand_total` | | | | |

| Raw notes kept independently | Literal text and source location |
|---|---|
| `date_note_raw` | |
| `diagram_notes_raw` | |
| `written_totals_raw` | |

Amounts are decimal strings with at most two decimal places. Ordinary item amounts/totals are nonnegative; `written_adjustment` can be signed. Currency must be established separately. Preserve written totals even if they differ from a calculated sum; ask the reviewer why rather than silently fixing them. Quantity, unit price, tax, account codes, year and VIN are not separate fields in the current draft contract; if the destination requires them, record the requirement in section 4 for an explicit implementation decision.

### Each written item, including crossed-out rows

Copy this table for every row in the source's original order. Retain cancelled rows and their literal text. Do not merge lines to improve a result.

| Item field | Reviewer answer |
|---|---|
| Source row number/location | |
| `description_raw`: exact written text | |
| `description`: established meaning or candidate | |
| `description_state`: confirmed / missing / unclear | |
| `amount_raw`: exact written amount/marks | |
| `amount`: established decimal value or unknown | |
| `amount_state`: confirmed / missing / unclear | |
| `cancelled`: yes / no / uncertain; explain the mark | |
| Is this amount per row, per panel/group or whole job? | |
| Who explained shorthand/repair operation and on what basis? | |
| Diagram link and vehicle left/right convention, if relevant | |

An area mark alone does not establish a repair operation. The current AI route does not interpret diagram meaning or choose a stage. Reviewer clarification belongs in `manual_provenance` when diagram meaning is confirmed. Keep original and interpreted values distinct.

If cancellation is uncertain, retain that uncertainty here. The current JSON contract uses a boolean cancellation flag; do not translate an unanswered flag into `false`. Obtain clarification or document why the case cannot yet enter the scored set. Excluded cases and reasons must remain visible in the study record.

The developer can convert these checked tables into private JSONL using the existing [input contract](WORKSHOP_EVALUATION_GUIDE.md#input-files). The reviewer should cross-check that conversion. Use `private_source` and `independent_company_review` for actual company labels. Preserve a separate original model prediction/failure file; never replace it with the human-corrected record. The comparator does not verify reviewer authority, stage correctness, permitted processing or business usefulness.

## 4. Optional: specify an external destination — Q03/Q04/Q10

Skip this section for the current standalone app. Complete it only if a specific external integration is selected later. Do not recreate the old software's contract as an assumed requirement.

Choose one actual copying destination first. Bring its permitted column/export/import example; a screenshot alone may need someone to explain types and rules. Blank invoice templates do not establish the software's import contract.

| Destination decision | Fill in privately |
|---|---|
| Selected destination and why | |
| Import supported? Format/version/encoding/example file | |
| If no import: what concrete reuse could remove retyping? | |
| Accepted stage and required identifiers/fields | |
| Unknown/unclear value handling and output-blocking conditions | |
| Approved rounding/currency/tax/account rules, if needed | |
| How duplicate output/import is identified | |
| How a later correction should reach the destination | |
| Person approving the mapping and actual decision date | |

Copy a row for **every** required destination column. Give exact names and types; do not invent rules from the demo CSV.

| Exact destination column/type | Source/reviewed field and evidence | Conversion and required stage | Required? Unknown/cancelled handling | Expected value for this case | Reviewer decision |
|---|---|---|---|---|---|
| | | | | | |

| Mapping check | Actual result and evidence |
|---|---|
| Expected output checked against the completed job chain | |
| Permitted test file accepted; exact environment and errors | |
| Repeat/corrected record handling checked | |
| Optional benefit observation: copying step actually removed, or still necessary | |

The existing CSV is `workshop-demo-v1`, not an approved company import. Record test acceptance separately from an actual import. This worksheet does not authorise live financial writes; those require an explicit later scope and operating authority.

## 5. Agree the permitted path and operating responsibilities — Q06/Q07/Q09

Record separate actual decisions. Interest in the project, uploading an example or a blank answer does not establish permission for later processing. Include restrictions and evidence of who made the decision.

| Decision | Allowed / refused / conditional / undecided | Exact scope, conditions and decision evidence |
|---|---|---|
| Photograph/copy selected completed records | | |
| Store/review real records on the selected local device | | |
| Retain sources, labels, predictions and output artifacts | | |
| Send selected records to a specifically named external model/provider | | |
| Use the selected host and grant named users access | | |
| Share any redacted summary/results outside the company | | |
| Run the selected workshop pilot | | |

| Operating requirement | Fill in privately |
|---|---|
| Named operator/reviewer and decision/support owner | |
| Intended host/location and who can administer it | |
| Users/access boundaries; who may view sources or export records | |
| Retention period, deletion rules and responsible person | |
| Backup location/schedule, recovery expectation and restore owner | |
| Credential custody, revocation and remote-access requirements | |
| What staff do during network/provider/app failure | |
| What must be checked before permitted actual use | |

The current prototype has one local account and a fictional recovery drill. Company policy and actual-host operation are not validated. Real-source AI remains blocked in the application; filling in an approval does not automatically change that boundary. The next implementer must review the decision and implement/test only the selected path.

## 6. Optional: measure the whole task — Q05/Q06/Q08

**This section is optional and does not block coding or build completion.** Usefulness is assumed by the user. Complete it only to establish measured time savings/removed copying or to inform later product decisions. Extraction correctness remains a separate check using the independent labels in section 3 and the evaluation guide.

Agree the comparison before collecting results. Compare the current routine, direct digital manual entry and AI draft plus human review on the same agreed task. Include all remaining destination entry. Record staff experience and task order; repeated familiarity can affect timing. A single developer run or one easy sheet is not a workshop productivity result.

| Trial design | Fill in privately |
|---|---|
| Operator ID/role/experience; reviewer ID | |
| Representative cases and inclusion/exclusion criteria | |
| Development vs held-out cases and agreed sample size | |
| Start/end of the complete task for all three methods | |
| Task order and how repetition/familiarity will be handled | |
| Acceptable critical errors and review burden, decided by company | |
| Conditions to retain manual entry, simplify or stop | |
| Trial decision owner, dates and evidence IDs | |

### One run record — copy for each case/method

| Run metadata | Fill in privately |
|---|---|
| Case/run ID, actual date/timezone and method | |
| Operator, task order and previous exposure to this case | |
| Model/SDK/prompt/schema versions for an AI run | |
| Source/capture procedure and label/prediction artifact IDs | |
| Total start/end and elapsed time; success/unfinished/failed | |
| Interruptions and how active vs elapsed time is recorded | |

| Task phase | Start/end or elapsed time | Errors, interruptions, retries and remaining work |
|---|---|---|
| Find the source | | |
| Photograph/capture and correct image quality, if needed | | |
| Enter values manually or wait for AI | | |
| Check values against the source | | |
| Clarify shorthand, amounts, stage or diagrams | | |
| Correct and confirm the record | | |
| Generate/check output | | |
| Enter/import into each remaining destination | | |
| Resolve destination errors and later rework | | |

Record zero or not applicable explicitly when a phase is unnecessary. Retain failed/interrupted attempts, provider failures and retries. Separate elapsed time from active time using the agreed method; do not quietly drop delay/rework. Keep raw predictions separate from reviewed final values. The existing evaluator supplies field/error counts, not automatic workflow-time statistics.

| Result review | Actual evidence/decision |
|---|---|
| Cases/runs counted, failures/exclusions and reasons | |
| Identity/amount/description/cancellation errors before human correction | |
| Unknown values guessed; missing/extra rows and provider failures | |
| Errors/rework remaining after human review and destination use | |
| Complete-task time by method: sample count, median/range and limitations | |
| Which copying destination genuinely stopped requiring entry | |
| Operator finds AI helpful / adds work / undecided; explanation | |
| Continue, keep manual-only, simplify or stop; owner/date | |

## 7. Return the evidence and unlock the next implementation branch

| Evidence to return privately | Present / missing / follow-up | Permitted path/evidence ID and next action |
|---|---|---|
| Checked source meaning, stage, row order and cancellations | | |
| Optional selected integration: final records and mapping/correction rules | | |
| Independent label tables and representative-case agreement | | |
| Named operator/owner for actual operation | | |
| Optional: baseline timings or an agreed observation appointment | | |
| Processing/access/host/retention/support decisions | | |

The master records usefulness and old-software removal as user assumptions, not company validation. External F09 is deferred unless later selected, then requires its checked destination contract. Start real F08/F11 with meanings/labels and permitted processing; select real F07/F12 changes after the processing/operating path is established. Timing and old-software mapping are not required. Partial answers can unlock one branch.

This worksheet does not prove old résumé claims about 24 mechanics, 500+ repair-manual pages, 90% retrieval precision, six-month adoption or internship history. Those remain separate evidence questions. Real accuracy, compatibility and usefulness remain unverified until the corresponding checks actually run.
