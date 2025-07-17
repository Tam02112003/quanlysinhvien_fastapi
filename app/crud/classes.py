from app.database import get_connection
from fastapi import HTTPException
import logging
import redis.asyncio as aioredis
import os
import json

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis = None

async def get_redis():
    global redis
    if redis is None:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return redis

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

async def create_classes_batch(classes_data):
    async with get_connection() as conn:
        async with conn.transaction():
            stmt = await conn.prepare("""
                INSERT INTO classes (name, grade, teacher_name)
                VALUES ($1, $2, $3) RETURNING id, name, grade, teacher_name
            """)
            return await stmt.executemany([(c.name, c.grade, c.teacher_name) for c in classes_data])

async def get_all_classes(limit: int = 50, offset: int = 0):
    redis = await get_redis()
    cache_key = f"classes:all:limit:{limit}:offset:{offset}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    async with get_connection() as conn:
        try:
            stmt = await conn.prepare("""
                SELECT id, name, grade, teacher_name
                FROM classes 
                ORDER BY id
                LIMIT $1 OFFSET $2
            """)
            rows = await stmt.fetch(limit, offset)
            result = [dict(r) for r in rows]
            await redis.set(cache_key, json.dumps(result), ex=300)  # cache 5 phút
            return result
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
            await conn.execute("DELETE FROM classes WHERE id = $1;", class_id)
            return True
        except Exception as e:
            logger.error(f"Delete class error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

async def get_classes_students_counts():
    redis = await get_redis()
    cache_key = "classes:stats"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
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
            result_dict = [dict(row) for row in result]
            await redis.set(cache_key, json.dumps(result_dict), ex=600)  # cache 10 phút
            return result_dict
        except Exception as e:
            logger.error(f"Get class counts error: {e}")
            raise HTTPException(status_code=500, detail="Database error")
