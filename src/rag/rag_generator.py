import os
from typing import List, Dict

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class RAGGenerator:
    def __init__(self):
        # Ưu tiên 1: Chạy trực tiếp Local LLM nếu có cấu hình đường dẫn
        local_path_raw = os.environ.get("LOCAL_LLM_PATH")
        self.local_path = local_path_raw.strip() if local_path_raw else None
        
        # Ưu tiên 2: Lấy link ngrok từ Colab nếu có
        colab_url_raw = os.environ.get("COLAB_LLM_URL")
        self.colab_url = colab_url_raw.strip() if colab_url_raw else None
        
        if self.local_path and os.path.exists(self.local_path):
            self.mode = "local"
            self.is_active = True
            print(f"🚀 RAGGenerator: Đang tải Local LLM trực tiếp từ: {self.local_path}")
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                import torch
                self.tokenizer = AutoTokenizer.from_pretrained(self.local_path)
                
                device = "cuda" if torch.cuda.is_available() else "cpu"
                dtype = torch.float16 if device == "cuda" else torch.float32
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.local_path, 
                    device_map="auto", 
                    torch_dtype=dtype
                )
                print(f"✅ Tải Local LLM thành công (Device: {device})!")
            except ImportError:
                print("Lỗi: Bạn cần cài đặt thư viện 'transformers' và 'torch' để chạy Local LLM.")
                self.is_active = False
            except Exception as e:
                print(f"Lỗi khi tải Local LLM: {e}")
                self.is_active = False
                
        elif self.colab_url:
            self.mode = "colab"
            self.is_active = True
            print(f"RAGGenerator: Đang sử dụng Local LLM thông qua Ngrok: {self.colab_url}")
        else:
            self.mode = "gemini"
            # Configure Gemini API fallback
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key and api_key != "MY_GEMINI_API_KEY":
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-3.1-flash-lite")
                self.is_active = True
                print("☁️ RAGGenerator: Đang sử dụng Gemini API (gemini-3.1-flash-lite)")
            else:
                print("Warning: Không có COLAB_LLM_URL, LOCAL_LLM_PATH và GEMINI_API_KEY. Hệ thống sẽ trả về câu mặc định.")
                self.is_active = False

    def generate_response(
        self,
        query: str,
        dish_name: str,
        contexts: List[Dict],
        history: List[Dict] = None,
        language: str = "VN"
    ) -> str:
        if not self.is_active:
            return "Xin lỗi, hệ thống AI đang bảo trì. Vui lòng cấu hình GEMINI_API_KEY hoặc COLAB_LLM_URL trong file .env."

        from backend.core.global_settings import settings_store
        dynamic_mode = self.mode
        llm_engine_pref = settings_store.llm_engine.lower()
        
        if "gemini" in llm_engine_pref:
            dynamic_mode = "gemini"
        elif "colab" in llm_engine_pref:
            dynamic_mode = "colab"
        elif "local" in llm_engine_pref:
            dynamic_mode = "local"

        if dynamic_mode == "local" and self.mode != "local":
            print("Warning: Local LLM chosen but not loaded in .env. Falling back to Gemini.")
            dynamic_mode = "gemini"
        elif dynamic_mode == "colab" and not self.colab_url:
            print("Warning: Colab URL not found in .env. Falling back to Gemini.")
            dynamic_mode = "gemini"

        # Format context into a string
        context_str = ""
        for idx, ctx in enumerate(contexts):
            # Lấy trường document từ dict trả về bởi retriever
            content = ctx.get("full_context") or ctx.get("document") or ""
            source = ctx.get("url") or ctx.get("source") or f"Nguồn {idx+1}"
            context_str += f"[Tài liệu {idx+1}] (Nguồn: {source}):\n{content}\n\n"

        language_instruction_local = ""
        if language == "EN":
            language_instruction_local = "CRITICAL: You MUST translate your final answer to ENGLISH. Do not answer in Vietnamese."

        # --- MODE 1: Chạy trực tiếp bằng Local LLM ---
        if dynamic_mode == "local":
            try:
                import torch
                # Format chuẩn Alpaca Prompt từ file 05_llm_finetune.ipynb
                prompt = f"""Dưới đây là một câu hỏi về món ăn Việt Nam, kèm theo danh sách nguyên liệu. Hãy trả lời chính xác và ngắn gọn.
{language_instruction_local}

### Câu hỏi:
Dựa vào các thông tin sau, hãy trả lời về món {dish_name}:
{query}
Hãy trả lời ngắn gọn trong 1-2 câu. Không lặp lại đề bài.

### Nguyên liệu:
{context_str}

### Trả lời:
"""
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
                
                # Không tính gradient lúc inference
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=256,
                        temperature=0.3,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )
                
                new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
                response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
                
                # Cleanup marker
                if "###" in response:
                    response = response.split("###")[0]
                elif "<|im_end|>" in response:
                    response = response.split("<|im_end|>")[0]
                    
                return response.strip()
            except Exception as e:
                print(f"Error generating text with Local LLM: {e}")
                return "Có lỗi xảy ra khi chạy mô hình AI trực tiếp trên máy của bạn."
                
        # --- MODE 2: Chạy bằng LLM Fine-tuned qua Colab (Ngrok) ---
        elif dynamic_mode == "colab":
            try:
                import requests
                # Inject translation instruction into query for Colab compatibility if needed
                actual_query = f"{language_instruction_local}\nUser query: {query}" if language == "EN" else query
                payload = {
                    "query": actual_query,
                    "dish_name": dish_name,
                    "context_str": context_str
                }
                url = self.colab_url.rstrip("/") + "/chat"
                headers = {"ngrok-skip-browser-warning": "true"}
                response = requests.post(url, json=payload, headers=headers, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "").strip()
                    if reply:
                        return reply
                    return "Sorry, AI could not answer. Please try again." if language == "EN" else "Xin lỗi, AI chưa trả lời được. Vui lòng thử lại!"
                else:
                    return "Sorry, AI could not answer. Please try again." if language == "EN" else "Xin lỗi, AI chưa trả lời được. Vui lòng thử lại!"
            except Exception as e:
                print(f"Error connecting to Colab LLM: {e}")
                return "Sorry, AI could not answer. Please try again." if language == "EN" else "Xin lỗi, AI chưa trả lời được. Vui lòng thử lại!"
                
        # --- MODE 3: Chạy dự phòng bằng Gemini API ---
        # System Instruction for the AI
        lang_prompt = "Hay tra loi cau hoi cua nguoi dung bang Tieng Viet" if language == "VN" else "CRITICAL: YOU MUST TRANSLATE YOUR ENTIRE RESPONSE TO ENGLISH. DO NOT REPLY IN VIETNAMESE."
        system_instruction = (
            f"Ban la 'Viet Food AI Expert', mot chuyen gia am thuc Viet Nam thong thai va chuyen nghiep. "
            f"Ban dang tu van cho nguoi dung ve mon an: '{dish_name}'. "
            f"Duoi day la cac tai lieu am thuc truyen thong duoc trich xuat tu co so du lieu cua chung toi:\n"
            f"--- BAT DAU TAI LIEU ---\n"
            f"{context_str}"
            f"--- KET THUC TAI LIEU ---\n"
            f"{lang_prompt} mot cach hap dan, chuyen nghiep va lich su. "
            f"HAY ket hop cac thong tin tu tai lieu duoc trich xuat o tren neu no lien quan den cau hoi. "
            f"Dinh dang cau tra loi su dung Markdown (in dam, danh sach) cho dep mat. "
            f"QUAN TRONG: Hay LUON co gang su dung dinh dang Bang (Markdown Table) de trinh bay cac nguyen lieu chinh, thanh phan dinh duong hoac huong dan nau an mot cach truc quan neu co the."
        )

        # Prepare Gemini messages format
        formatted_history = []
        if history:
            for msg in history:
                role = "model" if msg.get("role") == "assistant" else "user"
                content = msg.get("content", "")
                if role == "user" and content == query:
                    continue # Skip the current query if it's already in history to avoid duplication
                formatted_history.append({"role": role, "parts": [content]})
        
        full_prompt = f"HUONG DAN HE THONG:\n{system_instruction}\n\nCAU HOI NGUOI DUNG:\n{query}"
        
        formatted_history.append({"role": "user", "parts": [full_prompt]})

        # Dùng gemini_model nếu được tạo từ fallback của Colab, hoặc self.model nếu là Gemini mode gốc
        active_model = gemini_model if "gemini_model" in dir() else self.model

        try:
            response = active_model.generate_content(formatted_history)
            return response.text
        except Exception as e:
            print(f"Error generating response with Gemini: {e}")
            return "Xin loi, da co loi xay ra trong qua trinh tao cau tra loi. Vui long kiem tra lai ket noi mang hoac cau hinh API Key."
