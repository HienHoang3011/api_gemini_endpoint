# main.py
import os
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
load_dotenv()

# --- 1. Định nghĩa cấu trúc dữ liệu đầu vào bằng Pydantic ---
# Điều này giúp FastAPI tự động xác thực dữ liệu gửi lên.

class QAPair(BaseModel):
    question: str
    answer: str

class QASubmission(BaseModel):
    items: List[QAPair]

# --- 2. Khởi tạo ứng dụng FastAPI ---
app = FastAPI()
prompt = """
Chắc chắn rồi! Dưới đây là prompt được điều chỉnh lại theo đúng yêu cầu của bạn, tập trung vào cấu trúc đầu ra mong muốn và bước kêu gọi hành động cuối cùng.

Prompt này hướng dẫn AI thực hiện quá trình suy luận (chain-of-thought) một cách "ngầm" và chỉ hiển thị kết quả theo đúng định dạng bạn cần.

---

### Prompt Tối ưu cho Định dạng Đầu ra Cụ thể

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
# --- 3. Lấy API Key từ biến môi trường (an toàn hơn) ---
# Hãy chạy `export GEMINI_API_KEY="YOUR_API_KEY"` trong terminal trước khi khởi động server
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# --- 4. Tạo API Endpoint ---
@app.post("/analyze-answers/")
async def analyze_answers(submission: QASubmission):
    """
    Endpoint này nhận một danh sách các cặp Q&A,
    tạo prompt và gọi Gemini API để phân tích.
    """

    # --- 5. Xây dựng prompt từ dữ liệu nhận được ---
    # Đây là bước "tích hợp câu hỏi và câu trả lời vào prompt"
    prompt_lines = [prompt]
    
    for pair in submission.items:
        prompt_lines.append(f"\n- Câu hỏi: {pair.question}")
        prompt_lines.append(f"  Trả lời: {pair.answer}")

    final_prompt = "\n".join(prompt_lines)
    
    print("--- Prompt gửi đến Gemini ---")
    print(final_prompt)
    print("----------------------------")

    # --- 6. Gọi Gemini API bằng httpx ---
    # Sử dụng async client để không block server trong lúc chờ phản hồi
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                GEMINI_API_URL,
                json={
                    "contents": [{
                        "parts": [{"text": final_prompt}]
                    }]
                },
                timeout=30 # Đặt thời gian chờ để tránh treo
            )
            response.raise_for_status() # Báo lỗi nếu status code là 4xx hoặc 5xx

            gemini_data = response.json()
            analysis_result = gemini_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Không có nội dung trả về.")
            
            return {"analysis": analysis_result}

        except httpx.HTTPStatusError as e:
            # Xử lý lỗi từ API (ví dụ: key không hợp lệ)
            return {"error": f"Lỗi API: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            # Xử lý các lỗi khác (ví dụ: mạng)
            return {"error": "Đã xảy ra lỗi không xác định", "details": str(e)}