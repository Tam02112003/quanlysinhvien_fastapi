import os
import time
import asyncpg
import asyncio
import json
from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def setup_connection(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )
    await conn.execute("SET TIME ZONE 'UTC'")

POOL_CONFIG = {
    "min_size": 20,      # Giảm từ 100
    "max_size": 1600,     # Giảm mạnh từ 1600
    "max_inactive_connection_lifetime": 300,
    "timeout": 30,
    "command_timeout": 30,
    "setup": setup_connection

}

class MonitoredConnection:
    def __init__(self, pool: 'MonitoredPool', conn: asyncpg.Connection):
        self._pool = pool
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._pool.release(self._conn)


class MonitoredPool:
    def __init__(self, pool: asyncpg.pool.Pool):
        self._pool = pool
        self._acquired_total = 0
        self._current_acquired = 0
        self._lock = asyncio.Lock()
        self._last_adjustment = time.time()

    async def acquire(self) -> MonitoredConnection:
        conn = await self._pool.acquire()
        async with self._lock:
            self._current_acquired += 1
            self._acquired_total += 1
        return MonitoredConnection(self, conn)

    async def release(self, conn: asyncpg.Connection):
        """Giải phóng connection"""
        await self._pool.release(conn)
        async with self._lock:
            self._current_acquired -= 1

    async def close(self):
        """Đóng pool"""
        await self._pool.close()

    @property
    def stats(self):
        """Thống kê pool"""
        return {
            "pool_size": self._pool._maxsize,
            "acquired_total": self._acquired_total,
            "currently_acquired": self._current_acquired,
            "available": self._pool._maxsize - self._current_acquired
        }

pool: Optional[MonitoredPool] = None

async def create_pool() -> MonitoredPool:
    global pool
    logger.info("Creating database pool...")
    base_pool = await asyncpg.create_pool(dsn=DATABASE_URL, **POOL_CONFIG)
    pool = MonitoredPool(base_pool)
    await wait_for_database(pool)
    logger.info("Connection pool ready")
    return pool


async def wait_for_database(pool: MonitoredPool, retries: int = 10, delay: int = 2) -> None:
    for attempt in range(retries):
        try:
            # Thêm await trước pool.acquire()
            async with await pool.acquire() as conn:
                start = time.time()
                await conn.execute("SELECT 1")
                query_time = time.time() - start

                if query_time > 0.5:
                    logger.warning(f"Database slow response: {query_time:.2f}s")

            logger.info("Database connection test passed")
            return
        except Exception as e:
            logger.warning(f"DB check failed (attempt {attempt + 1}): {e}")
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay * (attempt + 1))

@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    global pool
    if pool is None:
        pool = await create_pool()
    async with await pool.acquire() as conn:
        yield conn

async def close_pool():
    global pool
    if pool:
        logger.info("Closing database pool...")
        await pool.close()
        pool = None


async def monitor_pool(interval: int = 5):
    while True:
        if pool:
            stats = pool.stats
            logger.info(f"POOL STATS: {stats}")

            # Tự động điều chỉnh pool size
            await pool.adjust_pool_size()

            # Cảnh báo chi tiết
            if stats['available'] < 10:
                logger.warning("⚠️ Low available connections!")
            if stats['currently_acquired'] / stats['pool_size'] > 0.9:
                logger.error("‼️ Connection pool nearing capacity!")

        await asyncio.sleep(interval)


@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    global pool
    if pool is None:
        pool = await create_pool()

    try:
        async with await pool.acquire() as conn:
            yield conn
    except asyncpg.exceptions.TooManyConnectionsError:
        logger.error("Database connection pool exhausted")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await create_pool()
        monitor_task = asyncio.create_task(monitor_pool())
        app.state._monitor_task = monitor_task

        # Health check background task
        async def health_check():
            while True:
                await asyncio.sleep(60)
                await wait_for_database(pool, retries=1)

        app.state._health_task = asyncio.create_task(health_check())

        yield

    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        raise
    finally:
        tasks = [
            app.state._monitor_task,
            getattr(app.state, "_health_task", None)
        ]

        for task in tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        await close_pool()

async def _finalize_shutdown(task):
    try:
        await task
    except asyncio.CancelledError:
        logger.info("[LIFESPAN] Monitor task cancelled")
    try:
        await close_pool()
    except Exception as e:
        logger.warning(f"[LIFESPAN] Error while closing pool: {e}")
