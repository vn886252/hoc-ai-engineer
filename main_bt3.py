from openai import OpenAI
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

class Cauhoi(BaseModel):
    noi_dung: str

@app.post("/chatbot")
def tra_loi(cau_hoi:Cauhoi):
    response =client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"user","content":cau_hoi.noi_dung}
        ]
    )
    return {"cau_tra_loi":response.choices[0].message.content}