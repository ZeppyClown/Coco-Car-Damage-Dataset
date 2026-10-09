"""Score frozen, independently labelled retrieval runs without calling a model."""
import argparse
import json
from pathlib import Path
from statistics import mean
from datetime import date

CATEGORIES = ("starting", "idle_stalling", "misfire_ignition", "fuel_pressure",
              "cooling", "charging", "sensor_emissions", "mechanical_noise")


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def evaluate(labels, retrieved):
    if not labels:
        raise ValueError("Independent labels are required")
    for rows, field in ((labels, "relevant_ids"), (retrieved, "retrieved_ids")):
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("query_id"), str) or not row["query_id"].strip():
                raise ValueError("Each record requires a nonempty query ID")
            ids = row.get(field)
            if not isinstance(ids, list) or not all(isinstance(value, str) and value.strip() for value in ids):
                raise ValueError(f"{field} must be a list of nonempty IDs")
    runs = {row["query_id"]: row["retrieved_ids"] for row in retrieved}
    if len(runs) != len(retrieved) or len({row["query_id"] for row in labels}) != len(labels):
        raise ValueError("Duplicate query IDs")
    if set(runs) - {row["query_id"] for row in labels}:
        raise ValueError("Unlabelled queries in retrieval output")
    categories, languages, scores = {}, {}, []
    details = []
    for row in labels:
        if row.get("category") not in CATEGORIES or not isinstance(row.get("reviewer"), str) or not row["reviewer"].strip():
            raise ValueError("Labels require a diagnostic category, reviewer and review date")
        if row.get("language") not in {"en", "zh", "ja"}:
            raise ValueError("Language must be en, zh or ja")
        try:
            if date.fromisoformat(row["reviewed_at"]).isoformat() != row["reviewed_at"]:
                raise ValueError("Noncanonical review date")
        except (KeyError, TypeError, ValueError):
            raise ValueError("Review date must be YYYY-MM-DD") from None
        relevant = set(row["relevant_ids"])
        if not relevant:
            raise ValueError("Negative queries belong in a separate abstention evaluation")
        ranked = list(dict.fromkeys(runs.get(row["query_id"], [])))[:5]
        score = sum(identifier in relevant for identifier in ranked) / 5
        scores.append(score)
        categories.setdefault(row["category"], []).append(score)
        languages.setdefault(row["language"], []).append(score)
        details.append({"query_id": row["query_id"], "precision_at_5": score,
                        "hit_at_5": bool(set(ranked) & relevant), "retrieved_ids": ranked})
    by_category = {key: {"queries": len(values), "precision_at_5": mean(values)} for key, values in categories.items()}
    return {"metric": "distinct-passage Precision@5; missing ranks count as zero",
            "queries": len(labels), "missing_query_results": len({row["query_id"] for row in labels} - set(runs)),
            "precision_at_5": mean(scores), "macro_precision_at_5": mean(value["precision_at_5"] for value in by_category.values()),
            "all_eight_categories_present": set(categories) == set(CATEGORIES),
            "by_category": by_category, "by_language": {key: mean(value) for key, value in languages.items()},
            "hit_at_5": mean(row["hit_at_5"] for row in details), "query_results": details}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--retrieval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(read_jsonl(args.labels), read_jsonl(args.retrieval))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Scored {report['queries']} queries; Precision@5 = {report['precision_at_5']:.3f}")


if __name__ == "__main__":
    main()
