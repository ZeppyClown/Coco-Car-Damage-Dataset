# Manual assistant quickstart (October 2026 rebuild)

Use Python 3.12. From the assistant directory, install `requirements.txt`. Put `GOOGLE_API_KEY` in its private `.env`; the application loads this file from its own directory. Both generation and embeddings use Google's supported `google-genai` SDK. The new default is `gemini-3.1-flash-lite`, which passed the live end-to-end check. Existing `.env` settings take precedence; set `GEMINI_GENERATION_MODEL=gemini-3.1-flash-lite` explicitly if an older configured model fails. Choose available models for your account.

## Ingest and build a new release

```sh
python -m src.document_processor --manifest runtime/corpus.json
python -m src.vector_store --output runtime/releases/initial
```

For another manual folder add `--knowledge-base /absolute/path/to/manuals` to either command. The builder refuses an existing output directory, retains failed staging directories for inspection and leaves the old serving index untouched. A model/dimension/schema mismatch requires a fresh release; no reset of the old index is performed.

Supported inputs: Markdown, text-based PDFs and DOCX. EN/CN/JP text extraction is tested with authored fixtures. PDF passages cite physical pages; DOCX passages retain block numbers and table row text. Scanned/image-only PDFs are rejected with an OCR requirement. OCR and repair correctness of scanned specifications are not claimed.

A neighbouring file such as `manual.pdf.metadata.json` can specify `make`, `model`, `engine`, `year_range`, `language`, `edition` and `scope`. Vehicle values are canonicalised; use `scope: generic` only for material verified as generally applicable. Untagged material is `unknown`, not universal. Originals must be authorised for this use. The manifest counts unique accepted PDF pages; DOCX is not counted as physical pages without a separate recorded rendering.

## Start locally

```sh
CHROMA_PERSIST_DIRECTORY=runtime/releases/initial python web_app.py
```

Open http://127.0.0.1:8080. For a production WSGI process on the same host:

```sh
CHROMA_PERSIST_DIRECTORY=runtime/releases/initial gunicorn --workers 1 --threads 4 --bind 127.0.0.1:8080 'web_app:create_app()'
```

The request lock serialises access to the shared assistant initially. A shared deployment still needs an authenticated HTTPS proxy, authorised manual access, retention policy, backups and a tested restore. Anonymous feedback cannot establish distinct mechanic identities.

Answers show retrieved source IDs, page/block locations and excerpts. Generic passages remain eligible alongside vehicle-filtered passages. Workshop policy is loaded separately and never counted as a retrieved hit. No applicable passage produces a coverage response instead of guessed specifications. Output text/source values are escaped before display.

Feedback is stored privately in `runtime/feedback.sqlite`, keyed to a recorded query ID. The initial record contains source provenance and ratings/comments, not verified mechanic identities or a month of completed reviews. `/health` reports liveness and whether the assistant has been initialised; it is not a paid model probe.

## Evaluate retrieval

```sh
python -m src.evaluate_retrieval --labels labels.jsonl --retrieval ranked-results.jsonl --output report.json
```

Each label record needs `query_id`, `category`, `language`, `relevant_ids`, `reviewer`, and `reviewed_at`. Each retrieval record needs `query_id` and ordered `retrieved_ids`. Category IDs are `starting`, `idle_stalling`, `misfire_ignition`, `fuel_pressure`, `cooling`, `charging`, `sensor_emissions`, `mechanical_noise`.

Passage Precision@5 uses a fixed denominator of five; missing ranks count as zero and exact duplicates do not earn extra credit. Hit@5 is reported separately. Labels must come from independent source review; no benchmark dataset or 90% result is supplied. Negative queries need a separate abstention evaluation. Confidence intervals, materially overlapping-passage adjudication, experiment tracking and frozen workshop evaluation remain later milestones.

Run automated tests from repository root using `python -m pytest -q`. Older summaries and saved smoke results describe the January prototype; consult BUILD_STATUS.md for the verified rebuild state.
