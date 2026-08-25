from fastapi import FastAPI, Request, Query
from chromadb.utils import embedding_functions
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import chromadb 
import json
import os
import requests

load_dotenv()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="tai_lieu_congty", embedding_function=openai_ef)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if collection.count() == 0:
    collection.add(
        documents=[
            "Giá 1 chiếc áo là 170.000đ phí ship 30.000đ",
            "2 áo là 300.000đ freeship",
            "combo 3 áo là 400.000đ freeship",
            "Khách hàng được kiểm tra hàng trước khi nhận, hàng kém chất lượng hoặc không giống hình cứ hoàn hàng",
            "size cho áo là từ 55 ký đến 105 ký được phân đều từ size S M L XL, ví dụ: khách hàng 60 ký cao 1m65 thì mặc size S",
            "size S từ 55kg tới 63kg, size M từ 64kg tới 72kg, size L từ 73kg tới 84kg, size XL là số còn lại",
            "lưu ý kỹ chiều cao của khách để chọn size tốt nhất ví dụ: khách cao 1m75 và nặng 80kg hãy chọn size XL, đối với khách nặng 75kg nhưng cao chỉ 1m60 thì cũng chọn size XL",
            "quần chỉ có 3 size M L XL phân bổ đều từ 55 ký đến 100 ký",
            "khách mua số lượng nhiều hơn thì báo với nhân viên tư vấn để chat trực tiếp",
            "quần và áo đồng giá với nhau có thể tính cùng combo",
            "mẫu áo và quần có hơn 50 mẫu khác nhau",
            "áo và quần chủ yếu khách hàng là dân tập gym, và có sở thích là cbum, tập thể hình, chú trọng cơ thể khỏe mạnh"
        ],
        ids=["cau1","cau2","cau3","cau4","cau5","cau6","cau7","cau8","cau9","cau10","cau11","cau12"]
    )

def tra_cuu_thoi_tiet(thanh_pho):
    return f"Thời tiết ở {thanh_pho}: 28°C, nắng"

def tinh_toan(bieu_thuc):
    try:
        return eval(bieu_thuc)
    except Exception:
        return "Không thể tính biểu thức này vui lòng thử lại biểu thức khác"

def tinh_size(can_nang, chieu_cao):
    if can_nang < 62:
        size = "S"
    elif can_nang <= 75:
        size = "M"
    elif can_nang <= 84:
        size = "L"
    else:
        size = "XL"
    thu_tu_size = ["S", "M", "L", "XL"]
    if chieu_cao < 1.65 and size != "XL":
        vi_tri = thu_tu_size.index(size)
        size = thu_tu_size[vi_tri + 1]
    return size

def tinh_gia(so_luong):
    if so_luong == 1:
        tong = 150000 + 30000
        return f"1 món giá 150.000đ + phí ship 30.000đ = {tong:,}đ"
    elif so_luong == 2:
        return "2 món giá 300.000đ (freeship)"
    elif so_luong == 3:
        return "3 món giá 400.000đ (freeship)"
    else:
        so_mon_them = so_luong - 3
        tong = 400000 + so_mon_them * 130000
        return f"{so_luong} món giá {tong:,}đ (freeship) — gồm combo 3 món 400.000đ + {so_mon_them} món thêm x 130.000đ"

def gui_thong_bao_telegram(noi_dung):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": noi_dung}
    response = requests.post(url, data=payload)
    return response.json()

def bao_khong_hieu(cau_hoi_goc):
    gui_thong_bao_telegram(f"Chatbot không hiểu câu hỏi của khách: {cau_hoi_goc}")
    return "Mình đã chuyển câu hỏi này cho nhân viên hỗ trợ, sẽ có người liên hệ lại sớm nhé!"

def gui_tin_nhan_facebook(sender_id, noi_dung_text, link_anh = None):
    page_token = os.getenv("FACEBOOK_PAGE_TOKEN")
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={page_token}"
    payload = {"recipient": {"id": sender_id}, "message": {"text": noi_dung}}
    requests.post(url, json=payload_text)
    if link_anh:
            payload_anh ={
                "recipient":{"id":sender_id},
                "message":{
                    "attachment":{
                        "type":"image",
                        "payload":{"url":link_anh,"is_reusable": True}
                    }
                }
            }
            requests.post(url, json=payload_anh)
    response = requests.post(url, json=payload)
    return response.json()

   

danh_muc_nhom = {
    "nhom_1": ["1", "5", "4", "6","15","20","17","16","19"],
    "nhom_2": ["9", "10", "11","12","3","8","14","2","7"],
    "nhom_3": ["Q1", "Q2", "Q3", "Q4"],
    "nhom_4": ["21", "22", "23", "24", "W1","W2","28","29","W7"],
    "nhom_5": ["34", "36", "35", "39", "31","30","32","Q6","Q7"],
    "nhom_6": ["43", "44", "45", "46", "47"],
    "bang_size":["bang size","size","bảng size"]
}
anh_theo_ma = {}
for ten_nhom, danh_sach_ma in danh_muc_nhom.items():
    duong_dan = f"static/products/{ten_nhom}.jpg"
    for ma in danh_sach_ma:
        anh_theo_ma[ma] = duong_dan

def gui_hinh_anh(ma_san_pham):
    if ma_san_pham not in anh_theo_ma:
        return "KHONG_TIM_THAY_ANH"
    duong_dan_tuong_doi = anh_theo_ma[ma_san_pham]
    duong_dan_day_du = os.path.join(BASE_DIR, duong_dan_tuong_doi)
    print("BASE_DIR:", BASE_DIR, flush = True)
    print("DUONG DAN DAY DU:", duong_dan_day_du, flush=True)
    print("TON TAI KHONG:", os.path.exists(duong_dan_day_du), flush=True)
    if os.path.exists(duong_dan_day_du):
        return f"https://chatbot-ao-thun.onrender.com/{duong_dan_tuong_doi}"
    return "KHONG_TIM_THAY_ANH"

tools = [
    {
        "type": "function",
        "function": {
            "name": "tra_cuu_thoi_tiet",
            "description": "Tra cứu thời tiết tại thành phố bạn muốn",
            "parameters": {
                "type": "object",
                "properties": {"thanh_pho": {"type": "string", "description": "tên thành phố"}},
                "required": ["thanh_pho"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tinh_toan",
            "description": "tính toán biểu thức nhập vào",
            "parameters": {
                "type": "object",
                "properties": {"bieu_thuc": {"type": "string", "description": "nhập vào biểu thức cần tính"}},
                "required": ["bieu_thuc"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tinh_size",
            "description": "tính size cho khách",
            "parameters": {
                "type": "object",
                "properties": {
                    "can_nang": {"type": "number", "description": "cân nặng đơn vị kg"},
                    "chieu_cao": {"type": "number", "description": "chiều cao đơn vị mét"}
                },
                "required": ["can_nang", "chieu_cao"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tinh_gia",
            "description": "Tính tổng giá tiền dựa trên TỔNG số lượng áo + quần khách muốn mua. LUÔN dùng tool này để tính giá, KHÔNG được tự cộng/suy luận giá bằng lời văn.",
            "parameters": {
                "type": "object",
                "properties": {"so_luong": {"type": "number", "description": "Tổng số lượng áo + quần khách muốn mua"}},
                "required": ["so_luong"]
            }
        }
    },
    {
            "type": "function",
            "function": {
                "name": "gui_hinh_anh",
                "description": "Gửi hình ảnh sản phẩm cho khách xem. Mỗi mẫu áo/quần có mã số riêng (ví dụ 43, Q6, W1). Nếu khách hỏi xem bảng size, dùng mã 'bang size'. Nếu khách không nói rõ mã, hỏi lại khách muốn xem mẫu số mấy.",
                "parameters": {
                    "type": "object",
                    "properties": {"ma_san_pham": {"type": "string", "description": "Mã sản phẩm khách muốn xem, ví dụ: 43, Q6, W1, hoặc 'bang size' nếu khách hỏi bảng size"}},
                    "required": ["ma_san_pham"]
            }
        }
    }
]

SYSTEM_PROMPT =  """Bạn là trợ lý bán hàng cho shop quần áo tập gym.

PHẠM VI ĐƯỢC PHÉP trả lời: giá, size, chất liệu, chính sách đổi trả của ÁO và QUẦN — dựa ĐÚNG trên thông tin có trong ngữ cảnh.

QUY TẮC BẮT BUỘC VỀ HÌNH ẢNH: Khi khách muốn xem hình ảnh/mẫu sản phẩm (dù chỉ nói "xem mẫu X", "cho xem áo X"), bạn TUYỆT ĐỐI KHÔNG được tự trả lời bằng lời văn kiểu "không tìm thấy" hay "tôi không có ảnh". Bạn PHẢI LUÔN gọi tool gui_hinh_anh với đúng mã khách nhắc tới trước, để hàm đó tự kiểm tra và quyết định. Không được tự đoán trước kết quả.

QUY TẮC NGHIÊM NGẶT: Với BẤT KỲ câu hỏi nào về chủ đề KHÔNG liên quan áo/quần của shop, bạn TUYỆT ĐỐI KHÔNG được tự suy luận hay phỏng đoán câu trả lời."""

def xu_ly_chatbot(noi_dung_cau_hoi):
    link_anh = None

    tu_khoa_xem_anh = ["xem", "hình", "mẫu", "ảnh", "bảng size"]
    co_the_hoi_anh = any(tu in noi_dung_cau_hoi.lower() for tu in tu_khoa_xem_anh)

    ket_qua_rag = collection.query(query_texts=[noi_dung_cau_hoi], n_results=5)
    ngu_canh = "\n".join(ket_qua_rag["documents"][0])
    khoang_cach_gan_nhat = ket_qua_rag["distances"][0][0]

    NGUONG_LIEN_QUAN = 0.48
    if khoang_cach_gan_nhat > NGUONG_LIEN_QUAN and not co_the_hoi_anh:
        return bao_khong_hieu(noi_dung_cau_hoi)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Ngữ cảnh:\n{ngu_canh}\n\nCâu hỏi: {noi_dung_cau_hoi}"}
    ]

    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
    reply = response.choices[0].message

    print("CO GOI TOOL KHONG:", reply.tool_calls, flush=True)

    if reply.tool_calls:
        messages.append(reply)
        for tool_call in reply.tool_calls:
            ten_ham = tool_call.function.name
            tham_so = json.loads(tool_call.function.arguments)
            if ten_ham == "tra_cuu_thoi_tiet":
                ket_qua = tra_cuu_thoi_tiet(tham_so["thanh_pho"])
            elif ten_ham == "tinh_toan":
                ket_qua = tinh_toan(tham_so["bieu_thuc"])
            elif ten_ham == "tinh_size":
                ket_qua = tinh_size(tham_so["can_nang"], tham_so["chieu_cao"])
            elif ten_ham == "tinh_gia":
                ket_qua = tinh_gia(tham_so["so_luong"])
            elif ten_ham == "gui_hinh_anh":
                ket_qua = gui_hinh_anh(tham_so["ma_san_pham"])
                if ket_qua != "KHONG_TIM_THAY_ANH":
                    link_anh = ket_qua
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(ket_qua)})
        response_cuoi = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return response_cuoi.choices[0].message.content
    else:
        return reply.content

class CauHoi(BaseModel):
    noi_dung: str

VERIFY_TOKEN = "1234567"



@app.post("/chatbot")
def chatbot(cau_hoi: CauHoi):
    return {"cau_tra_loi": xu_ly_chatbot(cau_hoi.noi_dung)}

@app.get("/webhook")
def xac_minh_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)
    return PlainTextResponse(content="Xac minh that bai", status_code=403)

@app.post("/webhook")
async def nhan_tin_nhan(request: Request):
    data = await request.json()
    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]
            if "message" in event and "text" in event["message"]:
                noi_dung_khach = event["message"]["text"]
                cau_tra_loi, link_anh = xu_ly_chatbot(noi_dung_khach)
                gui_tin_nhan_facebook(sender_id, cau_tra_loi, link_anh)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)