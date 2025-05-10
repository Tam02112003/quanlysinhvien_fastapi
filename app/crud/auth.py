from app.database import get_connection
from app.utils.security import hash_password, verify_password
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def register_user(name: str, email: str, password: str):
    async with get_connection() as conn:
        try:
            existing = await conn.fetchrow("SELECT 1 FROM users WHERE email=$1", email)
            if existing:
                logger.warning(f"Email already exists: {email}")
                return None

            hashed = hash_password(password)
            stmt = await conn.prepare("""
                INSERT INTO users (username, email, hashed_password)
                VALUES ($1, $2, $3)
                RETURNING id, username, email
            """)
            row = await stmt.fetchrow(name, email, hashed)
            return dict(row)
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def authenticate_user(email: str, password: str):
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT id, username, email, hashed_password 
                FROM users WHERE email=$1
            """)
            user = await stmt.fetchrow(email)

            if not user:
                logger.warning(f"User not found: {email}")
                return None

            if not verify_password(password, user["hashed_password"]):
                logger.warning(f"Invalid password for: {email}")
                return None

            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=500, detail="Database error")
