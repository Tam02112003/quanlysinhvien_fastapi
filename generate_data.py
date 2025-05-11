import asyncio
import asyncpg
from faker import Faker
import random
from datetime import datetime, timedelta

async def generate_data():
    # Kết nối database
    conn = await asyncpg.connect(
        user='postgres',
        password='minhtam123',  # Thay bằng mật khẩu bạn đặt
        database='studentdb',
        host='localhost'
    )

    fake = Faker()
    used_emails = set()
    # Tạo 50 lớp học
    print("Đang tạo lớp học...")
    class_ids = []
    for i in range(50):
        class_name = f"Lớp {fake.random_letter().upper()}{fake.random_int(1, 12)}"
        grade = f"Khối {fake.random_int(1, 12)}"
        teacher = fake.name()

        record = await conn.fetchrow(
            "INSERT INTO classes(name, grade, teacher_name) VALUES($1, $2, $3) RETURNING id",
            class_name, grade, teacher
        )
        class_ids.append(record['id'])

    # Tạo 1,000,000 sinh viên
        # Tạo sinh viên
        batch_size = 10000
        total_records = 1000000

        for i in range(0, total_records, batch_size):
            values = []
            for _ in range(batch_size):
                full_name = fake.name()

                # Tạo email độc nhất
                while True:
                    email_prefix = f"{full_name.replace(' ', '.').lower()}{random.randint(1, 10000)}"
                    email = f"{email_prefix}@example.com"
                    if email not in used_emails:
                        used_emails.add(email)
                        break

                dob = fake.date_of_birth(minimum_age=15, maximum_age=20)
                class_id = random.choice(class_ids) if random.random() > 0.1 else None

                values.append((full_name, email, dob, class_id))

            await conn.executemany(
                """INSERT INTO students(name, email, date_of_birth, class_id) 
                VALUES($1, $2, $3, $4)""",
                values
            )

            print(f"Đã thêm {min(i + batch_size, total_records)}/{total_records} bản ghi")

        await conn.close()

asyncio.run(generate_data())