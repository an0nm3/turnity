import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from pydantic import BaseModel
from typing import Optional

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class CheckRequest(BaseModel):
    text: str
    title: Optional[str] = ""

class UserSession(BaseModel):
    access_token: str
    user_id: str
    email: str
