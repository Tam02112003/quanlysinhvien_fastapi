from fastapi import APIRouter,Query, HTTPException
from app.schemas.student import StudentCreate, StudentOut
from app.crud import students
from app.crud.search import find_student_with_class_by_name

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=StudentOut)
async def create(student: StudentCreate):
    return await students.create_student(student)

@router.get("/search")
async def search_student_by_name(name: str = Query(..., description="Tên sinh viên")):
    results = await find_student_with_class_by_name(name)
    if not results:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return results


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