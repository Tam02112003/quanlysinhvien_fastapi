from fastapi import Query,HTTPException,APIRouter
from app.crud.search import find_student_with_class_by_name

router = APIRouter(prefix="/name", tags=["Search"])


@router.get("/search")
async def search_student_by_name(
        name: str = Query(..., description="Tên sinh viên"),
        limit: int = Query(50, description="Số lượng kết quả trả về"),
        page: int = Query(1, description="Trang kết quả", ge=1)
):
    offset = (page - 1) * limit
    results = await find_student_with_class_by_name(name, limit, offset)
    if not results:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")

    return {
        "data": results,
        "pagination": {
            "current_page": page,
            "per_page": limit,
            "total_results": len(results)
        }
    }