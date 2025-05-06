from app.database import get_connection

async def create_class(data):
    conn = await get_connection()
    query = """
        INSERT INTO classes (name, grade, teacher_name)
        VALUES ($1, $2, $3) RETURNING *;
    """
    row = await conn.fetchrow(query, data.name, data.grade, data.teacher_name)
    await conn.close()
    return dict(row)

async def get_all_classes():
    conn = await get_connection()
    rows = await conn.fetch("SELECT * FROM classes")
    await conn.close()
    return [dict(r) for r in rows]

async def get_class_by_id(class_id):
    conn = await get_connection()
    row = await conn.fetchrow("SELECT * FROM classes WHERE id = $1", class_id)
    await conn.close()
    return dict(row) if row else None

async def update_class(class_id, data):
    conn = await get_connection()
    query = """
        UPDATE classes SET name=$1, grade=$2, teacher_name=$3
        WHERE id=$4 RETURNING *;
    """
    row = await conn.fetchrow(query, data.name, data.grade, data.teacher_name, class_id)
    await conn.close()
    return dict(row) if row else None

async def delete_class(class_id):
    conn = await get_connection()
    await conn.execute("DELETE FROM classes WHERE id = $1", class_id)
    await conn.close()
    return True
