from app.database import get_connection
from app.utils.security import hash_password, verify_password


async def register_user(name: str, email: str, password: str):
    conn = await get_connection()
    existing = await conn.fetchrow("SELECT * FROM users WHERE email=$1", email)
    if existing:
        await conn.close()
        return None  # Email đã tồn tại

    hashed = hash_password(password)
    row = await conn.fetchrow("""
        INSERT INTO users (username, email,  hashed_password)
        VALUES ($1, $2, $3)
        RETURNING id, username, email
    """, name, email, hashed)
    await conn.close()
    return row

from app.utils.security import verify_password  # dùng passlib để kiểm tra

async def authenticate_user(email: str, password: str):
    conn = await get_connection()
    user = await conn.fetchrow("SELECT * FROM users WHERE email=$1", email)
    await conn.close()

    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    # Trả lại thông tin user cần thiết
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }
