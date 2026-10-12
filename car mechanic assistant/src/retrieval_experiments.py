"""
Retrieval Experiment Runner for Car Mechanic Assistant.

Supports declared experiment grids across chunking and retrieval ablation configurations,
isolated temporary index builds, existing evaluator reuse, development vs held-out split discipline,
offline deterministic embeddings, latency & error recording, query-level ranks, and comparison summaries
with bootstrap confidence intervals.
"""
import argparse
import hashlib
import json
import math
import random
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple

# Import existing modules from car mechanic assistant
from .config import Config
from .document_processor import DocumentProcessor, canonical_vehicle_value
from .evaluate_retrieval import evaluate, read_jsonl
from .vector_store import VectorStore


# Default Experiment Grid Declarations
CHUNK_GRID_CONFIGS = [
    {"chunk_size": 800, "overlap_pct": 0.10, "chunk_overlap": 80},
    {"chunk_size": 800, "overlap_pct": 0.20, "chunk_overlap": 160},
    {"chunk_size": 1200, "overlap_pct": 0.10, "chunk_overlap": 120},
    {"chunk_size": 1200, "overlap_pct": 0.20, "chunk_overlap": 240},
    {"chunk_size": 1600, "overlap_pct": 0.10, "chunk_overlap": 160},
    {"chunk_size": 1600, "overlap_pct": 0.20, "chunk_overlap": 320},
]

ABLATION_LADDER_STAGES = [
    "vector_only",
    "applicability_generic",
    "folder_priority",
    "exact_bonuses",
    "final_dedup_rerank",
]


class DeterministicTestEmbeddings:
    """Offline deterministic mock embedding model for reproducible testing."""

    def __init__(self, model_name: str = "deterministic-test-embedding", dimensions: int = 16):
        self.model = model_name
        self.dimensions = dimensions

    def _hash_vector(self, text: str) -> List[float]:
        # Generate deterministic vector from text tokens / hash
        clean = (text or "").lower().strip()
        tokens = re.findall(r"\w+", clean)
        raw = [0.0] * self.dimensions
        if not tokens:
            # Non-zero baseline
            raw[0] = 1.0
        else:
            for t in tokens:
                h = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dimensions
                raw[idx] += 1.0 + ((h >> 8) % 10) / 10.0

        # Normalize to unit sphere for cosine space
        norm = math.sqrt(sum(x * x for x in raw))
        if norm == 0.0:
            raw[0] = 1.0
            norm = 1.0
        return [x / norm for x in raw]

    def embed_query(self, query: str) -> List[float]:
        return self._hash_vector(query)

    def embed_text(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        return self._hash_vector(text)

    def embed_batch(self, texts: List[str], batch_size: int = 32, delay: int = 0) -> List[List[float]]:
        return [self._hash_vector(t) for t in texts]


class AblationRetrieverWrapper:
    """
    Wrapper around VectorStore that allows ablating retrieval stages:
    1. vector_only: pure vector similarity search, no vehicle filter, no generic pool, no folder priority, no code/vehicle bonuses, no text dedup.
    2. applicability_generic: adds vehicle filtering and generic candidate pool combining.
    3. folder_priority: adds folder priority scoring.
    4. exact_bonuses: adds fault code and vehicle exact match bonuses.
    5. final_dedup_rerank: adds whitespace-normalised exact-text suppression; every stage orders ties deterministically.
    """

    def __init__(self, vector_store: VectorStore, stage: str = "final_dedup_rerank"):
        self.vector_store = vector_store
        if stage not in ABLATION_LADDER_STAGES:
            raise ValueError(f"Unknown ablation stage: {stage}. Valid stages: {ABLATION_LADDER_STAGES}")
        self.stage = stage

    def retrieve(self, query_text: str, n_results: int = 5, vehicle_info: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        limit = n_results or Config.TOP_K_DOCUMENTS
        vehicle_info = vehicle_info or {}
        vector = self.vector_store.embeddings.embed_query(query_text)

        if self.stage == "vector_only":
            # Stage 1: pure vector retrieval without filters or bonuses
            pool = self.vector_store.query(query_text, limit * 6, query_embedding=vector)
            found = []
            for idx, identifier in enumerate(pool["ids"][0]):
                tags = pool["metadatas"][0][idx]
                if tags.get("folder") == "09_workshop_rules":
                    continue
                doc = {
                    "id": identifier,
                    "content": pool["documents"][0][idx],
                    "metadata": tags,
                    "distance": pool["distances"][0][idx],
                    "relevance_score": max(0.0, 1.0 - pool["distances"][0][idx]) * 100.0,
                    "score_components": {"similarity": max(0.0, 1.0 - pool["distances"][0][idx]) * 100.0},
                }
                found.append(doc)
            # Rank strictly by vector distance / similarity
            found.sort(key=lambda d: (-d["relevance_score"], d["id"]))
            return found[:limit]

        # Stage 2+: Candidate pools with vehicle applicability and generic docs
        conditions = [{"make": canonical_vehicle_value(vehicle_info["make"])}] if vehicle_info.get("make") else []
        if vehicle_info.get("year"):
            year = int(vehicle_info["year"])
            conditions += [{"year_start": {"$lte": year}}, {"year_end": {"$gte": year}}]
        where = conditions[0] if len(conditions) == 1 else {"$and": conditions} if conditions else None

        pools = [self.vector_store.query(query_text, limit * 6, where=where, query_embedding=vector)] if vehicle_info.get("make") else []
        pools.append(self.vector_store.query(query_text, limit * 3, where={"scope": "generic"}, query_embedding=vector))

        found = {}
        for pool in pools:
            for idx, identifier in enumerate(pool["ids"][0]):
                tags = pool["metadatas"][0][idx]
                if tags.get("folder") == "09_workshop_rules":
                    continue
                if not self.vector_store._applicable(tags, vehicle_info) or (1.0 - pool["distances"][0][idx]) < Config.MIN_RETRIEVAL_SIMILARITY:
                    continue

                doc = {
                    "id": identifier,
                    "content": pool["documents"][0][idx],
                    "metadata": tags,
                    "distance": pool["distances"][0][idx],
                }

                # Calculate score based on stage
                components = {"similarity": max(0.0, 1.0 - doc["distance"]) * 100.0}

                if self.stage in ("folder_priority", "exact_bonuses", "final_dedup_rerank"):
                    components["folder_priority"] = Config.FOLDER_PRIORITIES.get(doc["metadata"].get("folder"), 0)

                if self.stage in ("exact_bonuses", "final_dedup_rerank"):
                    codes = re.findall(r"\b[PCBU][0-9A-F]{4}\b", query_text.upper())
                    components["fault_code"] = 20 * sum(bool(re.search(r"\b" + code + r"\b", doc["content"], re.IGNORECASE)) for code in set(codes))
                    components["vehicle_match"] = 0
                    for key, value in (vehicle_info or {}).items():
                        if key in {"make", "model", "engine"} and doc["metadata"].get(key) == canonical_vehicle_value(value):
                            components["vehicle_match"] += 15

                doc["score_components"] = components
                doc["relevance_score"] = sum(components.values())
                found[identifier] = doc

        ranked = sorted(found.values(), key=lambda d: (-d["relevance_score"], d["id"]))

        if self.stage == "final_dedup_rerank":
            # Stage 5: Deduplication of whitespace-identical text
            selected = []
            seen = set()
            for doc in ranked:
                fingerprint = re.sub(r"\s+", " ", doc["content"]).strip()
                if fingerprint not in seen:
                    selected.append(doc)
                    seen.add(fingerprint)
                if len(selected) == limit:
                    break
            return selected

        return ranked[:limit]


def get_git_commit(cwd: Optional[Path] = None) -> str:
    """Return the current Git commit hash or 'unknown'."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(cwd or Path.cwd()),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "unknown"


def compute_dir_hash(directory: Path) -> str:
    """Compute sha256 checksum of all files in a directory."""
    h = hashlib.sha256()
    for p in sorted(directory.rglob("*")):
        if p.is_file():
            rel = p.relative_to(directory).as_posix()
            h.update(rel.encode("utf-8"))
            h.update(p.read_bytes())
    return h.hexdigest()


def compute_file_hash(path: Path) -> str:
    """Compute sha256 checksum of a single file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_bootstrap_ci(scores: List[float], n_bootstraps: int = 1000, ci: float = 0.95, seed: int = 42) -> Tuple[float, float]:
    """Compute query-level bootstrap confidence interval for a metric."""
    if not scores:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(scores)
    means = []
    for _ in range(n_bootstraps):
        sample = [scores[rng.randint(0, n - 1)] for _ in range(n)]
        means.append(mean(sample))
    means.sort()
    lower_idx = int((1.0 - ci) / 2.0 * n_bootstraps)
    upper_idx = int((1.0 + ci) / 2.0 * n_bootstraps)
    lower_idx = max(0, min(lower_idx, n_bootstraps - 1))
    upper_idx = max(0, min(upper_idx, n_bootstraps - 1))
    return (round(means[lower_idx], 4), round(means[upper_idx], 4))


def normalize_split(value: str) -> str:
    aliases = {"dev": "development", "development": "development",
               "held-out": "held-out", "heldout": "held-out", "held_out": "held-out", "test": "held-out"}
    if not isinstance(value, str) or value.strip().casefold() not in aliases:
        raise ValueError("split must explicitly be development/dev or held-out/heldout/held_out/test")
    return aliases[value.strip().casefold()]


class HeldOutGuard:
    """
    Enforces held-out evaluation discipline:
    Refuses to evaluate a split marked 'held-out' more than once per frozen release
    unless explicitly overridden, and records any override.
    """

    def __init__(self, ledger_path: Path):
        self.ledger_path = ledger_path

    def _read_ledger(self) -> List[Dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        try:
            entries = json.loads(self.ledger_path.read_text(encoding="utf-8"))
            if not isinstance(entries, list) or not all(
                    isinstance(entry, dict) and entry.get("frozen_release_id") and entry.get("split")
                    for entry in entries):
                raise ValueError("Invalid entries")
            return entries
        except (OSError, ValueError) as exc:
            raise ValueError("Cannot read held-out guard ledger; refusing evaluation") from exc

    def _write_ledger(self, entries: List[Dict[str, Any]]) -> None:
        # shortcut: single-process local ledger; add locking before concurrent experiment runs.
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.ledger_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    def check_and_record(
        self,
        frozen_release_id: str,
        split_name: str,
        allow_override: bool = False,
        override_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check if held-out evaluation was already executed for this release.
        Raises PermissionError if already run and allow_override is False.
        Records the run event in the ledger.
        """
        split_name = normalize_split(split_name)
        if allow_override and (not isinstance(override_reason, str) or not override_reason.strip()):
            raise ValueError("Held-out override requires a nonblank reason")
        is_held_out = split_name == "held-out"
        if not is_held_out:
            return {"split": split_name, "is_held_out": False, "allowed": True}

        ledger = self._read_ledger()
        prior_runs = [e for e in ledger if e.get("frozen_release_id") == frozen_release_id]

        if prior_runs and not allow_override:
            raise PermissionError(
                f"Held-out evaluation guard: Split '{split_name}' was already evaluated for release '{frozen_release_id}'. "
                f"Evaluation refused to prevent test-set leakage. Pass explicit override flag with rationale to proceed."
            )

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "frozen_release_id": frozen_release_id,
            "split": split_name,
            "is_held_out": True,
            "is_override": bool(prior_runs),
            "override_reason": override_reason if prior_runs else None,
        }
        ledger.append(entry)
        self._write_ledger(ledger)
        return entry


class RetrievalExperimentRunner:
    """
    Orchestrates bounded retrieval experiments across chunking grid and ablation ladder.
    Builds isolated temporary indexes, runs retrieval queries, evaluates with existing evaluator,
    and produces structured experiment records and comparison summaries.
    """

    def __init__(
        self,
        corpus_dir: Path,
        labels_file: Path,
        output_dir: Path,
        embeddings: Optional[Any] = None,
        held_out_guard: Optional[HeldOutGuard] = None,
        allow_held_out_override: bool = False,
        held_out_override_reason: Optional[str] = None,
        top_k: int = 5,
    ):
        self.corpus_dir = Path(corpus_dir)
        self.labels_file = Path(labels_file)
        self.output_dir = Path(output_dir)
        self.embeddings = embeddings or DeterministicTestEmbeddings()
        self.top_k = top_k
        self.allow_held_out_override = allow_held_out_override
        self.held_out_override_reason = held_out_override_reason
        self.held_out_guard = held_out_guard or HeldOutGuard(self.output_dir / "held_out_guard_ledger.json")
        if self.held_out_guard.ledger_path.resolve().parent != self.output_dir.resolve():
            raise ValueError("Held-out ledger must be inside the caller's output directory")
        implementation = type(self.embeddings)
        module = "src.retrieval_experiments" if implementation is DeterministicTestEmbeddings else implementation.__module__
        self.embedding_identity = {
            "embedding_implementation": f"{module}.{implementation.__qualname__}",
            "embedding_model": getattr(self.embeddings, "model", "unknown"),
            "embedding_dimensions": getattr(self.embeddings, "dimensions", 0),
        }

    def _validate_output(self) -> None:
        output = self.output_dir.resolve()
        if output.is_relative_to(self.corpus_dir.resolve()) or output.is_relative_to(Config.CHROMA_PERSIST_DIR.resolve()):
            raise ValueError("Experiment output must be separate from the corpus and serving index")
        if any((parent / name).exists() for parent in (output, *output.parents)
               for name in ("release.json", "chroma.sqlite3")):
            raise ValueError("Experiment output cannot be inside an index release")
        artifacts = [self.output_dir / "experiment_records.jsonl", self.output_dir / "comparison_summary.json",
                     self.held_out_guard.ledger_path]
        if any(path.is_symlink() for path in artifacts):
            raise ValueError("Experiment output artifacts cannot be symlinks")
        repository = Path(__file__).resolve().parents[2]
        if output.is_relative_to(repository) and any(subprocess.run(
                ["git", "check-ignore", "--quiet", "--", str(path.resolve())], cwd=repository,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0 for path in artifacts):
            raise ValueError("Experiment output inside the repository must be Git-ignored")

    def run_configuration(
        self,
        config_id: str,
        chunk_size: int,
        chunk_overlap: int,
        overlap_pct: float,
        ablation_stage: str,
        labels: List[Dict[str, Any]],
        evidence_origin: str,
        commit_hash: str,
    ) -> Dict[str, Any]:
        """Run a single experiment configuration in an isolated temporary index."""
        start_time = time.time()
        temp_dir = None
        store = None

        record: Dict[str, Any] = {
            "config_id": config_id,
            "corpus_hash": None,
            "label_file_hash": None,
            "evidence_origin": evidence_origin,
            **self.embedding_identity,
            "distance_metric": "cosine",
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "overlap_pct": overlap_pct,
            "ablation_stage": ablation_stage,
            "git_commit": commit_hash,
            "date": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress",
            "errors": [],
            "latency": {},
            "query_ranks": [],
            "evaluation_result": None,
        }

        try:
            record["corpus_hash"] = compute_dir_hash(self.corpus_dir)
            record["label_file_hash"] = compute_file_hash(self.labels_file)
            temp_dir = Path(tempfile.mkdtemp(prefix="retrieval_exp_"))
            index_dir = temp_dir / "chroma_index"
            # 1. Chunk documents with isolated DocumentProcessor
            t_chunk_start = time.time()
            processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            chunks = processor.process_knowledge_base(self.corpus_dir)
            t_chunk_end = time.time()
            record["latency"]["chunking_seconds"] = round(t_chunk_end - t_chunk_start, 4)
            record["chunk_count"] = len(chunks)

            # 2. Build isolated temporary vector store
            t_index_start = time.time()
            store = VectorStore(persist_directory=str(index_dir), embeddings=self.embeddings)
            store.add_documents(chunks)
            t_index_end = time.time()
            record["latency"]["indexing_seconds"] = round(t_index_end - t_index_start, 4)

            # 3. Retrieve for all label queries
            retriever = AblationRetrieverWrapper(store, stage=ablation_stage)
            t_retrieval_start = time.time()
            retrieved_records = []
            query_ranks = []

            for query_row in labels:
                q_id = query_row["query_id"]
                q_text = query_row.get("query_text") or query_row.get("text") or ""
                v_info = query_row.get("vehicle")

                q_t0 = time.time()
                docs = retriever.retrieve(q_text, n_results=self.top_k, vehicle_info=v_info)
                q_t1 = time.time()

                doc_ids = [d["id"] for d in docs]
                retrieved_records.append({"query_id": q_id, "retrieved_ids": doc_ids})

                query_ranks.append({
                    "query_id": q_id,
                    "query_text": q_text,
                    "retrieved_ids": doc_ids,
                    "scores": [round(d.get("relevance_score", 0.0), 3) for d in docs],
                    "score_components": [d.get("score_components", {}) for d in docs],
                    "query_latency_ms": round((q_t1 - q_t0) * 1000, 2),
                })

            t_retrieval_end = time.time()
            record["latency"]["retrieval_total_seconds"] = round(t_retrieval_end - t_retrieval_start, 4)
            record["latency"]["mean_query_latency_ms"] = round(
                mean(qr["query_latency_ms"] for qr in query_ranks) if query_ranks else 0.0, 2
            )
            record["query_ranks"] = query_ranks

            # 4. Evaluate using existing evaluate_retrieval logic
            # Reconstruct evaluation input: labels require exact chunk_ids in relevant_ids
            # If labels carry relevant_source_stem, we map it to the generated chunk IDs in this index
            eval_labels = []
            for query_row in labels:
                row_copy = dict(query_row)
                if "relevant_source_stem" in row_copy:
                    # shortcut: source-stem fixtures label whole sources; use passage labels for real studies.
                    stem = row_copy["relevant_source_stem"]
                    matched_chunk_ids = [c.chunk_id for c in chunks if Path(c.source_file).stem == stem]
                    if matched_chunk_ids:
                        row_copy["relevant_ids"] = matched_chunk_ids
                eval_labels.append(row_copy)

            eval_result = evaluate(eval_labels, retrieved_records)
            # Add bootstrap confidence interval
            scores = [qr["precision_at_5"] for qr in eval_result.get("query_results", [])]
            ci_low, ci_high = compute_bootstrap_ci(scores)
            eval_result["bootstrap_ci_95"] = [ci_low, ci_high]

            record["evaluation_result"] = eval_result
            record["status"] = "completed"

        except Exception as e:
            record["status"] = "failed"
            record["errors"].append(str(e))
        finally:
            if store is not None:
                try:
                    store.client.close()
                except Exception as exc:
                    record["status"] = "failed"
                    record["errors"].append(f"Index close failed: {exc}")
            if temp_dir is not None:
                try:
                    shutil.rmtree(temp_dir)
                except OSError as exc:
                    record["status"] = "failed"
                    record["errors"].append(f"Index cleanup failed: {exc}")
            record["latency"]["total_wallclock_seconds"] = round(time.time() - start_time, 4)

        return record

    def run_all(
        self,
        chunk_grid: Optional[List[Dict[str, Any]]] = None,
        ablation_ladder: Optional[List[str]] = None,
        run_chunk_grid: bool = True,
        run_ablation_ladder: bool = True,
    ) -> Dict[str, Any]:
        """Run the experiment suite and write records and comparison summary."""
        raw_labels = read_jsonl(self.labels_file)
        if not raw_labels:
            raise ValueError("No label rows found in labels file")

        origins = [row.get("evidence_origin") for row in raw_labels]
        if any(origin not in ("synthetic", "real", "independent") for origin in origins) or len(set(origins)) != 1:
            raise ValueError("Every label row must declare the same evidence_origin: synthetic, real or independent")
        splits = [normalize_split(row.get("split")) for row in raw_labels]
        if len(set(splits)) != 1:
            raise ValueError("Every label row must declare the same split; do not mix development and held-out")
        split_name = splits[0]
        evidence_origin = origins[0]
        self._validate_output()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        commit_hash = get_git_commit(self.corpus_dir)
        release_id = f"rel_{commit_hash[:10]}_{compute_dir_hash(self.corpus_dir)[:8]}"

        guard_record = self.held_out_guard.check_and_record(
            frozen_release_id=release_id,
            split_name=split_name,
            allow_override=self.allow_held_out_override,
            override_reason=self.held_out_override_reason,
        )

        chunk_configs = chunk_grid or CHUNK_GRID_CONFIGS
        ablation_stages = ablation_ladder or ABLATION_LADDER_STAGES

        run_records: List[Dict[str, Any]] = []

        # 1. Chunk Size x Overlap Grid (Ablation held constant at final_dedup_rerank)
        if run_chunk_grid:
            for cfg in chunk_configs:
                cs = cfg["chunk_size"]
                ov_pct = cfg["overlap_pct"]
                ov = cfg.get("chunk_overlap", int(cs * ov_pct))
                cfg_id = f"chunk_s{cs}_o{int(ov_pct*100)}"
                rec = self.run_configuration(
                    config_id=cfg_id,
                    chunk_size=cs,
                    chunk_overlap=ov,
                    overlap_pct=ov_pct,
                    ablation_stage="final_dedup_rerank",
                    labels=raw_labels,
                    evidence_origin=evidence_origin,
                    commit_hash=commit_hash,
                )
                run_records.append(rec)

        # 2. Retrieval Ablation Ladder (Chunk size held constant at 1000x200 or first cfg)
        if run_ablation_ladder:
            base_cs = 1000
            base_ov = 200
            base_pct = 0.20
            for stage in ablation_stages:
                cfg_id = f"ablation_{stage}"
                rec = self.run_configuration(
                    config_id=cfg_id,
                    chunk_size=base_cs,
                    chunk_overlap=base_ov,
                    overlap_pct=base_pct,
                    ablation_stage=stage,
                    labels=raw_labels,
                    evidence_origin=evidence_origin,
                    commit_hash=commit_hash,
                )
                run_records.append(rec)

        # Build Comparison Summary
        summary = self._build_comparison_summary(
            run_records=run_records,
            split_name=split_name,
            evidence_origin=evidence_origin,
            commit_hash=commit_hash,
            release_id=release_id,
            guard_record=guard_record,
        )

        # Save artifacts
        records_path = self.output_dir / "experiment_records.jsonl"
        with records_path.open("w", encoding="utf-8") as f:
            for rec in run_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        summary_path = self.output_dir / "comparison_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

        return summary

    def _build_comparison_summary(
        self,
        run_records: List[Dict[str, Any]],
        split_name: str,
        evidence_origin: str,
        commit_hash: str,
        release_id: str,
        guard_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Aggregate all runs into an auditable comparison summary."""
        evaluated_count = sum(1 for r in run_records if r["status"] == "completed")
        failed_count = sum(1 for r in run_records if r["status"] == "failed")
        skipped_count = 0

        runs_summary = []
        for r in run_records:
            eval_res = r.get("evaluation_result") or {}
            runs_summary.append({
                "config_id": r["config_id"],
                "status": r["status"],
                "errors": r["errors"],
                "chunk_size": r["chunk_size"],
                "chunk_overlap": r["chunk_overlap"],
                "ablation_stage": r["ablation_stage"],
                "precision_at_5": eval_res.get("precision_at_5"),
                "macro_precision_at_5": eval_res.get("macro_precision_at_5"),
                "hit_at_5": eval_res.get("hit_at_5"),
                "bootstrap_ci_95": eval_res.get("bootstrap_ci_95"),
                "by_category": eval_res.get("by_category", {}),
                "by_language": eval_res.get("by_language", {}),
                "all_eight_categories_present": eval_res.get("all_eight_categories_present", False),
                "mean_query_latency_ms": r.get("latency", {}).get("mean_query_latency_ms"),
                "total_wallclock_seconds": r.get("latency", {}).get("total_wallclock_seconds"),
            })

        return {
            "title": "Retrieval Experiment Comparison Report",
            "date": datetime.now(timezone.utc).isoformat(),
            "git_commit": commit_hash,
            "release_id": release_id,
            "split": split_name,
            "evidence_origin": evidence_origin,
            **self.embedding_identity,
            "held_out_guard": guard_record,
            "total_configurations": len(run_records),
            "evaluated_configurations": evaluated_count,
            "failed_configurations": failed_count,
            "skipped_configurations": skipped_count,
            "runs": runs_summary,
        }


def main():
    parser = argparse.ArgumentParser(description="Run retrieval experiments across chunk grid and ablation ladder")
    parser.add_argument("--corpus", type=Path, default=Path("car mechanic assistant/knowledge_base"), help="Corpus directory")
    parser.add_argument("--labels", type=Path, required=True, help="JSONL labels file")
    parser.add_argument("--output-dir", type=Path, default=Path("car mechanic assistant/runtime/experiments"), help="Output directory")
    parser.add_argument("--embeddings", choices=("offline", "configured"), default="offline",
                        help="offline deterministic test embeddings (default); configured explicitly uses Gemini")
    parser.add_argument("--allow-held-out-override", action="store_true", help="Explicitly allow re-evaluating a held-out split")
    parser.add_argument("--held-out-override-reason", type=str, default=None, help="Documented reason for held-out re-evaluation")
    parser.add_argument("--skip-chunk-grid", action="store_true", help="Skip chunk grid experiments")
    parser.add_argument("--skip-ablation-ladder", action="store_true", help="Skip retrieval ablation ladder")
    args = parser.parse_args()

    if args.embeddings == "configured":
        from .embeddings import GeminiEmbeddings
        embeddings = GeminiEmbeddings()
    else:
        embeddings = DeterministicTestEmbeddings()

    runner = RetrievalExperimentRunner(
        corpus_dir=args.corpus,
        labels_file=args.labels,
        output_dir=args.output_dir,
        embeddings=embeddings,
        allow_held_out_override=args.allow_held_out_override,
        held_out_override_reason=args.held_out_override_reason,
    )

    summary = runner.run_all(
        run_chunk_grid=not args.skip_chunk_grid,
        run_ablation_ladder=not args.skip_ablation_ladder,
    )

    print(f"Executed {summary['total_configurations']} configurations "
          f"({summary['evaluated_configurations']} evaluated, {summary['failed_configurations']} failed).")
    print(f"Results written to: {args.output_dir}")


if __name__ == "__main__":
    main()
