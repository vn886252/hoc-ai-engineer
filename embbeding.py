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

vec1 = tao_embedding("ngọn lửa là năng lượng")
vec2 = tao_embedding("điện gió cũng là năng lượng")
vec3 = tao_embedding("ăn cơm với trái cây rất ngon")
vec4 = tao_embedding("ăn cơm với hải sản ngon hơn nữa")
vec5 = tao_embedding("tôi không có xem đá banh nên không biết tỉ số hiện tại thế nào")

print("vec1 vs vec2:",cosine_similarity(vec1, vec2))
print("vec3 vs vec4:",cosine_similarity(vec3, vec4))
print("vec5 vs vec2:",cosine_similarity(vec5, vec2))
print("vec5 vs vec4:",cosine_similarity(vec5, vec4))
print("vec1 vs vec3:",cosine_similarity(vec1, vec3))
print("vec2 vs vec4:",cosine_similarity(vec2, vec4))
                   