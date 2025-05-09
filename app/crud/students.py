from app.database import get_connection

async def create_student(data):
    conn = await get_connection()
    query = """
        INSERT INTO students (name, email, date_of_birth, class_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id, name, email, date_of_birth, class_id;
    """
    student = await conn.fetchrow(query, data.name, data.email, data.date_of_birth, data.class_id)
    await conn.close()
    return dict(student)

async def get_all_students():
    conn = await get_connection()
    students = await conn.fetch("SELECT id, name, email, date_of_birth, class_id FROM students")
    await conn.close()
    return [dict(s) for s in students]

async def get_student_by_id(student_id):
    conn = await get_connection()
    student = await conn.fetchrow("SELECT id, name, email, date_of_birth, class_id FROM students WHERE id = $1", student_id)
    await conn.close()
    return dict(student) if student else None

async def update_student(student_id, data):
    conn = await get_connection()
    query = """
        UPDATE students SET name=$1, email=$2, date_of_birth=$3, class_id=$4
        WHERE id=$5 RETURNING id, name, email, date_of_birth, class_id;
    """
    updated = await conn.fetchrow(query, data.name, data.email, data.date_of_birth, data.class_id, student_id)
    await conn.close()
    return dict(updated) if updated else None

async def delete_student(student_id):
    conn = await get_connection()
    await conn.execute("DELETE FROM students WHERE id = $1", student_id)
    await conn.close()
    return True
