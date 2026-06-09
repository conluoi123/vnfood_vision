import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

DEFAULT_FIXES_PATH = "configs/text_cleaning_fixes.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def load_phrase_fixes(fixes_path: str = DEFAULT_FIXES_PATH) -> dict:
    path = Path(fixes_path)
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def fix_measurement_units(text: str) -> str:
    text = re.sub(r"(\d)([^\W\d_])", r"\1 \2", text, flags=re.UNICODE)

    unit_fixes = [
        (r"\b(\d+(?:[.,]\d+)?)\s*g(?=[^\W\d_])", r"\1 g "),
        (r"\b(\d+(?:[.,]\d+)?)\s*g\s*ram\s*", r"\1 g "),
        (r"\b(\d+(?:[.,]\d+)?)\s*gram\s*", r"\1 g "),
        (r"\b(\d+(?:[.,]\d+)?)\s*kg(?=[^\W\d_])", r"\1 kg "),
        (r"\b(\d+(?:[.,]\d+)?)\s*k\s*g\s*", r"\1 kg "),
        (r"\b(\d+(?:[.,]\d+)?)\s*ml(?=[^\W\d_])", r"\1 ml "),
        (r"\b(\d+(?:[.,]\d+)?)\s*m\s*l\s*", r"\1 ml "),
        (r"\b(\d+(?:[.,]\d+)?)\s*l\s*ít\s*", r"\1 lít "),
        (r"\b(\d+(?:[.,]\d+)?)\s*tbs\s*p?\s*", r"\1 tbsp "),
        (r"\b(\d+(?:[.,]\d+)?)\s*tsp\s*", r"\1 tsp "),
    ]
    for pattern, repl in unit_fixes:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE | re.UNICODE)

    units = [
        "muỗng canh", "muỗng cà phê", "thìa canh", "thìa cà phê",
        "muỗng", "thìa", "cây", "củ", "trái", "quả", "con", "miếng",
        "nhánh", "tép", "bát", "chén", "gói", "bông", "lát",
        "kg", "ml", "lít", "tbsp", "tsp",
    ]
    unit_pattern = "|".join(re.escape(unit) for unit in sorted(units, key=len, reverse=True))
    return re.sub(
        rf"\b(\d+(?:[.,]\d+)?\s+)({unit_pattern})(?=[^\W\d_])",
        r"\1\2 ",
        text,
        flags=re.IGNORECASE | re.UNICODE,
    )


def apply_phrase_fixes(text: str, phrase_fixes: dict) -> str:
    for wrong, right in phrase_fixes.items():
        text = text.replace(wrong, right)
        text = text.replace(wrong.capitalize(), right.capitalize())
    return text


def normalize_punctuation(text: str) -> str:
    text = re.sub(r"\s*([,.;:!?])\s*", r"\1 ", text)
    text = re.sub(r"(?:\.\s*){3,}", "... ", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s*\|\s*", " | ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text, phrase_fixes: dict | None = None):
    """Clean noisy Cookpad crawl text before storing it in the RAG knowledge base."""
    if not isinstance(text, str):
        return ""

    phrase_fixes = phrase_fixes or {}
    text = normalize_text(text)
    text = fix_measurement_units(text)
    text = apply_phrase_fixes(text, phrase_fixes)
    return normalize_punctuation(text)


def process_golden_records(
    csv_path: str,
    output_json_path: str,
    fixes_path: str = DEFAULT_FIXES_PATH,
):
    print(f"Đang đọc dữ liệu từ: {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Lỗi đọc file CSV: {e}")
        return

    required_columns = {"label", "tieu_de", "nguyen_lieu", "cach_lam", "url"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"CSV thiếu cột bắt buộc: {sorted(missing_columns)}")

    phrase_fixes = load_phrase_fixes(fixes_path)
    print(f"Đã load {len(phrase_fixes)} text cleaning fixes từ: {fixes_path}")

    df["nguyen_lieu"] = df["nguyen_lieu"].fillna("")
    df["cach_lam"] = df["cach_lam"].fillna("")
    df["score"] = df["nguyen_lieu"].str.len() + df["cach_lam"].str.len()

    golden_records = {}

    for label, group in df.groupby("label"):
        top_rows = group.nlargest(10, "score")

        for i, (_, row) in enumerate(top_rows.iterrows()):
            record_key = f"{label}_{i + 1}"
            golden_records[record_key] = {
                "ten_mon": clean_text(row["tieu_de"], phrase_fixes),
                "nguyen_lieu": clean_text(row["nguyen_lieu"], phrase_fixes),
                "cach_lam": clean_text(row["cach_lam"], phrase_fixes),
                "url_tham_khao": row["url"],
                "di_ung_enriched": None,
                "calo_enriched": None,
                "english_translation": None,
            }

    out_path = Path(output_json_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(golden_records, f, ensure_ascii=False, indent=4)

    print(f"Đã trích xuất {len(golden_records)} Golden Records!")
    print(f"Đã lưu tại: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Build RAG knowledge base from recipes.csv")
    parser.add_argument("--csv", default="backend/data/raw/recipes.csv")
    parser.add_argument("--output", default="backend/data/knowledge_base/rag_knowledge_base.json")
    parser.add_argument("--fixes", default=DEFAULT_FIXES_PATH)
    args = parser.parse_args()

    process_golden_records(args.csv, args.output, args.fixes)


if __name__ == "__main__":
    main()
