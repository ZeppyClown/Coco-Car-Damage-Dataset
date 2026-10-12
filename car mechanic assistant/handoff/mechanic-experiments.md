# Retrieval Experiment Runner Handoff: `kobold-bieresel/mechanic-experiments`

**Date:** 12 October 2026  
**Worker handle:** `kobold-bieresel/mechanic-experiments`  
**Target branch:** `mechanic-experiments`  

---

## 1. Delivered Behaviour

Delivered the retrieval experiment runner harness specified in `car mechanic assistant/RESUME_DELIVERY_PLAN.md` section "C2. Compare a bounded sequence of experiments".

Key capabilities delivered:
1. **Experiment Grid Execution (`car mechanic assistant/src/retrieval_experiments.py`):**
   - **Chunk Grid:** Evaluates chunk size 800 / 1200 / 1600 characters $\times$ overlap 10% / 20% (6 configurations), holding model and corpus constant.
   - **Retrieval Ablation Ladder:** Step-by-step ablation via a non-invasive wrapper `AblationRetrieverWrapper` without modifying `rag_system.py`:
     1. `vector_only`: pure vector cosine similarity retrieval (no filters, no generic pools, no folder priority, no bonuses, no text dedup).
     2. `applicability_generic`: adds vehicle applicability filters and generic candidate pool combining.
     3. `folder_priority`: adds folder priority ranking.
     4. `exact_bonuses`: adds OBD-II fault code and vehicle metadata match bonuses.
     5. `final_dedup_rerank`: adds near-duplicate text suppression and deterministic rank ordering.
2. **Isolated Temporary Indexes:**
   - Every configuration builds an isolated temporary directory and Chroma index, evaluates via the existing evaluator (`src/evaluate_retrieval.py`), and cleans up temporary directories.
   - Serving indexes, releases, and production environments are never touched or reset.
3. **Comprehensive Run Records & Audit:**
   - Writes `experiment_records.jsonl` with every required field: corpus/manifest hash, label file hash, embedding model/dimensions/distance metric, chunk size/overlap, filter/rerank settings, git commit, date, latency (chunking, indexing, retrieval, mean query ms, wallclock), status (`completed` or `failed`), error list, query-level ranks with score components, and full evaluation results.
   - Writes `comparison_summary.json` containing evaluated/failed/skipped counts, macro/micro Precision@5, Hit@5, per-category breakdown, per-language breakdown, and 95% bootstrap confidence interval computed from query-level scores.
4. **Development vs Held-Out Split Discipline (`HeldOutGuard`):**
   - Refuses to evaluate a split marked `held-out` more than once per frozen release ID (`rel_<commit>_<corpus_hash>`) unless explicitly overridden with `--allow-held-out-override` and a recorded `--held-out-override-reason`.
   - Records all attempts and overrides in `held_out_guard_ledger.json`.
5. **Synthetic Data Provenance Protection:**
   - Summaries and individual records enforce an explicit `evidence_origin: synthetic` field derived from input labels.
   - Synthetic test fixtures can never be reported or mistaken as real workshop accuracy numbers.
6. **Fully Offline Deterministic Testing:**
   - Offline deterministic mock embeddings (`DeterministicTestEmbeddings`) allow fast, reproducible offline tests without external API calls or Gemini costs.

---

## 2. Files Changed and Delivered

- `car mechanic assistant/src/retrieval_experiments.py` (New: runner module, wrapper, held-out guard, CLI entrypoint)
- `tests/fixtures/retrieval_experiments/README.md` (New: fictional synthetic corpus documentation)
- `tests/fixtures/retrieval_experiments/synthetic_kb/` (New: 8 diagnostic categories + workshop policy synthetic markdown fixtures with metadata sidecars)
- `tests/fixtures/retrieval_experiments/synthetic_dev_labels.jsonl` (New: 10 synthetic development labels covering 8 diagnostic categories, EN/ZH/JA, labeled `evidence_origin: synthetic`)
- `tests/fixtures/retrieval_experiments/synthetic_heldout_labels.jsonl` (New: 8 synthetic held-out labels covering 8 diagnostic categories, labeled `evidence_origin: synthetic`)
- `tests/unit/test_retrieval_experiments.py` (New: comprehensive unit tests proving grid enumeration, record completeness, determinism, failure recording, held-out guard, synthetic provenance, and bootstrap interval calculation)
- `car mechanic assistant/handoff/mechanic-experiments.md` (New: this hand-off document)

Files not modified (preserved unmodified per constraints):
- `car mechanic assistant/src/document_processor.py` (unmodified)
- `car mechanic assistant/src/config.py` (unmodified)
- `car mechanic assistant/src/rag_system.py` (unmodified)
- `car mechanic assistant/src/vector_store.py` (unmodified)
- `car mechanic assistant/src/embeddings.py` (unmodified)
- `car mechanic assistant/src/evaluate_retrieval.py` (reused as-is; unmodified)
- Shared master plans (`WORKSHOP_MASTER_PLAN.md`, `BUILD_STATUS.md`, `README.md`, `QUICKSTART.md`) left unmodified for manager integration.

---

## 3. CLI Usage

From repository root:

```bash
PYTHONPATH="car mechanic assistant" .venv-worker/bin/python -m src.retrieval_experiments \
  --corpus tests/fixtures/retrieval_experiments/synthetic_kb \
  --labels tests/fixtures/retrieval_experiments/synthetic_dev_labels.jsonl \
  --output-dir "car mechanic assistant/runtime/experiments/dev_run_01"
```

CLI options:
- `--corpus PATH`: path to knowledge base directory (defaults to assistant knowledge base).
- `--labels PATH`: path to JSONL query labels file (required).
- `--output-dir PATH`: destination directory for experiment outputs (defaults to `car mechanic assistant/runtime/experiments`).
- `--allow-held-out-override`: flag to allow re-evaluating a held-out split for the same release.
- `--held-out-override-reason TEXT`: documentation string for the held-out re-evaluation override.
- `--skip-chunk-grid`: skip the 6-configuration chunk size $\times$ overlap grid.
- `--skip-ablation-ladder`: skip the 5-configuration retrieval ablation ladder.

---

## 4. Verification Commands and Exact Results

### A. All Assistant Unit Tests (including new retrieval experiment tests)
Command:
```bash
.venv-worker/bin/python -m pytest -q tests/unit/test_manual_assistant.py tests/unit/test_rag_audit.py tests/unit/test_retrieval_experiments.py
```
Output:
```text
38 passed, 7 warnings in 12.60s
```

All 7 new targeted tests in `test_retrieval_experiments.py` pass:
- `test_grid_enumerates_exactly_declared_configurations`: PASSED
- `test_records_contain_every_required_field`: PASSED
- `test_identical_inputs_give_identical_results`: PASSED
- `test_failed_configuration_is_recorded_as_failed_not_dropped`: PASSED
- `test_held_out_guard_enforces_single_run_and_records_override`: PASSED
- `test_synthetic_output_never_reported_as_real_result`: PASSED
- `test_bootstrap_ci_computation`: PASSED

### B. CLI Runner Verification with Synthetic Fixtures
Command:
```bash
PYTHONPATH="car mechanic assistant" .venv-worker/bin/python -m src.retrieval_experiments \
  --corpus tests/fixtures/retrieval_experiments/synthetic_kb \
  --labels tests/fixtures/retrieval_experiments/synthetic_dev_labels.jsonl \
  --output-dir "car mechanic assistant/runtime/experiments/dev_test"
```
Output:
```text
Executed 11 configurations (11 evaluated, 0 failed).
Results written to: car mechanic assistant/runtime/experiments/dev_test
```
Verified that `car mechanic assistant/runtime/experiments/dev_test/experiment_records.jsonl` contains 11 complete records and `comparison_summary.json` contains full summary metrics with bootstrap confidence intervals and explicit `evidence_origin: "synthetic"`.

---

## 5. Limitations

1. **Synthetic Fixtures Only:** Evaluation was conducted entirely on synthetic fictional fixtures. Real diagnostic accuracy cannot be evaluated until real workshop manuals and independent mechanic labels are provided.
2. **Zero Invasiveness on Existing Modules:** The ablation ladder is provided via `AblationRetrieverWrapper` wrapping `VectorStore` queries rather than modifying `rag_system.py` or `vector_store.py`.
3. **ChromaDB In-Memory vs Temporary Directory:** Temporary Chroma persistence directories are created on disk under `tempfile.mkdtemp` and cleaned up in a `finally` block to strictly isolate experiments and avoid cross-test contamination.

---

## 6. Ready-to-Paste Entries for Documentation

### For `car mechanic assistant/BUILD_STATUS.md`
Add to table under "Manual retrieval assistant":

```markdown
| Retrieval experiment runner | Bounded experiment grid (6 chunking configs: 800/1200/1600 × 10%/20% overlap; 5 ablation ladder stages), isolated temporary index builds, existing evaluator reuse, held-out split guard with override audit, query-level bootstrap intervals, and synthetic evidence origin enforcement. | 7 unit tests passed; CLI verified on synthetic fixtures (11/11 configurations evaluated, 0 failed); total suite 38 passed. No real accuracy numbers claimed. |
```

### For `car mechanic assistant/WORKSHOP_MASTER_PLAN.md`
Add to Work Log (Section 16):

```markdown
### 12 October 2026 — Retrieval experiment runner delivered

- **Worker:** `kobold-bieresel/mechanic-experiments`
- **Scope:** Delivery plan section C2 (retrieval experiment layer).
- **Delivered:**
  - `src/retrieval_experiments.py`: experiment runner and CLI entrypoint.
  - 6 chunk configurations (800/1200/1600 × 10%/20%) and 5-stage ablation ladder (`vector_only`, `applicability_generic`, `folder_priority`, `exact_bonuses`, `final_dedup_rerank`) via non-invasive wrapper `AblationRetrieverWrapper`.
  - Isolated temporary Chroma index construction and cleanup per configuration.
  - Reuse of existing `evaluate_retrieval.py` metrics (distinct-passage Precision@5, Hit@5, per-category, per-language).
  - Query-level bootstrap 95% confidence intervals.
  - Held-out evaluation guard enforcing single evaluation per release unless explicitly overridden.
  - Explicit `evidence_origin: synthetic` enforcement.
  - Fictional synthetic corpus and label fixtures in `tests/fixtures/retrieval_experiments/`.
- **Verification:**
  - Automated unit tests: `tests/unit/test_retrieval_experiments.py` (7/7 passed).
  - Assistant suite: `tests/unit/test_manual_assistant.py tests/unit/test_rag_audit.py tests/unit/test_retrieval_experiments.py` (38 passed, 0 failed, 7 warnings).
  - CLI execution: 11/11 configurations evaluated in isolated temporary directories.
- **Handoff:** `car mechanic assistant/handoff/mechanic-experiments.md`.
```

## 7. Integration review — 12 October 2026

The original 7-test/38-total verification above is historical to `mechanic-experiments`. After the `--no-ff` integration, **39 runner cases** pass within the **103 passed, 0 skipped, 0 failed** combined assistant/OCR suite. Final fictional CLI execution still completes **11/11 configurations, 0 failed**, with truthful offline embedding identity in records and summary. Exact combined/full commands/counts and preliminary failures are recorded in [master section 16](../WORKSHOP_MASTER_PLAN.md#16-work-log) and [BUILD_STATUS](../BUILD_STATUS.md); those are the current ledger entries.

Failure-first fixes reject mixed/missing/unknown origins and splits, canonicalise held-out aliases, refuse corrupt ledgers/reasonless overrides, confine custom ledgers/output artifacts, identify default/configured embedding implementations (including module CLI identity), close indexes and surface cleanup/hash failures, and preserve relevant source chunks beyond the first five. The configured Gemini path was already injectable through Python; new CLI `--embeddings configured` selects it explicitly and was tested with a mock only. Every row must now declare a consistent origin/split; output inside the repository must be Git-ignored and separate from corpus/index releases. The default remains deterministic offline testing, not a real-model result.

The six real processor sizes/overlaps and every ladder step have behavior checks. Deduplication is whitespace-normalised exact-text suppression, not general near-duplicate adjudication; all stages order ties deterministically. Records contain corpus/label hashes, not persisted index/manifest hashes or a complete configuration snapshot. The local ledger records allowed held-out runs/overrides, not refusals; moving/resetting it, concurrent writers or relabelling data are outside its guarantee. It does not enforce choosing one frozen configuration before held-out use. Source-stem fixtures label whole matching sources and can conflate duplicate stems; real studies need independently adjudicated passages. No real labels/result, live inference, alternative-model comparison, company approval or adoption evidence was obtained. The requested shared-ledger/run updates are applied; remaining manual-assistant work stays listed in BUILD_STATUS.
