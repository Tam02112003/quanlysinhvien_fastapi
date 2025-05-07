from app.database import get_connection

async def find_student_with_class_by_name(name: str):
    conn = await get_connection()
    query = """
        SELECT s.id, s.name, s.email, s.date_of_birth, c.name AS class_name
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE s.name ILIKE $1
    """
    result = await conn.fetch(query, f"%{name}%")
    await conn.close()
    return [dict(row) for row in result]