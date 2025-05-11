from app.database import get_connection
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def find_student_with_class_by_name(name: str, limit: int = 50, offset: int = 0):
    async with get_connection() as conn:
        try:
            # Sử dụng toán tử similarity cho tìm kiếm tiếng Việt tốt hơn
            stmt = await conn.prepare("""
                SELECT s.id, s.name, s.email, s.date_of_birth, c.name AS class_name
                FROM students s
                JOIN classes c ON s.class_id = c.id
                WHERE s.name % $1  -- Sử dụng toán tử similarity
                ORDER BY similarity(s.name, $1) DESC, s.name
                LIMIT $2 OFFSET $3
            """)
            result = await stmt.fetch(name, limit, offset)
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm: {e}")
            raise HTTPException(status_code=500, detail="Lỗi database")