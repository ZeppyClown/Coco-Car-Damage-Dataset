import json
import pytest
from pathlib import Path
from statistics import mean
import sys
import os
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock


ASSISTANT = Path(__file__).resolve().parents[2] / 'car mechanic assistant'
sys.path.insert(0, str(ASSISTANT))
import src.retrieval_experiments as experiments

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
        "embedding_implementation",
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
    assert summary["embedding_implementation"] == "src.retrieval_experiments.DeterministicTestEmbeddings"
    assert summary["embedding_model"] == "deterministic-test-embedding"

    records = read_jsonl(output_dir / "experiment_records.jsonl")
    for r in records:
        assert r["evidence_origin"] == "synthetic"


def test_bootstrap_ci_computation():
    """Prove bootstrap confidence interval computation is robust and bounded."""
    scores = [0.2, 0.4, 0.6, 0.8, 1.0, 0.4, 0.6]
    low, high = compute_bootstrap_ci(scores, n_bootstraps=500, ci=0.95, seed=123)
    assert 0.0 <= low <= high <= 1.0
    assert low <= mean(scores) <= high


def write_labels(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    return path


@pytest.mark.parametrize("origins", [
    ["real", "synthetic"], ["independent", None], [None, None],
    ["synthetic", "invented"],
])
def test_rejects_mixed_missing_or_unknown_origins(tmp_path, origins):
    rows = read_jsonl(DEV_LABELS)[:2]
    for row, origin in zip(rows, origins):
        if origin is None:
            row.pop("evidence_origin")
        else:
            row["evidence_origin"] = origin
    runner = RetrievalExperimentRunner(SYNTHETIC_KB,
        write_labels(tmp_path / "labels.jsonl", rows), tmp_path / "out")
    with pytest.raises(ValueError, match="evidence_origin"):
        runner.run_all(run_chunk_grid=False, run_ablation_ladder=False)
    assert not (runner.output_dir / "comparison_summary.json").exists()


@pytest.mark.parametrize("alias", ["HELD-OUT", "heldout", "held_out", "test"])
def test_guard_cannot_be_bypassed_by_split_alias(tmp_path, alias):
    guard = HeldOutGuard(tmp_path / "ledger.json")
    guard.check_and_record("frozen", "held-out")
    with pytest.raises(PermissionError, match="Held-out evaluation guard"):
        guard.check_and_record("frozen", alias)


@pytest.mark.parametrize("splits", [
    ["development", "held-out"], ["renamed-test", "renamed-test"], [None, None],
])
def test_rejects_mixed_missing_or_renamed_splits(tmp_path, splits):
    rows = read_jsonl(DEV_LABELS)[:2]
    for row, split in zip(rows, splits):
        if split is None:
            row.pop("split")
        else:
            row["split"] = split
    runner = RetrievalExperimentRunner(SYNTHETIC_KB,
        write_labels(tmp_path / "labels.jsonl", rows), tmp_path / "out")
    with pytest.raises(ValueError, match="split"):
        runner.run_all(run_chunk_grid=False, run_ablation_ladder=False)


def test_guard_fails_closed_on_corrupt_ledger_and_requires_override_reason(tmp_path):
    path = tmp_path / "ledger.json"
    guard = HeldOutGuard(path)
    path.write_text("broken JSON")
    with pytest.raises(ValueError, match="ledger"):
        guard.check_and_record("frozen", "held-out")
    path.write_text("[]")
    guard.check_and_record("frozen", "held-out")
    with pytest.raises(ValueError, match="reason"):
        guard.check_and_record("frozen", "held-out", allow_override=True)


def test_runner_refuses_guard_outside_output_directory(tmp_path):
    with pytest.raises(ValueError, match="output directory"):
        RetrievalExperimentRunner(SYNTHETIC_KB, HELDOUT_LABELS, tmp_path / "out",
            held_out_guard=HeldOutGuard(tmp_path / "outside.json"))
    assert not (tmp_path / "outside.json").exists()


def test_output_artifact_symlink_cannot_write_outside_output(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("preserve me")
    (out / "comparison_summary.json").symlink_to(outside)
    with pytest.raises(ValueError, match="output"):
        RetrievalExperimentRunner(SYNTHETIC_KB, DEV_LABELS, out).run_all(
            run_chunk_grid=False, run_ablation_ladder=False)
    assert outside.read_text() == "preserve me"


def test_refuses_serving_release_output(tmp_path, monkeypatch):
    serving = tmp_path / "serving"
    serving.mkdir()
    (serving / "release.json").write_text('{"preserved": true}')
    monkeypatch.setattr(experiments.Config, "CHROMA_PERSIST_DIR", serving)
    with pytest.raises(ValueError, match="output"):
        RetrievalExperimentRunner(SYNTHETIC_KB, DEV_LABELS, serving / "experiments").run_all(
            run_chunk_grid=False, run_ablation_ladder=False)
    assert list(serving.iterdir()) == [serving / "release.json"]


def test_refuses_unignored_repository_output(monkeypatch):
    output = ASSISTANT / "handoff"
    original = Path.mkdir
    def mkdir(path, *args, **kwargs):
        assert path != output, "Would write into tracked documentation"
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "mkdir", mkdir)
    with pytest.raises(ValueError, match="output"):
        RetrievalExperimentRunner(SYNTHETIC_KB, DEV_LABELS, output).run_all(
            run_chunk_grid=False, run_ablation_ladder=False)


def test_configured_gemini_embeddings_use_mock_provider_and_record_implementation(tmp_path):
    from src.embeddings import GeminiEmbeddings
    client = Mock()
    def response(**kwargs):
        texts = kwargs["contents"]
        texts = texts if isinstance(texts, list) else [texts]
        return SimpleNamespace(embeddings=[SimpleNamespace(values=[1.0, 0.5, 0.25]) for _ in texts])
    client.models.embed_content.side_effect = response
    embeddings = GeminiEmbeddings(client=client, dimensions=3)
    out = tmp_path / "out"
    summary = RetrievalExperimentRunner(SYNTHETIC_KB, DEV_LABELS, out, embeddings=embeddings).run_all(
        chunk_grid=CHUNK_GRID_CONFIGS[:1], run_ablation_ladder=False)
    assert summary["evaluated_configurations"] == 1
    record = read_jsonl(out / "experiment_records.jsonl")[0]
    for result in (summary, record):
        assert result["embedding_implementation"] == "src.embeddings.GeminiEmbeddings"
        assert result["embedding_model"] == experiments.Config.EMBEDDING_MODEL
    assert {call.kwargs["config"].task_type for call in client.models.embed_content.call_args_list} == {
        "RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"}


@pytest.mark.parametrize("mode", ["offline", "configured"])
def test_cli_embedding_selection_is_explicit(tmp_path, monkeypatch, mode):
    import src.embeddings
    factory = Mock(return_value=DeterministicTestEmbeddings())
    monkeypatch.setattr(src.embeddings, "GeminiEmbeddings", factory)
    runner = Mock()
    runner.run_all.return_value = {"total_configurations": 0, "evaluated_configurations": 0, "failed_configurations": 0}
    constructor = Mock(return_value=runner)
    monkeypatch.setattr(experiments, "RetrievalExperimentRunner", constructor)
    args = ["runner", "--labels", str(DEV_LABELS), "--output-dir", str(tmp_path)]
    if mode == "configured":
        args += ["--embeddings", "configured"]
    monkeypatch.setattr(sys, "argv", args)
    experiments.main()
    assert factory.call_count == (mode == "configured")
    assert isinstance(constructor.call_args.kwargs["embeddings"], DeterministicTestEmbeddings)


def test_each_ablation_stage_changes_ranked_candidates():
    class CandidateStore:
        embeddings = DeterministicTestEmbeddings()
        _applicable = staticmethod(experiments.VectorStore._applicable)
        def query(self, query_text, n_results, where=None, **kwargs):
            rows = [
                ("wrong", "inapplicable", 0.02, "01_vehicle_specs", "vehicle", "Toyota"),
                ("a", "similarity leader", 0.10, "01_vehicle_specs", "generic", ""),
                ("b", "folder leader", 0.12, "10_troubleshooting_database", "generic", ""),
                ("c", "P0300 exact leader", 0.14, "01_vehicle_specs", "generic", ""),
                ("d", "P0300  exact leader", 0.15, "01_vehicle_specs", "generic", ""),
            ]
            if where == {"scope": "generic"}:
                rows = [row for row in rows if row[4] == "generic"]
            elif where:
                rows = []
            return {"ids": [[r[0] for r in rows]], "documents": [[r[1] for r in rows]],
                "distances": [[r[2] for r in rows]], "metadatas": [[{
                    "folder": r[3], "scope": r[4], "make": r[5]} for r in rows]]}
    store = CandidateStore()
    ranks = [[d["id"] for d in AblationRetrieverWrapper(store, stage).retrieve(
        "P0300", 5, {"make": "Honda"})] for stage in ABLATION_LADDER_STAGES]
    assert ranks == [
        ["wrong", "a", "b", "c", "d"], ["a", "b", "c", "d"],
        ["b", "a", "c", "d"], ["c", "d", "b", "a"], ["c", "b", "a"],
    ]


@pytest.mark.parametrize("cfg", CHUNK_GRID_CONFIGS)
def test_grid_uses_declared_chunk_sizes_and_overlaps(tmp_path, monkeypatch, cfg):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    text = "".join(f"fictional-{i:04d} " for i in range(600))
    (corpus / "long.md").write_text(text)
    captured = []
    class CapturingStore:
        def __init__(self, persist_directory, embeddings):
            assert Path(persist_directory).name == "chroma_index"
            self.client = Mock()
        def add_documents(self, chunks):
            captured.extend(chunks)
            raise RuntimeError("Fictional capture stop")
    monkeypatch.setattr(experiments, "VectorStore", CapturingStore)
    out = tmp_path / "out"
    summary = RetrievalExperimentRunner(corpus, DEV_LABELS, out).run_all(
        chunk_grid=[cfg], run_ablation_ladder=False)
    assert summary["failed_configurations"] == 1
    size, overlap = cfg["chunk_size"], cfg["chunk_overlap"]
    assert len(captured) > 5
    assert captured[0].content == text[:size]
    assert captured[1].content == text[size - overlap:2 * size - overlap]
    assert all(len(c.content) <= size for c in captured)


@pytest.mark.parametrize("fail", [False, True])
def test_temporary_indexes_cleaned_and_serving_untouched(tmp_path, monkeypatch, fail):
    import tempfile
    original = tempfile.mkdtemp
    created = []
    def create(**kwargs):
        path = Path(original(dir=tmp_path, **kwargs))
        created.append(path)
        return str(path)
    monkeypatch.setattr(experiments.tempfile, "mkdtemp", create)
    serving = tmp_path / "serving"
    serving.mkdir()
    release = serving / "release.json"
    release.write_text("untouched serving release")
    monkeypatch.setattr(experiments.Config, "CHROMA_PERSIST_DIR", serving)
    if fail:
        def broken(*args, **kwargs):
            raise RuntimeError("Fictional index failure")
        monkeypatch.setattr(experiments.VectorStore, "add_documents", broken)
    summary = RetrievalExperimentRunner(SYNTHETIC_KB, DEV_LABELS, tmp_path / "out").run_all(
        chunk_grid=CHUNK_GRID_CONFIGS[:1], run_ablation_ladder=False)
    assert summary["failed_configurations"] == int(fail)
    assert created and all(not path.exists() for path in created)
    assert release.read_text() == "untouched serving release"
    assert list(serving.iterdir()) == [release]


def test_hash_failure_is_recorded_and_does_not_leak_temp_index(tmp_path, monkeypatch):
    def broken(*args):
        raise OSError("Fictional hash failure")
    monkeypatch.setattr(experiments, "compute_dir_hash", broken)
    runner = RetrievalExperimentRunner(SYNTHETIC_KB, DEV_LABELS, tmp_path / "out")
    record = runner.run_configuration("hash_fail", 800, 80, 0.10,
        "vector_only", read_jsonl(DEV_LABELS), "synthetic", "frozen")
    assert record["status"] == "failed"
    assert "Fictional hash failure" in record["errors"]


def test_cleanup_failure_is_visible(tmp_path, monkeypatch):
    original = experiments.shutil.rmtree
    def cleanup(path, **kwargs):
        original(path)
        raise OSError("Fictional cleanup failure")
    monkeypatch.setattr(experiments.shutil, "rmtree", cleanup)
    summary = RetrievalExperimentRunner(SYNTHETIC_KB, DEV_LABELS, tmp_path / "out").run_all(
        chunk_grid=CHUNK_GRID_CONFIGS[:1], run_ablation_ladder=False)
    assert summary["failed_configurations"] == 1
    assert "Fictional cleanup failure" in summary["runs"][0]["errors"][0]


def test_source_stem_mapping_does_not_discard_chunks_after_first_five(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "long.md").write_text("fictional long passage " * 400)
    rows = read_jsonl(DEV_LABELS)[:1]
    rows[0]["relevant_source_stem"] = "long"
    labels = write_labels(tmp_path / "labels.jsonl", rows)
    original = experiments.evaluate
    captured = []
    def evaluate(labels, retrieved):
        captured.extend(labels[0]["relevant_ids"])
        return original(labels, retrieved)
    monkeypatch.setattr(experiments, "evaluate", evaluate)
    summary = RetrievalExperimentRunner(corpus, labels, tmp_path / "out").run_all(
        chunk_grid=CHUNK_GRID_CONFIGS[:1], run_ablation_ladder=False)
    assert summary["evaluated_configurations"] == 1
    assert len(captured) > 5


def test_module_cli_names_offline_implementation_by_stable_import_path(tmp_path):
    env = {**os.environ, "PYTHONPATH": str(ASSISTANT), "PYTHON_DOTENV_DISABLED": "1"}
    result = subprocess.run([sys.executable, "-m", "src.retrieval_experiments",
        "--corpus", str(SYNTHETIC_KB), "--labels", str(DEV_LABELS), "--output-dir", str(tmp_path),
        "--skip-chunk-grid", "--skip-ablation-ladder"], cwd=tmp_path, env=env,
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    summary = json.loads((tmp_path / "comparison_summary.json").read_text())
    assert summary["embedding_implementation"] == "src.retrieval_experiments.DeterministicTestEmbeddings"
