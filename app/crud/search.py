from app.database import get_connection
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def find_student_with_class_by_name(name: str):
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT s.id, s.name, s.email, s.date_of_birth, c.name AS class_name
                FROM students s
                JOIN classes c ON s.class_id = c.id
                WHERE s.name ILIKE $1
            """)
            result = await stmt.fetch(f"%{name}%")
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise HTTPException(status_code=500, detail="Database error")