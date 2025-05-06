import asyncpg

DATABASE_URL = "postgresql://postgres:minhtam123@localhost:5432/studentdb"

async def get_connection():
    return await asyncpg.connect(DATABASE_URL)