# app/adapters/http/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .schemas import SignupIn, TokenOut

router = APIRouter()

# Use Security so OpenAPI marks routes as requiring Bearer auth
bearer = HTTPBearer(auto_error=False)

def get_auth(request: Request):
    return request.app.container.auth  # type: ignore[attr-defined]

@router.post("/signup", response_model=TokenOut)
async def signup(body: SignupIn, auth = Depends(get_auth)):
    if body.email in auth.users:
        raise HTTPException(400, "user exists")
    auth.users[body.email] = auth.hash_password(body.password)
    token = auth.create_access_token(body.email)
    return TokenOut(access_token=token)

@router.post("/login", response_model=TokenOut)
async def login(body: SignupIn, auth = Depends(get_auth)):
    hashed = auth.users.get(body.email)
    if not hashed or not auth.verify_password(body.password, hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    token = auth.create_access_token(body.email)
    return TokenOut(access_token=token)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer),  # ← Security here
    auth = Depends(get_auth),
):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = auth.decode_token(credentials.credentials)
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
