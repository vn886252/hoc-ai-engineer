import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def tao_embedding(text):
    response = client.embeddings.create(
        model = "text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    return np.dot(a, b)/ (np.linalg.norm(a) * np.linalg.norm(b))

def tim_cau_giong_nhat(cau_hoi, danh_sach_cau):
    vec_cau_hoi = tao_embedding(cau_hoi)
    diem_cao_nhat = -1
    cau_giong_nhat = None
    for cau in danh_sach_cau:
        vec_cau = tao_embedding(cau)
        diem = cosine_similarity(vec_cau_hoi, vec_cau)
        if diem > diem_cao_nhat:
            diem_cao_nhat = diem
            cau_giong_nhat = cau
    return cau_giong_nhat, diem_cao_nhat

danh_sach =[
     "ngọn lửa là năng lượng",
    "điện gió cũng là năng lượng",
    "ăn cơm với trái cây rất ngon",
    "ăn cơm với hải sản ngon hơn nữa",
    "tôi không có xem đá banh nên không biết tỉ số hiện tại thế nào"
]

ket_qua, diem = tim_cau_giong_nhat("nguồn năng lượng tái tạo là gì?", danh_sach)
print("câu giống nhất:",ket_qua)
print("điểm", diem)


                   