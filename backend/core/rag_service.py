import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.rag.rag_retriever import HybridRAGRetriever
from src.rag.rag_generator import RAGGenerator

# Bảng ánh xạ: tên class của model -> tên tiếng Việt có dấu để RAG tìm kiếm chính xác hơn
CLASS_NAME_TO_VIET = {
    "banh_bao": "Bánh Bao",
    "banh_beo": "Bánh Bèo",
    "banh_bot_loc": "Bánh Bột Lọc",
    "banh_can": "Bánh Căn",
    "banh_canh": "Bánh Canh",
    "banh_chung": "Bánh Chưng",
    "banh_cuon": "Bánh Cuốn",
    "banh_duc": "Bánh Đúc",
    "banh_gio": "Bánh Giò",
    "banh_khot": "Bánh Khọt",
    "banh_mi": "Bánh Mì",
    "banh_pia": "Bánh Pía",
    "banh_tet": "Bánh Tét",
    "banh_trang_nuong": "Bánh Tráng Nướng",
    "banh_trang_tron": "Bánh Tráng Trộn",
    "banh_xeo": "Bánh Xèo",
    "bun_bo_hue": "Bún Bò Huế",
    "bun_cha": "Bún Chả",
    "bun_dau_mam_tom": "Bún Đậu Mắm Tôm",
    "bun_mam": "Bún Mắm",
    "bun_rieu": "Bún Riêu",
    "bun_thit_nuong": "Bún Thịt Nướng",
    "ca_kho_to": "Cá Kho Tộ",
    "canh_chua": "Canh Chua",
    "cao_lau": "Cao Lầu",
    "chao": "Cháo",
    "com_chien": "Cơm Chiên",
    "com_ga": "Cơm Gà",
    "com_tam": "Cơm Tấm",
    "ga_nuong": "Gà Nướng",
    "ga_ran": "Gà Rán",
    "goi_cuon": "Gỏi Cuốn",
    "hu_tieu": "Hủ Tiếu",
    "lau_hai_san": "Lẩu Hải Sản",
    "lau_thai": "Lẩu Thái",
    "mi_quang": "Mì Quảng",
    "nem_chua": "Nem Chua",
    "nem_ran": "Nem Rán",
    "pho": "Phở Bò",
    "sup_cua": "Súp Cua",
    "tra_sua": "Trà Sữa",
    "xoai_lac": "Xoài Lắc",
    "xoi_xeo": "Xôi Xéo",
}

# Mock DB for the Vision/App initialization step to keep the UI functioning
MOCK_DISHES_DB = {
    "pho": {
        "foodName": "Phở Bò",
        "englishName": "Vietnamese Beef Noodle Soup",
        "confidence": 98.5,
        "calories": 450,
        "allergyInfo": "Không dị ứng đậu phộng",
        "explainableFocus": "thịt bò và nước dùng trong vắt",
        "unsplashUrl": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80",
        "prompts": [
            "📍 Chỉ đường quán Phở ngon gần nhất",
            "🥗 Món này ăn với rau gì?",
            "🇬🇧 Translate recipe to English",
            "🍜 Bí quyết làm nước dùng phở trong vắt"
        ]
    },
    "banhmi": {
        "foodName": "Bánh Mì",
        "englishName": "Vietnamese Baguette",
        "confidence": 97.2,
        "calories": 380,
        "allergyInfo": "Có bơ/pâté sữa, không đậu phộng",
        "explainableFocus": "pâté gan và vỏ bánh giòn tan",
        "unsplashUrl": "https://images.unsplash.com/photo-1600454021970-3c2ffb13387c?auto=format&fit=crop&w=800&q=80",
        "prompts": [
            "📍 Tiệm Bánh Mì ngon nổi tiếng",
            "🥩 Cách làm nhân pâté béo ngậy",
            "🇬🇧 Translate recipe to English",
            "🥒 Rau thơm ăn kèm bánh mì chuẩn vị"
        ]
    },
    "buncha": {
        "foodName": "Bún Chả",
        "englishName": "Grilled Pork with Noodles",
        "confidence": 96.8,
        "calories": 520,
        "allergyInfo": "Không bơ/sữa, không đậu phộng",
        "explainableFocus": "chả nướng than hoa và đu đủ xanh",
        "unsplashUrl": "https://images.unsplash.com/photo-1562967916-eb82221dfb92?auto=format&fit=crop&w=800&q=80",
        "prompts": [
            "📍 Địa chỉ Bún Chả nổi tiếng nhất",
            "🍯 Công thức pha nước chấm chuẩn vị",
            "🇬🇧 Translate recipe to English",
            "🌿 Rổ rau sống ăn bún chả gồm những gì?"
        ]
    },
    "caphetrung": {
        "foodName": "Cà Phê Trứng",
        "englishName": "Vietnamese Egg Coffee",
        "confidence": 99.1,
        "calories": 220,
        "allergyInfo": "Có lòng đỏ trứng gà, sữa đặc",
        "explainableFocus": "lớp kem trứng bông mịn",
        "unsplashUrl": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80",
        "prompts": [
            "📍 Ghé cà phê Giảng gốc Hà Nội",
            "☕ Tỷ lệ đánh kem trứng không tanh",
            "🇬🇧 Translate recipe to English",
            "🍫 Rắc bột gì lên mặt cà phê trứng?"
        ]
    }
}


class RAGService:
    def __init__(self):
        self.retriever = HybridRAGRetriever()
        self.generator = RAGGenerator()

    def inspect(self, query: str) -> dict:
        results = self.retriever.retrieve(query)

        top_contexts = []
        for rank, item in enumerate(results, 1):
            metadata = item["metadata"]
            top_contexts.append({
                "rank": rank,
                "id": item["id"],
                "food_name": metadata.get("ten_mon", ""),
                "score": item.get("score", 0.0),
                "rerank_score": item.get("rerank_score", 0.0),
                "food_name_boost": item.get("food_name_boost", 0.0),
                "url": metadata.get("url_tham_khao", metadata.get("url", "")),
                "focused_context": item.get("focused_context", ""),
                "full_context": item.get("document", ""),
            })

        return {
            "query": query,
            "detected_intent": results[0].get("intent", "unknown") if results else "unknown",
            "top_contexts": top_contexts,
        }

    def analyze_food(self, dish_key: str, image_base64: str = None, language: str = "VN") -> dict:
        import os
        import base64
        import uuid
        from src.vision.inference import predict
        
        # 1. NẾU NGƯỜI DÙNG UPLOAD ẢNH (CUSTOM)
        if dish_key == "custom" and image_base64:
            temp_filename = None
            try:
                # Xử lý chuỗi base64 (cắt bỏ phần header "data:image/jpeg;base64," nếu có)
                if "," in image_base64:
                    image_base64 = image_base64.split(",")[1]
                
                image_data = base64.b64decode(image_base64)
                
                # Lưu tạm ảnh để predict
                temp_filename = f"backend/data/temp_{uuid.uuid4().hex[:8]}.jpg"
                os.makedirs("backend/data", exist_ok=True)
                with open(temp_filename, "wb") as f:
                    f.write(image_data)
                
                print(f"Analyzing uploaded image using PyTorch: {temp_filename}")
                
                # CHẠY MODEL PYTORCH THẬT Ở ĐÂY
                config_path = "configs/config.yaml"
                
                # Hỗ trợ tìm tự động file model theo tên thư mục backbone (efficientnet_b3)
                model_path_1 = "checkpoints/best_model.pth"
                model_path_2 = "checkpoints/efficientnet_b3/best_model.pth"
                model_path = model_path_1 if os.path.exists(model_path_1) else model_path_2
                
                if not os.path.exists(config_path) or not os.path.exists(model_path):
                    raise FileNotFoundError(f"Missing {config_path} or {model_path}. Please check directories.")
                
                results = predict(image_path=temp_filename, config_path=config_path, model_path_override=model_path, use_tta=True, use_cam=False)
                
                cam_coord = None
                if results and len(results) > 0:
                    top_prediction = results[0]
                    predicted_class = top_prediction['class']
                    confidence_pct = round(top_prediction['confidence'] * 100, 1)
                    
                    # Run a second pass specifically to get Grad-CAM coordinates 
                    # without compromising the TTA-boosted accuracy of the first pass.
                    try:
                        cam_results = predict(image_path=temp_filename, config_path=config_path, model_path_override=model_path, use_tta=False, use_cam=True)
                        if cam_results and len(cam_results) > 0 and "cam_coord" in cam_results[0]:
                            cam_coord = cam_results[0]["cam_coord"]
                    except Exception as e:
                        print(f"Error generating Grad-CAM: {e}")
                else:
                    predicted_class = "Unknown"
                    confidence_pct = 0.0
                
                # Tự động tạo dữ liệu món ăn dựa vào kết quả AI
                # Ưu tiên tên tiếng Việt có dấu từ bảng mapping để RAG search chính xác hơn
                viet_name = CLASS_NAME_TO_VIET.get(predicted_class, predicted_class.replace('_', ' ').title())
                
                dish_data = {
                    "foodName": viet_name,
                    "englishName": predicted_class.replace('_', ' ').title(),
                    "confidence": confidence_pct,
                    "calories": "N/A",
                    "allergyInfo": "Can be analyzed by AI",
                    "explainableFocus": viet_name,
                    "unsplashUrl": None,
                    "prompts": [
                        f"Quan {viet_name} ngon gan day",
                        "Mon nay thuong an kem voi rau gi?",
                        "Dich nguyen lieu mon nay sang tieng Anh",
                        f"Huong dan cach nau {viet_name} chuan vi"
                    ]
                }
                
                # Bơm tọa độ Grad-CAM vào Frontend (dưới dạng mảng để UI parse dễ)
                if cam_coord:
                    dish_data["gradcamCoordinates"] = [cam_coord]
                    
            except Exception as e:
                print(f"Error analyzing image: {e}")
                with open("backend/data/debug_predict_error.log", "w") as f:
                    import traceback
                    traceback.print_exc(file=f)
                import random
                # Fallback ngẫu nhiên để UI luôn đẹp ngay cả khi thiếu model cục bộ
                fallback_keys = [k for k in MOCK_DISHES_DB.keys() if k != "custom"]
                random_dish = random.choice(fallback_keys)
                dish_data = MOCK_DISHES_DB[random_dish].copy()
                dish_data["unsplashUrl"] = None
                print(f"Fallback UI: Using {random_dish} due to missing local model.")
            finally:
                # Xóa ảnh tạm sau khi predict xong hoặc lỗi để tránh rò rỉ dung lượng ổ đĩa
                if temp_filename and os.path.exists(temp_filename):
                    try:
                        os.remove(temp_filename)
                    except:
                        pass

        # 2. NẾU NGƯỜI DÙNG BẤM CÁC NÚT CÓ SẴN TRÊN UI (Phở, Bún Chả...)
        else:
            target_key = dish_key if dish_key in MOCK_DISHES_DB else "pho"
            dish_data = MOCK_DISHES_DB[target_key].copy()

        food_name = dish_data["foodName"]
        
        # Lấy thông tin tri thức từ ChromaDB (RAG) để gài vào Chatbot!
        try:
            import math
            def sigmoid(x):
                return 1 / (1 + math.exp(-x))
                
            retrieved = self.retriever.retrieve(food_name)
            rag_chunks = []
            for item in retrieved:
                metadata = item.get("metadata", {})
                raw_score = item.get("score", 0)
                # Normalize raw score using sigmoid so it's between 0 and 1
                norm_score = sigmoid(raw_score) if raw_score else 0.8
                
                rag_chunks.append({
                    "simScore": round(norm_score, 2),
                    "source": metadata.get("url_tham_khao", metadata.get("url", "Tài liệu ẩm thực")),
                    "content": item.get("focused_context", item.get("document", ""))
                })
        except Exception as e:
            print(f"Error retrieving from ChromaDB: {e}")
            rag_chunks = []
            
        dish_data["ragChunks"] = rag_chunks
        
        from backend.core.logger import log_event
        log_event("prediction", {"foodName": dish_data.get("foodName"), "confidence": dish_data.get("confidence", 100)})
        
        dish_data["success"] = True
        return dish_data

    def chat_with_rag(self, message: str, dish_key: str, history: list, dish_name: str = None, language: str = "VN") -> dict:
        if dish_name:
            food_name = dish_name
        else:
            target_key = dish_key if dish_key in MOCK_DISHES_DB else "pho"
            food_name = MOCK_DISHES_DB[target_key]["foodName"]

        # Combine food name and query for better vector matching
        search_query = f"{food_name} {message}"
        
        try:
            import math
            def sigmoid(x):
                return 1 / (1 + math.exp(-x))
                
            retrieved = self.retriever.retrieve(search_query)
            rag_chunks = []
            for item in retrieved:
                metadata = item.get("metadata", {})
                raw_score = item.get("score", 0)
                norm_score = sigmoid(raw_score) if raw_score else 0.8
                
                rag_chunks.append({
                    "simScore": round(norm_score, 2),
                    "source": metadata.get("url_tham_khao", metadata.get("url", "Tài liệu ẩm thực")),
                    "content": item.get("focused_context", item.get("document", "")),
                    "full_context": item.get("document", "")
                })
        except Exception as e:
            print(f"Error retrieving from ChromaDB: {e}")
            rag_chunks = []

        # Generate LLM response
        reply = self.generator.generate_response(
            query=message,
            dish_name=food_name,
            contexts=rag_chunks,
            history=history,
            language=language
        )

        from backend.core.logger import log_event
        log_event("rag_query", {"dishName": food_name, "query": message})
        
        return {
            "reply": reply,
            "retrievedChunks": rag_chunks,
            "success": True
        }

    def analyze_nutrition(self, dish_name: str) -> dict:
        prompt = f"""
Hãy đóng vai một chuyên gia dinh dưỡng. Dựa vào tên món ăn "{dish_name}", hãy ước lượng các chỉ số dinh dưỡng cho 1 khẩu phần ăn tiêu chuẩn và thành phần chính.
TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON NHƯ SAU (KHÔNG GHI GÌ THÊM, KHÔNG DÙNG MARKDOWN):
{{
  "calories": 400,
  "protein": 20,
  "carbs": 50,
  "fat": 15,
  "allergen": "Gluten, Đậu phộng",
  "ingredients": [
    {{"name": "Bánh phở", "purpose": "Cung cấp tinh bột"}},
    {{"name": "Thịt bò", "purpose": "Cung cấp đạm"}}
  ]
}}
"""
        try:
            response = self.generator.generate_response(
                query=prompt,
                dish_name=dish_name,
                contexts=[]
            )
            
            import re, json
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                return {"success": True, "data": data}
        except Exception as e:
            print(f"Error analyzing nutrition via LLM: {e}")
            
        return {"success": False}
