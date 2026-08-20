# Bước 1: tìm đoạn liên quan nhất trong Chroma
ket_qua = collection.query(query_texts=["năng lượng tái tạo là gì?"], n_results=2)
ngu_canh = "\n".join(ket_qua["documents"][0])

# Bước 2: đưa ngữ cảnh tìm được vào prompt, gửi cho GPT trả lời
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Trả lời câu hỏi CHỈ dựa trên ngữ cảnh được cung cấp, không dùng kiến thức ngoài."},
        {"role": "user", "content": f"Ngữ cảnh:\n{ngu_canh}\n\nCâu hỏi: năng lượng tái tạo là gì?"}
    ]
)
print(response.choices[0].message.content)