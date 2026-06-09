import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.rag.data_prep_rag import clean_text, load_phrase_fixes


def main():
    fixes = load_phrase_fixes()
    cases = [
        ("500gramthịtbò", "500 g thịt bò"),
        ("6câysả", "6 cây sả"),
        ("raumuống", "rau muống"),
        ("1 g iờ", "1 giờ"),
        ("2muỗngnướcmắm", "2 muỗng nước mắm"),
        ("bánhphởcắtsợinhỏ", "bánh phở cắt sợi nhỏ"),
    ]

    for raw, expected in cases:
        result = clean_text(raw, fixes)
        assert expected in result, f"{raw!r} -> {result!r}; expected to contain {expected!r}"

    print(f"Text cleaning tests passed: {len(cases)}/{len(cases)}")


if __name__ == "__main__":
    main()
