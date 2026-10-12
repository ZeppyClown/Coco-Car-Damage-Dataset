# Mechanic OCR handoff — 12 October 2026

Worker: `kobold-bieresel/mechanic-ocr`; branch: `mechanic-ocr`. Scope: resume plan B2 items 5–7, within the existing document processor. Commit hash is reported in manager mail after committing. No push or merge.

## Delivered behaviour

- OCR stays OFF by default (`OCR_ENABLED=false`). Existing callers, including both ingestion/index CLIs, obtain OCR configuration through `DocumentProcessor`; their source code is unchanged. Image-only PDF pages still fail with the existing “needs OCR” message when disabled.
- With explicit opt-in, pages with nonempty extracted text keep the existing pypdf path. Only image-only pages render through pip-installed PDFium at 300 DPI and run locally through RapidOCR 3.10.0 / ONNX Runtime / PP-OCRv6 small. English, Simplified Chinese, Traditional Chinese and Japanese passed the authored raster fixtures. No Tesseract or system installs.
- The three local model files must exist and match pinned SHA-256 values. Recognition vocabulary is embedded in the verified ONNX model. No model or dictionary download occurs during ingestion. Missing packages/models, corrupt models and OCR engine failures raise clear errors and reject the document, rather than silently dropping pages. Rendering is limited to 20 megapixels per page before bitmap allocation.
- PDF chunk provenance adds physical `page`, `extraction_method` (`text` or `OCR`), and for OCR `ocr_engine`, `ocr_confidence`, `ocr_min_confidence`. Existing source path/hash/location/chunk ID fields remain. Language is inferred per page from scripts. Manifest file records add `pages` and `quarantined_pages`; each inspected page carries method/status/location and OCR confidence when extraction succeeds.
- Confidence is the minimum recognition score across detected text lines. Engine text-score filtering is disabled, so a weak detected specification cannot vanish before the confidence check. A score below the configured threshold, or no readable text, quarantines the whole page. The manifest retains extracted text, score, reason and `review_required=true`. Quarantined pages produce no chunks, no embeddings and no accepted unique-page count. All-quarantined files return zero chunks and status `quarantined`; mixed files use `partially_quarantined` while returning accepted pages. CLI manifests therefore need review even when processing exits successfully.
- Recognised original-language text is joined with newlines; no translation, spelling repair, Unicode compatibility normalisation or number/unit/identifier rewriting. Existing whitespace normalisation is used only for duplicate-page hashes. Tests preserve `42.5 Nm`, `K24`, `P0300`, `FX-1234`; a controlled boundary test also preserves a nonbreaking space, `N·m` and `40–45 Nm` exactly.

## Files

- `car mechanic assistant/src/document_processor.py`: optional per-page OCR, quarantine and provenance.
- `car mechanic assistant/src/ocr.py`: offline engine, model checks, rendering/resource cleanup, confidence validation.
- `car mechanic assistant/src/config.py`: OCR settings only.
- `car mechanic assistant/requirements.txt`: pinned `rapidocr==3.10.0`, `pypdfium2==5.14.0`, `onnxruntime==1.31.0` (ONNX Runtime was already a transitive Chroma dependency).
- `car mechanic assistant/.env.example`: OCR keys only.
- `tests/unit/test_manual_ocr.py`: 33 new tests alongside the existing processor tests; real-model tests never download and skip explicitly when models are absent. Network connections are blocked in these tests. Index boundary uses temporary Chroma storage and fictional test embeddings.
- `tests/fixtures/ocr/generate.py` and eight `fictional_*.pdf` files: EN, Simplified/Traditional ZH, JA, mixed text/scan/unreadable, unreadable, small two-column/table layout with torque range/footnote, and 90-degree rotation. Every scanned page is image-only; tests inspect the PDF readers to prove it. Fixtures were authored here using Pillow/reportlab and an existing local PingFang font; they contain no real repair instructions or company records. To regenerate on another platform, provide an existing local CJK font through `CJK_FONT=/path/to/font.ttf python tests/fixtures/ocr/generate.py`.
- This handoff supplies shared-ledger/run-instruction text for the manager. No existing shared test file, root/shared Markdown or prohibited retrieval module was edited. Unrelated pre-existing `.gitignore` modification is preserved and excluded from this commit.

## Configuration and setup

| Key | Default | Meaning |
|---|---|---|
| `OCR_ENABLED` | `false` | Enable only by setting `true` explicitly. |
| `OCR_MODEL_DIR` | unset | Directory containing the exact three verified local models. No implicit download. |
| `OCR_MIN_CONFIDENCE` | `0.90` | Minimum permitted detected-line recognition score; must be greater than zero and at most one. |

Install into a virtualenv. Worker dependencies and downloaded models live in ignored `.venv-worker/` and `.context/ocr-models/`, never in Git. Models total 31,749,509 bytes; they must be downloaded/provisioned before first OCR use. Cold ingestion fails helpfully rather than downloading. Upstream model routes/language coverage: [RapidOCR model documentation](https://rapidai.github.io/RapidOCRDocs/main/en/model_list/); exact source URLs/hashes: [pinned RapidOCR package model table](https://github.com/RapidAI/RapidOCR/blob/v3.10.0/python/rapidocr/default_models.yaml). Preserve upstream model notices/licences when distributing models.

From the worktree root, this explicit provisioning command downloads model assets only; it does not send documents anywhere:

```sh
mkdir -p .context/ocr-models
PYTHONPATH='car mechanic assistant' PYTHON_DOTENV_DISABLED=1 .venv-worker/bin/python - <<'PY'
from pathlib import Path
import hashlib
import requests
from src.ocr import MODEL_HASHES
root = Path('.context/ocr-models')
base = 'https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.10.0/onnx/'
for name, digest in MODEL_HASHES.items():
    route = 'PP-OCRv4/cls/' if name.startswith('ch_ppocr') else 'PP-OCRv6/det/' if '_det_' in name else 'PP-OCRv6/rec/'
    response = requests.get(base + route + name, timeout=120)
    response.raise_for_status()
    assert hashlib.sha256(response.content).hexdigest() == digest, name
    (root / name).write_bytes(response.content)
PY
```

Set `OCR_ENABLED=true`, `OCR_MODEL_DIR` to the absolute provisioned directory and choose a review threshold explicitly for an approved corpus. Normal assistant index commands need no new framework/flags. Keep corpus manifests private when they contain real source text: quarantine records now retain extracted text for review.

## Actual verification

Commands below run from `.context/` inside this worktree. `PYTHON_DOTENV_DISABLED=1` prevents assistant `.env` loading, and this empty scratch working directory prevents API settings from reading a root `.env`. Only fictional documents/temp indexes were used; no Gemini/external inference calls, private records, runtime databases or built indexes were read.

1. Failure-first new tests: `PYTHONPATH=.. PYTHON_DOTENV_DISABLED=1 ../.venv-worker/bin/python -m pytest ../tests/unit/test_manual_ocr.py -q` — 21 setup errors because the new settings/module did not exist yet. An earlier invocation used the wrong scratch-relative output path and ran no tests; corrected before this failure-first run.
2. Initial implementation: same OCR command with `OCR_TEST_MODEL_DIR=ocr-models` — **14 passed, 7 failed**, 7 warnings, 37.16 s. Actual engine tests exposed unsupported PDFium `PdfPage` context-manager usage; changed to standard-library `closing`.
3. After correction: `PYTHONPATH=.. PYTHON_DOTENV_DISABLED=1 OCR_TEST_MODEL_DIR=ocr-models ../.venv-worker/bin/python -m pytest ../tests/unit/test_manual_ocr.py -q --tb=short` — **21 passed**, no skips, 7 warnings, 27.11 s.
4. Existing complete assistant regression: `PYTHONPATH=.. PYTHON_DOTENV_DISABLED=1 ../.venv-worker/bin/python -m pytest ../tests/unit/test_manual_assistant.py ../tests/unit/test_rag_audit.py -q` — **31 passed**, no skips, 7 warnings, 4.47 s. Existing test files unchanged.
5. Final combined suite after adding resource/error/fixture/threshold/duplicate tests: `PYTHONPATH=.. PYTHON_DOTENV_DISABLED=1 OCR_TEST_MODEL_DIR=ocr-models ../.venv-worker/bin/python -m pytest ../tests/unit/test_manual_assistant.py ../tests/unit/test_rag_audit.py ../tests/unit/test_manual_ocr.py -q` — **64 passed**, no skips, 7 pre-existing deprecation warnings, 34.79 s. This includes all 33 new OCR cases, all 31 existing assistant cases, real-model multilingual/rotation/layout/mixed/unreadable checks and mocked-embedding Chroma isolation.
6. Models-unavailable skip verification: `PYTHONPATH=.. PYTHON_DOTENV_DISABLED=1 ../.venv-worker/bin/python -m pytest ../tests/unit/test_manual_ocr.py -q` (no `OCR_TEST_MODEL_DIR`) — **26 passed, 7 skipped**, 7 warnings, 10.67 s. Each real-model skip explicitly states models are unavailable and instructs provisioning/setting the test path; tests do not fetch models or fake results.
7. Real configuration/CLI smoke: `PYTHONPATH='../car mechanic assistant' PYTHON_DOTENV_DISABLED=1 OCR_MODEL_DIR=ocr-models OCR_ENABLED=true ../.venv-worker/bin/python -m src.document_processor --knowledge-base ../tests/fixtures/ocr --manifest ocr-manifest.json` — exit 0, **Processed 8 chunks**. Manifest: eight fictional files, ten physical pages, eight accepted pages, two quarantined pages, seven unique extracted-page texts by the existing whitespace-normalised hash. Mixed file `partially_quarantined`; unreadable-only file `quarantined`; both unreadable confidence values were 0.0. Accepted language-fixture minimum line scores: EN 0.98428, JA 0.94464, Simplified ZH 0.94218, Traditional ZH 0.9554. These scores are engine outputs, not measured technical accuracy. Manifest stayed ignored in `.context/`.
8. Final fixture packaging: staged whitespace checks initially flagged ASCII85 PDF internals. Disabled ASCII85 in the generator (same raster content, binary Flate streams), regenerated and reran the complete 64-test suite successfully. Final staged `git diff --cached --check` passed. `.venv-worker/bin/python -m pip check` — **No broken requirements found**. `git diff --check` passed. Fixture pypdf inspection reported extracted-text lengths zero on every scanned page, with exactly one text page in the mixed fixture.

## Limits, prerequisites and next task

- This verifies small authored fictional pages, not real-manual accuracy, engine confidence calibration, safe torque/part-number correctness, mechanic usage, corpus size or company approval. A confident OCR transcription can still be wrong. Confidence cannot expose wholly undetected text.
- OCR returns reading-order text lines; table cell/merged-cell relationships, arbitrary multi-column reading order, handwriting, arbitrary rotations and broken nonempty text layers are not comprehensively solved. The small rotated/table fixtures prove retained text/identifiers, not complex layout correctness. Usable text follows the existing nonempty text-layer criterion; pages with both a text layer and embedded scanned regions keep the text path.
- Scans beyond the 20-megapixel render limit fail explicitly. OCR model cold load/CPU inference adds latency; full-corpus throughput has not been measured. Models are pinned to this tested package/model release rather than accepting arbitrary replacement weights.
- Existing duplicate-page accounting hashes extracted text, not page images. Rotated/scan variations can produce different spacing/transcriptions and evade deduplication; the fictional CLI smoke's seven unique text hashes are not a real-manual unique physical-page claim.
- No quarantine-review UI or automatic release of quarantined text. A mechanic must review the source and supply corrected approved text through the existing text ingestion path; lowering the threshold does not establish correctness.
- Approved real sources, permitted processing/storage/access, independent original-language technical labels and mechanic review remain company prerequisites. No private sample or external provider was used.
- Next ready manager work: apply the ledger entries below, then obtain permitted representative EN/ZH/JA scans and independent technical labels for numerical/unit/identifier and layout review. Keep unresolved/quarantined pages out of usable page counts; retain pending real-corpus and precision claims.

## Ready-to-paste BUILD_STATUS.md table entry

Replace the “Scanned PDF rejection” row:

| Scanned PDF OCR (B2.5–B2.7) | Off by default; explicit opt-in uses local checksum-verified RapidOCR/PP-OCRv6 small ONNX models for EN/Simplified ZH/Traditional ZH/JA. Mixed PDFs retain text pages and OCR only image-only pages. Page confidence/provenance recorded; low-confidence/unreadable pages quarantined and excluded from chunks/embeddings/page counts. Missing dependency/models fail explicitly; model provisioning required. | Existing assistant plus new offline OCR suite: **64 passed, no skips**, including 33 authored-fictional OCR tests. Real-model numeric/code, mixed, rotated and small table checks passed; no real-manual accuracy/calibration/company-use evidence. See `handoff/mechanic-ocr.md`. |

For “Remaining evidence and release gates”, replace the OCR bullet with:

- Opt-in OCR is verified on fictional EN/Simplified ZH/Traditional ZH/JA scans; authorised real scans, independently checked technical numbers/units/identifiers, confidence calibration, complex scanned-table/layout review and quarantine resolution remain pending. Models must be provisioned locally before offline OCR.

## Ready-to-paste master plan work-log entry

### 12 October 2026 — separate manual assistant B2.5–B2.7 offline OCR

Delivered optional per-page scanned-PDF OCR in the existing `DocumentProcessor`, with config-only opt-in (default rejection preserved), local checksum-verified RapidOCR 3.10.0 / PP-OCRv6 small / ONNX Runtime and PDFium rendering. Mixed pages retain their physical locations and text/OCR method; OCR chunks and manifest pages carry confidence/engine/threshold. Low-confidence or unreadable pages retain review text/reason in the manifest, produce no chunks/embeddings and do not count as accepted usable pages. Missing dependency/models and execution/render-limit errors reject explicitly. No text/number/unit/code normalisation or translation was added.

Files: `src/document_processor.py`, new `src/ocr.py`, OCR settings in `src/config.py`/`.env.example`, pinned assistant requirements, `tests/unit/test_manual_ocr.py`, eight authored fictional raster PDFs plus generator, and `handoff/mechanic-ocr.md`. No route/schema/index-store/retrieval framework changes; shared test files unchanged. Keys: `OCR_ENABLED=false`, `OCR_MODEL_DIR` unset, `OCR_MIN_CONFIDENCE=0.90`. Models require explicit pre-download; no runtime fetch or external inference.

Verification: `.context/` command `PYTHONPATH=.. PYTHON_DOTENV_DISABLED=1 OCR_TEST_MODEL_DIR=ocr-models ../.venv-worker/bin/python -m pytest ../tests/unit/test_manual_assistant.py ../tests/unit/test_rag_audit.py ../tests/unit/test_manual_ocr.py -q` — **64 passed/no skips**, 7 deprecation warnings, 34.79 s. EN/both ZH scripts/JA real-model fixtures preserved `42.5 Nm`, `K24`, `P0300`, `FX-1234`; unreadable/mixed quarantine, rotation and small layout checks passed. Initial real-model PDFium resource API failure was corrected and rerun; dependency consistency passed. No real sources/provider calls/company benchmark or adoption claim.

Status: verified for authored-fictional ingestion, real quality pending. Limits: line-based OCR does not establish complex table/merged-cell relationships, arbitrary scan quality or calibrated confidence; high-confidence transcription still needs technical source review. Pending prerequisites: approved sources/processing/storage path and independent mechanic labels; these do not block this fictional implementation. Next task: apply this handoff and evaluate permitted real scans/technical values without releasing unresolved pages or claiming real-corpus precision.

## Integration follow-up — 12 October 2026

The original commands/counts above describe the OCR branch before integration. `mechanic-integration` retained this handoff, provisioned the same three models under ignored `.context/ocr-models/` and verified all pinned hashes. The final combined four-file assistant suite is **103 passed, 0 skipped, 0 failed, 7 warnings**, including all 33 OCR cases and seven model-dependent cases; the experiment review adds 39 runner cases. Exact combined/full commands, results and failed preliminary checks are in [master section 16](../WORKSHOP_MASTER_PLAN.md#16-work-log) and [BUILD_STATUS](../BUILD_STATUS.md). The ledger/run/resume updates are now applied; real-source/quality/company prerequisites remain pending. No live inference or company data was used.
