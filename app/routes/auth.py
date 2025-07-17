from fastapi import APIRouter, HTTPException, Request
from app.schemas.auth_schema import UserRegister, UserLogin, UserOut
from app.crud import auth
from app.utils.token import create_access_token
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from fastapi import status

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserOut)
async def register(user: UserRegister):
    row = await auth.register_user(user.username, user.email, user.password)
    if not row:
        raise HTTPException(status_code=400, detail="Email already registered")
    return dict(row)

@router.post("/login")
@limiter.limit("1000000/minute")  # Giới hạn 5 login attempts/phút
async def login(request: Request, user: UserLogin):
    row = await auth.authenticate_user(user.email, user.password)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": row["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": dict(row)
    }