from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[

        {"role": "user", "content": "Trích xuất thông tin từ câu sau thành JSON với các trường ten,tuoi,nghe_nghiep: 'Tôi tên Khuê, năm nay vừa tròn 35 tuổi, tôi hiện tại là một AI engineering cho tập đoàn fitman'"}
    ],
    response_format={"type":"json_object"}
)

print(response.choices[0].message.content)
