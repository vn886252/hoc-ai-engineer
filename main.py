from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/chao")
def chao_ten(ten: str):
    return {"message": f"Xin chào, {ten}, đang học AI Engineer!"}