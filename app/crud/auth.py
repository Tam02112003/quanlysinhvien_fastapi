from app.database import get_connection
from app.utils.security import hash_password

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

async def authenticate_user(email: str, password: str):
    conn = await get_connection()
    hashed = hash_password(password)
    row = await conn.fetchrow("""
        SELECT id, username, email FROM users WHERE email=$1 AND  hashed_password=$2
    """, email, hashed)
    await conn.close()
    return row
