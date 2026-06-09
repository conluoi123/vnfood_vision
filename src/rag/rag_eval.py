import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import json
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.rag.rag_retriever import HybridRAGRetriever


def normalize_for_eval(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def food_matches(result: dict, expected_food: str) -> bool:
    expected = normalize_for_eval(expected_food)
    actual_name = normalize_for_eval(result["metadata"].get("ten_mon", ""))
    actual_context = normalize_for_eval(result.get("focused_context") or result.get("document", ""))

    if expected in actual_name:
        return True

    expected_tokens = expected.split()
    if expected_tokens and all(token in actual_name.split() for token in expected_tokens):
        return True

    return bool(expected and expected in actual_context)


def fallback_keyword_match(results: list, expected_keywords: list) -> bool:
    combined = "\n".join(
        result["metadata"].get("ten_mon", "") + "\n" + result.get("document", "")
        for result in results
    )
    combined = normalize_for_eval(combined)
    return all(normalize_for_eval(keyword) in combined for keyword in expected_keywords)


def hit_at_k(results: list, item: dict, k: int) -> bool:
    top_k = results[:k]
    expected_food = item.get("expected_food", "")
    if expected_food:
        return any(food_matches(result, expected_food) for result in top_k)

    return fallback_keyword_match(top_k, item.get("expected_keywords", []))


def main():
    eval_path = Path("backend/data/eval/rag_eval_questions.json")
    output_path = Path("backend/data/eval/rag_eval_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(eval_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    retriever = HybridRAGRetriever()

    results_report = []
    total = len(questions)
    hit_1_count = 0
    hit_3_count = 0

    for item in questions:
        query = item["query"]
        results = retriever.retrieve(query)

        hit_1 = hit_at_k(results, item, 1)
        hit_3 = hit_at_k(results, item, 3)

        hit_1_count += int(hit_1)
        hit_3_count += int(hit_3)

        results_report.append({
            "query": query,
            "expected_food": item.get("expected_food", ""),
            "expected_intent": item.get("expected_intent", ""),
            "expected_keywords": item.get("expected_keywords", []),
            "hit_at_1": hit_1,
            "hit_at_3": hit_3,
            "top_results": [
                {
                    "rank": rank,
                    "id": result["id"],
                    "ten_mon": result["metadata"].get("ten_mon", ""),
                    "score": result["score"],
                    "rerank_score": result.get("rerank_score"),
                    "food_name_boost": result.get("food_name_boost"),
                    "intent": result.get("intent"),
                }
                for rank, result in enumerate(results, 1)
            ],
        })

        status = "PASS" if hit_3 else "FAIL"
        print(f"[{status}] {query}")
        print(f"  Hit@1: {'Y' if hit_1 else 'N'} | Hit@3: {'Y' if hit_3 else 'N'}")
        for rank, result in enumerate(results, 1):
            print(f"  {rank}. {result['metadata'].get('ten_mon', '')} | {result['score']:.4f}")

    hit_at_1 = hit_1_count / total if total else 0
    hit_at_3 = hit_3_count / total if total else 0

    report = {
        "total": total,
        "metrics": {
            "hit_at_1": hit_at_1,
            "hit_at_3": hit_at_3,
            "hit_at_1_count": hit_1_count,
            "hit_at_3_count": hit_3_count,
        },
        "results": results_report,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print(f"Hit@1: {hit_1_count}/{total} = {hit_at_1:.2%}")
    print(f"Hit@3: {hit_3_count}/{total} = {hit_at_3:.2%}")
    print(f"Saved report to: {output_path}")


if __name__ == "__main__":
    main()
