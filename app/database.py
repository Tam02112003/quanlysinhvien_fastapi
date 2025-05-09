import os
import asyncpg
import asyncio
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def wait_for_database(pool=None):
    retries = 10
    for i in range(retries):
        try:
            # Kiểm tra kết nối với pool nếu có
            if pool:
                async with pool.acquire() as conn:
                    pass
            else:
                # Kết nối trực tiếp nếu không có pool
                conn = await asyncpg.connect(DATABASE_URL)
                await conn.close()
            print("Cơ sở dữ liệu đã sẵn sàng!")
            return
        except Exception as e:
            print(f"Thử kết nối lần {i + 1} thất bại: {e}")
            await asyncio.sleep(5)
    raise Exception("Cơ sở dữ liệu không sẵn sàng sau nhiều lần thử.")

async def get_connection():
    # Tạo pool kết nối với max_size 10 (tùy chỉnh theo nhu cầu)
    pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=5, max_size=2000)
    await wait_for_database(pool)
    return pool

# Sử dụng connection pool trong các thao tác cơ sở dữ liệu
async def fetch_data():
    pool = await get_connection()
    async with pool.acquire() as conn:
        result = await conn.fetch("SELECT * FROM your_table;")
        print(result)
