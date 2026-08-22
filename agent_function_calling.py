from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cong_hai_so(a, b):
    return a + b

def nhan_hai_so(a, b):
    return a* b

def kiem_tra_thoi_tiet(tp):
    return f"Thời tiết ở {tp}: 28°C, nắng"

tools = [
    {
        "type":"function",
        "function": {
            "name": "cong_hai_so",
            "description":"Cộng lại 2 số với nhau",
            "parameters": {
                "type": "object",
                "properties": {
                    "a":{"type":"number","description":"Số thứ nhất"},
                    "b":{"type":"number","description":"Số thứ hai"}
                },
                "required":["a","b"]
            }
        }        
    },
    {
           "type":"function",
            "function": {
                "name": "nhan_hai_so",
                "description":"Nhân lại 2 số với nhau",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a":{"type":"number","description":"Số thứ nhất"},
                        "b":{"type":"number","description":"Số thứ hai"}
                    },
                    "required":["a","b"]
            }
        }
    },
    {
            "type":"function",
            "function":{
                "name":"kiem_tra_thoi_tiet",
                "description": "Kiểm tra thời tiết tại thành phố bất kỳ",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "tp":{"type":"string","description":"Tên thành phố"},
                    },
                    "required":["tp"]
                }
            }
    }
]

mes1 ="Cho tôi biết 300 cộng 150 bằng bao nhiêu?"
mes2 ="Cho tôi biết 3 nhân 15 bằng bao nhiêu?"
mes3 ="cho tôi biết thời tiết Sóc Trăng hiện tại"
mes4 = "cho tôi biết 3 nhân 5 bằng mấy và saigon hiện tại thời tiết như thế nào?"

messages = [{"role":"user","content":mes4}]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools
)

reply = response.choices[0].message

if reply.tool_calls:
    messages.append(reply)

    for tool_call in reply.tool_calls:
        ten_ham = tool_call.function.name
        tham_so = json.loads(tool_call.function.arguments)

        print("AI muốn gọi hàm:",ten_ham,"với tham số:", tham_so)

        if ten_ham == "cong_hai_so":
            ket_qua = cong_hai_so(tham_so["a"],tham_so["b"])

        if ten_ham == "nhan_hai_so":
            ket_qua = nhan_hai_so(tham_so["a"],tham_so["b"])

        if ten_ham == "kiem_tra_thoi_tiet":
            ket_qua = kiem_tra_thoi_tiet(tham_so["tp"])

        messages.append({
            "role":"tool",
            "tool_call_id":tool_call.id,
            "content": str(ket_qua)
    })

    response_cuoi = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    print(response_cuoi.choices[0].message.content)
else:
    print(reply.content)


    #testing
    