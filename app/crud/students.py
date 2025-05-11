from app.database import get_connection
from fastapi import HTTPException
import logging
import asyncpg
logger = logging.getLogger(__name__)


async def create_student(student_data):
    conn = await asyncpg.connect(...)
    try:
        # Kiểm tra trước khi insert
        exists = await conn.fetchval(
            "SELECT 1 FROM students WHERE email = $1 LIMIT 1",
            student_data.email
        )

        if exists:
            raise HTTPException(
                status_code=400,
                detail="Email đã tồn tại trong hệ thống"
            )

        # Sử dụng UPSERT pattern
        student_id = await conn.fetchval(
            """INSERT INTO students(name, email, date_of_birth, class_id)
            VALUES($1, $2, $3, $4)
            ON CONFLICT (email) DO UPDATE
            SET name = EXCLUDED.name,
                date_of_birth = EXCLUDED.date_of_birth,
                class_id = EXCLUDED.class_id
            RETURNING id""",
            student_data.name,
            student_data.email,
            student_data.date_of_birth,
            student_data.class_id
        )

        return student_id

    except asyncpg.UniqueViolationError as e:
        logger.error(f"Lỗi trùng lặp email: {e}")
        raise HTTPException(
            status_code=409,
            detail="Xung đột dữ liệu: Email đã tồn tại"
        )
    finally:
        await conn.close()

async def get_all_students():
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT id, name, email, date_of_birth, class_id 
                FROM students
            """)
            students = await stmt.fetch()
            return [dict(s) for s in students]
        except Exception as e:
            logger.error(f"Get all students error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def get_student_by_id(student_id):
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT id, name, email, date_of_birth, class_id 
                FROM students WHERE id = $1
            """)
            student = await stmt.fetchrow(student_id)
            return dict(student) if student else None
        except Exception as e:
            logger.error(f"Get student error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def update_student(student_id, data):
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                UPDATE students 
                SET name=$1, email=$2, date_of_birth=$3, class_id=$4
                WHERE id=$5 
                RETURNING id, name, email, date_of_birth, class_id;
            """)
            updated = await stmt.fetchrow(
                data.name, data.email, data.date_of_birth, data.class_id, student_id
            )
            return dict(updated) if updated else None
        except Exception as e:
            logger.error(f"Update student error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def delete_student(student_id):
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                DELETE FROM students WHERE id = $1
            """)
            await stmt.execute(student_id)
            return True
        except Exception as e:
            logger.error(f"Delete student error: {e}")
            raise HTTPException(status_code=500, detail="Database error")