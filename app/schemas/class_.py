from pydantic import BaseModel

class ClassCreate(BaseModel):
    name: str
    grade: str
    teacher_name: str

class ClassOut(ClassCreate):
    id: int
