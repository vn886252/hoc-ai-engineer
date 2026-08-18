
from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

@app.get("/cong")
def cong_ab(a:int, b:int):
    return {"mesenger": f"a + b bằng,{a + b}" }

