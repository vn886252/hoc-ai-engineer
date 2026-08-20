import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Tạo client lưu dữ liệu trên ổ đĩa (persistent — không mất khi tắt chương trình)
client = chromadb.PersistentClient(path="./chroma_data")

# Tạo hoặc lấy 1 "collection" — giống 1 bảng trong database thông thường
collection = client.get_or_create_collection(name="cau_hoc")

# Thêm dữ liệu — Chroma TỰ ĐỘNG tính embedding, không cần gọi tao_embedding() thủ công
collection.add(
    documents=[
        "ngọn lửa là năng lượng",
        "điện gió cũng là năng lượng",
        "ăn cơm với trái cây rất ngon",
        "ăn cơm với hải sản ngon hơn nữa",
        "tôi không có xem đá banh nên không biết tỉ số hiện tại thế nào"
    ],
    ids=["cau1", "cau2", "cau3", "cau4", "cau5"]   # mỗi document cần 1 id duy nhất
)

ket_qua = collection.query(
    query_texts=["nguồn năng lượng tái tạo là gì?"],
    n_results=2   # lấy 2 kết quả gần nhất
)

print(ket_qua)

print("Câu liên quan nhất:", ket_qua["documents"][0])
print("Khoảng cách:", ket_qua["distances"][0])

collection.add(
    documents=["mặt trời cũng là 1 nguồn năng lượng tái tạo",
               "cà phê việt nam được làm từ 70 robusta và 30 arabica",
               "người việt nam uống rất thích uống cà phê buổi sáng",
               "cà phê sữa người việt nam dùng sữa đặc",
               "không ai pha cà phê sữa việt nam bằng sữa tươi"],
    ids=["cau6","cau7","cau8","cau9","cau10"]
    
)
ket_qua2 = collection.query(
    query_texts=["có thể làm tràn đầy năng lượng bằng 1 tách cà phê việt nam buổi sáng"],
    n_results=3
)
ket_qua3 = collection.query(query_texts=["có thể lấy bã cà phê làm nhiệt điện không?"],n_results=3)

print(ket_qua2)

print("Câu liên quan nhất:", ket_qua2["documents"][0])
print("Khoảng cách:", ket_qua2["distances"][0])

print(ket_qua3)

print("Câu liên quan nhất:", ket_qua3["documents"][0])
print("Khoảng cách:", ket_qua3["distances"][0])

collection.delete(ids=["cau5"])
print(collection.get(ids=["cau5"]))


# Bước 1: tìm đoạn liên quan nhất trong Chroma
cau_hoi1 = "bã cà phê có thể làm năng lượng không?"
ket_qua = collection.query(query_texts=[cau_hoi1], n_results=3)
ngu_canh = "\n".join(ket_qua["documents"][0])

# Bước 2: đưa ngữ cảnh tìm được vào prompt, gửi cho GPT trả lời

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Trả lời câu hỏi CHỈ dựa trên ngữ cảnh được cung cấp, không dùng kiến thức ngoài."},
        {"role": "user", "content": f"Ngữ cảnh:\n{ngu_canh}\n\nCâu hỏi: {cau_hoi1}"}
    ]
)
print(response.choices[0].message.content)

# Bước 1: tìm đoạn liên quan nhất trong Chroma
cau_hoi2 = "có nên uống cà phê buổi sáng?"
ket_qua = collection.query(query_texts=[cau_hoi2], n_results=3)
ngu_canh = "\n".join(ket_qua["documents"][0])

# Bước 2: đưa ngữ cảnh tìm được vào prompt, gửi cho GPT trả lời

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Trả lời câu hỏi CHỈ dựa trên ngữ cảnh được cung cấp, không dùng kiến thức ngoài."},
        {"role": "user", "content": f"Ngữ cảnh:\n{ngu_canh}\n\nCâu hỏi: {cau_hoi2}"}
    ]
)
print(response.choices[0].message.content)