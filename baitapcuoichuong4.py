from fastapi import FastAPI
from chromadb.utils import embedding_functions
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import chromadb
import json
import os

load_dotenv()
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="tai_lieu_congty",embedding_function=openai_ef )

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if collection.count() == 0:

    collection.add(
        documents=["Giá 1 chiếc áo là 170.000đ phí ship 30.000đ",
                "2 áo là 300.000đ freeship, combo 3 áo là 400.000đ freeship",
                "Khách hàng được kiếm tra hàng trước khi nhận, hàng kém chất lượng hoặc không giống hình cứ hoàn hàng",
                "size cho áo là từ 55 ký đến 105 ký được phân đều từ size S M L XL, ví dụ: khách hàng 60 ký cao 1m65 thì mặc size S",
                "size S từ 55kg tới 63kg, size M từ 64kg tới 72kg, size L từ 73kg tới 84kg, size XL là số còn lại",
                "lưu ý kỹ chiều cao của khách để chọn size tốt nhất ví dụ: khách cao 1m75 và nặng 80kg hãy chọn size XL, đối với khách nặng 75kg nhưng cao chỉ 1m60 thì cũng chọn size XL",
                "quần chỉ có 3 size M L XL phân bổ đều từ 55 ký đến 100 ký",
                "khách mua số lượng nhiều hơn thì báo với nhân viên tư vấn để chat trực tiếp",
                "quần và áo đồng giá với nhau có thể tính cùng combo",
                "mẫu áo và quần có hơn 50 mẫu khác nhau",
                "áo và quần chủ yếu khách hàng là dân tập gym, và có sở thích là cbum, tập thể hình, chú trọng cơ thể khỏe mạnh"
        ],
        ids=["cau1","cau2","cau3","cau4","cau5","cau6","cau7","cau8","cau9","cau10","cau11"]
    )
# (thêm dữ liệu vào collection nếu chưa có — chỉ cần chạy 1 lần)

def tra_cuu_thoi_tiet(thanh_pho):
    return f"Thời tiết ở {thanh_pho}: 28°C, nắng"

def tinh_toan(bieu_thuc):
    try:
        return eval(bieu_thuc)  # CHỈ dùng cho mục đích học tập
    except Exception:
        return "Không thể tính biểu thức này vui lòng thử lại biểu thức khác"
    
def tinh_size(can_nang, chieu_cao):
        if 55 <= can_nang <= 63:
            size = "S"
        elif 64 <= can_nang <= 72:
            size = "M"
        elif 73 <= can_nang <= 84:
            size = "L"
        else:
            size = "XL"
    
        thu_tu_size = ["S", "M", "L", "XL"]
        if chieu_cao < 1.65 and size != "XL":
            vi_tri = thu_tu_size.index(size)
            size = thu_tu_size[vi_tri + 1]

        return size

    

tools = [ 
    {
        "type":"function",
        "function":{
            "name":"tra_cuu_thoi_tiet",
            "description":"Tra cứu thời tiết tại thành phố bạn muốn",
            "parameters":{
                "type":"object",
                "properties":{
                    "thanh_pho":{"type":"string", "description":"tên thành phố"}
                },
            "required":["thanh_pho"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"tinh_toan",
            "description":"tính toán biểu thức nhập vào",
            "parameters":{
                "type":"object",
                "properties":{
                    "bieu_thuc":{"type":"string", "description":"nhập vào biểu thức cần tính"}
                },
            "required":["bieu_thuc"]
            }
        }
    }, 
    {
            "type":"function",
            "function":{
                "name":"tinh_size",
                "description":"tính size cho khách",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "can_nang":{"type":"number", "description":"nhập vào cân nặng"},
                        "chieu_cao":{"type":"number","description":"nhập vào chiều cao"}
                    },
                "required":["can_nang","chieu_cao"]
            }
        }
    }
    

 ]  # định nghĩa 2 tool theo đúng JSON Schema đã học

app = FastAPI()

class CauHoi(BaseModel):
    noi_dung: str
@app.post("/chatbot")
def chatbot(cau_hoi: CauHoi):
    # Bước 1: RAG
    ket_qua_rag = collection.query(query_texts=[cau_hoi.noi_dung], n_results=5)
    print("NGỮ CẢNH LẤY ĐƯỢC:", ket_qua_rag["documents"][0]) 
    ngu_canh = "\n".join(ket_qua_rag["documents"][0])

    messages = [
        {"role": "system", "content": "Trả lời dựa trên ngữ cảnh cung cấp. Nếu ngữ cảnh có đủ thông tin giá, hãy tự tính toán cụ thể, không hỏi lại người dùng thông tin đã có sẵn trong ngữ cảnh, trả lời ngắn gọn không dài dòng."},
        {"role": "user", "content": f"Ngữ cảnh:\n{ngu_canh}\n\nCâu hỏi: {cau_hoi.noi_dung}"}
    ]

    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
    reply = response.choices[0].message

    if reply.tool_calls:
        messages.append(reply)
        for tool_call in reply.tool_calls:
            ten_ham = tool_call.function.name
            tham_so = json.loads(tool_call.function.arguments)

            if ten_ham == "tra_cuu_thoi_tiet":
                ket_qua = tra_cuu_thoi_tiet(tham_so["thanh_pho"])

            elif ten_ham =="tinh_toan":
                ket_qua = tinh_toan(tham_so["bieu_thuc"])

            elif ten_ham == "tinh_size":
                
                ket_qua = tinh_size(tham_so["can_nang"], tham_so["chieu_cao"])
                print("TOOL tinh_size TRẢ VỀ:", ket_qua)
            # ... xử lý từng tool_call, append kết quả

            messages.append({
                        "role":"tool",
                        "tool_call_id":tool_call.id,
                        "content": str(ket_qua)
            })
        response_cuoi = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return {"cau_tra_loi": response_cuoi.choices[0].message.content}
    else:
        return {"cau_tra_loi": reply.content}