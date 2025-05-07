from fastapi import APIRouter, HTTPException
from app.schemas.class_ import ClassCreate, ClassOut
from app.crud import classes
from app.crud.classes import get_classes_students_counts

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("/class-stats")
async def class_stats():
    return await get_classes_students_counts()

@router.get("/", response_model=list[ClassOut])
async def get_all():
    return await classes.get_all_classes()

@router.post("/", response_model=ClassOut)
async def create(c: ClassCreate):
    return await classes.create_class(c)

@router.get("/{class_id}", response_model=ClassOut)
async def get_one(class_id: int):
    c = await classes.get_class_by_id(class_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return c

@router.put("/{class_id}", response_model=ClassOut)
async def update(class_id: int, c: ClassCreate):
    res = await classes.update_class(class_id, c)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return res

@router.delete("/{class_id}")
async def delete(class_id: int):
    await classes.delete_class(class_id)
    return {"message": "Deleted"}


