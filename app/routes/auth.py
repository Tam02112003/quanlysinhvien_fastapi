from fastapi import APIRouter, HTTPException
from app.schemas.auth_schema import UserRegister, UserLogin, UserOut
from app.crud import auth
from app.utils.token import create_access_token
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
async def register(user: UserRegister):
    row = await auth.register_user(user.username, user.email, user.password)
    if not row:
        raise HTTPException(status_code=400, detail="Email already registered")
    return dict(row)

@router.post("/login")
async def login(user: UserLogin):
    row = await auth.authenticate_user(user.email, user.password)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": row["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": dict(row)
    }