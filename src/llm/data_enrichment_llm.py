import json 
import time 
import os 
from pathlib import Path 
import google.generativeai as genai 
from dotenv import load_dotenv 


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY: 
    raise ValueError("Không tìm thấy API@")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

def enrich_data(json_path: str, output_filetune_path: str): 
    with open(json_path, 'r', encoding='utf-8') as f: 
        data = json.load(f)
    
    finetune_data = []

    print(f"Bắt đầu sinh...")
    for key, info in data.items(): 
        # Bỏ qua nếu đã làm giàu
        if info.get('calo_enriched') is not None: 
            continue 
        ten_mon = info['ten_mon']
        nguyen_lieu = info['nguyen_lieu']
        print(f"Đang xử lý món {ten_mon}....")  

        prompt = f"""
        Bạn là chuyên gia dinh dưỡng và ẩm thực Việt Nam. Đọc nguyên liệu của món "{ten_mon}": "{nguyen_lieu}".
        1. Ước tính tổng lượng Calo (trả về khoảng số, vd: "400 - 500 kcal").
        2. Liệt kê thành phần dễ gây dị ứng (hải sản, đậu phộng...). Nếu không, ghi "Không".
        3. Dịch tên món sang Tiếng Anh.
        
        TRẢ VỀ CHỈ LÀ CHUỖI JSON ĐÚNG ĐỊNH DẠNG SAU, KHÔNG GIẢI THÍCH GÌ THÊM:
        {{
            "calo_enriched": "...",
            "di_ung_enriched": "...",
            "english_translation": "..."
        }}
        """

        try:
            response = model.generate_content(prompt)
            result_text = response.text.replace('```json', '').replace('```', '').strip()
            ai_data = json.loads(result_text)
            
            data[key]['calo_enriched'] = ai_data.get('calo_enriched')
            data[key]['di_ung_enriched'] = ai_data.get('di_ung_enriched')
            data[key]['english_translation'] = ai_data.get('english_translation')
            
            finetune_data.append({
                "instruction": f"Tôi bị dị ứng đồ ăn, tôi có thể ăn {ten_mon} không?",
                "input": nguyen_lieu,
                "output": f"Dựa trên nguyên liệu, món ăn này chứa các chất gây dị ứng: {ai_data.get('di_ung_enriched')}."
            })
            
            finetune_data.append({
                "instruction": f"Món {ten_mon} bao nhiêu calo?",
                "input": nguyen_lieu,
                "output": f"Theo ước tính thành phần, món {ten_mon} cung cấp khoảng {ai_data.get('calo_enriched')}."
            })
            
            time.sleep(3) 
            
        except Exception as e:
            print(f" Lỗi ở món {ten_mon}: {e}")

    with open(json_path, 'w', encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    
    out_ft_path = Path(output_filetune_path)
    out_ft_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_ft_path, 'a', encoding='utf-8') as f: 
        for item in finetune_data: 
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"Dữ liệu đã được làm giàu tại {out_ft_path}")
        
# test 
if __name__ == "__main__": 
    RAG_DB = "backend/data/knowledge_base/rag_knowledge_base.json"
    FINETUNE_DB = "backend/data/finetune/finetune_dataset.jsonl"
    enrich_data(RAG_DB, FINETUNE_DB)
        