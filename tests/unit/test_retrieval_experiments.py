import json
import pytest
from pathlib import Path
from statistics import mean
import sys

ASSISTANT = Path(__file__).resolve().parents[2] / 'car mechanic assistant'
sys.path.insert(0, str(ASSISTANT))

from src.retrieval_experiments import (
    RetrievalExperimentRunner,
    DeterministicTestEmbeddings,
    HeldOutGuard,
    AblationRetrieverWrapper,
    CHUNK_GRID_CONFIGS,
    ABLATION_LADDER_STAGES,
    compute_bootstrap_ci
)
from src.evaluate_retrieval import read_jsonl

FIXTURES_DIR = Path(__file__).resolve().parents[1] / 'fixtures' / 'retrieval_experiments'
SYNTHETIC_KB = FIXTURES_DIR / 'synthetic_kb'
DEV_LABELS = FIXTURES_DIR / 'synthetic_dev_labels.jsonl'
HELDOUT_LABELS = FIXTURES_DIR / 'synthetic_heldout_labels.jsonl'


def test_grid_enumerates_exactly_declared_configurations():
    """Prove the grid enumerates exactly the declared configurations: 6 chunking + 5 ablation."""
    assert len(CHUNK_GRID_CONFIGS) == 6
    expected_chunk_sizes = {800, 1200, 1600}
    expected_overlap_pcts = {0.10, 0.20}
    actual_chunk_sizes = {c["chunk_size"] for c in CHUNK_GRID_CONFIGS}
    actual_overlap_pcts = {c["overlap_pct"] for c in CHUNK_GRID_CONFIGS}
    assert actual_chunk_sizes == expected_chunk_sizes
    assert actual_overlap_pcts == expected_overlap_pcts

    assert ABLATION_LADDER_STAGES == [
        "vector_only",
        "applicability_generic",
        "folder_priority",
        "exact_bonuses",
        "final_dedup_rerank"
    ]


def test_records_contain_every_required_field(tmp_path):
    """Prove every experiment run record contains every required field."""
    output_dir = tmp_path / "exp_out"
    runner = RetrievalExperimentRunner(
        corpus_dir=SYNTHETIC_KB,
        labels_file=DEV_LABELS,
        output_dir=output_dir,
        embeddings=DeterministicTestEmbeddings(dimensions=16),
    )
    summary = runner.run_all(run_chunk_grid=True, run_ablation_ladder=True)
    assert summary["evaluated_configurations"] == 11
    assert summary["failed_configurations"] == 0

    records_file = output_dir / "experiment_records.jsonl"
    assert records_file.exists()
    records = read_jsonl(records_file)
    assert len(records) == 11

    required_fields = {
        "config_id",
        "corpus_hash",
        "label_file_hash",
        "evidence_origin",
        "embedding_model",
        "embedding_dimensions",
        "distance_metric",
        "chunk_size",
        "chunk_overlap",
        "overlap_pct",
        "ablation_stage",
        "git_commit",
        "date",
        "status",
        "errors",
        "latency",
        "query_ranks",
        "evaluation_result"
    }

    for rec in records:
        missing = required_fields - set(rec.keys())
        assert not missing, f"Missing fields in record: {missing}"
        assert rec["distance_metric"] == "cosine"
        assert rec["embedding_dimensions"] == 16
        assert "chunking_seconds" in rec["latency"]
        assert "indexing_seconds" in rec["latency"]
        assert "mean_query_latency_ms" in rec["latency"]
        assert len(rec["query_ranks"]) > 0
        for qr in rec["query_ranks"]:
            assert "query_id" in qr
            assert "retrieved_ids" in qr
            assert "scores" in qr
            assert "query_latency_ms" in qr

        eval_res = rec["evaluation_result"]
        assert "precision_at_5" in eval_res
        assert "macro_precision_at_5" in eval_res
        assert "hit_at_5" in eval_res
        assert "by_category" in eval_res
        assert "by_language" in eval_res
        assert "bootstrap_ci_95" in eval_res


def test_identical_inputs_give_identical_results(tmp_path):
    """Prove that running identical inputs with deterministic embeddings yields identical results."""
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"

    runner1 = RetrievalExperimentRunner(
        corpus_dir=SYNTHETIC_KB,
        labels_file=DEV_LABELS,
        output_dir=out1,
        embeddings=DeterministicTestEmbeddings(dimensions=16),
    )
    runner2 = RetrievalExperimentRunner(
        corpus_dir=SYNTHETIC_KB,
        labels_file=DEV_LABELS,
        output_dir=out2,
        embeddings=DeterministicTestEmbeddings(dimensions=16),
    )

    s1 = runner1.run_all(run_chunk_grid=True, run_ablation_ladder=False)
    s2 = runner2.run_all(run_chunk_grid=True, run_ablation_ladder=False)

    rec1 = read_jsonl(out1 / "experiment_records.jsonl")
    rec2 = read_jsonl(out2 / "experiment_records.jsonl")

    assert len(rec1) == len(rec2) == 6
    for r1, r2 in zip(rec1, rec2):
        assert r1["config_id"] == r2["config_id"]
        assert r1["chunk_size"] == r2["chunk_size"]
        assert r1["chunk_overlap"] == r2["chunk_overlap"]
        assert r1["corpus_hash"] == r2["corpus_hash"]
        assert r1["label_file_hash"] == r2["label_file_hash"]
        # Retrieved IDs must be strictly identical
        ranks1 = [qr["retrieved_ids"] for qr in r1["query_ranks"]]
        ranks2 = [qr["retrieved_ids"] for qr in r2["query_ranks"]]
        assert ranks1 == ranks2
        assert r1["evaluation_result"]["precision_at_5"] == pytest.approx(r2["evaluation_result"]["precision_at_5"])
        assert r1["evaluation_result"]["hit_at_5"] == pytest.approx(r2["evaluation_result"]["hit_at_5"])


def test_failed_configuration_is_recorded_as_failed_not_dropped(tmp_path):
    """Prove a failed configuration is recorded with status='failed' and errors rather than dropped."""
    class FailingEmbeddings(DeterministicTestEmbeddings):
        def embed_batch(self, texts, **kwargs):
            raise RuntimeError("Synthetic injected embedding failure")

    output_dir = tmp_path / "exp_fail"
    runner = RetrievalExperimentRunner(
        corpus_dir=SYNTHETIC_KB,
        labels_file=DEV_LABELS,
        output_dir=output_dir,
        embeddings=FailingEmbeddings(dimensions=16),
    )
    summary = runner.run_all(run_chunk_grid=False, run_ablation_ladder=True)

    assert summary["total_configurations"] == 5
    assert summary["evaluated_configurations"] == 0
    assert summary["failed_configurations"] == 5

    records = read_jsonl(output_dir / "experiment_records.jsonl")
    assert len(records) == 5
    for r in records:
        assert r["status"] == "failed"
        assert len(r["errors"]) > 0
        assert "Synthetic injected embedding failure" in r["errors"][0]


def test_held_out_guard_enforces_single_run_and_records_override(tmp_path):
    """Prove the held-out discipline: rejects evaluating held-out more than once without override."""
    ledger_path = tmp_path / "held_out_ledger.json"
    guard = HeldOutGuard(ledger_path=ledger_path)

    # First run on held-out passes
    entry1 = guard.check_and_record(frozen_release_id="rel_frozen_v1", split_name="held-out")
    assert entry1["is_held_out"] is True
    assert entry1["is_override"] is False

    # Second run without override MUST raise PermissionError
    with pytest.raises(PermissionError, match="Held-out evaluation guard"):
        guard.check_and_record(frozen_release_id="rel_frozen_v1", split_name="held-out", allow_override=False)

    # Third run with explicit override passes and records override
    entry2 = guard.check_and_record(
        frozen_release_id="rel_frozen_v1",
        split_name="held-out",
        allow_override=True,
        override_reason="Testing held-out re-evaluation protocol"
    )
    assert entry2["is_held_out"] is True
    assert entry2["is_override"] is True
    assert entry2["override_reason"] == "Testing held-out re-evaluation protocol"


def test_synthetic_output_never_reported_as_real_result(tmp_path):
    """Prove summary carries explicit evidence_origin: synthetic taken from label file."""
    output_dir = tmp_path / "synthetic_check"
    runner = RetrievalExperimentRunner(
        corpus_dir=SYNTHETIC_KB,
        labels_file=DEV_LABELS,
        output_dir=output_dir,
        embeddings=DeterministicTestEmbeddings(dimensions=16),
    )
    summary = runner.run_all(run_chunk_grid=True, run_ablation_ladder=False)

    assert summary["evidence_origin"] == "synthetic"
    assert summary["split"] == "development"

    records = read_jsonl(output_dir / "experiment_records.jsonl")
    for r in records:
        assert r["evidence_origin"] == "synthetic"


def test_bootstrap_ci_computation():
    """Prove bootstrap confidence interval computation is robust and bounded."""
    scores = [0.2, 0.4, 0.6, 0.8, 1.0, 0.4, 0.6]
    low, high = compute_bootstrap_ci(scores, n_bootstraps=500, ci=0.95, seed=123)
    assert 0.0 <= low <= high <= 1.0
    assert low <= mean(scores) <= high
