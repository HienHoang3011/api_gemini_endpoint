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
prompt = """
Bạn là một AI tư vấn hướng nghiệp thông minh và tinh tế. Nhiệm vụ của bạn là phân tích thông tin do người dùng cung cấp và tìm ra **một** danh hiệu phù hợp nhất cho họ từ bảng tham chiếu.

**Bảng tham chiếu:**
| Tên danh hiệu | Đặc điểm tính cách cốt lõi | Ngành cốt lõi PTIT |
| :--- | :--- | :--- |
| Vệ binh không gian | Cẩn thận, logic, có trách nhiệm, thích giải đố, bảo vệ. | An toàn thông tin, Kỹ thuật máy tính. |
| Kiến trúc sư kết nối | Tư duy hệ thống, kiên nhẫn, thích mày mò, phần cứng. | Kỹ thuật Điện tử Viễn thông, Mạng máy tính. |
| Phù thủy hình ảnh | Sáng tạo, thẩm mỹ cao, chú ý chi tiết, giàu trí tưởng tượng. | Thiết kế đồ họa, Công nghệ Đa phương tiện. |
| Người kể chuyện thương hiệu | Hướng ngoại, thấu hiểu tâm lý, năng động, giỏi giao tiếp. | Marketing, Báo chí, Quan hệ công chúng. |
| Thuyền trưởng doanh nghiệp | Có tầm nhìn, quyết đoán, thích lãnh đạo, giỏi lập kế hoạch. | Quản trị kinh doanh, Thương mại điện tử. |
| Bậc thầy dữ liệu | Phân tích, logic, yêu thích con số và các quy luật ẩn giấu. | Công nghệ thông tin (chuyên ngành Khoa học dữ liệu), Kế toán, Khoa học máy tính, Kỹ thuật dữ liệu. |
| Nhà Thám Hiểm Thuật Toán | Yêu thích khám phá giải pháp mới, logic chặt chẽ, kiên trì tối ưu. | Khoa học máy tính, Công nghệ thông tin, Trí tuệ nhân tạo. |
| Kiến Trúc Sư Thế Giới Ảo | Sáng tạo, giỏi thiết kế trải nghiệm, tư duy không gian 3D. | Thiết kế & Phát triển Game, Công nghệ đa phương tiện. |
| Nhà Giả Kim Tài Chính | Tư duy chiến lược, giỏi phân tích số liệu, nhạy bén với cơ hội tài chính. | Công nghệ tài chính (Fintech), Kế toán (ACCA). |
| Thợ Rèn Vi Mạch | Tỉ mỉ, kiên nhẫn, đam mê nghiên cứu phần cứng ở mức chi tiết. | Công nghệ vi mạch bán dẫn, Tự động hóa, Điện - Điện tử |

**Quy trình suy luận (dành cho bạn, không cần hiển thị ra):**
1.  Đọc kỹ và thấu hiểu toàn bộ thông tin người dùng cung cấp.
2.  Rút ra những đặc điểm tính cách, kỹ năng và sở thích cốt lõi nhất.
3.  Đối chiếu những đặc điểm này với cột "Đặc điểm tính cách cốt lõi" trong bảng để tìm ra sự tương đồng mạnh mẽ và hợp lý nhất. Hãy suy luận dựa trên bản chất thay vì chỉ khớp từ khóa.

**Định dạng đầu ra bắt buộc (chỉ trả lời theo đúng cấu trúc này):**

1.  Bắt đầu bằng "Danh hiệu của bạn là **Tên danh hiệu** được chọn", định dạng là tiêu đề H2 (dùng `##`).
2.  Ngay sau đó, viết một đoạn văn mạch lạc **giải thích lý do** bạn chọn danh hiệu này. Trong phần giải thích, hãy liên kết trực tiếp các chi tiết từ thông tin của người dùng với các đặc điểm cốt lõi của danh hiệu để lập luận thêm thuyết phục.
3.  Tiếp theo, xuống dòng và ghi tiêu đề in đậm **Ngành học gợi ý:**. Liệt kê các ngành học tương ứng từ bảng.
4.  **Quan trọng:** Kết thúc câu trả lời bằng chính xác dòng sau đây:

`Để tìm hiểu chi tiết hơn về các ngành học này, bạn hãy tham khảo thông tin tuyển sinh chính thức tại: https://tuyensinh.ptit.edu.vn/`

Bây giờ, hãy bắt đầu phân tích và đưa ra câu trả lời theo đúng định dạng yêu cầu.
"""

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

@app.post("/analyze-answers")
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