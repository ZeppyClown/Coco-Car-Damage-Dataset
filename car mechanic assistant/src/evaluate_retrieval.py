"""Score frozen, independently labelled retrieval runs without calling a model."""
import argparse
import json
from pathlib import Path
from statistics import mean

CATEGORIES = ("starting", "idle_stalling", "misfire_ignition", "fuel_pressure",
              "cooling", "charging", "sensor_emissions", "mechanical_noise")


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def evaluate(labels, retrieved):
    if not labels:
        raise ValueError("Independent labels are required")
    runs = {row["query_id"]: row["retrieved_ids"] for row in retrieved}
    if len(runs) != len(retrieved) or len({row["query_id"] for row in labels}) != len(labels):
        raise ValueError("Duplicate query IDs")
    if set(runs) - {row["query_id"] for row in labels}:
        raise ValueError("Unlabelled queries in retrieval output")
    categories, languages, scores = {}, {}, []
    details = []
    for row in labels:
        if row["category"] not in CATEGORIES or not row.get("reviewer") or not row.get("reviewed_at"):
            raise ValueError("Labels require a diagnostic category, reviewer and review date")
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
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Scored {report['queries']} queries; Precision@5 = {report['precision_at_5']:.3f}")


if __name__ == "__main__":
    main()
