# app/infrastructure/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt
from passlib.context import CryptContext
from ..settings import settings

# No 72-byte limit; stable & dependency-light
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)

class AuthService:
    def __init__(self):
        self.users: Dict[str, str] = {}

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        return pwd_context.verify(password, hashed)

    def create_access_token(self, subject: str, expires_delta: Optional[timedelta] = None) -> str:
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        to_encode = {"sub": subject, "exp": expire}
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

    def decode_token(self, token: str):
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
