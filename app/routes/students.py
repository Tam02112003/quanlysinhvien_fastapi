from fastapi import APIRouter, HTTPException
from app.schemas.student import StudentCreate, StudentOut
from app.crud import students

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=StudentOut)
async def create(student: StudentCreate):
    return await students.create_student(student)

@router.get("/", response_model=list[StudentOut])
async def get_all():
    return await students.get_all_students()

@router.get("/{student_id}", response_model=StudentOut)
async def get_one(student_id: int):
    s = await students.get_student_by_id(student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    return s

@router.put("/{student_id}", response_model=StudentOut)
async def update(student_id: int, student: StudentCreate):
    s = await students.update_student(student_id, student)
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    return s

@router.delete("/{student_id}")
async def delete(student_id: int):
    await students.delete_student(student_id)
    return {"message": "Deleted"}