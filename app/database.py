import os
import asyncpg
import asyncio
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def wait_for_database():
    retries = 10
    for i in range(retries):
        try:
            conn = await asyncpg.connect(DATABASE_URL)
            await conn.close()
            print("Cơ sở dữ liệu đã sẵn sàng!")
            return
        except Exception as e:
            print(f"Thử kết nối lần {i + 1} thất bại: {e}")
            await asyncio.sleep(5)
    raise Exception("Cơ sở dữ liệu không sẵn sàng sau nhiều lần thử.")

async def get_connection():
    await wait_for_database()
    return await asyncpg.connect(DATABASE_URL)