from fastapi import Query,HTTPException,APIRouter
from app.crud.search import find_student_with_class_by_name

router = APIRouter(prefix="/name", tags=["Search"])

@router.get("/search")
async def search_student_by_name(name: str = Query(..., description="Tên sinh viên")):
    results = await find_student_with_class_by_name(name)
    if not results:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return results
