from app.database import get_connection
from fastapi import HTTPException
import logging
import asyncpg
import redis.asyncio as aioredis
import os
import json
from datetime import datetime, date

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis = None

async def get_redis():
    global redis
    if redis is None:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return redis

async def create_student(student_data):
    async with get_connection() as conn:
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

            # Trả về đầy đủ thông tin sinh viên vừa tạo
            student = await conn.fetchrow(
                """
                SELECT id, name, email, date_of_birth, class_id
                FROM students WHERE id = $1
                """,
                student_id
            )
            return dict(student) if student else None

        except asyncpg.UniqueViolationError as e:
            logger.error(f"Lỗi trùng lặp email: {e}")
            raise HTTPException(
                status_code=409,
                detail="Xung đột d�� liệu: Email đã tồn tại"
            )

async def get_all_students(page: int = 1, limit: int = 100):
    redis = await get_redis()
    cache_key = f"students:all:page:{page}:limit:{limit}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    offset = (page - 1) * limit
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT id, name, email, date_of_birth, class_id 
                FROM students ORDER BY id LIMIT $1 OFFSET $2
            """)
            students = await stmt.fetch(limit, offset)
            result = [dict(s) for s in students]
            # Convert date_of_birth to string for JSON serialization
            for s in result:
                if isinstance(s.get('date_of_birth'), (datetime, date)):
                    s['date_of_birth'] = s['date_of_birth'].isoformat()
            await redis.set(cache_key, json.dumps(result), ex=60)  # cache 60s
            return result
        except Exception as e:
            logger.error(f"Get all students error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def get_student_by_id(student_id):
    redis = await get_redis()
    cache_key = f"students:id:{student_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT id, name, email, date_of_birth, class_id 
                FROM students WHERE id = $1
            """)
            student = await stmt.fetchrow(student_id)
            result = dict(student) if student else None
            if result:
                await redis.set(cache_key, json.dumps(result), ex=60)
            return result
        except Exception as e:
            logger.error(f"Get student error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def update_student(student_id, data):
    redis = await get_redis()
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
            # Invalidate cache khi update
            await redis.delete(f"students:id:{student_id}")
            await redis.delete_pattern("students:all:*")
            return dict(updated) if updated else None
        except Exception as e:
            logger.error(f"Update student error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def delete_student(student_id):
    redis = await get_redis()
    async with get_connection() as conn:
        try:
            await conn.execute("DELETE FROM students WHERE id = $1", student_id)
            # Invalidate cache khi xóa
            await redis.delete(f"students:id:{student_id}")
            await redis.delete_pattern("students:all:*")
            return True
        except Exception as e:
            logger.error(f"Delete student error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

# Helper for Redis pattern deletion (aioredis 2.x workaround)
aioredis.Redis.delete_pattern = lambda self, pattern: self.eval(
    """
    local keys = redis.call('keys', ARGV[1])
    for i=1,#keys,5000 do
        redis.call('del', unpack(keys, i, math.min(i+4999, #keys)))
    end
    return keys
    """, 0, pattern)