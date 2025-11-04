from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SignupIn(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ItemIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class ItemOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
