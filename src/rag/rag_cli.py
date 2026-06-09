import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.rag.rag_retriever import HybridRAGRetriever


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--full", action="store_true", help="Hiển thị context đầy đủ thay vì phần liên quan theo intent.")
    args = parser.parse_args()

    retriever = HybridRAGRetriever()
    results = retriever.retrieve(args.query)

    print(f"\nQuery: {args.query}")
    if results:
        print(f"Detected intent: {results[0].get('intent', 'unknown')}")
    print("\nTop contexts:")

    for i, item in enumerate(results, 1):
        meta = item["metadata"]

        print("=" * 80)
        print(f"Rank: {i}")
        print(f"ID: {item['id']}")
        print(f"Tên món: {meta.get('ten_mon', '')}")
        print(f"Score: {item['score']:.4f}")
        if "rerank_score" in item:
            print(
                f"Rerank: {item['rerank_score']:.4f} | "
                f"Food-name boost: {item.get('food_name_boost', 0.0):.4f}"
            )
        print(f"URL: {meta.get('url_tham_khao', meta.get('url', ''))}")
        print("-" * 80)
        context = item["document"] if args.full else item["focused_context"]
        print(context[:1800])


if __name__ == "__main__":
    main()
