import pandas as pd
import json
import re
from pathlib import Path

'''
 Sử dụng Regex để cải thiện lỗi kí tự khi crawl về, tuy chỉ khắc phục được một ít. Nhưng sẽ có ích cho LLMs 

'''
def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # 1. Tách số và chữ nếu dính nhau (vd: 1lòng -> 1 lòng)
    text = re.sub(r'(\d+)([a-zA-ZđĐáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ])', r'\1 \2', text)
    
    # 2. Tách đơn vị đo lường bị dính với chữ cái (vd: 150 gbột -> 150 g bột, 1 củcà -> 1 củ cà)
    units = r'(g|kg|ml|l|gram|muỗng|cf|củ|trái|quả|con|miếng|nhánh|tép|bát|chén|gói|tbs)'
    vn_chars = r'[A-ZđĐa-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ]'
    pattern = r'(\d+\s*)' + units + r'(' + vn_chars + r')'
    text = re.sub(pattern, r'\1\2 \3', text, flags=re.IGNORECASE)
    
    # 3. Chữa cháy một số cụm từ hay dính nhau do scraper của Cookpad
    fixes = {
        "trứnggà": "trứng gà", 
        "bămnhuyễn": "băm nhuyễn", 
        "nướclạnh": "nước lạnh",
        "khôngđường": "không đường",
        "ănkiêng": "ăn kiêng",
        "nguyêncám": "nguyên cám"
    }
    for wrong, right in fixes.items():
        text = text.replace(wrong, right)
        
    return text.strip()

def process_golden_records(csv_path: str, output_json_path: str):
    print(f"Đang đọc dữ liệu từ: {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f" Lỗi đọc file CSV: {e}")
        return

    df['nguyen_lieu'] = df['nguyen_lieu'].fillna('')
    df['cach_lam'] = df['cach_lam'].fillna('')
    df['score'] = df['nguyen_lieu'].str.len() + df['cach_lam'].str.len()

    golden_records = {}

    for label, group in df.groupby('label'):
        # Lấy Top 10 bài viết chi tiết nhất cho mỗi món thay vì chỉ 1 bài
        top_rows = group.nlargest(10, 'score')
        
        for i, (_, row) in enumerate(top_rows.iterrows()):
            # Đặt tên key có thêm số thứ tự, ví dụ: pho_1, pho_2...
            record_key = f"{label}_{i+1}"
            
            golden_records[record_key] = {
                "ten_mon": clean_text(row['tieu_de']),
                "nguyen_lieu": clean_text(row['nguyen_lieu']),
                "cach_lam": clean_text(row['cach_lam']),
                "url_tham_khao": row['url'],
                "di_ung_enriched": None,
                "calo_enriched": None,
                "english_translation": None
            }
        
    out_path = Path(output_json_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(golden_records, f, ensure_ascii=False, indent=4)
        
    print(f"Đã trích xuất {len(golden_records)} Golden Records!")

if __name__ == "__main__":
    CSV_FILE = "backend/data/raw/recipes.csv"
    OUTPUT_JSON = "backend/data/knowledge_base/rag_knowledge_base.json"
    
    process_golden_records(CSV_FILE, OUTPUT_JSON)
