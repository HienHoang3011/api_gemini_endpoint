# main.py
import os
import requests
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool # 1. Import run_in_threadpool
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
load_dotenv()

# --- (Phần Pydantic và prompt giữ nguyên) ---

class QAPair(BaseModel):
    question: str
    answer: str

class QASubmission(BaseModel):
    items: List[QAPair]

app = FastAPI()
prompt = """...""" # (Nội dung prompt của bạn)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# 2. Tách code blocking (requests) ra một hàm đồng bộ (sync) riêng
def call_gemini_sync(prompt_text: str):
    """Hàm này chứa code blocking và sẽ được chạy trong một thread riêng."""
    try:
        response = requests.post(
            GEMINI_API_URL,
            json={
                "contents": [{"parts": [{"text": prompt_text}]}]
            },
            timeout=120
        )
        response.raise_for_status()

        gemini_data = response.json()
        analysis_result = gemini_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Không có nội dung trả về.")
        return {"analysis": analysis_result}

    except requests.HTTPError as e:
        # Xử lý lỗi và trả về để endpoint chính có thể bắt được
        resp = e.response
        details = resp.text if resp is not None else str(e)
        status = resp.status_code if resp is not None else None
        # Trả về một dictionary lỗi thay vì raise exception trực tiếp ở đây
        # để dễ xử lý ở hàm async bên ngoài
        return {"error": f"Lỗi API: {status}", "details": details}
    except Exception as e:
        return {"error": "Đã xảy ra lỗi không xác định", "details": str(e)}

@app.post("/analyze-answers/")
async def analyze_answers(submission: QASubmission):
    """
    Endpoint này nhận Q&A, xây dựng prompt và gọi hàm đồng bộ
    trong một thread riêng để lấy kết quả phân tích.
    """
    prompt_lines = [prompt]
    for pair in submission.items:
        prompt_lines.append(f"\n- Câu hỏi: {pair.question}")
        prompt_lines.append(f"  Trả lời: {pair.answer}")

    final_prompt = "\n".join(prompt_lines)
    
    print("--- Prompt gửi đến Gemini ---")
    print(final_prompt)
    print("----------------------------")

    # 3. Gọi hàm đồng bộ bằng `run_in_threadpool`
    # FastAPI sẽ chạy `call_gemini_sync` trong một luồng khác
    # và `await` sẽ đợi cho đến khi nó hoàn thành.
    result = await run_in_threadpool(call_gemini_sync, final_prompt)
    
    return result