from app.database import get_connection
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def create_class(data):
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                INSERT INTO classes (name, grade, teacher_name)
                VALUES ($1, $2, $3) 
                RETURNING id, name, grade, teacher_name;
            """)
            row = await stmt.fetchrow(data.name, data.grade, data.teacher_name)
            return dict(row)
        except Exception as e:
            logger.error(f"Create class error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def get_all_classes():
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT id, name, grade, teacher_name
                FROM classes 
                ORDER BY id;
            """)
            rows = await stmt.fetch()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Get all classes error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def get_class_by_id(class_id):
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT id, name, grade, teacher_name
                FROM classes
                WHERE id = $1;
            """)
            row = await stmt.fetchrow(class_id)
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Get class error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def update_class(class_id, data):
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                UPDATE classes
                SET name = $1,
                    grade = $2,
                    teacher_name = $3
                WHERE id = $4
                RETURNING id, name, grade, teacher_name;
            """)
            row = await stmt.fetchrow(data.name, data.grade, data.teacher_name, class_id)
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Update class error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def delete_class(class_id):
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                DELETE FROM classes WHERE id = $1;
            """)
            await stmt.execute(class_id)
            return True
        except Exception as e:
            logger.error(f"Delete class error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def get_classes_students_counts():
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT c.id, c.name, COUNT(s.id) AS student_count
                FROM classes c
                LEFT JOIN students s ON c.id = s.class_id
                GROUP BY c.id, c.name
                ORDER BY c.id;
            """)
            result = await stmt.fetch()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Get class counts error: {e}")
            raise HTTPException(status_code=500, detail="Database error")
