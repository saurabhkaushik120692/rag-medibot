# app/models.py
from pydantic import BaseModel
from typing import List

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    role: str
    username: str

class ChatRequest(BaseModel):
    query: str
    role: str

class ChatResponse(BaseModel):
    answer: str
