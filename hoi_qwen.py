import requests

def hoi_qwen_code(yeu_cau):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3.8:27b",
            "prompt": yeu_cau,
            "stream": False
        }
    )
    return response.json()["response"]


if __name__ == "__main__":
    prompt =  """Bạn là lập trình viên Python cho hệ thống chatbot bán áo/quần tập gym.

Bối cảnh: hãy kiểm tra xem code này đã đúng chưa? nếu sai thì sai chỗ nào?

Yêu cầu viết 2 phần:

1. Một dict tên "danh_muc_nhom", key là tên nhóm (ví dụ "nhom_1"), value là list các mã sản phẩm có trong ảnh đó.

2. Đoạn code tự động tạo dict "anh_theo_ma" bằng cách duyệt qua danh_muc_nhom, ánh xạ MỖI mã sản phẩm riêng lẻ sang đường dẫn file ảnh chứa nó (dạng static/products/ten_nhom.jpg)

3. Hàm gui_hinh_anh(ma_san_pham):
   - Tra trong anh_theo_ma
   - Dùng os.path.exists() kiểm tra file có tồn tại không
   - Nếu có, trả về link dạng https://chatbot-ao-thun.onrender.com/ + đường dẫn
   - Nếu không, trả về chuỗi "KHONG_TIM_THAY_ANH"

Chỉ trả về code Python, không giải thích dài dòng."""

    ket_qua = hoi_qwen_code(prompt)
    print(ket_qua)