# Workshop evaluation guide

Last updated: 12 October 2026. Current evidence: evaluator and fictional workflow tests only. There is no measured company extraction accuracy, staff time saving, accounting compatibility or adoption result. The [master plan](WORKSHOP_MASTER_PLAN.md) is the implementation ledger.

## Run the development comparison

From the repository root:

```sh
.venv/bin/python -m scripts.evaluate_workshop \
  --labels tests/fixtures/workshop/evaluation-labels.jsonl \
  --predictions tests/fixtures/workshop/evaluation-mocked-predictions.jsonl \
  --prediction-kind mocked
```

The command reads two files and prints aggregate JSON. It never calls a model, writes a job, changes labels, imports accounting data or scans the company archive. The three public cases are authored **contract fixtures**, not a handwriting benchmark. The predictions deliberately contain wrong/missing values and a simulated timeout so errors remain visible. Label values were specified separately; do not derive real expected labels from model output.

The sample has five resolved identity values, two amount/currency values, three description values, zero dates, eight literal text values and four cancellation flags. It includes three proposed values where the labels say unknown, two missing rows from a failed case, and two cancelled interpretation fields excluded from active-work comparison. These are fixed test inputs, not actual model performance. A zero denominator returns null accuracy.

## Input files

Each nonblank JSONL line is one case. All rows require a nonempty `case_id`; duplicate IDs and unmatched label/prediction sets fail. Case IDs need not be identifying names. Use opaque IDs for real records. Extra properties are rejected.

Expected-label line:

```json
{
  "case_id": "fictional-case-01",
  "labeler": "Fictional fixture author",
  "label_source": "synthetic_authored",
  "source_note": "Authored contract fixture; source meaning supplied by its author.",
  "record": {
    "data_origin": "synthetic_demo",
    "job_reference": "DEMO-01",
    "field_states": {"job_reference": "confirmed"},
    "items": [{"description": "Fictional inspection", "description_state": "confirmed"}]
  }
}
```

Prediction line:

```json
{
  "case_id": "fictional-case-01",
  "record": {
    "data_origin": "synthetic_demo",
    "job_reference": "DEMO-01",
    "items": [{"description": "Fictional inspection", "description_state": "proposed"}]
  }
}
```

Or retain an explicit failed attempt:

```json
{"case_id":"fictional-case-01","failure":"timeout"}
```

Failure kinds: `timeout`, `provider_error`, `invalid_response`, `disabled`. Supply exactly one record or failure. Every scheduled case must remain represented; dropping failures inflates results. A successful extraction response can be wrapped as the prediction `record`. Do not copy expected labels into predictions for a model evaluation. `--prediction-kind` must explicitly be `mocked`, `live_model` or `manual`; this declaration does not authenticate how predictions were produced.

`record` uses the shared `WorkshopDraft` schema, including decimal strings/null and explicit item states. Gold interpreted fields must be confirmed or explicitly missing/unclear; proposed labels fail. Cancelled rows can retain unreviewed interpretations but those values are excluded. Use the source's original row order; no fuzzy matching or merging is performed. Extra/missing rows have separate counts. If a real extractor changes row order, inspect that as an error and adapt the evaluation protocol explicitly before comparing runs.

For permitted real labels, use `private_source` and `independent_company_review`, with the actual reviewer/source explanation kept privately. The evaluator checks those declarations and shapes, not the reviewer's authority or independence. The current project has no such company-labelled evaluation set. Never relabel company records as synthetic to bypass processing restrictions. Keep real labels, predictions and results under ignored private storage, outside the public fixtures/Git.

## Read the report

`by_origin` keeps synthetic and private-origin cases separate. There is no combined score and `is_company_outcome` is always false: a comparison file alone cannot establish a workshop trial.

Each category reports:

- `resolved`: known gold values in the denominator.
- `correct`: exact canonical value match; money uses the schema's two-decimal representation.
- `incorrect`: a supplied different value.
- `missing_prediction`: a known value absent or lost to a failed response/row.
- `resolved_value_accuracy`: correct/resolved, null if resolved is zero.
- `unknown_expected`: gold missing/unclear values, outside resolved accuracy.
- `unknown_kept`: absent predictions for those values in an observed response.
- `values_proposed_for_unknown`: supplied candidates where the gold labels do not establish a value; inspect separately, never count as correctly inferred.
- `unknown_not_observed`: unknown fields in a failed response or missing row, not credited as abstention.

Identity, amount/currency, description, date, literal transcription and cancellation each have their own denominators. Critical errors report incorrect+missing identity, amount, description and cancellation values. Read unknown candidates, unexpected rows and failure counts alongside them; no single accuracy percentage captures these risks. Literal text comparisons remain exact, including Unicode/whitespace. An empty literal field is absent, not a fabricated value.

Cancelled interpretations do not earn active-work correctness; literal cancelled text and cancellation flags still matter. Metadata and review states are excluded from value accuracy: stage, origin, source UUID, provenance and proposed/confirmed labels have separate lifecycle/permission tests. In particular, the AI route leaves stage unknown for the operator. A field-comparison percentage is not retrieval precision or a measure of completed repairs.

Aggregate output does not echo case IDs, reviewer names, customer values, raw notes or images. Invalid CLI input produces a generic error and no report. Examine sensitive inputs locally rather than attaching full validation tracebacks to a public issue.

## Company trial prerequisites and protocol

Use the [workshop validation worksheet](WORKSHOP_VALIDATION_WORKSHEET.md) as a private fill-in copy for the reviewer/operator. It captures one job chain, independently checked values, destination rules, separate permissions and per-run full-task timings. The developer can translate checked tables to the [JSONL input contract](#input-files); the reviewer must verify that translation. The blank worksheet is not a dataset, company approval or trial result.

Before any real AI call, resolve Q07 processing permission. Before calling a result meaningful, resolve Q01/Q02/Q08: a workshop reviewer supplies meanings, stage and expected labels independently, and an operator agrees to a task comparison. F09 also needs the real source→final invoice/software→spreadsheet chain and destination mapping. The demo CSV is not that destination.

1. Freeze permitted source cases and assign opaque IDs. Include representative legibility, languages, crossed-out rows, ambiguous amounts, diagrams and missing fields. Record inclusion/exclusion reasons; do not select only easy sheets.
2. Have the reviewer label from the source without seeing model output. Distinguish readable literal text from inferred meaning. Leave unresolved shorthand/diagram directions unknown until the reviewer explains the vehicle convention and authorised operation. Store label version and review date privately alongside the JSONL/source.
3. Reserve cases that are not used for prompt/tuning decisions. Keep tuning and held-out results separate. Decide sample size and acceptable critical-error/review burden with the company; none has been approved yet.
4. Freeze model name, SDK/prompt/schema versions, image capture procedure and prediction kind for a run. Capture all scheduled responses/failures. Never silently replace bad predictions with human corrections in the raw extraction set.
5. Run the field comparison. Inspect identity/currency/amount/description/cancellation errors and unknown candidates first. Store residual errors and reviewer decisions privately. Compare a corrected final record separately if needed; human-corrected values do not establish automatic extraction accuracy.
6. Compare the same agreed job across the existing copying routine, direct manual digital entry and AI draft+review. Rotate task order where practical to reduce familiarity effects. Use representative staff, not just the developer. Record who performed each task and relevant experience privately.
7. Time the complete workflow: locate/photograph source, capture quality corrections, provider wait/failure, initial entry, review, clarification, correction, output and every remaining downstream copying step. Record interrupted/failed attempts and rework. Report sample counts, median/range and uncertainty; do not measure only model latency.
8. Verify which destination actually stopped needing retyping, if any. A generated CSV/download is not evidence that a copying step was removed. Check destination acceptance and correction/version handling under F09 before counting reuse.
9. Have the company review remaining critical errors and maintenance work. If AI adds effort, retain manual entry and record that observation. Agree scope/access/retention/backup/support before any pilot. Keep actual approval, participants, dates and limitations privately; publish only permitted summaries backed by those records.

No real trial has run. Internship dates, “first AI system,” 24 mechanics, 500+ company-manual pages, 90% retrieval precision and six-month adoption remain separate historical evidence questions, not outputs of this evaluator.
